---
title: Why a Mismanaged Context Window Makes Even the Smartest Agent Dumb
module: b
order: 1
slug: context-engineering
nav: Context Engineering
summary: Context is an Agent's scarcest resource—treat it as a system to be engineered, using a seven-dimension lens and a composition audit.
tags: [工程地基, 上下文工程, 七维透镜]
---

## Setting the Target: How an Agent Dies When Context Goes Unmanaged

Let's start with a counterintuitive fact: what determines whether an Agent is actually usable is usually not how strong the model is or how elegantly the prompt is written—it's **what actually gets packed into its context window on every single turn**.

The context window is an Agent's scarcest resource. It has a hard ceiling; every extra token you stuff in crowds out room for another token, and every stuffing costs money. Mismanage it, and things break in three typical ways:

**First, the window blows up.** Multi-turn conversation, multiple tool calls, long-document retrieval injection—tokens only grow, never shrink. Once you approach the ceiling, either you get an error and truncation, or the framework quietly drops the earliest few turns—and what gets dropped is often exactly that crucial original constraint about "what the user actually wants." The Agent then starts answering off-topic, and you assume the model is just dumb.

**Second, lost in the middle.** This is a repeatedly verified phenomenon: when critical information is buried in the middle of a long context, the model's utilization of it is significantly lower than when it sits at the beginning or end. In other words, "stuffed in" does not equal "actually used." You retrieve ten passages and dump them all in, and the genuinely useful one is sandwiched as passage six—the model will most likely look right past it. **Stuffed in ≠ read.**

**Third, and most insidious—silent-default contamination.** The Agent SDK, framework, or plugin you're using will inject things into your context without your knowledge: a default system preamble, auto-concatenated tool descriptions, an implicit history summary, a skill some hook sneaks in. These "silent defaults" aren't written in your code, yet they really do occupy the window and shape the output. You tune your prompt for ages with no effect, and the real source of contamination may be entirely outside your field of view.

These three ailments share a common root cause: **most people optimize context as if it were "copywriting," when it's actually a "system" that needs to be engineered.** Optimizing how to phrase a passage well is Prompt Engineering; assembling the complete context the Agent sees on each turn is Context Engineering. The latter is the core battleground of Agent engineering.

## Framework: The Seven-Dimension Lens

Any extension system that "injects knowledge into an Agent on demand"—plugins, skill routing, rules, RAG injection—is fundamentally answering the same question: **at the right moment, with the right judgment, within budget, put the right knowledge into the Agent's head—and don't put in the wrong thing.**

Break that question down and you get seven dimensions. They're not an arbitrarily listed checklist but a chain of decisions: first decide when to intervene, then decide what to judge by, then rank, cap the budget, set guardrails, and finally solve component cooperation and observability.

| # | Dimension (the question to answer) | Focus / what to probe when dissecting |
|---|---|---|
| 1 | When · when to intervene | At which node in the Agent loop do you step in? Too early wastes budget; too late and you can't influence the decision in time |
| 2 | Signal · what to judge by | What signal decides whether to inject? How do you trade off precision and recall |
| 3 | Rank · how to order | How do you prioritize multiple candidates? Is the scoring explainable or based on dark arts |
| 4 | Budget · resource constraint | How is the context budget managed? Have you written "scarcity" into the code as a hard constraint |
| 5 | Guardrail · how to prevent errors | How do you prevent injecting the wrong thing or injecting too much? Do you accept that "wrong injection is worse than no injection" |
| 6 | State · cross-component cooperation | Between stateless components, how do you share judgments already computed |
| 7 | Observe · observability | Can this black box be debugged, verified, regression-tested |

These seven dimensions are useful because they break an invisible, intangible "attention scheduling" problem into seven concrete engineering questions you can answer cell by cell. It's both a lens for dissecting other people's systems and a checklist for designing your own.

Why do dimensions 4 and 5 carry the weight? Because the restraint of mature Agent tooling lives entirely in these two: **better to under-inject than to contaminate the context.** A system that can't tell its budget apart and has no defense against wrong injection will, no matter how flashy the first three dimensions are, degrade under real load into the three ailments from section one.

## Data / Case: What a Production-Grade Injection Engine Looks Like

Below we use a real extension system (anonymized as "a certain Agent plugin") to fill in all seven dimensions and see the shape of an injection engine that's been seriously engineered. This plugin manages twenty-some skills and several commands, and its real product proposition is not "lots of features" but: on every turn, decide which few pages of knowledge are worth occupying the precious window.

| Dimension | This plugin's engineering answer |
|---|---|
| When | 4 hook points: session start / before tool call / when the user submits a prompt / session end |
| Signal | File globs, bash command regexes, import statements, prompt keywords, dependency-manifest mapping—multi-signal fusion |
| Rank | Weighted scoring: exact phrase +6 / all-match +4 / any-match +1 (capped at 2), plus sniffer hit +5 |
| Budget | At most 18KB injected before a tool call, at most 8KB on user submit; at most 3 / 2 skills respectively |
| Guardrail | A negative signal vetoes outright (score driven to negative infinity); if it detects a test framework already in use, it suppresses the related injection; session-level atomic dedup |
| State | Hooks use an environment variable as a bus: the sniffer first writes a "possibly relevant skills" list, and later hooks read it to add score |
| Observe | Provides explain and doctor commands, leveled logging, golden snapshot tests |

Three designs here are worth pulling out on their own, and they map neatly onto the three ailments from section one:

- **Negative signal = negative infinity.** A single negative signal can instantly kill an entire skill's injection. This is the conservative stance of "rather not load than load wrong"—a direct cure for "silent-default contamination."
- **Adaptive lexical fallback.** The lower the exact score, the more it dares to amplify with fuzzy matching; when the score is near the threshold, it only nudges. This is a confidence-calibration scheme—essentially shifting gears dynamically between precision and recall.
- **Translate complaints into skills.** Regex detects natural-language complaints like "works locally but not in prod," "stuck / timeout," "blank screen," and routes them to the corresponding troubleshooting skill; but once the user mentions they're using a particular test framework, it suppresses the injection.

![Context split into a stable block (persona + tools + instructions, unchanged across the whole call, hits cache) and a volatile block (runtime state, rewritten each turn)](../assets/diagrams/context-engineering.svg)

Now for the cautionary tale. Another voice-Agent project hit a classic Budget / observability pitfall early on: it mixed the runtime context that changes every turn (current state, fields already collected, the prompt for the next call) into the stable system block. The result: prompt caching was wholly invalidated, and a thirty-turn phone call rewrote over two hundred thousand tokens at full price. The fix was to split the context into two blocks—a stable block (persona + tools + stage instructions, unchanged across the whole call) and a volatile block (runtime context, not cached). After the split, the cache hit rate climbed back to about 97%, and per-call cost dropped by more than eighty percent.

The general lesson here is: **context is not only about "what to stuff in" but also "in what structure to stuff it."** Mixing stable and volatile together both burns money (cache invalidation) and is hard to debug (you don't know which block is changing).

## Actionable Practices: Two Checklists

**Checklist one · How to draw a context composition table (do this before building)**: before you write the first line of Agent code, list out "every segment the model will see on this turn" as a table, and answer clearly for each segment:

- What this segment is (system persona / tool description / history / retrieval injection / runtime state / framework default)
- Where it comes from (written by me / added by the SDK / injected by a hook / left over from the previous turn)
- Whether it changes each turn (stable → can go in the cache block; volatile → its own block, not cached)
- How much budget it takes (give a token order of magnitude, mark who the big consumer is)
- Where in the window it sits (don't bury critical constraints in the middle—cure for lost in the middle)
- What its injection condition is (always resident unconditionally / enters only when a signal is met / killed if there's a negative signal)
- How you'd know if it goes wrong (does this segment have logging, can it be verified in isolation)

**Checklist two · How to audit an SDK's silent defaults (do this when taking over an existing framework)**: every Agent SDK / framework / plugin you use is stuffing things into the context behind your back. Audit steps:

- Dump the **complete final prompt** of one real request and read it segment by segment
- Annotate the source of each segment: which I wrote explicitly, which the framework concatenated by default (system preamble, tool schema, auto summary, implicit few-shot)
- Count tokens: default config vs. everything-optional-turned-off, compare how much the window occupancy differs—the difference is the bulk of the "silent defaults"
- Check hooks / middleware: is any third-party component sneaking in an injection at some lifecycle node
- Turn the audit conclusion into a CONTEXT.md, writing clearly "which blocks make up this Agent's per-turn context, and who owns each"

Put the two checklists together, and you turn "context" from a murky black box into an engineering blueprint you can inspect cell by cell and defend item by item.

## Closing

> Context is an Agent's scarcest resource—at the right moment, with the right judgment, within budget, put the right knowledge in, and don't put in the wrong thing. Stop treating it as "a sentence to phrase well"; engineer it as a system that has a budget, a structure, failure modes, and a need to be observed.
