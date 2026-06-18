---
title: Why Capable Agents Still Fail
module: c
order: 0
slug: why-agents-fail
nav: Why They Still Fail
summary: Most failures aren't in the model weights, but in the layer of engineering infrastructure outside the weights — the thing we call the harness.
tags: [Harness, 失败归因, 方法论]
---

## Setting up the target: drop a model that aces the test into a real task

Start with a set of uncomfortable numbers.

Today's strongest coding Agents pass only about 50%–60% of tasks on public benchmarks. And these are carefully scrubbed problems — clear requirements, clean environments, hard-coded acceptance criteria. The moment you switch to a real engineering setting, the pass rate usually drops even lower. Not because the model got dumber, but because the real world adds three things benchmarks leave out:

- **Requirements are vague**: the user says "fix the login for me," without saying what "fixed" means.
- **Rules are implicit**: in this repo, commits must pass lint, must come with fixtures, the production branch is read-only — none of which is written into the task.
- **The environment is broken**: dependencies won't install, external services time out, last round's half-finished work is still sitting there.

So it's easy to land on the wrong conclusion: **"The model just isn't strong enough yet — let's wait for the next generation."**

This lecture is here to dismantle that conclusion. The core claim is a single sentence:

**What makes an Agent fail, most of the time, isn't the model weights — it's the layer of engineering infrastructure outside the weights, which we call the harness.**

## Framework: five layers of failure attribution

"The Agent failed" is a sentence with no information in it, like saying "the program crashed." To fix it, you first have to attribute the failure to **a specific layer**. walkinglabs' Harness Engineering breaks an Agent task into five layers, and any failure should fall into exactly one of these cells:

| Layer | What this layer is responsible for | What failure looks like | Typical fix (change the harness, not the model) |
|---|---|---|---|
| 1. Task specification | Translating vague intent into a clear goal the Agent can execute | Drifting off, answering the wrong question, declaring "done" halfway through | Write a PRD/SPEC; make acceptance criteria, anti-patterns, and constraints explicit |
| 2. Context supply | Feeding the right information to the model at the right moment | Reinventing the wheel, violating the repo's implicit rules, forgetting the previous step | Persisted files (CLAUDE.md/STATUS.md) + context isolation |
| 3. Execution environment | Providing a reproducible, runnable environment | Dependencies won't install, services won't connect, runs locally but not in prod | init.sh self-check + fixtures + frozen environment |
| 4. Verification feedback | Letting the Agent know whether it got it right, and self-correct | Output looks right but is wrong; stalls because there's no signal | Attach an executable verify to every task (fixture/metric/log) |
| 5. State management | Preserving progress and decisions across steps and sessions | Long tasks get messier as they run; new sessions can't pick up | Single source of truth + slice-by-slice progress + persist state at session wrap-up |

The value of this table isn't memorizing five terms — it's that it forces you to do one thing: **when you hit a failure, first ask "which layer is this," instead of vaguely blaming the model.** The model weights occupy only a small slice across these five layers — they handle the "thinking," while the other four layers are engineering handling "making it think correctly, see clearly, remember reliably, and run at all."

## Data and case: the same model, the distance from 0 to 1

The most telling evidence is a kind of **controlled experiment**: don't touch a single line of the model weights, and only work on the harness layer wrapped around it.

- **Bare run**: hand a real task directly to the strongest model, with no specification, no environment, no verification. The result is failure — it might drift off, it might claim "done" after fixing half of it, it might spin in place in front of a dependency that won't install.
- **After adding a full harness**: same model, same task, but first fill in the task specification, freeze the environment into a one-command self-check, and attach an executable verification to every step. The result is success.

In the case walkinglabs presents, this kind of rework can push a task's success rate from **roughly 20% all the way up to nearly 100%** — **without changing a single model parameter.** Those tens of percentage points all come from engineering outside the weights.

The methodological implication is powerful: when you see an Agent fail, **your first instinct should not be "let's get a stronger model," but "which layer of my harness is missing something."** Swapping models is the most expensive move, the slowest to pay off, and often ineffective — because if the failure is in layer 3 (the environment won't install), no model, however strong, can install that dependency.

## Grounding the framework in real practice

The abstract five layers — what do they look like dropped into a real project? Below we corroborate them with a methodology that has been run over and over across multiple long-running Agent projects. At its core it simply equips each of these five layers with deterministic engineering backstops, organized into a "four-layer defense system" that maps almost one-to-one onto the five layers of failure attribution above.

**First, a counterintuitive discipline: documentation first — no writing code until the docs are done.** It sounds like bureaucracy, but it maps precisely onto layer 1 (task specification) and layer 2 (context supply). The practice: for any new project — even just a small CLI, a one-off technical spike — before touching code, land five files: project instructions, status file, requirements, technical specification, architecture. These five files move "vague intent" and "implicit rules" out of the Agent's unreliable memory and onto deterministic disk.

Here's a real pothole someone stepped in: a module was once "spun out into a standalone project" from a larger one, judged at the time as "just moving files," so only the code was moved with a README added, skipping documentation-first. The result was a problem that surfaced only after being probed three times — and the root cause was **scenario-recognition failure**: the wording "spin out" sounded like a move, but in substance it was a new project, which must go through the full specification. The lesson hardened into a criterion: **the moment it produces a new top-level directory, it's a new project, and documentation-first cannot be skipped.** This is a textbook case of layer 1 collapsing — not that the model couldn't do it, but that nobody fed it the spec that "this is a new project" clearly.

**Second discipline: single source of truth + executable verification.** This maps onto layers 4 and 5. Maintain a `features.json`, break the task into atomic features, each carrying a status field of `pending / in_progress / failing / passing`. The iron rule:

> The status can only be changed to passing once verify actually passes.

This rule directly kills the Agent's most common failure — "declaring victory too early." Models are very good at saying "I'm done," but **their saying it doesn't count; verify passing is what counts.** And if a feature's `verify` field is empty, **work is not allowed to start** — this is a kickoff gate that forces you to think through "what counts as correct" before touching anything.

It's more concrete when you check it against this course's own configuration: the success signal this course defines for "each lecture's handout" is a string of deterministic checks — build runs without errors, produces the corresponding HTML, key headings appear in the HTML, `grep` confirms no emoji anywhere in the text, and it's reachable by clicking through the nav. All five pass, and only then is a lecture allowed to go from `in_progress` to `passing`. Not one of them is "I think it reads pretty well."

**Third discipline: reproducible environment + fixtures before code.** This maps onto layer 3. Each milestone comes with an `init.sh` that runs six self-check segments (dependencies, env, external services, schema, fixtures, end-to-end), deliberately not using `set -e` — it runs through all six segments before reporting in one go. Paired with **fixtures before code**: if a fixture the verification needs doesn't exist, build it first; no mocking, no "waiting for real data." In this course, the first lecture's markdown is itself the fixture for the build script — write the handout first, then write the script.

**Fourth discipline: context isolation — outsource the grunt work to sub-Agents.** This maps onto layer 2. The most insidious failure in long tasks is the context getting polluted by noise. The fix is to dispatch "grunt work that eats a lot of context" to an independent sub-Agent, let it run to completion in its own context, and **return only the conclusion**, keeping the main thread clean. In this course: when bulk-reading knowledge-base notes to rewrite a handout, dispatch a sub-Agent to read the raw notes and return only the distilled handout draft — the main Agent never Reads the full original text into the main context.

Mapping the four disciplines back onto the five layers:

| Failure attribution layer | Engineering backstop | How it lands in this course |
|---|---|---|
| 1 Task specification | Documentation-first five-piece set | CLAUDE.md + PRD + SPEC + architecture |
| 2 Context supply | Persistence + context-isolated sub-Agent | STATUS.md + dispatch a sub-Agent to read notes and return only a draft |
| 3 Execution environment | init.sh six-segment self-check + fixtures before code | `bash M1/init.sh` all green before starting |
| 4 Verification feedback | Executable verify + kickoff gate | Five machine-decidable checks per lecture |
| 5 State management | Single source of truth + slicing + persist at wrap-up | features.json four states + STATUS updated at every wrap-up |

## Wrapping up

Back to the numbers we opened with. A 50%–60% benchmark pass rate is not the ceiling of the model's capability — it's the ceiling of the "bare model." Those remaining tens of percentage points are hidden in the layer of engineering infrastructure outside the weights that you can build, debug, and harden with your own hands.

> When you hit an Agent failure, first attribute the failure to one of the five layers, then fix that layer's harness — swapping the model is the last step, not the first.
