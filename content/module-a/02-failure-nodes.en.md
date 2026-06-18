---
title: Why You Can't Blame Agent Failures in the Abstract — Break Them Down by Node
module: a
order: 2
slug: failure-nodes
nav: Failure Nodes
summary: Split Agent failures into four node types — input / tool / reasoning / output — locate first, then improve.
tags: [L3, 失败节点, 维度2]
---

## Setting up the target: Skip failure classification and all you'll get is "it kind of sucks"

Start with a real scenario. A team ships a voice-conversation Agent, and ops reports that "it often answers the wrong thing." The PM forwards that line verbatim to engineering. Engineering investigates for three days and concludes: "the model has limited capabilities, wait for the next version." Two weeks later the problem is exactly the same.

The problem isn't the model — it's the attribution. "Answers the wrong thing" is a **result**, not a **node**. The same phrase "answers the wrong thing" could mean any of these:

- The user's sentence was never heard clearly in the first place (the input layer broke)
- It was heard clearly, but the tool that needed to be queried timed out and returned empty (the tool layer broke)
- The tool returned fine, but the model swapped two fields (the reasoning layer broke)
- The reasoning was correct, but the output JSON was missing a bracket and downstream parsing failed (the output layer broke)

These four versions of "answers the wrong thing" demand **completely different** fixes: the first needs noise reduction and read-back confirmation, the second needs retries and graceful degradation, the third needs prompt changes or added validation, the fourth needs format constraints. If all the PM can say is "it kind of sucks," the team is left flailing blindly across these four directions.

Three classic consequences of skipping failure classification:

1. **Vague attribution** — every problem gets dumped into "the model isn't good enough" or "not enough data." These two buckets hold anything, which means they say nothing.
2. **No localization** — you can't say which step a given failure happened at, so the engineer has to reproduce it from scratch, and investigation costs skyrocket.
3. **No improvement** — without per-node statistics, you'll never know whether changing the prompt or adding retries has higher ROI, so iteration becomes guesswork.

The PM's core value on the failure front isn't fixing bugs — it's **cutting "a blob of failure" into nodes that can be located, counted, and assigned**.

## Framework: the MECE four-way classification of failure nodes

An Agent task is essentially a pipeline: understand input → call tools → reason and decide → produce output. Failure can only happen at one of these four nodes (or along the orthogonal dimension of rollback). Cutting by node is naturally MECE — no overlaps, no gaps.

![The four-node failure pipeline: A input understanding / B tool calling / C reasoning / D output format, with rollback as an orthogonal dimension](../assets/diagrams/failure-nodes.svg)

| Category | Node | Typical symptoms | Root cause | Corresponding fix |
|------|------|---------|------|---------|
| **Type A · Input-understanding failure** | Task entry | Not heard, intent misclassified, missing parameter extraction, ambiguous phrasing | Poor physical channel, vague phrasing, lost context | Read-back confirmation, multiple-choice questioning, noise scoring, entry-point filtering |
| **Type B · Tool-calling failure** | External dependency | Timeout, rate limiting, empty return, wrong tool called | Transient network issue, dependency outage, wrong tool/parameter choice | Exponential backoff retries, graceful degradation, dual-vendor hot standby, idempotency protection |
| **Type C · Reasoning failure** | Inside the model | Swapped fields, skipped steps, hallucination, logical leaps | Ambiguous prompt, context window overflow, beyond capability boundary | Revise prompt, add intermediate validation, decompose steps, confidence gating |
| **Type D · Output-format failure** | Task exit | Invalid JSON, missing fields, structure doesn't match schema | Missing constraints, truncated long output, format drift | Structured-output constraints, schema validation, fallback regeneration on parse failure |

Beyond these four there's an **orthogonal dimension · rollback**: after a failure, did it produce side effects, and do they need cleanup? This isn't about "which node failed" but "what mess the failure left behind," so it's pulled out separately and must not be mixed into the share statistics of the four categories above. This maps to the "4+1" handling in error-recovery strategy — the main path answers how the task gets done, and rollback answers how side effects get cleaned up.

A few key judgment calls when dividing things up:

- **Type A and Type C are easily confused.** The distinguishing point: whether the input signal itself is complete. The signal never arrived (not heard) is Type A; the signal arrived but the model used it wrong is Type C.
- **Type B should be further split into transient and permanent.** Network timeouts and rate limiting are transient — retries help; a tool returning "no such data" is permanent — retrying just wastes time.
- **Type D is often mistaken for Type C.** When the reasoning content is correct but only the packaging is broken, it's Type D, solved by format constraints — don't go messing with the prompt's reasoning logic.

## Case: breaking down a Type A failure in a voice Agent

Let's land the framework above on a de-identified real case — a voice-conversation Agent built for phone scenarios. The physical channel in phone scenarios is uncontrollable (noise, network jitter, accents, slow speech from older users), so **Type A input-understanding failure is the highest-frequency failure node here**.

The team didn't treat "can't hear clearly" as one vague problem; instead they first did a root-cause split within Type A:

| Root cause | Characteristics | Handling direction |
|------|------|---------|
| Ambient noise | Empty transcripts, high ratio of filler words, very few recognized characters | Gradual persuasion to disengage / transfer to human |
| Slow user speech | Long thinking pauses, repeated confirmations | Parameter self-adaptation / don't interrupt |

The key insight is "human traits are stable, environmental signals are dynamic," so identify the human first, then judge the environment. In practice they did three things:

1. **Quantified capture** — rather than relying on a single-shot judgment, they cumulatively scored every user utterance across four signals (empty transcript, filler-word ratio, character density, short answer + pause), turning "can't hear clearly" from a subjective feeling into an observable score.
2. **Tiered response** — when the score is low, proceed normally; medium, adjust the Agent's own phrasing (avoid open-ended questions, switch to either/or); high, negotiate with the user ("would it be convenient to move somewhere else?"); over threshold, cut losses by transferring to a human and tag a lead for callback.
3. **Boundary cap** — when the character error rate exceeds threshold, trigger human intervention directly; the AI stops toughing it out. At the same time, dual-vendor hot standby auto-switches when the error rate stays over target.

Note that this also invokes Type B handling techniques (vendor hot standby = tool-layer degradation/fault tolerance). That's exactly the value of classification: **once you've located a failure at a specific node, every node has its own mature playbook to apply** — instead of being helpless in the face of "it kind of sucks."

To avoid collateral damage, they also added three layers of false-positive backstops — a confirmation-word allowlist, a legitimate-elongated-sound exemption, and a strict scoring threshold. This maps to a general rule: **failure detection itself can fail (false positives) — when instrumenting, you must monitor the false-positive rate alongside everything else.**

## Actionable practices: how to instrument for capture, and how to localize

**Instrumentation capture checklist:**

- Tag every node explicitly — a task flows through four nodes, and each node's entry/exit/exception gets a data point; forbid silent fallthrough (errors getting silently swallowed is the number-one anti-pattern).
- Failures must carry a node field — every failure record in the logs carries `failure_node ∈ {A,B,C,D}`, which is what makes the "four-category share" distribution table possible.
- Type A logs an input snapshot — store the raw input signal (recognized text, confidence) so you can replay whether the signal never arrived or was used wrong.
- Type B logs a transient/permanent flag — distinguish whether a retry is warranted, and record retry count and final result.
- Type C logs intermediate reasoning — record the model's intermediate steps / tool choices so you can pinpoint which step jumped.
- Type D logs schema-validation results — parse failures must be their own category, don't lump them into "model answered wrong."
- Monitor the false-positive rate alongside — the failure detector's own false triggers must be observable, otherwise it over-intervenes.

**The discipline of localization — answer four questions before judging (borrowing the diagnostic SOP from error recovery):**

```
Q1 Error type?    Transient (network/timeout/rate-limit) vs permanent (input quality/out of bounds)
Q2 Side effects?  None vs written-but-not-delivered vs already delivered to the user
Q3 Recoverable?   Resumable vs must redo vs unrecoverable
Q4 Which layer?   Prevention layer (design flaw) vs recovery layer (runtime)
```

Make no judgment before answering these four. This blocks the two most common mistakes: treating a permanent error as transient and blindly retrying it, and tossing a design flaw into the runtime layer to paper over.

**Statistics and prioritization:**

- Produce a **node failure distribution table** (what share goes to A/B/C/D), and let the shares decide iteration priority — don't go by gut, let the data talk.
- Track the rollback trigger rate separately (orthogonal dimension); an abnormal spike means frequent side-effect cleanup, which is a red flag for system stability.
- Each category's fix has a different ROI: Type D adding schema constraints is often the cheapest and fastest to take effect; Type C revising the prompt is slow to take effect but has a high ceiling. Pick the low-hanging fruit first, then gnaw on the hard bones.

## Wrap-up

> Failure isn't a blob — it's four nodes on a pipeline. The PM's craft isn't fixing bugs; it's whether you can say at a glance "which node did it die at" — input misheard, tool didn't reply, model thought wrong, or output came back in broken packaging. Can't tell the nodes apart, and every improvement is a gamble.
