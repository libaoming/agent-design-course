---
title: Why Multi-Agent Orchestration Should Be a Script, Not Model Improvisation
module: c
order: 7
slug: workflow-orchestration
nav: Workflow Orchestration
summary: The quality of multi-agent collaboration comes from a hard-coded blueprint — where to parallelize, where to barrier, how many votes to verify, when to exit early. We dissect that blueprint using Claude Code's Workflow tool.
tags: [Workflow, Multi-Agent, Harness]
---

> Setting up the target: in 2026, "multi-agent" is one of the hottest words around — and one of the highest-crash-rate practices. Hand a task to a crowd of agents "collaborating freely" and the usual ending looks like this: two agents duplicate the same work, a third half-believes each of their contradictory conclusions, nobody is responsible for verification, and the summarizing agent passes off "I looked at it" as "I checked it." Each model generation gets stronger; none of these diseases go away — because they are not intelligence problems. They are **structure** problems.

The core claim of this lecture in one sentence:

**The quality of multi-agent collaboration comes from a hard-coded blueprint, not from how smart the agent in each cell is.** The blueprint decides: how the task splits, where things run in parallel, where everything must sync up, who verifies whom, how many votes count, and what condition triggers early exit. That blueprint should be deterministic code — not the model's improvisation.

In 2026 Claude Code productized this blueprint as the Workflow tool: orchestration logic is written in JavaScript and executed deterministically — loops, branches, fan-out all fixed; only the concrete work inside each cell (searching, judging, rewriting) goes to sub-agents. This lecture uses it as the running example, but blueprint thinking applies to any multi-agent framework.

## Which tasks deserve orchestration: three motives

Cold water first: most tasks **don't** deserve orchestration. Single-fact lookups, one or two independent subtasks, conversational Q&A, trivial edits — anything one agent can do correctly end-to-end makes orchestration pure overhead. The test is "does structure create value."

Tasks worth orchestrating come from exactly three motives:

| Motive | What's missing | Typical tasks | Orchestration shape |
| --- | --- | --- | --- |
| Coverage | One perspective can't sweep it all | Whole-repo audits, multi-channel research, competitor scans | Decompose, cover in parallel, synthesize |
| Confidence | One judgment can't be trusted | Bug confirmation, design review, fact-checking | N independent perspectives, adversarial verify, keep survivors only |
| Scale | One context window can't hold it | Large migrations, per-file rewrites, hundreds of items | Discover the work list, pipeline each item |

The boundary versus "spawn a sub-agent": a sub-agent is *sending one person to do one job*; orchestration is *building an assembly line where N people cooperate by blueprint*. Only when you need the blueprint itself — where deduplication goes, how many verification votes, when to exit early — is an orchestration script worth writing.

## The most important stroke on the blueprint: pipeline or barrier

Ninety percent of orchestration mistakes happen at the same spot: **using a barrier where a pipeline belongs.**

The two primitives:

- **Pipeline**: each item walks through all stages independently; stages don't wait for each other. Item A can be at stage three while item B is still at stage one. Wall-clock equals the slowest single-item chain.
- **Barrier**: wait for **all** items to finish this stage before any enters the next. Wall-clock equals the sum of each stage's slowest member.

Default to pipeline, always. A barrier is justified only when the next stage genuinely needs **all** results from the previous one, and there are only three legitimate reasons:

1. **Cross-item deduplication or merging** — you can't judge duplicates without the full set;
2. **Zero-result early exit** — "no bugs found, skip the whole verification phase";
3. **The next stage compares against "the other findings"** — scoring, ranking, picking representatives.

These reasons do **not** count: "I need to tidy the data first" (put the tidying inside a pipeline stage), "the stages are conceptually separate" (that's exactly what a pipeline models), "the code looks cleaner." The barrier's cost is real wall-clock: if the slowest of five parallel searchers takes three times the fastest, a barrier wastes two-thirds of the fast ones' time idling.

## A pattern library: buying confidence with structure

Orchestration's second payoff is quality — structural redundancy purchasing certainty. The recurring shapes:

| Pattern | How | What it cures |
| --- | --- | --- |
| Adversarial verify | N independent skeptics per finding, prompted to refute it; majority refutation kills it | Plausible-but-wrong findings |
| Diverse-lens verify | N verifiers each with a different lens (correctness, security, reproducibility), not N clones | Failure modes redundancy can't catch |
| Judge panel | N independent attempts from different angles, scored in parallel; synthesize from the winner, graft runner-up highlights | Local optima of "one draft, endlessly revised" |
| Loop until dry | Stop only after K consecutive rounds yield nothing new — not after counting to N | Missing the long tail in unknown-size tasks |
| Multi-modal sweep | Parallel agents each searching a different way (by container, content, entity, time) | Blind spots of a single search angle |
| Completeness critic | A final agent asks "what's missing"; its output becomes the next round of work | Stopping too early |
| No silent caps | Any truncation (top-N, sampling) must log what was dropped | The illusion of "covered everything" |

Readers of the earlier lectures in this module will recognize these: **adversarial verify is the multi-agent version of keeping verify independent from implementation; loop-until-dry mirrors running fixtures until no new errors surface; no-silent-caps is "read it back before declaring done."** The same harness discipline, relocated to the multi-agent runtime.

## A real case: a candidate-sourcing pipeline

The trigger was a Claude Code product manager at Anthropic publicly sharing her daily-driver use case: give the agent a role profile, have it run a dynamic workflow to find 100 candidates — each with public-footprint links and a one-line pitch — render a page, email it to her, and close the laptop for the day. We replicated a scaled-down pipeline of the same shape:

```text
Role profile (a constant, injected into every agent's prompt)
   |
Source phase   4 channel agents searching in parallel
               (social platforms / GitHub / Chinese communities / podcasts and talks)
   |           barrier justified here: cross-channel dedup needs the full set
Pure-code dedup and ranking (zero tokens): 29 people -> 26, take top 12
               (log reports 14 dropped)
   |
Verify phase   12 "skeptic" agents check every link in parallel; refuted means removed
   |
Return structured JSON -> main loop renders the deliverable page
```

Measured: 16 agents, six and a half minutes, funnel of 29 found, 26 after dedup, 12 into verification, 11 survived. Three lessons worth more than the numbers:

1. **Deterministic work goes to code, not tokens.** Dedup, ranking, link merging were plain JavaScript — agents only did what requires judgment: searching and verifying.
2. **Finders and verifiers must be different agents.** Finders have an incentive to pad the list (the prompt asks for 5–8 people), so each candidate went to an independent agent that re-opened every link. In the actual run, verification eliminated nobody outright but stripped several dead or misattributed links.
3. **The dedup key breaks first.** Name normalization couldn't catch the same person reported by two channels under different spellings (one channel used the Chinese name, another the romanized handle), and a duplicate slipped into the final list. Production should key on "domain plus handle." These pits only surface when you actually run — so validate the shape at one-tenth scale, then scale up.

## Actionable practice: minimal skeleton and eight disciplines

The minimal runnable skeleton of a Workflow script (plain JavaScript, opening with a pure-literal meta block):

```javascript
export const meta = {
  name: 'review-changes',
  description: 'Review changes by dimension, adversarially verify each finding',
  phases: [{ title: 'Review' }, { title: 'Verify' }],
}

phase('Review')
// schema forces sub-agents to return validated JSON — no prose parsing
const r = await agent('Review src/ for correctness issues…', { schema: FINDINGS })

phase('Verify')
const v = await parallel(r.findings.map(f => () =>
  agent(`Adversarially verify: try to refute ${f.title}`, { schema: VERDICT })))

return { confirmed: v.filter(Boolean).filter(x => x.isReal) }
```

Eight disciplines, ordered by how often each pit gets stepped in:

1. **Scout before orchestrating**: the main loop first maps the work list (which files, channels, items), then feeds it to the script. You don't need the shape before the task — only before the orchestration step.
2. **Pipeline by default, barriers need a reason**: see above; this is the first lever on wall-clock time.
3. **All sub-agent output goes through a schema**: validation happens at the tool layer with automatic retries; the main loop always receives structured objects.
4. **Prompts must be self-contained**: sub-agents cold-start with no conversation history — profiles, rules, and dates get written into the prompt.
5. **Separate finding from verifying; verifiers play skeptic**: better to spend an extra round of verification than let plausible fakes into the final output.
6. **Deterministic logic is code**: dedup, sorting, counting, filtering never go to an agent.
7. **Truncation must leave a trace**: "took top 12, dropped 14" belongs in the log — readers of the result deserve to know the coverage boundary.
8. **Small before big**: validate the shape at one-tenth scale where the pits surface cheaply, then scale up reusing cached results.

And one meta-discipline: **split big jobs into multiple workflows and keep the human in the loop.** Understand, design, implement, review — one workflow each, and you read each result before deciding the next. Orchestration solves the structure problem inside one pipeline; the steering wheel between pipelines stays in human hands.

## One-sentence close

Multi-agent isn't turning one unreliable thing into N of them — it's using a deterministic blueprint to make N unreliable things cancel out each other's unreliability. How well the blueprint is drawn is the entire difficulty of orchestration.
