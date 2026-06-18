---
title: A Panoramic Map of the 21 Agent Design Patterns
module: d
order: 0
slug: overview
nav: 21-Pattern Panorama
summary: Lay out all 21 patterns from Google's "Agentic Design Patterns" at once, group them into 6 clusters, and mark which ones this course has already covered.
tags: [设计模式, 全景, 速查]
---

## Setting the Target: Patterns Aren't for Memorizing — They're for "Looking Up"

A lot of people bookmark a list of "21 Agent Design Patterns" and then never open it again — because they treat it as facts to memorize, can't memorize it, and never end up using it.

The right way to use patterns is **reverse lookup**: you have a concrete problem in hand, and you go to this map to find "is there an off-the-shelf playbook the industry already has?" For example —

- "My Agent's output quality is inconsistent — how do I get it to revise its own work?" → leads you to **Reflection**
- "A task needs to be split across several Agents working together — how do they talk to each other?" → leads you to **Agent-to-Agent communication (A2A)**
- "The model doesn't know about my company's internal docs — what do I do?" → leads you to **knowledge retrieval (RAG)**

If you don't know what patterns exist, you'll either **reinvent the wheel** (clumsily re-invent a playbook someone else already shaped) or **reach for the wrong move** (you should be using Reflection, but instead you're frantically tweaking the prompt). This lecture goes deep on no single pattern; it does just one thing: **lay out all 21 patterns at once, so you know "when I hit a certain kind of problem, which page should I flip to."**

This set of patterns comes from Google's *Agentic Design Patterns* (Antonio Gulli). Below they're grouped into 6 clusters, with a note on **whether the first three modules of this course have covered each one** — covered ones point you back to where, and the uncovered ones (the blind spots) are exactly what the rest of this module goes deep on.

## The Framework: The Full 21-Pattern Map

Legend: ✅ already covered in depth in the first three modules · 🟡 mentioned in passing somewhere · ❌ a blind spot in this course (covered later in this module)

| Cluster | Pattern | In a sentence | Course coverage |
|---|---|---|---|
| Foundational execution | Prompt Chaining | Break a complex task into serial prompt steps | 🟡 B framework selection |
| Foundational execution | Routing | Dispatch by input type to different handling branches | 🟡 B Gateway / evaluation |
| Foundational execution | Parallelization | Run independent subtasks in parallel, then aggregate | 🟡 B framework selection (Map-Reduce) |
| Foundational execution | Tool Use | Let the model call on capabilities in the external world | ✅ A tech-foundation 5 layers, L2 |
| Foundational execution | Planning | Decompose a goal into ordered steps | ✅ A 5 layers L3 + task path |
| Quality & safety | Reflection | Have the Agent self-critique and revise | ❌ blind spot → covered in this module |
| Quality & safety | Evaluation | Systematically test whether the Agent is any good | ✅ B evaluation & Benchmark |
| Quality & safety | Guardrails | Block out-of-bounds / harmful inputs and outputs | ✅ A boundary behavior |
| Memory & knowledge | Memory | Remember what should be remembered across sessions | ✅ A 5 layers L4 + B context engineering |
| Memory & knowledge | Learning | Improve its own strategy from interactions | ❌ blind spot → covered in this module |
| Memory & knowledge | RAG | Retrieve external knowledge into the context | ❌ blind spot → covered in this module |
| Collaboration & connectivity | Multi-Agent | Multiple Agents split work that a single one can't hold | ✅ A 5 layers L5 + B multi-Agent platforms |
| Collaboration & connectivity | A2A | What protocol Agents use to talk to each other | ❌ blind spot → covered in this module |
| Collaboration & connectivity | MCP | A standardized protocol for tool integration | 🟡 A 5 layers (MCP as a cross-cut) |
| Control & governance | Goal Setting | Give the Agent a clear goal and keep an eye on it | 🟡 A task path / B evaluation |
| Control & governance | Exception | How to survive after something goes wrong | ✅ A error recovery 4+1 |
| Control & governance | HITL | Put a human in the loop at critical nodes | 🟡 A transparency / boundary (no standalone lecture) |
| Control & governance | Prioritization | Which of multiple tasks/requests to do first | ❌ blind spot → covered in this module |
| Control & governance | Resource-Aware | Make trade-offs under cost/latency constraints | 🟡 B Gateway / evaluation |
| Reasoning & exploration | Reasoning | CoT / ToT and the like to make the model think deeper | ❌ blind spot → covered in this module |
| Reasoning & exploration | Exploration | Actively explore an unknown space | ❌ blind spot → covered in this module |

## How to Use This Map

There are two ways to open it:

**Reverse lookup by problem (the most common)**: you have a sticking point, scan the "in a sentence" column for the closest pattern, then go deep with the corresponding material. This table is your index page.

**Use 🟡 and ❌ to fill the gaps**:
- 🟡 patterns were mentioned somewhere in this course but never as the lead — to go deeper, follow the "course coverage" column back to where.
- The 6 ❌ blind-spot clusters (Reflection / Learning / RAG / A2A / Reasoning / Prioritization & Exploration) are the ones the first three modules never properly covered — **and those are exactly what the next few lectures of Module D go deep on**. In other words, this table is both the table of contents for the 21 patterns and the roadmap for the rest of this module's lectures.

## One Judgment Call: More Patterns Is Not Better

One last reminder, so you don't treat the 21 patterns as a checklist of "things you must all use." Patterns are an **optional move set**, not a to-do list:

- A simple single-step Q&A Agent might not "explicitly" use a single pattern.
- Patterns **stack**: a production-grade Agent is often a combination of "Tool Use + Planning + Memory + Exception handling + Evaluation."
- Every pattern you add is one more dose of complexity — same logic as Module B's "framework selection": **let a pattern's complexity match the problem's complexity exactly**; anything extra is a liability.

## Wrap-Up

> The 21 patterns aren't 21 problems to memorize — they're an index map of "when I hit this kind of problem, which off-the-shelf playbook does the industry have?" Knowing how to look it up matters more than knowing how to recite it; and those 6 clusters this course hasn't covered are exactly the path this map will walk you down next.

## References

The 21-pattern framework in this module comes from the following material; for deeper study we recommend reading the original:

- Original book: *Agentic Design Patterns*, Antonio Gulli (Google)
- Chinese translation project (xindoo): [github.com/xindoo/agentic-design-patterns](https://github.com/xindoo/agentic-design-patterns)

This module is a distillation and "mapped-to-this-course" rewrite built on top of that framework. The naming and grouping of patterns follow the original book; the explanations and the parts that tie back to this course are original.
