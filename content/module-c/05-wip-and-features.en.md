---
title: "Why Agents Overreach Yet Finish Nothing: WIP=1 and the Feature-List Primitive"
module: c
order: 5
slug: wip-and-features
nav: Boundaries and the Feature List
summary: Running many tasks at once means all of them fail; lock the boundaries with WIP=1 plus feature primitives backed by executable verification.
tags: [Harness, WIP, feature原语]
---

## What Happens When One Agent Builds Five Features at Once

Hand an agent a to-do list: implement login, add a shopping cart, write the order API, wire up payments, and fill in the unit tests. Come back an hour later and you'll find all five branches touched, all five "almost done," and not one of them runnable end to end. Login is missing a callback, the cart skips its stock check, the order API returns 500, payments are still mid-SDK-integration, and the tests are all red because nothing upstream works.

This isn't the agent slacking off — it's the agent being too eager. It tends to "kick off every task at once," because each one looks easy in isolation. The problem is in how attention gets allocated.

Call the effective attention an agent can invest in a single work cycle its capacity C. When it pushes k tasks forward at the same time, each task gets only C/k on average. Every task has a minimum attention threshold T below which it can't actually be finished.

| k (concurrent tasks) | Per-task share | Relation to threshold T | Result |
|---|---|---|---|
| 1 | C | C ≥ T | 1 finished |
| 2 | C/2 | possibly < T | 0–1 finished |
| 5 | C/5 | almost certainly < T | 0 finished |

Note the nonlinearity here: it's not that "the number finished drops proportionally" — it's that once each slice of attention falls below T, **all the tasks fail together**. The output of doing five things at once isn't "five tasks each 20% done," it's "five tasks each stalled at 80%, with nothing shippable." A half-finished feature is worth roughly zero — code that doesn't run can't ship, can't be depended on by the next step, and still eats your time later when you have to debug it.

So let's put the core takeaway up front: **"do less but finish" always beats "do more but leave it half-done."** And to actually make an agent obey, writing "please focus" into the prompt does nothing — you have to turn the constraint into a data structure it can't route around. That's the feature-list primitive.

## Framework 1: The Two Rules of WIP=1

WIP (Work In Progress) = work in progress. WIP=1 is a scheduling discipline:

> At any given moment, only one task may be in the active state.

It pairs with a quantified gate — VCR (Verified Completion Rate): the share of opened tasks that have been verified as passing.

| Concept | Definition | Role in the harness |
|---|---|---|
| WIP | Number of tasks active at the same time | Limit = 1 |
| VCR | Passing tasks / opened tasks | When < 1.0, no new tasks allowed |
| active | In progress, not yet verified as passing | At most one globally |

Two rules: ① Only one task is active at any moment — this forcibly locks k from the attention math to 1, guaranteeing each task gets the full C. ② No new task may be opened while VCR < 1.0 — as long as any task has been started but not wrapped up, you don't touch the next one. This rule directly seals off "overreach yet finish nothing": when the agent wants to open a second task, the gate stops it and forces it to verify the current one to passing first.

This is exactly the heart of the "feature-selection algorithm" in this project's `M1/AGENTS.md`: prioritize the lowest-numbered feature whose `status=failing` and whose dependencies are all passing, finish one before picking the next, and only move to the next slice once the current slice is done. The algorithm's output is always "the next thing to do" — singular.

## Framework 2: The Feature List Is a Primitive, Not a Document

For WIP=1 to be enforceable, you first need a machine-readable task list. That's the feature list — it's the harness's **foundational data structure (a primitive)**, not a requirements document for humans to read. Why insist on the word "primitive"? Because all three core components of the harness depend on it directly:

| Component | Which part of the feature list it depends on | What it does |
|---|---|---|
| Scheduler | the status field | Computes the single next active task |
| Verifier | the verify command | Runs the command to decide whether it can be promoted to passing |
| Handoff | the full triplet | Lets a new session take over in 10 minutes |

A feature is a **triplet**:

| Field | Meaning | Example |
|---|---|---|
| Behavior description | What the feature does (observable by users/externally) | "Create-order API returns 201 and persists to the DB" |
| Verify command | How you know it's truly done (executable) | `curl -X POST .../orders → 201` |
| Current state | Which cell of the state machine it's in right now | `failing` |

The key insight: **a document can be ignored; a primitive can't be bypassed.** It's like a comment in a database versus a trigger constraint — a comment saying "please don't insert negative stock" can be ignored by anyone, while a `CHECK(stock >= 0)` constraint makes the offending INSERT fail outright. For the feature list to work, it has to be the latter: the agent can't know the next step without reading it, and can't claim completion without updating it. Putting the task list in the README makes it a document; putting it in a structured file that the scheduler and verifier read makes it a primitive.

## Framework 3: The State Machine — Passing Verification Is the Only Path to Promotion

Each feature moves through an irreversible state machine:

```
not_started → active → blocked ⇄ active → passing
```

![feature state machine: not_started→active⇄blocked, and active is promoted to passing only after verify succeeds (terminal, irreversible)](../assets/diagrams/feature-state-machine.svg)

Two iron laws: **passing verification is the only path to the passing state** — the agent can't set the state to passing itself; the verifier must run the verify command to completion and obtain executable proof of success before promotion; and **passing is irreversible** — once passed, it's locked, avoiding the back-and-forth of "finished it, then changed it back." This state machine is the enforcement mechanism for WIP=1: as long as an active task exists and hasn't reached passing, the scheduler won't produce a new active.

Proof of completion must be executable: "the code looks fine" isn't proof; "`curl` returns 201" is proof. The bar is this — let someone else, on another machine, run it as-is, and the result is stable.

## Case: How This Project's features.json Lands All Four

**Status enum = state machine.** The convention hardcodes `status ∈ {pending, in_progress, failing, passing}`, paired with the rule "you may only change to passing once build produces correct HTML and clears the checklist; finishing the draft only gets you to in_progress." That extra `in_progress` sits precisely between "looks done" and "verified to pass," preventing the agent from mistaking "I wrote it" for "it passed."

**Verifier hard gate = the primitive can't be bypassed.** The hardest rule in the convention: "an empty verify field = no work allowed to start." This makes "executable proof" a precondition for starting — if a feature can't even articulate "how do you know it's done," it isn't allowed to begin. Look at one feature's verify:

```
test -f assets/orangebook.css && ! grep -lP '[\x{1F300}-\x{1FAFF}]' assets/orangebook.css
```

File exists + no emoji anywhere — one command yields true or false, with no room for "looks like it meets the bar."

**Linear slices = the macro version of WIP=1.** The features are cut into four slices, S1→S2→S3→S4, each with explicit exit_criteria. The rule is "finish a slice before moving to the next one, no skipping." This lifts "only do one task at a time" from the single-feature level up to the slice level: you're not allowed to open S2 before S1 runs end to end.

**Three-part relations = the primitive carries its own boundaries.** Each feature carries three sections: `related / affected / out_of_scope`. The out_of_scope section explicitly tells the agent "these aren't part of your task," structurally suppressing its urge to do a little extra on the side — it's both context routing and an anti-overreach guardrail.

Connect these four points: the author didn't repeatedly nag "please focus, don't overreach" in the prompt. He translated all of that into field constraints in `features.json` and the selection algorithm in `AGENTS.md`. The constraints are triggers, not comments.

## Actionable Steps: Installing These Gates on Your Own Project

1. **Build a single-source-of-truth file.** Move the task list into a structured file — the one truth that the scheduler and verifier read.
2. **Fill in the full triplet for every feature.** Behavior description + verify command + current state. **Anything with an empty verify command can't enter the list and can't start work.**
3. **Allow only these few states, and let the verifier stamp passing.** After writing code, the agent can at most mark `in_progress`; it must pass verify to be promoted to `passing`.
4. **Enforce WIP=1.** Before starting work, check the list: is there an active task that hasn't reached passing? If so, finish it first. No new task until VCR hits 1.0.
5. **Turn proof into a command.** Write "is it done?" as a single runnable line — `curl`, `pytest`, `grep`, `test`.
6. **Mark boundaries with the three parts.** out_of_scope is the anti-overreach guardrail; related is context routing.
7. **When tasks overflow one screen, slice them.** Split into linear slices, define exit_criteria for each, and finish one before moving to the next.

## Closing

Agents overreach yet finish nothing not because they aren't smart enough, but because you've tacitly let their attention get spread thin. The fix has never been longer nagging — it's harder structure.

> The output of doing five features at once is often zero runnable features. Do one fewer thing and finish it; that beats opening five and throwing all five away.
