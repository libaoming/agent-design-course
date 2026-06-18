---
title: "Teardown: Claude Code — A Coding Agent That Nails All Five Layers"
order: 0
slug: claude-code
nav: Claude Code
target: Claude Code
summary: Using the course framework as a lens to dissect Claude Code's five-layer foundation, transparency, error recovery, and context management.
tags: [实战示例, Claude Code, 拆解]
---

## Why Claude Code Makes a Good Sample

Claude Code is Anthropic's command-line coding Agent — in one sentence, it's "a programming agent that lives in your terminal, can read and write your codebase, run commands, and autonomously plan multi-step tasks."

It's worth dissecting not because it's the most hyped, but because it gives every layer of abstraction we cover in this course a concrete, tangible engineering counterpart. Loop, Tool, Planning, Memory, Multi-Agent — these five layers are mashed together into one blob in many Agent products; in Claude Code, nearly every layer has its own independent, explicit, configurable design. It's an ideal "framework X-ray" — point any lens at it and a clear structure jumps out.

The game here is: instead of reciting a feature list, we'll mount the course's frameworks onto it one by one and see what a real product looks like under each.

## Lens One: The Five Foundational Layers

Let's start by sweeping through with Module A's "five foundational layers." The table below shows how each layer concretely lands in Claude Code:

| Foundation Layer | How Claude Code Implements It | Key Design Point |
|--------|-------------------|-----------|
| Loop | A dynamic three-phase loop of gather → act → verify, with standard ReAct underneath | Five termination conditions: success / max_turns / max_budget_usd / during_execution / max_structured_output_retries — termination keys off cost ceilings and exceptions, not a hardcoded step count |
| Tool | 13 core built-in tools (files / search / execution / Web / orchestration) + MCP external hookups | Permissions go down to command granularity (`Bash(npm run test *)`); read-only tools run concurrently, writes run serially; ToolSearch loads tool schemas on demand |
| Planning | plan mode: read-only exploration → produce a plan → human approval → execute | Splits "one high-risk step" into "two low-risk steps," decoupling planning from execution |
| Memory | Dual track: CLAUDE.md (project/team level) + Auto Memory (user/cross-project level) | Four-tier coverage (Managed > User > Project > Local) + `@import` + upward directory-tree lookup |
| Multi-Agent | Three tiers: Subagent (one-way summary handback) / Agent Teams (two-way collaboration) / Background (async) | Each tier solves a different problem: Subagent tames context bloat, Teams tame the emergent behavior of collaboration |

This table is itself an insight: **the five layers are not equally developed**. Loop and Tool are the stable foundation, Planning (plan mode) is the most refined piece, and within Multi-Agent only Subagent is stable while Agent Teams is still marked experimental. A mature product daring to label an advanced feature "experimental" is precisely a sign that it knows which layers hold up in production and which are still being polished.

The Loop's termination conditions deserve a callout of their own. Most people instinctively reach for "at most N steps" as a backstop for an Agent, whereas Claude Code's backstop is a **cost ceiling + exception type**. This is an institutional trust in the model's autonomous judgment — it doesn't assume "the Agent will run off the rails, so we must cap its steps," but rather "the Agent will judge for itself when to stop; I just need to guard the wallet and the exceptions." This choice determines that its users are delegating, not co-piloting.

## Lens Two: Picking Three Dimensions to Go Deep

The five foundational layers are the skeleton. Next we'll use the L3 capability dimensions and the Harness subsystems as a lens, picking the three most interesting dimensions to dig into.

### Dimension A: Transparency (How It Lets You See What It's Thinking)

The L3 transparency dimension asks: can the user understand what the Agent is doing right now, and why? Claude Code's answer is hidden in a few unassuming engineering details:

- **Every tool call carries a description**. Not "executing a command," but an action-level, plain-language explanation like "discard local changes and align with remote main." This lets a bystander grasp the intent without having to read the command itself.
- **plan mode is itself a transparency device**. It forces the Agent to lay out a full plan in front of you for approval before acting — which amounts to pulling "the Agent's intent" out of the black box and turning it into readable text.
- **Hooks expose a range of lifecycle events** (PreToolUse / PostToolUse / Stop / PreCompact, etc.). You can hook into any point to observe or even intercept, turning "what the Agent is doing" into a programmable, observable stream.

Transparency here isn't "print a few more log lines" — it's broken out across three levels: interaction design (plan mode), the tool contract (description), and observability infrastructure (Hooks).

### Dimension B: Error Recovery (What It Does After Hitting a Wall)

The L3 error-recovery dimension examines an Agent's autonomy after hitting a wall. A classic example: a tool call returns `python: command not found`, and the Agent doesn't keep banging out the same command — it infers that macOS has no `python` by default, switches to `python3`, and succeeds. This is the standard recovery loop of "fail → diagnose → adjust the tool → retry → verify," and the key is that it **adjusted its strategy rather than retrying blindly**.

Looking one layer up, error recovery in Claude Code has an institutionalized backstop: the Loop's `error_during_execution` termination condition ensures exceptions aren't swallowed indefinitely; Subagents isolate potentially-failing exploratory subtasks in their own context, so even if a subtask goes off the rails it doesn't pollute the main thread. Error recovery isn't just "the Agent is smart" — it's that the architecture hands it a safety net of "failures can be isolated, exceptions have an exit."

### Dimension C: Context Management (How Its Memory Doesn't Blow Up)

This is the most hardcore part of the Harness "knowledge subsystem." Claude Code's context management is dual-track:

- **CLAUDE.md**: solves "how to pass team conventions to the Agent." It goes into git, stacks across four tiers, supports `@import` for splitting, and does upward directory-tree lookup — essentially compiling project knowledge into the starting point of every session.
- **Auto Memory**: solves "how a personal workflow gets remembered." It lives under `~/.claude/`, and on read it first ingests the top 200 lines (or 25KB), then expands topic files on demand, accumulating continuously across projects.
- **Multi-layer Compaction Pipeline**: when context approaches the limit, it frees up space in the order of "old tool outputs → compress the conversation → keep the most recent exchanges → re-inject the root CLAUDE.md → user can specify focus." Note the last two steps — after compaction it **re-injects** CLAUDE.md, guaranteeing that no matter how long the session runs, project conventions never get squeezed out of the window.

Add one more detail about ToolSearch: MCP tool schemas aren't preloaded — they're discovered on demand. This means no matter how many MCP servers you connect, the startup context overhead stays nearly flat — compressing the context cost of multi-tool scenarios from O(n) down toward O(1). The core proposition of context engineering here is consistent throughout: **the window is a scarce resource; what should stay resident, what should be on-demand, what should be compressed — each category gets its own dedicated mechanism**.

## Key Insights: The Two Design Decisions Most Worth Stealing

**Decision One: plan mode — defusing high risk by "splitting into steps."** An Agent's most dangerous moment is "autonomously executing an irreversible operation." Claude Code didn't try to brute-force this problem with "a more accurate risk classifier"; it sidestepped it with an interaction structure: first read-only exploration, then produce a plan, then human approval, then execute. One high-risk step becomes two low-risk steps. This is a textbook case of converting an "accuracy problem" into a "process problem" — because even the most accurate classifier has that 1%, and a 1% misjudgment landing on an irreversible operation is a disaster.

**Decision Two: dual-track memory — cultivating two kinds of stickiness separately.** CLAUDE.md manages team knowledge, Auto Memory manages personal workflow. It didn't blend the two into one "memory system" — it cleanly split them by "who owns this knowledge, and what scope it should apply in." The result: project knowledge spreads within the team alongside git, personal knowledge accumulates across a user's projects — two independent accumulation curves. For anyone building Agents, this points to an often-overlooked design question: **the "scope" and "ownership" of memory often matter more than "how much" you remember**.

## A Checklist of Takeaways for Building Your Own Agent

Having used Claude Code as a mirror, here's a ready-to-use checklist distilled from it:

1. **Think through whether the Loop's termination condition is "step count" or "budget + exceptions."** The former treats the Agent as an untrustworthy script, the latter as a delegable colleague — and this choice reverse-defines your product positioning (co-pilot vs delegate).
2. **Make tool permissions command-level, not just tool-level.** Opening `Bash` wide versus only allowing `npm run test *` differs by an order of magnitude in security boundary.
3. **For high-risk, irreversible operations, prefer "split + approve" over "a more accurate judgment."** Process decoupling is more reliable than model accuracy.
4. **Design memory along "scope × ownership" tracks.** Team-level goes into git, user-level spans projects — don't mash them into one pot.
5. **Budget context like a scarce resource**: distinguish resident (project conventions), on-demand (lazy-loaded tool schemas), and compressed (old outputs), and make sure core conventions are re-injected after compaction.
6. **Break transparency into three levels of implementation**: tool calls carry plain-language descriptions, key checkpoints are approvable, and the lifecycle is hookable for observation — rather than just piling up logs.
7. **Error recovery needs an architectural backstop, not just a smart model**: isolate failure-prone exploration into a sub-context, and give exceptions an explicit exit.
8. **Dare to label advanced features "experimental"**: polish the basics to stability first, then push complex collaboration, rather than dumping every feature out at once.

Hold up Claude Code as a mirror and you'll find that the hard part of building Agents is rarely "making the model smarter" — it's almost entirely "building the model a structure where its smarts can land safely." That is exactly what the two frameworks, Harness and the five foundational layers, are all about.
