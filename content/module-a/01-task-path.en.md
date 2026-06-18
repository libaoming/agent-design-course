---
title: Why an Agent's First Move Shouldn't Be to Start Doing
module: a
order: 1
slug: task-path
nav: Task Completion Path
summary: The task completion path is an Agent's ability to break down and drive a request from need to output. PMs should design it to be observable and instrumentable.
tags: [L3, 任务路径, 维度1]
---

## Setting Up the Target: An Agent With an Unclear Path Will Fail You in Three Ways

Start with a scenario. You hand a coding Agent a job: "Clean up these raw logs, compute the daily effective-call rate, and plot a trend chart."

An Agent with an unclear path tends to open like this: it immediately opens a single file and crams reading the data, cleaning it, computing stats, and plotting all into one script, banging it out in one shot. On the surface it "finished" — a chart came out. But when you take over, you discover: the data cleaning and the analysis are mashed together, so changing the statistical definition means rewriting half the script; somewhere in the middle a step errored out, it never noticed, kept computing on top of it, and the final chart is wrong — yet it reports "done."

This is the first failure of an unclear task path: **going off the rails**. The Agent starts doing before it has broken the request into ordered steps, so it has no concept of "which step of the whole path am I on right now." When it goes wrong, it doesn't know where it went wrong.

The second is **giving up halfway**. The Agent treats the task as one indivisible black box. Partway through execution it hits a blocker (say, a missing dependency) and either stops to ask you "what now?" or just abandons it, leaving behind a broken intermediate state. Because it never planned out "how many steps are on this path," it naturally has no idea which step it's stuck on or how many remain.

The third is **overstepping**. It does finish the stats you asked for, but along the way it also refactors your entire project's codebase and adds three features you never requested. It stretches the "path" out infinitely, unable to tell where the task boundary is.

These three failures share a single root cause: **the Agent has no explicit task completion path that both it and you can observe.** It short-circuits straight from "received the request" to "produced the result," and the stretch in between — which should be planned, segmented, and checked — is dark.

So as a capability dimension, what "task completion path" measures is not "did it eventually get done," but: **from request to output, how does this Agent decompose and drive the task — does it turn a vague request into a string of ordered, verifiable, bounded actions?**

## Framework: Breaking the Task Completion Path Into Four Stages

To evaluate an invisible process, you first need to give it a structure. I break the task completion path into four stages: Understand, Plan, Execute, Converge. Each stage has its key actions, its corresponding failure risk, and — most important for PMs — metrics you can instrument and observe.

![The four observable stages of the task completion path: understand the request → plan and decompose → execute and drive → converge and deliver](../assets/diagrams/task-path.svg)

| Stage | Key Actions | Failure Risk | Instrumentable Metrics |
|------|---------|---------|-----------|
| 1. Understand the request | Restate the task, identify implicit constraints, confirm acceptance criteria, judge the boundary | Executing a vague request as if it were precise; missing implicit constraints | Whether a task restatement/plan is produced; clarifying-question rate |
| 2. Plan & decompose | Break the task into ordered substeps, separate concerns, order the dependencies | Diving in without decomposing; steps mashed together and impossible to verify individually | Number of substeps; whether an explicit plan/todo is generated; whether steps carry acceptance points |
| 3. Execute & drive | Execute step by step, self-check each step, maintain progress state, adapt when blocked | Going wrong without noticing and pressing on; stalling or giving up when stuck | Whether each step has a result check; mid-task abandonment rate; blocker-asks vs. autonomous-progress ratio |
| 4. Converge & deliver | Self-check against acceptance criteria, report the path and result, stop inside the boundary | Overstepping into unrelated work; claiming done without self-checking | Whether delivery aligns with the initial acceptance criteria; number of overstepping actions; completion self-check coverage |

The way to use this table isn't to tick boxes cell by cell — it's to help you locate "which stage is this Agent weakest at." A common diagnosis: many Agents have strong execution (stage 3), with single tool calls that are fast and accurate, but their Understand and Plan stages (1, 2) are nearly empty — they skip "think it through first" and go straight to "head-down doing." The result is exactly the three failures from the last section.

> [!NOTE]
> A good Agent makes reasonable engineering decisions on its own before it starts — for example, splitting data generation and data analysis into two files, even if you didn't explicitly ask. This "separation of concerns" is itself a signal of high-quality planning: it shows the Agent walked the path in its head first, rather than figuring it out as it wrote.

Here you must especially distinguish two kinds of "exceeding expectations," because it bears directly on the stage 4 score. Valuable exceeding-of-expectations is being more thorough *within* the task path: handling edge cases ahead of time, providing two useful statistical definitions at once. Worthless exceeding-of-expectations is extending the path *beyond* the task boundary: adding features you didn't ask for, refactoring unrelated code. The former deserves credit; the latter deserves a deduction. An Agent with a clear path knows where its road leads — and knows where the road ends.

## Case: Two Agents Run the Same Cleaning Task

Back to the opening task — clean logs, compute the effective-call rate, plot a trend chart (the scenario is anonymized from a real internal data-analysis request). I ran it with two Agents and compared their task paths.

**Agent A (black-box-path type)**: On receiving the request, it immediately creates one script and writes everything from reading the CSV to plotting in a single file. At runtime it errors with `python: command not found`, stops, and asks: "There doesn't seem to be python in the environment — what should I do?" — that's a stage 3 blocker abandonment. After the environment is fixed it produces a chart and reports "done." But it used total calls as the denominator without distinguishing effective calls, and the "effective-call rate" in the request implied exactly that constraint. It missed an implicit constraint in stage 1, then failed to self-check against acceptance in stage 4, so it delivered a result that looked complete but used the wrong definition.

**Agent B (clear-path type)**: On receiving the request, it first restated: "My understanding is to clean the raw logs, compute the share of effective calls per day, then plot the trend," and proactively confirmed the definition of "effective call." Then it split the task into two files: one for data cleaning and definition computation, one for stats and plotting — separating concerns, making it easy to swap the definition later. During execution it hit the same `python: command not found`, but instead of stopping to ask, it autonomously judged "macOS doesn't have python by default, switch to python3," retried, and succeeded — the textbook "tool failure → autonomous adjustment → success" recovery. Finally it self-checked against the initial definition and additionally provided two versions of the data, "total-call rate" and "effective-call rate," clearly labeling the difference.

Both Agents "finished" the task. But A's path was dark, so its errors were invisible to you and its blockers needed you to backstop them; B's path was lit, leaving an observable trace at every stage. The gap isn't about who's smarter — it's about who treats the task as a path that needs planning and verification, rather than a one-shot black box.

## Actionable Practices: How to Design the Task Path Into an Observable Capability

**At the design level — make the path observable:**

- Force the Agent to produce an explicit plan or todo list before executing, even for a tiny task. This externalizes the internal thinking of stages 1 and 2 into an artifact you can see and instrument.
- Make every substep carry its own acceptance point (when this step is done, what counts as correct). A step with no acceptance point is a stage 3 with no interface for self-checking.
- Spell out the task boundary explicitly in the prompt / system design: what counts as in-scope, what counts as overstepping. Give stage 4 a clear "stop here" line.
- Distinguish "should ask" from "shouldn't ask." When the Understand stage is missing a key constraint, it should clarify; when the Execute stage hits a blocker it can debug itself, it shouldn't ask.

**At the measurement level — how to set KPIs:**

- Don't use "task completion rate" as your only metric — it rewards the Agent that "went off the rails but delivered." At minimum, split out two definitions: "completion rate" and "completion quality (self-check pass rate against acceptance criteria)."
- Instrument "explicit plan production rate": for what share of tasks did the Agent give a decomposition before starting? This is the most direct proxy metric for planning ability.
- Instrument "mid-task abandonment rate" and "blocker-ask rate": a high abandonment rate points to weak stage 3 driving ability; the ask rate needs to be read per scenario.
- Instrument "number of overstepping actions" and manually annotate the valuable vs. worthless ratio, to tune the stage 4 boundary.
- All metric thresholds must be calibrated against real task data — don't set them off the top of your head.

One reminder: these metrics don't simply add up. High completion rate but lots of overstepping and low self-check coverage doesn't necessarily mean good overall path quality. When evaluating, read strength and weakness by dimension, rather than synthesizing one total score that masks the specific shortfalls.

## Closing

> When you evaluate an Agent, don't only ask "did it finish." Ask "from request to output, how did it walk this road — and could you see every step?"
