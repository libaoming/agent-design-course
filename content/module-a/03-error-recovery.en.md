---
title: Why an Agent With No Error-Recovery Strategy Falls Apart at the First Mistake
module: a
order: 3
slug: error-recovery
nav: Error Recovery 4+1
summary: A 4+1 taxonomy, a 4-question diagnostic SOP, and an anti-pattern checklist that explain how an Agent survives after it goes wrong.
tags: [L3, 错误恢复, 维度3]
---

## Setting up the target: an Agent with no recovery strategy breaks at the first mistake

Picture an Agent with zero error-recovery design. It calls an external API, hits a single network timeout—and throws an exception that terminates the whole task. What the user sees is a spinner that resolves into a blank screen, or worse, a context-free "Something went wrong."

The sneakier way to fail is "silently." Internally the Agent walks down a branch that nobody handles, so it quietly returns an empty result, a half-finished one, or even an answer that looks fine but is actually wrong. The user doesn't know, and neither does the system. By the time downstream catches it, the error has already propagated as if it were fact.

These two failure modes carry two kinds of cost:

- **Explicit crash**: high task-failure rate, and the user loses patience on the spot.
- **Silent error**: collapse of trust—once a user discovers the Agent "will confidently deliver wrong things," they'll never hand it anything important again.

What an error-recovery strategy solves is precisely "what to do after something goes wrong." It's not as simple as wrapping the Agent in a try/catch—it's a **structured triage-and-remediation system**: what errors to retry, what to degrade, what to honestly give up on, and what must escalate to a human.

The key takeaway, up front: **error recovery has 5 actions, but only 4 are main paths when you count them—the 5th, "rollback," is an orthogonal dimension.**

## Framework: the 4+1 taxonomy

Split "what to do after an error" into two independent questions: how to complete the task (4 main paths, mutually exclusive and collectively exhaustive, summing to 100%), and how to clean up side effects (rollback, an orthogonal dimension independent of the 4).

![Error-recovery escalation path: error occurs → explicit capture → triage → retry → degrade → graceful failure / human handoff, with rollback overlaid orthogonally](../assets/diagrams/error-recovery.svg)

| Strategy | Weight | When it applies | Tell the user? | Main risk |
|---|---|---|---|---|
| **Retry** | Light | Transient errors: network jitter / timeout / rate limiting | Usually not (silent retry) | Retrying a non-idempotent operation → duplicate side effects |
| **Degrade** | Medium | Main path blocked but a sub-optimal result can still be delivered | Disclose if quality is visibly reduced | User thinks they got a complete result |
| **Graceful failure** | —— | Low value / unrecoverable, no room to remediate | **Must be disclosed honestly** | Abused into "give up at the first obstacle" |
| **Human handoff** | Heavy | Irreversible + low confidence + repeated failures + user explicitly requests it | Must disclose and hand over | SLA timeout with nobody to receive → task left hanging |
| **Rollback** (orthogonal) | —— | Side effects already produced, inconsistent state needs cleanup | Depends on whether the side effect has reached the user | Mistaking valuable intermediate artifacts for garbage and deleting them |

A few things to make clear:

- **Retry** is premised on **idempotency**; use exponential backoff, at most N=3 attempts. Idempotency itself belongs to the "prevention layer," not the recovery layer.
- **Degrade** isn't a single action but 4 sub-types: model degradation / capability degradation / scope degradation / latency degradation.
- **Graceful failure** is fail-safe close—better to do nothing than to do it wrong. The key is "honesty": tell the user clearly that it can't be done, rather than pretending it was.
- **Human handoff** is the heaviest backstop; suggested SLA is 30s, after which it falls back to graceful failure to avoid leaving the task hanging indefinitely.

**Why is rollback orthogonal rather than a 5th main path?** The 4 main paths × rollback {triggered / not triggered} = 8 combinations, and every one of them holds: you can "retry with no rollback needed," and you can also "degrade while rolling back dirty data already written." Every cell fills in, which shows the two are independent. The practical value of orthogonality shows up in measurement: the main-path distribution (sums to 100%) and the rollback trigger rate are two independent metrics—you can't blend them into one 100%.

## Case: a real lesson in "side effects already delivered"

> [!NOTE]
> The case comes from a document-auto-review Agent (scenario anonymized). This kind of Agent reviews a batch of compliance documents for the user and outputs a "risk / no risk" conclusion.

What happened: on one run the Agent missed a clause that should have been flagged red, and **had already delivered the conclusion "this document passes" to the user**, who then acted on it. The miss was only caught later during a QA spot check.

A beginner's first instinct is usually: "Just escalate to a human." That answer is a failing grade. Because the side effect has already **reached the user**, escalating to a human alone does nothing about the wrong conclusion that's already been sent out. The correct handling is a 5-step sequence:

1. **Retract**: pull back or flag the wrong conclusion as fast as possible to stop further propagation.
2. **Re-review**: re-review the document at a higher tier (human / a stronger model).
3. **Communicate**: proactively and honestly tell the user "that earlier conclusion was wrong," instead of waiting for them to find out.
4. **Compliance reporting + RCA**: report within the compliance deadline (e.g., 72h) and conduct a root-cause analysis.
5. **Concrete remediation**: offer an actionable fix, not just an "I'm sorry."

The key takeaway from this case: **whether the side effect has already reached the user determines the weight of the recovery action.** Even for the same missed detection, "only wrote an internal draft, not sent" and "already sent to the user and acted upon" are two completely different things.

Another common misconception: contract-review-type scenarios should prioritize **recall** (better to over-flag than to miss—a miss equals legal risk), whereas scenarios like code review and user-facing outbound calls should prioritize **precision** (false positives cause alert fatigue or harass users). The same recovery mechanism gets tuned in opposite directions depending on the business.

## Operational practices

**The 4-question diagnostic SOP (most important—answer these 4 before judging):**

```
Q1 Error type?    Transient (network/timeout/rate limit)   vs  Permanent (poor input quality / out of bounds)
Q2 Side effects?  None  vs  Written but not delivered  vs  Already delivered to the user
Q3 Recoverable?   Can resume  vs  Must redo  vs  Unrecoverable
Q4 Layer?         Prevention layer (design flaw)  vs  Recovery layer (runtime remediation)
```

These 4 questions map directly to strategy selection: transient + can resume → retry; permanent but a sub-optimal result is still possible → degrade; unrecoverable + low value → graceful failure; already reached the user / irreversible → human handoff + rollback; lands in the prevention layer → go back to the design phase to fix it, don't patch it at runtime. **Until all 4 questions are answered, no recovery judgment is allowed.**

**The escalation path after an error occurs:**

```
Error occurs → explicit capture (silent fallthrough strictly forbidden)
   ↓ triage (4 questions)
retry (still failing after N=3) → escalate
   ↓
degrade (pick from the 4 sub-types per scenario)
   ├─ side effects already written → rollback (orthogonal overlay, doesn't take a main-path slot)
   ├─ low value / unrecoverable → graceful failure
   └─ all failed and severe → human handoff (SLA 30s, fall back to graceful failure on timeout)
```

**5 anti-patterns (check yourself against each):**

1. **"Retry" as a cure-all**—no number of retries fixes a permanent error; it just wastes tokens and time.
2. **"Rollback = delete data"**—rollback is cleaning up inconsistent state, not mindless deletion; valuable intermediate artifacts should be kept.
3. **Answering "escalate to a human" for an already-delivered side effect**—you must run the 5 steps: retract + re-review + communicate + compliance reporting/RCA + remediation.
4. **Treating idempotency problems as error recovery**—idempotency and atomicity belong to the prevention layer; confusing the two layers turns an architecture problem into a misdiagnosed occasional glitch.
5. **Intercepting boundary problems at the tail end**—dirty input that should have been blocked at the entry stage, discovered only at the end of the pipeline, is costly to fix and likely to have already produced side effects.

**Metrics: don't measure only outcomes, measure the process too.** The North Star is "post-recovery completion rate" (tasks finally completed after recovery / tasks that triggered recovery); orthogonally, watch the rollback trigger rate (an abnormal spike is a bad signal); for process cost, watch the extra latency / interruption count / token cost that recovery introduces—a high completion rate bought with frantic retries and frequent user interruptions is not healthy.

## Wrap-up

> Error recovery has 5 actions—4 main paths plus 1 orthogonal rollback; before any judgment, run the "4-question diagnostic" (transient or permanent / side effects or none / can resume or not / prevention layer or recovery layer), and—every unexpected path must be handled explicitly; silent fallthrough is always an anti-pattern.
