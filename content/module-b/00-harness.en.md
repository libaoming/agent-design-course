---
title: Why a Stronger Model Won't Save Your Agent — Fix the Harness First
module: b
order: 0
slug: harness
nav: Harness Engineering
summary: The model is the driver, the Harness is the car. If it can't deliver, it's usually the car's fault, not the driver's.
tags: [工程地基, Harness, 五子系统]
---

## Why a Capable Model Still Fails to Deliver

You wired up the strongest model available, wrote a prompt you were rather proud of, and fired up the Agent. The first three steps look great — then on step four it goes off the rails: calls the wrong tool, loses context, "helpfully" tacks on features nobody asked for, and after an error it neither retries nor raises an alarm. What you end up with is a heap that looks finished but is actually unusable.

The first instinct is usually "the model isn't smart enough, let me swap in a stronger one." That's the first faulty intuition this lecture is here to dismantle.

There's one sentence worth nailing to the wall first:

> Agency (the ability to perceive, reason, and act) comes from model training, not from external code orchestration. But a usable Agent product needs both — the model is the driver, the Harness is the car.

Translate that into an operational judgment: when an Agent can't deliver, the problem falls into two camps. One is a driver problem — the model genuinely can't reason its way through the task, and here swapping models actually helps. The other is a car problem — the tools weren't provided right, the knowledge wasn't injected, the state wasn't persisted, errors had nobody to catch them, permissions had no boundaries. The latter accounts for the vast majority, and swapping models does nothing for them, because you're replacing the driver when the car is what's broken.

The cost of swapping models without fixing the harness compounds:

- The money and waiting you spent on "swapping models" could have been saved, because the root cause was never touched.
- You misdiagnose an engineering defect as a model defect, so you're forever chasing "the next stronger model" while the real bottleneck stays put.
- The more insidious cost: you pile on more and more if-else branches and hardcoded routing, trying to "simulate" intelligence through program control flow. This is a textbook Rube Goldberg machine — a pile of contraptions that look like they're working, but what they simulate is a process, not Agency. The stronger the model gets, the more this scaffolding actually gets in the way.

So the core idea of this lecture is just one sentence: **when you hit a failure, fix the harness first, then consider swapping the model.** The entire Module B is about teaching you how to build that car solid.

## What a Harness Is Made Of

First, the definition: a Harness is the **infrastructure** an Agent runs on — everything engineered outside the model weights. The model does the "thinking"; the Harness makes the model "actually run in this specific domain."

It's made of five subsystems. Below we use a generic "voice outbound-call Agent" (auto-dials customers, looks up information, records results) as the running example for the concrete deliverables:

![The five Harness subsystems: model Agency at the center, with Instructions/Tools/Environment/State/Feedback surrounding it](../assets/diagrams/harness.svg)

| Subsystem | What problem it solves | Typical deliverables |
|--------|-------------|-----------|
| Tools | The model can think but not act — it needs hands to execute actions | Speech recognition, speech synthesis, CRM lookup, hang-up interface |
| Knowledge | A general model doesn't know the proprietary rules of your domain | Main prompt + domain knowledge fields injected on demand |
| Observation | The model can't make decisions if it can't see the environment | Voice stream, emotion signals, conversation history, state feedback |
| Action | Ideas have to land in the real environment | Voice output, calendar booking, triggering human handoff |
| Permissions | An Agent without boundaries is a source of accidents | Call-duration caps, industry-compliance word filtering, action allowlists |

The key to reading this table is to treat it as a debugging checklist, not a knowledge point. When an Agent breaks, go through each subsystem in turn: is a tool missing, or was the tool just mis-dispatched? Is knowledge missing, or was it simply not injected? Did it fail to observe the state, or did it observe it but not know how to use it? Is the action interface broken, or did it overstep and get blocked? Almost always one of the five columns lights up red first — that's the spot you should fix.

One thing worth emphasizing specifically: what it is **not**. A Harness is not Prompt Engineering. Piling branch logic and routing into hardcode is simulating intelligence through program control flow; a Harness is building infrastructure for the model so its own Agency can come through. The two point in opposite directions.

> [!NOTE] An often-overlooked sixth piece: a mature Harness also hangs a "self-improvement loop" alongside the "execution loop" — once the work is done, it asks itself "what should I learn from this round?" and distills the results into better skills / memory. A Harness doesn't just let the model finish the job; it lets the model get better at it over time.

## A Few Real Numbers and Examples

**Three meanings for one term — align on which one you mean before the meeting.** The word "Harness" gets used in three different senses in the industry, and without declaring which one upfront, people easily talk past each other:

| Context | What Harness refers to | Emphasis |
|------|---------------|------|
| Course / infrastructure sense (the main subject of this lecture) | The five subsystems Tools / Knowledge / Observation / Action / Permissions | Structure: getting the model to run in the domain |
| Engineering-practice sense | Layered defense: persistence layer (spec files + memory) / automation-hook layer / context-isolation layer (sub-Agents) | Process: migrating specs from model memory to a deterministic file system |
| QA / eval sense | A standardized evaluation pipeline (prompt → context → Harness, i.e. "how to ask → what to feed → how to verify") | Outlet: evaluation ensures reliability |

The three senses don't contradict each other: eval is the outlet, layered defense is the structure, and runtime infrastructure is the foundation. But when you present to others, you must declare which sense you're using first, or someone will argue against you using a different definition.

**Two hard thresholds, from a self-improving Agent system.** It turned "when to distill" into event-driven numeric triggers that you can copy straight into your SOP:

- A single task **exceeding 5 tool calls** → this workflow is complex enough to be worth solidifying into a reusable skill (update an existing similar one if there is one; don't create a new one).
- Every **10 messages** → force a pause for reflection once, and decide what goes into long-term memory.

**Putting a character cap on memory files is a feature, not a bug.** The same system set hard caps on its compact memory files (user profile around 500 tokens, core memory around 800 tokens), while full sessions are stored in their entirety and remain searchable. The cap looks like a restriction, but it actually forces keeping only relevant information — otherwise the files keep piling up, and every future run gets heavier and slower instead of smarter.

**The implicit-feature-replication trap.** It's been observed in engineering practice that during integration an Agent will auto-complete features you never explicitly stated. This means your verification step must guard against exactly this — you can't default to "if I didn't ask for it, it won't do it." This maps directly to "completeness of verification": test what it did, not just whether it did what you asked.

## Actionable Practices

When your Agent can't deliver, follow the sequence below, and don't skip steps:

1. **Attribute first, then act.** Ask yourself: is this a driver problem (the model can't reason it through) or a car problem (an engineering defect)? Without evidence that it's the former, default to the latter.
2. **Use the five subsystems as a debugging checklist.** Go column by column through Tools / Knowledge / Observation / Action / Permissions and locate the one that lit up red first.
3. **Resist the urge to "add one more if-else."** Every time you want to patch a case with a hardcoded branch, pause — are you building infrastructure, or building a Rube Goldberg machine?
4. **Migrate specs from model memory to the file system.** Anything you can write into a deterministic file (spec docs / hooks / memory) shouldn't be left in the prompt relying on the model to remember.
5. **Give state a home on disk.** Persist task state, support resuming from a checkpoint; for concurrency, prefer directory isolation over locking.
6. **Set permission boundaries, and default to tight.** Get call duration, compliance words, and action allowlists in place first. An Agent without boundaries isn't more free, it's more dangerous.
7. **Cap memory.** Add a hard character cap to compact files, and store the full history separately and searchably.
8. **Verification must guard against implicit completion.** Test what the Agent actually did, and write checks specifically for "the things it did on its own initiative."
9. **Swap the model last.** Once you've gone through all of the above and confirmed the root cause is in the driver and not the car, then talk about swapping models.

## Wrap-Up

> The model is the driver, the Harness is the car. When it can't deliver, check the car first — don't rush to swap the driver. The best Agent products come from engineers who understand their job as "building a car" rather than "building intelligence."
