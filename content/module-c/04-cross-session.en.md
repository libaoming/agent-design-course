---
title: Why Long Tasks Lose the Thread Across Sessions
module: c
order: 4
slug: cross-session
nav: Cross-Session Continuity
summary: A long task is bound to exhaust its context; initialization plus persisted artifacts let a fresh session take over in three minutes.
tags: [Harness, 持久化, 初始化]
---

## Setting the Target: The Second Session's Agent Doesn't Know What It Did Yesterday

Picture a task that spans three days: rewriting a batch of study notes into public-course lecture material. Day one goes great — the Agent settles on a lecture-style structure, picks a build-script approach, and gets the first lecture working end to end. You close the session.

Day two you open a new session, and what the Agent sees is a pile of half-finished files. It doesn't know: why the first lecture was segmented the way it was (the decision history is gone), why the build script avoids third-party libraries (the design rationale is gone), how many lectures are already done, or what to do next (the work progress is gone).

So it starts making "reasonable guesses." And those guesses often clash with what yesterday's version of itself decided: it reinvents a segmentation scheme, pulls in a third-party dependency, reworks a lecture that was already finished. This is **amnesia**.

Amnesia isn't the model being dumb — it's an **objective limit of the context window**. However large the window, it has a ceiling, and the complexity of a long task fills it mercilessly: decisions, code, logs, errors, dialogue all pile up until, at some point, the earliest critical information is either squeezed out or compressed into a distorted summary. Hoping that "a bigger window will fix it" is an illusion: task complexity will always catch up with window capacity.

What's sneakier is the **prelude** to amnesia — context anxiety. As context approaches the ceiling, the Agent's behavior visibly degrades, like someone scrambling to wrap up unfinished work right before clocking out: skipping verification ("should be fine, just mark it done"), choosing a faster but inferior approach, finishing sloppily. This is called **context anxiety**. What makes it dangerous is that the degradation happens while the Agent still seems "confident" — the output looks complete but is quietly cutting corners.

The core tension is: **a single session has limited capacity, but the lifecycle of a task far outlasts a single session.** The fix comes in two steps — first recognize the two continuation strategies, then treat "how to start a new session" as a standalone engineering problem to design for.

## Framework One: Compaction vs. Reset — Two Strategies for Crossing Sessions

| Dimension | Compaction | Reset |
|------|---------|---------|
| Where it happens | Within the same session | Open a brand-new session |
| Mechanism | Summarize existing context into a shorter version, keep going | Discard old context, rebuild state from persisted artifacts |
| What it keeps | The conclusions and outputs of "what was done" | Rebuilds "why it was done this way" + "how far it got" from files |
| What it loses | The "why" — decision reasoning gets flattened by the summary | The session's transient memory (which should have been persisted anyway) |
| Best for | Short tasks, local trimming within a single session | Long tasks, handoffs across days and across people |
| Risk | Summary distortion — the more you compress, the more it drifts, and errors get baked in | Rebuild fails if the artifacts are incomplete |

The key judgment: **compaction is convenient but has a ceiling.** Every compaction loses information, and after several rounds the Agent is working on "a summary of a summary," with the original "why" of its decisions long worn away. For genuinely long tasks, **reset is often unavoidable** — proactively throwing away the dirtied context and reloading from clean persisted artifacts turns out to be more reliable than soldiering on with an ever-more-distorted summary. But reset has a precondition: **the cost of rebuilding state must be low enough.** If a new session has to spend half an hour on archaeology just to get oriented, nobody will choose to reset.

## Framework Two: Four Layers of Persistence — Migrating State from LLM Memory to Deterministic Files

The essence of amnesia is "state lives in unreliable LLM memory." The fix is to externalize state into deterministic files on disk. Four kinds of artifact each play their part:

| Layer | Artifact | Question it answers | This project's counterpart |
|----|------|-----------|-----------|
| Progress | PROGRESS.md / STATUS.md | How far did we get? What's next? | `STATUS.md` one-line status + next entry point; `M1/PROGRESS.md` active_feature/blockers |
| Decisions | DECISIONS.md | Why this choice? What paths were rejected? | The `related`/`affected`/`out_of_scope` three-part links in `features.json` |
| Checkpoint | Git commit | Which known-good state is the code in? | `feat/{feature_id}` branch + normalized commit message |
| Initialization | Startup-flow doc + self-check script | How do you bring the environment up from scratch and get oriented? | `M1/AGENTS.md` handoff guide + `M1/init.sh` environment self-check |

Note that **the decision log and the progress file are two different things.** Progress answers "how far," decisions answer "why." The compaction strategy loses precisely the latter — so even if you only ever compact, you should still persist the key decisions separately.

## Framework Three: Initialization Is Its Own Phase, Not an Appendage to Implementation

Beginners tend to mix "configuring the environment" and "writing features" into the first session. That's wrong, because the **optimization targets of the two are fundamentally different**: the implementation phase optimizes for "the feature is correct," while the initialization phase optimizes for "any future session can take over at low cost." Mix them, and initialization gets done shoddily under feature-delivery pressure — dependencies left unpinned, the test framework left unverified, nobody writing down "how to start."

So **the first session should be pure initialization**: no business features, just four things — configure the dependencies, verify that the test/build framework actually runs, write down the startup contract, and leave empty shells for the progress files. To gauge whether initialization is complete, use a **startup-readiness checklist**:

| Readiness item | Criterion | This project's implementation |
|--------|------|-----------|
| Can start | One command brings the environment up with all dependencies in place | `bash M1/init.sh` runs six self-check stages; FAIL=0 means green |
| Can test | The test/build framework is verified runnable | init.sh stage 6, "end-to-end smoke test": run build and check the artifact exists |
| Can see progress | A file answers "how far did we get" | `STATUS.md` + `M1/PROGRESS.md` are in place |
| Can take the next step | There's a clear "pick the next thing" algorithm | `AGENTS.md`'s "feature-selection algorithm" + "5-step session startup" |

**The goal is a single quantifiable number: new-session rebuild cost < 3 minutes.** Cross that line and reset becomes a burden, and the team (and future you) will instinctively dodge resets in favor of soldiering on with compaction — landing you right back in amnesia. A warm start also has an accelerator: **project templates** — turn this structure into reusable scaffolding so a new project's first session just slots it in, and initialization goes from "improvise it" to "fill in the blanks."

## Case Study: How This Project's "Three-Piece Set" Squeezes Reset Cost Under Three Minutes

**A single, ordered entry point.** CLAUDE.md hard-codes the onboarding sequence: read `STATUS.md` first, then the three-piece-set docs, then run `init.sh`. A new session relies on nobody verbally explaining the background.

**STATUS.md is "one-line status + next entry point."** It doesn't pile up history; it answers only two questions: what state are we in now, and what's the next thing to do. Once a new session reads that one line, the direction is set.

**AGENTS.md is the "handoff guide," breaking the vague "start working" into deterministic steps**: ① `cat M1/PROGRESS.md` to see active_feature/blockers/next_candidates ② read `STATUS.md` ③ `bash M1/init.sh` — only start once the environment is all green ④ pick the next thing via the "feature-selection algorithm" ⑤ do the work → wrap up by updating PROGRESS + STATUS. It even turns "which feature to pick" — that most gut-feel of decisions — into an algorithm: prefer the lowest-numbered `failing` feature whose blockers are cleared; finish a slice before moving to the next, no skipping.

**init.sh is the deterministic evidence of "can start + can test."** Six stages, one unified report, deliberately **not using `set -e`** — it runs all the way through, surfacing every problem in one pass, then gives the `FAIL=0` green light. It distinguishes WARN (non-blocking) from FAIL (blocking). A new session runs it once and knows whether the environment is ready to work.

Put the three pieces together, and a new session's handoff routine is: read the one-line status (30 seconds) → follow the 5 steps (including one run of the self-check script, 1-2 minutes) → get a concrete next thing to do. Reset cost is squeezed under three minutes, so "reset" goes from a painful event to a routine operation you can do anytime.

## Actionable Practices: Bolt an Anti-Amnesia Foundation onto Your Long Tasks

1. **Make the first session initialization only — don't touch business features.** Accept it against the four items of the "startup-readiness checklist."
2. **Write an init.sh-style self-check script that doesn't use `set -e`.** Run all checks in one pass and report FAIL/WARN in a unified way.
3. **Persist progress and decisions separately.** STATUS/PROGRESS answer "how far"; DECISIONS (or the features three-part fields) answer "why."
4. **Write an AGENTS.md-style handoff guide that turns 'pick the next thing' into an algorithm.**
5. **Force an update of STATUS + the progress files at the end of every session.** This is the only moment to cash in "session memory" for "artifacts the next session can read."
6. **Prefer reset over endless compaction.** When context starts getting anxious, don't soldier on — reset proactively and rebuild from artifacts. The precondition is that rebuild cost is already squeezed under three minutes.
7. **Distill this structure into a project template.**

## Wrap-Up

Amnesia in long tasks isn't a question of whether it happens, but when — the physical ceiling of the context window makes it inevitable.

> [!NOTE]
> What you should really optimize isn't "making a single session live longer," but "letting any new session take over at full strength within three minutes." A session that can be discarded and rebuilt at any time is the session that never loses the thread.
