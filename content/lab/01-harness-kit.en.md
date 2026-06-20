---
title: harness-kit
nav: harness-kit
section: lab
status: open-source
repo: https://github.com/libaoming/harness-kit
slug: harness-kit
tags: [project scaffold, engineering methodology, Claude Code]
related_lecture: c
summary: The engineering method for "running long tasks with Claude Code", distilled into a project skeleton you can clone and use.
order: 1
---

> A long-running Agent's worst enemy isn't a lack of intelligence — it's getting lost on a long task: forgetting the goal, losing track of progress, drifting off plan, finishing with no way to verify. The root cause is entrusting all of that to the model's unreliable memory. A harness is the rig you strap around the model: a deterministic engineering structure that moves the goal, the progress, and the verification criteria into external files, so the Agent re-anchors at every step and doesn't drift. harness-kit turns "how to build that rig" into a cloneable methodology with templates.

## What it solves

Run a long task with Claude Code that spans multiple sessions and you've probably hit these four walls:

| Failure | Symptom |
|---|---|
| Cross-session amnesia | New session, the Agent forgot where it left off and why it was designed that way |
| Progress drift | Set out to build A, drifted to B along the way, no single source of truth |
| Missing verification | Claims "done" with no reproducible passing criteria |
| Context explosion | Material dumped into the window all at once, important info buried |

They share one root: business rules, progress, and verification criteria were entrusted to unreliable LLM memory. harness-kit moves them all into deterministic files.

## Core mechanism: four layers of defense

| Layer | Role | Artifact |
|---|---|---|
| L1 Persistence | Rules/progress on disk | CLAUDE.md + STATUS.md + Auto Memory |
| L2 Methodology | Single source of truth + verifiable slices | features.json + milestone trio + fixtures |
| L3 Automation hooks | Deterministic automation | hooks (Stop/SessionStart progress append) |
| L4 Context isolation | Outsource dirty work to subagents | isolation discipline + dedicated subagent |

These land in five core components: CLAUDE.md (project constitution), STATUS.md (single-page state), features.json (atomic-task source of truth, pending/in_progress/failing/passing), the milestone trio (init.sh / AGENTS.md / PROGRESS.md), and fixtures-before-code.

## How to use

After git clone, two ways: manual — copy the 11 templates under templates/, fill in the placeholders, and start; one-shot — install it as a Claude Code plugin, run /harness-kit:harness-init, answer a few questions, and the whole skeleton is scaffolded. The repo ships a filled-in examples/demo-cli/ minimal sample and docs/methodology.md with the four-layer walkthrough.

## In one line

Not template-nesting — it's moving the fact that "this project is still alive, and here's how far it got" out of your memory and into files.
