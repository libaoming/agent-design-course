---
title: agent-memory-kit
nav: agent-memory-kit
section: lab
status: open-source
repo: https://github.com/libaoming/agent-memory-kit
slug: agent-memory-kit
tags: [agent memory, runtime, closed loop]
summary: A runtime memory layer for the product Agent you're building — four roles that distill experience into reusable lessons.
order: 2
---

> A stateless Agent learns nothing from its own history: it steps in the same hole again and again, and forgets the preference the user corrected last time. What it lacks isn't intelligence — it's a loop that captures "what it did, got wrong, was corrected on" and can retrieve it next time. agent-memory-kit gives the product Agent you're building exactly that loop.

## What it solves

This is runtime memory for **the product Agent you are building** — not Claude Code's own development memory; don't conflate the two. It targets these symptoms:

| Symptom | Root cause |
|---|---|
| Same class of task fails repeatedly | Failures are never recorded, let alone reviewed |
| Corrected preferences get forgotten | The correction lives only in that one conversation, never persisted |
| Experience can't migrate across sessions | There's no step that retrieves the relevant lessons |

## Core mechanism: a four-role loop

| Role | Responsibility |
|---|---|
| Doer | The product Agent does the work, leaving a trace |
| Reflector | A second Agent independently judges whether it was done right |
| Store | Distilled lessons are persisted as markdown |
| Retrieval injection | Before the next task, relevant lessons are retrieved back to the Doer |

The key is separating Doer and Reflector: the one doing the work and the one judging it aren't the same context, which avoids self-endorsement. Lessons land as human-readable markdown — auditable and hand-editable.

## How to use

After git clone, wire the four roles into your Agent: the Doer is your existing executor, hook a trace onto it; fill in Reflector / Store / retrieval-injection from the templates. The repo ships working implementations for retrieval-injection and the optimization loop, with Reflector / Librarian left as interface stubs.

## In one line

Let the Agent record "last time I did it this way I face-planted" as a lesson it can actually retrieve next time, instead of starting from zero every run.
