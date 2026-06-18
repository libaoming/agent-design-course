---
title: Why an Agent Without an Eval System Can Only Iterate on Gut Feel
module: b
order: 4
slug: evaluation
nav: Evaluation & Benchmarks
summary: A thorough walkthrough of the four pieces — Agent eval dimensions, building test sets, input-quality tiered routing, and model-routing selection.
tags: [工程地基, 评测, Benchmark]
---

## Setting the Target: How an Agent Dies Without Systematic Eval

Picture the daily life of an Agent team with no eval system. Someone posts in the group chat, "this version feels smarter today," so it gets merged and shipped. The next day someone else says, "why did it get dumber again?" — and nobody can pin down which change introduced the regression, because there's no repeatable yardstick at all. This is **gut-feel iteration**: every "improvement" is a vibe, and every "degradation" has no traceable root cause.

Without an eval system, you'll hit at least three traps at once:

1. **Gut-feel iteration**: the direction of iteration relies on subjective impressions, and you can't answer "did this change actually go up or down?"
2. **Can't localize regressions**: which prompt change last week introduced today's bad case? With no fixed test set as a baseline for comparison, a regression is a black hole.
3. **High Benchmark scores but real-world collapse**: the model looks great on public leaderboards, then collapses the moment it ships. The cause isn't the model — it's the input.

Remember this judgment that runs through the whole lecture: **90% of AI product failures are input problems, not model problems.** The whole point of an eval system is to swap "I think" for "I measured." It takes these four pieces fitted together to make a complete eval system: eval dimensions, test sets, input-quality tiered routing, and model-routing selection.

## Framework: The Eval Dimension System

An Agent needs numbers on at least five dimensions:

| Dimension | What it measures | Method |
|---|---|---|
| Recall | Share of real issues that get correctly identified | Run against an expert-labeled positive test set, count missed detections |
| Precision | Share of flagged issues that are genuinely problems | Run against a clean negative test set, count false positives |
| Suggestion usefulness | Whether the fix suggestions are directly usable | Sample for human evaluation, look at the adoption rate of suggestions |
| Issue-type coverage | Whether every category of issue gets covered | Bucket by issue type and count hits |
| P99 latency / token cost | Whether responses are fast enough, and how much one call costs | Instrument production to track tail latency and token consumption |

There's a key trade-off here: **precision and recall can't both be maxed out at once, and the priority depends on which kind of error is more costly in your business.**

- Code-review scenario: **precision first**. Too many false positives cause Alert Fatigue — once developers start ignoring alerts, the whole tool is dead.
- Contract-review scenario: **recall first**. Missing a single risky clause can carry enormous legal cost; better to over-report than to under-report.

The same set of dimensions needs weights assigned according to the business's "error cost structure." This is the PM's lens, not the algorithm's — the algorithm only hands you an F1 score; the PM decides whether this scenario should lean toward precision or recall.

One more view: a capability breakdown from public Benchmarks. AgentBench decomposes Agent capability into five core dimensions: instruction following, coding ability, knowledge acquisition, logical reasoning, and commonsense understanding. A few of its key findings are worth remembering: the dominant failure type is TLE (exceeding the turn limit), accounting for 23%–82%, the single biggest bottleneck — the Agent isn't incapable, it just can't work its way out and burns through its turns; pairing high-quality alignment data with a small model is roughly as effective as low-quality data with a large model; and training on code data is a double-edged sword — static-process ability rises but general reasoning ability drops.

## Data & Case: A Benchmark Cheat Sheet and a Real Incident

The same Benchmark can be wildly more or less relevant to different businesses; when you read a leaderboard, always ask "is this relevant to my scenario?":

| Benchmark | What it measures | Relevance to contract review |
|---|---|---|
| MMLU | Breadth of knowledge | Low |
| SWE-bench Verified | Code fixing | Very low |
| GAIA | Multi-step tasks | Medium |
| LegalBench | Legal-task specialization | High |
| LongBench | Long-document understanding | High |
| TruthfulQA / HaluEval | Hallucination rate | High |

For a contract-review Agent, picking a model by staring at MMLU and SWE-bench scores is barking up the wrong tree; what you should really look at are these three — LegalBench, LongBench, and hallucination rate. **Benchmarks aren't better when there are more of them; they're better when they're more relevant.**

Now a real incident (anonymized). A legal-document review Agent had beautiful metrics on its offline test set and crashed the moment it shipped. The post-mortem found the root cause wasn't the model but the input: users were uploading scanned documents, the OCR came back as a mess of garbage text, and the model gamely answered against the garbage, producing nonsense. Why couldn't this be caught before launch? Three root causes:

1. **Test-set bias**: the quality distribution of the test samples was idealized — all clean scans, no garbled documents.
2. **Long-tail neglect**: when building the test set, edge cases (blurry documents, missing-page documents) got skipped because they were a hassle.
3. **Missing PM lens**: the eval dimensions only watched precision and recall; nobody ever looked at "what does the distribution of input quality actually look like?"

This is where the opening line comes from — 90% of failures are in the input. If input quality had been tiered before launch, the garbled documents should never have reached the LLM in the first place; they should have been intercepted and routed to a human or a clarifying question.

## Actionable Practices

**How to build a test set**

- **Positive cases**: cases reviewed by senior experts and confirmed to contain real issues.
- **Negative cases**: clean cases that experts have labeled as "no substantive issue" — used specifically to test false positives and stress precision. Lots of people only accumulate positives; negatives are just as important as positives.
- **Scale**: 200–500 offline cases as a base, plus 20–50 cases for human evaluation.
- **Dual baseline comparison**: don't just look at the Agent's own score — compare against baselines: bare LLM vs Agent, traditional static tool vs Agent.
- **Cover the long tail**: deliberately put edge cases like blurry, missing-page, and garbled documents in; don't skip them for convenience.

**Launch process and production-data feedback**: meet the offline test-set bar → run Shadow Mode (about 2 weeks) → 10% canary → gradually ramp up. The core online metric to watch is suggestion adoption rate, with a reference line of ≥ 40%. Launch isn't the finish line; the test set has to be continuously recalibrated by feeding production data back in: at T+1d, set up input-quality anomaly monitoring; at T+1w, sample real failure cases and add them to the test set; at T+1m, iterate monthly and re-run the baseline; at T+3m, the test-set distribution gradually converges to the real production distribution. The core idea: let the test set slowly grow from an "idealized distribution" into the "production distribution," otherwise you're forever testing a world that doesn't exist.

**Input-quality tiered routing**: add an ingest layer before the LLM that first scores input quality, then routes by tier based on the score. Low-quality input shouldn't reach the LLM.

| Business | Input-quality scoring dimension | Routing strategy |
|---|---|---|
| Contract review | Scan clarity / OCR confidence | Clear goes to default, blurry routes to a human |
| Voice recruiting | SNR / ASR confidence / speaking rate | Noisy switches to a phone call or routes to a human |
| Code review | Code completeness / compile pass rate | Compile failure is rejected outright |
| Customer-service Agent | Question clarity / history completeness | Ask a clarifying question if info is missing |

**How to do model-routing selection**: here you need to distinguish two orthogonal kinds of routing — input-quality tiered routing (which governs "does this input deserve to enter an LLM at all") and model routing (which selects among multiple models by task difficulty/type/cost, governing "which LLM does it enter"). The trend is that model selection is shifting from a "one-time decision before launch" to "dynamic runtime routing": automatically picking a model by task difficulty, sending hard tasks to a frontier large model and pushing simple tasks down to a small model, saving about 25% on cost with no drop in performance. Design points: make "cost vs. quality" an adjustable knob rather than mindlessly fixing on the strongest model; the routing decision itself must be observable and replayable; and the tier boundaries get calibrated by the offline test set plus production feedback. Whether to switch on a model upgrade is decided by this framework: check the relevant Benchmark → run your own offline test set → compare cost and latency → validate in Shadow Mode → ship at 10% canary — don't skip a single step.

## Wrap-up

> 90% of failures are input problems, not model problems — so build an ingest layer in front of the LLM first: quality scoring + tiered routing, and low-quality input shouldn't reach the LLM. Model selection isn't done once you pick the strongest one before launch, either; it's runtime tiered routing, making "cost vs. quality" an adjustable knob — push simple tasks down, and only send hard tasks to the frontier.
