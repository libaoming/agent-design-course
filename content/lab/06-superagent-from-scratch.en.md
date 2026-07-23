---
title: superagent-from-scratch
nav: superagent-from-scratch
section: lab
status: open-source
repo: https://github.com/libaoming/superagent-from-scratch
slug: superagent-from-scratch
tags: [teaching rebuild, agent loop, zero framework]
related_lecture: c
summary: A ~1,000-line, zero-framework, teaching-first rebuild of a modern SuperAgent harness — the agent core distilled out of deer-flow's 185k lines, readable in an afternoon.
order: 6
---

> If you want to understand the core of a modern Agent framework, both usual roads are blocked: top open-source projects are unlearnable — deer-flow (76k stars) has a 185k-line backend with 2,300 lines of agent core buried inside a product shell; tutorials are too shallow — they stop at function calling and never reach context management, defensive middleware, or subagent isolation. superagent-from-scratch takes a third road: distill deer-flow's core architecture into a zero-framework teaching implementation with under 700 lines in src/, where the `messages → LLM → tools → append` loop is finally laid bare.

## What it solves

| Obstacle | Symptom |
|---|---|
| Top open source is unlearnable | Finding 2,300 core lines in a 185k-line codebase means drowning in the product shell first |
| Tutorials are too shallow | They end at function calling — middleware, subagents, and long-horizon tasks never appear |
| Frameworks hide the essence | One LangChain black-box line, and you never see what the loop actually looks like |

## How it works: five linear slices

Each slice has a git tag (sfs-s1…s5), offline tests, and a why-first teardown note:

| Slice | Content |
|---|---|
| S1 | Agent loop + LLM seam + 3 real tools |
| S2 | Middleware pipeline (before_model / after_model / wrap_tool_call) |
| S3 | Task tool + subagent delegation — context isolation, conclusions only |
| S4 | Skills system (SKILL.md discovery + slash activation) |
| S5 | Long-horizon tasks (write_todos + goal-resume loop + HITL interrupts) |

Tests run on recorded LLM fixtures, never mock.patch — 62 offline tests all green, and the only runtime dependencies are anthropic + pyyaml.

## How to use it

`git clone` → `uv sync` → `uv run pytest -q`. Fully offline, no API key needed. Read the code and teardown notes slice by slice — done in an afternoon.

## In one sentence

Not yet another Agent framework — it lays out "what actually happens inside the framework" in a thousand lines for you to read.
