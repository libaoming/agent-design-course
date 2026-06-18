---
title: Why the Repo Must Be the Agent's Single Source of Truth
module: c
order: 2
slug: repo-source-of-truth
nav: Repo as Source of Truth
summary: Information that isn't in the repo effectively doesn't exist for an Agent. Knowledge must be committed to files, not scattered across tools.
tags: [Harness, 事实源, ACID]
---

## Setting the Target: What Happens When Project Knowledge Lives in Slack

Picture a team like this: architectural decisions live in some Slack channel, requirements are scattered across dozens of cards in a ticketing system, the gotchas hit during deploys are buried in the comments of some collab doc, and who owns what is settled verbally in the group chat. The human members keep things barely running on the strength of "I remember seeing that in some message somewhere."

Now hand the same task to an Agent. Its performance suddenly tanks: it has no idea about the conventions everyone discussed in the chat last week; it repeats a pitfall someone wrote down in a ticket comment three days ago; it's completely wrong about "where are we now," because it can't read any of that scattered context.

The root cause comes down to one sentence: **information that isn't in the repo effectively doesn't exist for an Agent.**

Humans have an implicit information-retrieval network—memory, relationships, "let me go ask so-and-so." An Agent has none of that. Its information inputs come from exactly three defined sources, and everything outside them is a blind spot. This lecture lays out why the repo must be the Agent's single source of truth, and how to make that real through engineering.

## Framework: An Agent Has Only Three Sources of Information

walkinglabs' Harness Engineering framework collapses all of an Agent's information inputs down to three—and only three—sources:

| Source | Content | Maintained by | Characteristics |
|---|---|---|---|
| System Prompt | Role, discipline, global constraints | Harness designer | Injected fresh every session, limited capacity |
| Repo Files | Code, docs, state, decisions, progress | Team + Agent | Infinitely extensible, versionable, the main battlefield |
| Tool Output | Command execution results, contents of read files | Produced at runtime | Ephemeral, evaporates when the session ends |

The key corollary: **the system prompt has limited capacity and tool output evaporates, so any knowledge that needs to persist long-term must land in repo files.** Whatever lives in Slack, collab docs, or the ticketing system—no matter how important it is to humans—sits outside those three sources for the Agent, which means it doesn't exist.

Around this fact, the framework offers four principles for committing knowledge into the repo:

| Principle | Meaning | Flip side (consequence of violating it) |
|---|---|---|
| Keep knowledge close to the code | Write decisions and conventions next to the code they affect | Knowledge drifts away from code; after the Agent edits the code it has no idea which convention it broke |
| Standardized entry point | Have one fixed landing page (AGENTS.md / this project's STATUS.md) that every new session reads first | The Agent doesn't know where to begin and has to feel its way around from scratch every time |
| Minimal but complete | Write only the necessary information, but don't omit a single necessary piece | Information overload buries the key points, or a missing link leads to a wrong judgment |
| Synced with the code | Knowledge is updated and committed together with the code | The docs say one thing and the code does another; the Agent gets misled |

The accompanying state management is bound by the four ACID properties (borrowing the database-transaction metaphor):

| Property | What it means inside an Agent repo |
|---|---|
| Atomicity | One complete action maps to one commit—either it all lands or no half-finished work is left behind |
| Consistency | There's an executable verification predicate (verify); before and after a state change, the repo is always in a valid state |
| Isolation | Concurrent sessions/branches are isolated, avoiding races where they overwrite each other |
| Durability | State is persisted via git, never dependent on the memory of any single session |

There's a dead-simple test for whether this whole system is in place—**the fresh-session test**: spin up a brand-new Agent session, give it no verbal supplements, let it read only the repo files, and see whether it can answer "what is this project, where are we now, what's the next step, and what pitfalls must we avoid." If it can, the source of truth lives in the repo; if it can't, the knowledge is still scattered outside the repo.

## Case: Landing the Abstract Principles in a Set of Real Files

Below, using this course site project's own engineering practices, we map each of the principles above onto a real file. This project itself was built with this very methodology, so it can serve as a living sample.

**Standardized entry point = STATUS.md, the first file read every session.** The very first line of the file spells out its contract: "The first file read every session. Must be updated at wrap-up." It contains exactly three just-enough chunks of information: a one-line status (what got done today, what's left), the next entry point (specific down to "read this file first, then PROGRESS, run which init script, which slice to work on now"), and a list of pitfalls. A brand-new session that reads this one file knows where it stands and where to head next.

The project's CLAUDE.md turns the onboarding order into a hard rule: read STATUS.md first, then the trio of requirements/design/architecture/slices, and run the init script before starting work to confirm the environment is green. This effectively institutionalizes the "fresh-session test": every session is forced to be treated as a brand-new session, never allowed to rely on memory from the previous round.

**Single source of truth = features.json.** Information like "what tasks exist right now, what state each is in, who's blocking whom" is the most prone to scattering and drifting. The project collapses it into the structured file features.json: each feature has a definite state machine `pending → in_progress → failing → passing`, with one iron rule hard-coded—

> Only flip to passing when verify actually passes; finishing a draft only gets you to in_progress.

This is the on-the-ground realization of "Consistency" in ACID: state isn't something the Agent changes on a whim—a transition is only allowed once an executable verification predicate passes. features.json also fills in a three-part association `related / affected / out_of_scope` for each feature, explicitly stating "which files this touches, what it impacts, and what it explicitly does not do"—an extension of "keep knowledge close to the code," letting any session (especially an isolated sub-agent) instantly judge what to read and what to skip without reading the entire repo.

**Progress persistence = M1/PROGRESS.md, migrating progress from LLM memory to a deterministic file.** The most dangerous way to store "where we got to" is inside the Agent's conversational memory—it evaporates the moment the session ends, which is exactly the "Durability" that tool output lacks. The project writes progress into PROGRESS.md: a table at the top marks the currently active feature and slice, the middle is a reverse-chronological Session Log, and the bottom even holds "if… then…" decision contingencies. The "Incremental Stream (pending cleanup)" section at the end of the file is appended to by an automation hook every round, with the convention that the next startup merges it in first and then clears it—so even "progress not yet cleaned up" doesn't slip through the cracks.

## Actionable Practices

1. **Create a standardized landing page** (AGENTS.md or STATUS.md), placed at the repo root. The first line spells out the contract ("read first every session / must update at wrap-up"). Put only three things in it: a one-line current status, the next entry point, and a list of pitfalls.
2. **Write the onboarding order into CLAUDE.md**: force every session to read the landing page first, then the requirements/design docs. Make the "fresh-session test" the default flow.
3. **Collapse task state into one structured single source of truth**, and give every task an executable verify. Set the iron rule: if verify hasn't passed, state may not be marked done; if verify is empty, work may not begin.
4. **Write progress into a deterministic file, never leave it in memory**. At each session's wrap-up, append a log: what was done, where the pitfalls are, what the verification concluded. Even better if a hook appends it automatically.
5. **Keep knowledge close to the code and synced with the code**: write decisions next to the code they affect, and commit them along with the code. Keep every commit atomic.
6. **Run the fresh-session test regularly**: spin up a clean session, feed it only files, and ask it about the project's current state and next step. Wherever it can't answer is a hole—patch it into the files.
7. **Isolate the context-hogging grunt work**: have a sub-agent read the scattered materials in an independent context and report back only the conclusion, while the main line always works off the deterministic files in the repo.

## Wrap-up

An Agent won't "go ask so-and-so," nor will it "scroll back through last week's group chat." Its world consists only of the system prompt, the repo files, and tool output—and of those, only repo files can carry knowledge over the long term.

> Anything you want the Agent to know long-term must be written into the repo; knowledge that can't make it into the repo will sooner or later turn into a pitfall the Agent can't see.
