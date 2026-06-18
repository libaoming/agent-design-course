---
title: Why "the optimization worked" means nothing without the logs to back it up
module: e
order: 6
slug: observability-and-eval
nav: Observability & Eval
summary: Cache hits, leaner context, compaction kicking in—every one of these claims has to be reconstructable from the usage logs. An optimization with no observability is just superstition.
tags: [上下文工程, 可观测, 评估, usage, p95, Goodhart]
---

## Setting up the target: you say the optimization worked—but which number are you looking at?

The previous lectures walked through a chain of moves: fatten up the static prefix so cache hits, pull the lookup table out of the prompt to save tokens, wire up compaction for history. After each step you felt "okay, that saved something." But the moment someone presses you—**how much did it save, and how do you know?**—you probably can't answer, or you toss out a number on the fly, and that number is usually the most prominent one on the dashboard and also the least trustworthy.

This lecture is where the whole of Module E comes together. Every earlier lecture planted a line like "this should save / should be faster"—all of them design-time assumptions. Observability and eval is the layer that converts every one of those verbal IOUs into a number: how many tokens the model **actually** received this turn, whether the cache really hit, and whether things genuinely got better after your change or you just wanted them to.

There's only one core question: **for every optimization you claim, what's your proof?** One of CE's principles is "iterative optimization can't run on gut feel"—CE without observability is, at bottom, superstition. CONTEXT.md is your **design-time ledger** (what you think the model sees), and the usage logs are the **runtime reconciliation statement** (what the model actually sees). The two must reconcile; **the gap that won't reconcile is the dark matter in your context.**

Inheriting any Agent, two questions are enough to gauge its CE maturity: "Where does each turn's usage land?" and "Have the token estimates in CONTEXT.md ever been reconciled against the logs?" If neither can be answered, this project's context engineering is still stuck at the design-doc stage.

## Framework: first learn to read usage, then build three layers of observability, finally evaluate across 4 dimensions

### The usage fields: the two camps measure things in exactly opposite ways—misread it and you're off by an order of magnitude

The thing that trips people up isn't how elaborate the observability setup is; it's the very first step—reading the usage fields correctly. The same "token usage" is measured in opposite directions by the two major API families, and mixing them up guarantees an error.

Under Anthropic's convention, the four fields are **mutually exclusive and non-overlapping**:

| Field | Meaning | Pricing (relative to input) |
|------|------|---------|
| `input_tokens` | Uncached portion only, **excludes the two below** | 1× |
| `cache_creation_input_tokens` | Portion newly written to cache this turn | 1.25× (5min) / 2× (1h) |
| `cache_read_input_tokens` | Portion read from cache this turn | 0.1× |
| `output_tokens` | Output | output price |

> [!WARNING]
> True total input = `input` + `cache_creation` + `cache_read`. The most lethal misread is seeing `input_tokens: 800` and declaring "this turn was only 800"—there could be several thousand more tokens sitting in `cache_read`. **Don't let the smallest field fool you.**

The OpenAI-compatible convention is the exact reverse: `prompt_tokens` is the **cache-inclusive total**, `prompt_tokens_details.cached_tokens` is the cache-hit subset within it, and `completion_tokens` is the output. Anthropic's `input_tokens` is "the remainder after subtracting cache," while OpenAI's `prompt_tokens` is "the total including cache"—**one has subtracted, the other hasn't.** When comparing numbers across endpoints or writing a generic logging layer, you must first normalize to two columns, "total + cache hits," or the logs for the very same conversation can differ by a whole cache's worth of tokens between the two sides.

### Three layers of observability: from a single log line to a comparison table

Observability isn't some fancy dashboard; it's three layers stacked on top of each other, each answering a class of question.

| Layer | What it looks like | What it answers |
|------|---------|---------|
| Layer 1 · per-turn snapshot | One jsonl/tsv line per turn: `{turn, ts, prompt_tokens, completion_tokens, cached, ttft, duration, cancelled}` | How much the model saw this turn, how much it cost, how long it waited |
| Layer 2 · session curve | One line per conversation, x=turn, y=prompt_tokens | How history grew, whether compaction fired, whether you hit the context ceiling |
| Layer 3 · version comparison | Same fixture set × N runs × before/after change → 4-dimension comparison table | Whether this change actually helped, on which dimension, and at what cost on which dimension |

Layer 1 is the foundation: **one line per turn, machine-readable**—exactly the "tsv bookkeeping" discipline common to long-running Agents, and the input to any automated eval harness.

The key to Layer 2 is that **the shape of the curve talks**: linear growth = no compaction, full history retained; sawtooth drops = compaction / truncation fired; a sudden step = some turn injected a big chunk (a large tool_result JSON, a memory dump); a flat line = fixed-window truncation. You don't even need to read the content—the shape alone tells you which turn the problem is in.

Layer 3 has the hardest discipline: **baseline first, then change, and move only one variable at a time.** Change the system prompt and casually swap the model too, and your attribution is worthless—you'll never be able to say which move caused the change.

### 4-dimension eval: efficiency and cost are machine-measurable, quality and experience must keep a human in the loop

Token counts alone aren't enough. Whether a change actually "pays off" has to be judged across four dimensions together.

| Dimension | Metric | How to measure | Fully automatable? |
|------|------|--------|-----------|
| Efficiency | input/output tokens, cache hit rate, ttft, total | usage fields + timestamps | pure machine |
| Quality | response relevance, task completion rate | smoke assertions + LLM-as-judge + manual spot-check | semi-automatic |
| Experience | satisfaction, perceived first-turn latency (look at **p95**, not the average) | real interaction + user feedback | human required |
| Cost | per-turn / monthly cost | usage × unit price, accumulated | pure machine |

Three takeaways for putting this into practice:

First, **efficiency and cost can run fully automatically; quality and experience must have a human backstop.** The quality dimension can be semi-automated with LLM-as-judge, but the judge itself needs periodic manual calibration, or it quietly drifts and no one notices.

Second, **look at p95 for latency, not the average.** A voice scenario with an average ttft of 800ms looks healthy, but if p95 is 3s, what the user remembers is that one awkward 3-second silence. Experience is determined by the tail; the average lies.

Third, the four dimensions often **fight each other**: cut tokens and you raise efficiency but hurt quality; pre-generate to lower latency but raise cost. So the comparison table must show all four dimensions together—**a one-dimensional victory lap = an incomplete eval.**

## Data / cases: three de-identified field stories

**The dashboard's convention underestimated real traffic by nearly two orders of magnitude.** One team summed up all the historical session usage for a mature Agent product of theirs and found that the token figure shown on the usual stats dashboard had only taken the smallest one or two of the four fields (`input` + `output`), completely ignoring the cache pair. Real traffic was nearly two orders of magnitude higher than the dashboard number. This isn't a toy problem—"don't let the smallest field fool you" can be off by about 90× on a real ledger. Incidentally, `input_tokens` made up less than 1% of the true total for this product, which actually confirms its cache engineering was excellent: over ninety percent of input went through the 0.1× cache read. **Before reporting a token number, first clarify which convention it's in**—display convention, traffic convention, and billing convention are three completely different numbers.

**A framework black box can hide the messages, but not the metrics.** A certain voice Agent used a framework that hosted the conversation history internally—you literally can't see that array in the code—so someone concluded "history growth is unmeasurable, the framework is a black box." Not true: the framework emits a metrics event after every LLM call, and it carries `prompt_tokens`. Hang a listener on it, copy that number into a jsonl every turn, and you can reconstruct the black box's input volume from the outside, turn by turn, **without touching the framework's internals at all.** Connect the per-turn `prompt_tokens` into a line—linear growth nails down "no compaction, full retention"—then extrapolate by slope to the expected turn count, and you'll know how far a long conversation is from the context ceiling and whether you need to take over compaction yourself. The black box hides the content, not the input volume.

**All metrics green, and you can still crash.** Suppose you've wired up full observability for some Agent, shipped three optimizations in a month, and the dashboard shows per-turn cost down 55% and ttft down 30%—you're about to declare victory in the weekly report. Hold on—this report is missing the quality and experience dimensions, which happen to be the two dimensions a machine can't measure on its own. And the means of cutting cost by 55% (trimming the prompt, capping output length, turning off pre-generation) could each be quietly hurting call quality and connection experience, and the dashboard **simply has no column for those two**—if they're hurt, it doesn't show. This is the Goodhart trap: **once a metric becomes a target, it stops being a good metric.** Hand someone a set of automatic metrics and the instinct is to optimize the metric itself, not the real workflow behind it.

## Actionable practices: two tracks, PM and engineering

**The PM lens—use it to judge and to sign off:**

1. When anyone reports "the optimization worked," first ask "which convention is your number in, and is there a baseline to compare against?" Any "it got better" without a baseline is treated as unverified.
2. Signing off on a CE change means demanding all four dimensions: not just how many tokens / dollars were saved, but whether the quality and experience columns have a manual spot-check behind them. A weekly report that only mentions efficiency and cost is a danger sign.
3. Watch for Goodhart: once you've set automatic metrics, keep an eye on whether the team is improving the real workflow or just pleasing the metric itself. Metrics serve the workflow, not the other way around.
4. Any latency-related commitment must come with both p50 and p95. A latency report that gives only the average is no report at all.

**The engineering lens—use it to build observability:**

1. **Layer-1 per-turn logging stays always-on—it's not a debug switch.** Turning logging on only after something breaks means you have no baseline; when a problem arrives there's nothing to compare against and no way to attribute it.
2. When writing a generic logging layer, normalize usage first: no matter whose convention the underlying API uses, land it uniformly as three columns—"total + cache hits + output"—so you can compare directly across endpoints.
3. Record failed turns and voided turns too, flagged in a separate column. Voided calls from pre-generation / retries still cost you input fees; logging only successful turns misses a cost black hole.
4. Always do observability at the API-return layer, **never at the prompt layer**—don't expect the model to self-report its token count; it doesn't know its own token count, and asking it to is pure hallucination.
5. Hold to three eval disciplines: baseline before change, one variable at a time, and `runs ≥ 3` averaged (LLMs are non-deterministic, a single result doesn't count). Fixtures must cover the scenario the changed item serves—if you touched the ASR disambiguation table, the fixtures had better contain typo samples.
6. The output of observability isn't the log file itself, it's **backfilling CONTEXT.md**: the real measured tokens and the confirmed dark matter all get written back into the design ledger. This is how CONTEXT.md functions as a living document.

By the way, this layer doesn't mean reinventing the wheel from scratch. Some mature desktop clients already turn "what this turn's context is made of" into a user-visible breakdown bar (how much is system / tools / memory / history), and some CLIs offer a similar `/context` command—they are the runtime-visualization version of CONTEXT.md. Design ledger (static document) → reconciliation statement (per-turn logs) → dashboard (live visualization) are three levels of the same thing. Your own Agent doesn't have to reach the third level, but the first-level per-turn jsonl is the floor.

## Wrapping up

> Context you can't observe doesn't exist—you can't optimize what you can't see. CONTEXT.md is the design ledger, the usage logs are the reconciliation statement, and the gap that won't reconcile is the dark matter. This is where the whole of Module E closes a loop: first light up the seven layers and balance the books, then talk about how to save and how to stay stable—and every "saved it / stabilized it" ultimately has to come back to this log to be put to the test.
