---
title: "Prioritization + Exploration: Which to Do First, and How to Avoid Always Taking the Beaten Path"
module: d
order: 4
slug: prioritization-exploration
nav: Prioritization & Exploration
summary: Prioritization answers "which to do first"; exploration answers "do you dare walk an untrodden path"—the finale of Module D.
tags: [设计模式, 优先级, 探索, 盲区]
---

## Setting the Target: Two Blind Spots That Trip People Up

Module D has worked through quite a few design patterns. Today we wrap up by adding the two that are most easily overlooked yet most decisive for an Agent's real-world performance—**Prioritization** and **Exploration and Discovery**.

Why are they blind spots? Because unlike "tool calling," they have no clear-cut API shape. They live in the Agent's **decision layer**: faced with a pile of things it could do, which does it touch first? When the known path is a dead end, should it probe in a direction it hasn't tried? Get these two questions wrong and the Agent won't error out or crash—it'll just "stay busy for ages, heading the wrong way." That's the most expensive kind of failure.

Start with the negative case to make the target sharp. **An Agent without prioritization**: grabbing everything at once. The user crams five demands into one sentence, and it processes them in order; ten to-dos arrive from the backend, and it queues them by arrival time. The result is **getting dragged off by low-value tasks**—spending 80% of its compute on things that are "convenient but unimportant," while the real global blocker sits at position eight, untouched. **An Agent that can't explore**: only walks the beaten path. Give it an open-ended question—"track down this intermittent bug," "investigate whether this new direction is worth pursuing"—and it walks the most obvious known path to the end, stops when it hits a wall, and outputs "no relevant information found." It won't proactively generate hypotheses, won't think "maybe it's in another module I haven't looked at yet." One is about **how to choose**, the other about **whether you dare head into the unknown**.

## Framework One: Prioritization—Which to Do First

The essence of prioritization is the Agent **computing an execution order across multiple candidate tasks/subgoals/requests using explicit dimensions**, rather than processing by arrival order or at random. At its core are four dimensions, applied in a judgment sequence:

| Dimension | What it asks | Its role in ordering |
|------|--------|----------------|
| Dependency | Is this thing blocked by something else? What does finishing it unlock? | **Hard constraint**, ahead of everything—blocked items can't go first; items that unlock multiple things go first |
| Urgency | How soon must it be done? How close is the deadline? | Timeline ordering, near-deadline items float up |
| Importance | How much does doing it contribute to the overall goal? | Value ordering, decides "is it worth doing now" |
| Cost-benefit | How much goes in? How much comes out? | Efficiency tiebreaker within the same tier, high-ROI first |

The practical judgment sequence: **resolve dependencies first (topological sort) → then look at the urgent × important combination → break ties within a tier using cost-benefit**. Dependency is the hard constraint (get the order wrong and everything downstream is wasted); urgent × important is the classic Eisenhower matrix; cost-benefit is the final cut when items sit tied in the same cell:

![Priority urgent × important quadrants: urgent and important do now / urgent not important delegate / not urgent important schedule / neither cut](../assets/diagrams/prioritization-exploration.svg)

| | Important | Not important |
|--|------|--------|
| **Urgent** | Do now (active) | Handle quickly or delegate, keep off the main line |
| **Not urgent** | Schedule it, don't forget it | Cut if you can, don't let it eat resources |

One often-confused boundary worth spelling out: **prioritization ≠ scheduling**. Prioritization answers "which one" (picking the next thing to act on from the candidate set); scheduling answers "how many at once" (concurrency, WIP limit, when to switch). The two work together: prioritization orders the queue, scheduling pulls tasks off the head of the queue under the WIP limit.

## Framework Two: Exploration and Discovery—Do You Dare Walk an Untrodden Path

The exploration pattern solves this: in an **unknown or open solution space**, the Agent proactively tries paths it hasn't walked, instead of circling repeatedly along the known optimum. The core tension in one phrase—**exploration vs exploitation**:

| | Exploration | Exploitation |
|--|---------------------|----------------------|
| What it does | Try new hypotheses, new paths, new regions | Keep digging along the current known optimum |
| What it bets on | There may be a better solution not yet found | The current path's payoff is certain |
| Risk | Spend budget and come up empty | Stuck in a local optimum, missing something better |
| When to favor | Insufficient info, large solution space, repeatedly hitting walls | Sufficient info, a good-enough solution found, budget running out |

What kind of task must lean on exploration to hold up? Three typical types: **research tasks** (the answer isn't in some fixed document, you have to cast a wide net), **bug hunting / troubleshooting** (intermittent problems, unclear root cause, you list several suspects and verify each), and **open-ended problem solving** (no standard answer, generate multiple candidates then filter). Exploration runs as a loop that doesn't stop easily: **generate hypothesis → verify → adjust direction based on results → (if coverage is insufficient) generate new hypotheses again**. The key discipline is **coverage first, don't stop easily**—an Agent that can't explore quits after its first hypothesis fails verification, while an Agent that can explore asks "which regions haven't I looked at yet" and keeps expanding coverage until the budget runs out.

## Case: One Task, How the Two Patterns Cooperate

Task: **"There's an intermittent 500 error in production. Track it down and fix it—we need a conclusion before end of day."**

**Prioritization steps in first**, breaking the task apart and ordering it: dependency—you have to locate it before you can fix it, "locate" blocks "fix," so locate goes first; urgency—there's a deadline, lock the main line onto this, downgrade other backend requests; importance—a production error affects users, lands in the "urgent and important" quadrant → active; cost-benefit—locating starts with the logs (low cost, high information), rather than jumping straight to load testing.

**Exploration takes over the "locate" step**—root cause unclear, this is exactly an open solution space: generate hypotheses (A upstream timeout / B connection pool exhausted / C edge-case input), don't just verify A but list all three, verify the cheapest first by cost; A fails → don't stop, pivot to B (the NEVER STOP discipline); coverage first—within the fixed budget of end-of-day, sweep across the suspect surface as much as possible. **Prioritization decides "the main line right now is locating this bug," exploration decides "while locating, don't fixate on a single suspect"**: one governs which thing to do, the other governs how to avoid dead ends within that thing.

## Weaving It Into This Course

**Prioritization ↔ Module C's "boundaries & feature list."** Module C set `WIP=1` and a "feature-selection algorithm"—that **"feature-selection algorithm" is in essence prioritization, and `WIP=1` is in essence scheduling**. The dependency field in features.json is the dependency dimension, a feature's business value is the importance dimension, and this lecture's four-dimension matrix makes that earlier algorithm explicit and reusable. Prioritization is "which one goes active," WIP is "how many active at once"—Module C used both long ago; only today do we give them their proper names.

**Exploration ↔ harness's autoresearch "NEVER STOP" + Module A task paths.** The autoresearch paradigm in the harness methodology: within a fixed budget, let the Agent run nonstop, score with a single scalar, keep books in a tsv, **NEVER STOP**—this is exactly the engineering realization of the exploration pattern ("fixed budget" maps to the budget constraint, "NEVER STOP" maps to coverage-first don't-stop-easily, and a new hypothesis each round is one act of exploration). So prioritization and exploration were never new things—they're the **general names** behind those concrete practices from earlier lectures. The value of naming them is that next time you hit a new scenario, you can call on them deliberately instead of reinventing them each time.

## Actionable Practices

**Prioritization**: ① Have the Agent explicitly output its ordering rationale (list candidates first, tag the four dimensions, then give the order); ② build the dependency graph first, topologically sort whenever you can, gray out blocked items and never touch them first; ③ treat deadline/SLA as a hard float-up signal; ④ distinguish prioritization from WIP—order the queue first, then pull from the head under the WIP limit, don't mash them into one pot; ⑤ low-value tasks need an explicit discard mechanism.

**Exploration**: ① Force generating multiple hypotheses at once (≥3), don't verify-one-stop-one; ② give a fixed exploration budget (rounds/tokens/time), NEVER STOP within budget, converge when budget is exhausted; ③ use a single scalar to gauge "is it good enough," switch from exploration to exploitation only at the threshold; ④ keep books (write each round's hypotheses, verification results, and regions covered into a traceable log); ⑤ set a convergence signal (coverage met or budget exhausted or a good-enough solution found—stop only when one is satisfied).

The two lines together: **prioritization keeps you from being dragged off by low-value tasks, exploration keeps you from being stuck on the known beaten path.** The former governs where resources go, the latter governs how wide a path you walk.

## Closing

> Prioritization answers "which to do first," exploration and discovery answers "do you dare walk an untrodden path." One makes the Agent spend its effort where it counts; the other makes the Agent refuse to give up easily in the unknown—the former cures "busywork," the latter cures "laziness."

And finally, a wrap-up for all of Module D:

> The 21 design patterns we've worked through aren't 21 mandatory exam questions—they're a **move set**. The real skill isn't memorizing every move, but knowing, when facing a concrete task, which few moves to look up and how to combine them. Reflection paired with planning, guardrails paired with tools, prioritization paired with scheduling, exploration paired with evaluation—being able to look up and combine matters far more than being able to recite.
