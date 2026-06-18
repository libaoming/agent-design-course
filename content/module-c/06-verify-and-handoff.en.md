---
title: Why a Task Only Counts as Done After End-to-End Passes, and Why Every Session Must Leave a Clean State
module: c
order: 6
slug: verify-and-handoff
nav: End-to-End & Handoff
summary: Unit tests passing ≠ task done. The done-decision must be externalized by running E2E for real, and every session must close out against a five-dimension clean state to fight entropy.
tags: [Harness, 端到端验证, 清洁交接]
---

## A "Done" That Keeps Getting Announced

You've almost certainly lived through this scene: the agent finishes writing code, runs the unit tests, gets a green light, and then solemnly declares "feature implemented, everything passes." You believe it, you merge, you ship — and then the very first real request in production blows up. Trace it back, and the downstream service that the unit test had mocked out turns out to have a field name that doesn't match.

This isn't a mistake some agent makes once in a while; it's the **structural overconfidence** of agent systems. The agent's judgment of "done" stops at the layer it can directly observe: no syntax errors, unit tests turning green. But between "the syntax is right" / "the tests pass" and "the task is actually finished," there sit two chasms it cannot cross.

This is the closing lecture of Module C. It wraps up two things on the output side: **how to decide a task is truly done**, and **how to leave the state clean when a session ends**. Both point to the same underlying fact: you cannot trust an agent's subjective sense of its own work — you have to let the harness verify it externally through deterministic means.

## Framework 1: Three-Layer Termination Verification, Where Each Jump Loses Information

"Done" isn't a boolean; it's a ladder you have to climb rung by rung. Each layer verifies something different and can catch different problems:

![Three-layer termination verification: L1 syntax/static / L2 runtime behavior / L3 system-level E2E. Each jump loses information; defects hide in L3](../assets/diagrams/verify-handoff.svg)

| Layer | What it verifies | Typical means | Problems it can catch | Problems it can't catch |
|---|---|---|---|---|
| L1 syntax/static | Whether the code is legal | Compile / lint / type check | Typos, types, missing imports | Logic errors, wrong runtime behavior |
| L2 runtime behavior | Whether a single component runs correctly | Unit tests / function-level assertions | Logic defects in a single function | How components interact with each other |
| L3 system-level E2E | Whether the whole system behaves correctly as a whole | Real startup, real input, observing real output | Interface mismatches, state propagation, resource leaks, environment dependencies | (This is the last line — there's no escaping it) |

The key insight is in the last column: **each time you jump up a layer, part of the information held by the lower layer's verification is lost**. L1 knows every token is legal but doesn't know whether the function logic is correct; L2 knows every function runs correctly on its own, but precisely because it mocked out the dependencies, it has no idea what happens when those functions are wired together. The agent's overconfidence is, at its core, **passing off a lower-layer pass as a higher-layer completion** — it stops at the L2 green light and declares victory, while real-world defects overwhelmingly hide in L3.

## Framework 2: Why Unit Tests Have a Systematic Blind Spot

It's not that unit tests are useless — it's that their isolation, their greatest strength, is at the same time the biggest source of their blind spots. To make unit tests fast, stable, and repeatable, we carve the component under test out of its real environment and use mocks to replace the world around it with fakes. As a result, the following four classes of problems are structurally pushed outside the unit test's field of view:

| Blind spot type | Why the unit test can't see it | The scene only E2E exposes |
|---|---|---|
| Interface mismatch | Each side's own unit tests use the interface shape it imagined | When wired together for real, field names/types/nullability don't match |
| State propagation | In unit tests each component's state is hand-placed | Real upstream output is fed into downstream, and intermediate state gets contaminated |
| Resource leaks | Unit test processes are short-lived and exit right after running | After running for a long time, connections/handles/memory are exhausted |
| Environment dependencies | The isolated environment assumes config, time zone, and paths are all ideal | The real environment lacks a variable, lacks a permission, or the path doesn't exist |

The deeper value is this: **E2E isn't just after-the-fact defect detection — it reshapes the agent's coding strategy in reverse**. An agent that knows it will ultimately have to pass E2E will, while writing code, proactively think about how components connect, how state flows, and how resources are released — because it knows mocks won't get it past that gate. Put the acceptance criteria up front, and the behavior moves up front too. This is why the E2E gate has to be made known to the agent at the start of the job, not revealed only after the code is written.

## Framework 3: Externalize the Done-Decision + Observability Is an Architectural Property

Since the agent's judgment of itself can't be trusted, the conclusion is straightforward: **the authority to decide "done" must be taken out of the agent's hands and given to the harness**. Land this as a separation of responsibilities: the planning agent defines what "done" looks like (acceptance criteria, E2E scenarios) → the generating agent writes code to satisfy it → the evaluating agent / harness independently runs the verification and only accepts objective signals. Once these three are separated, the defect rate can drop from very high to near zero — because no single role can get away with "I feel like it's done."

When E2E goes red, the next question is "why is it red?" If you have to rely on adding prints, re-running, and guessing, then 30%–50% of session time gets burned on repeated diagnosis. Observability can't be an "add logs after something breaks" afterthought — it has to be a structure grown into the harness at design time, in two layers: runtime observability (what the system **did**: each step's input and output, state transitions, the error scene) + process observability (why this result should be **accepted/rejected**: acceptance criteria, scoring rubric, the basis for the decision). With both layers in place, diagnosis goes from "guessing" to "reading."

## Framework 4: The Five Dimensions of a Clean State, the Must-Have Checklist for Ending a Session

Passing the task isn't the end. The state you leave behind when a session ends determines whether the next one can take over cleanly. **Entropy is the default**, and "clean it up later" is practically equivalent to "abandon it forever." So the session close-out has to pass this five-dimension checklist:

| Dimension | Acceptance signal | Cost of not doing it |
|---|---|---|
| Build passes | A clean checkout can build successfully | Next session opens with fixing someone else's half-finished work |
| Tests pass | The full test suite is green, including E2E | You don't know which reds were newly introduced |
| Progress recorded | The progress file states where things got to and the next entry point | All context is lost; you rebuild it by archaeology |
| Temp artifacts cleaned | Debug output / scratch files / dead code are removed | The repo drowns in noise and the signal-to-noise ratio collapses |
| Startup path works | The "how to run it" in the docs actually works right now | The README lies; the new person / new agent gets stuck on step one |

## Case: This Course Site's Own verify Discipline

**The done-decision is externalized into a script, not a declaration.** In the project, `scripts/verify.sh` is the end-to-end verification script, running 6 checks: ① the build actually produces `site/index.html`; ② the home page contains both modules and the sidebar; ③ the lecture pages are generated, and every expected heading listed in the fixture is hit; ④ tables are actually rendered as `<table>`; ⑤ a site-wide grep finds no emoji; ⑥ navigation links and style references are in place. Note that all of these checks are done against the **final product** (the HTML under site/) — instead of asking the build script "did you succeed?", it goes into the built pages and verifies for real. This is exactly L3 system-level E2E.

**`passing` is a gate guarded by E2E.** In `features.json`, each feature's status is `pending → in_progress → passing`. The rule is hard-coded in the verify discipline of CLAUDE.md: finishing a draft only gets you to `in_progress`; **only when the build produces correct HTML and passes the full checklist are you allowed to change it to `passing`**. "Written" and "passed" are two different states, separated by the exit code of verify.sh.

**Fixture before code is the concrete form of putting acceptance criteria up front.** The markdown from Lecture 1 isn't "just a sample written casually" — it's the fixture for the build script, and it exists before the script does; the headings listed in `fixtures/first-lecture/expected-headings.txt` are exactly the acceptance criteria that check ③ of verify must hit one by one. The script isn't even written yet, and the acceptance criteria are already there waiting — so when the agent writes the build script, it already knows what the finish line looks like.

**Updating progress at close-out is a mandatory action of the clean state.** `M1/PROGRESS.md` records, in reverse order, what each session did, what pitfalls it hit, and the verification results, with the active_feature/slice/update-date at the top making the next entry point visible at a glance. The very first item in CLAUDE.md's session-entry order is "read STATUS first" — this record isn't written for an archive, it's written for yourself at the next opening.

One honest detail worth naming: at one point a browser screenshot preview was blocked by an extension permission, and the project didn't pretend it had "passed visual inspection" — instead it explicitly wrote into the progress file "objective verification defers to verify.sh." This is exactly the discipline of not trusting subjective feelings and only accepting deterministic signals.

## Actionable Practices

1. **When you write the verify script, put the assertions on the final product, not on the intermediate process.** Go into the finished output and grep / start it up / send a real request to verify for real. The exit code is the done-decision.
2. **Make "written" and "passed" two different states.** Track status in a single source of truth, and stipulate that only when the E2E script is green can it enter `passing`.
3. **Put acceptance criteria up front, ideally as a fixture.** Land the expected output as a file before the job starts, so the agent knows which gate it has to pass from the very first line of code.
4. **Treat observability as architectural design, not an after-the-fact patch.** Both layers — runtime and process — are required.
5. **Pass the five-dimension checklist at session close-out, missing nothing.** Write the progress into a deterministic file and mark the "next entry point" at the top of the file.
6. **When verification gets blocked by the environment, honestly record the fallback — don't fake a pass.**

## Wrap-Up

Code will lie to you, unit tests will lie to you, and an agent's feelings about itself will lie to you even more; only an end-to-end run that passes in a clean environment, and a clean state the next session can open from directly, won't lie to you.

> Done isn't decided by the agent — it's verified by the harness; a handoff isn't "I did my best," it's something the next person can actually catch. Entropy is the default, so every "clean it up later" is one permanent act of giving up.
