---
title: context-engineering-kit
nav: context-engineering-kit
section: lab
status: open-source
repo: https://github.com/libaoming/context-engineering-kit
slug: context-engineering-kit
tags: [context engineering, CONTEXT.md, caching]
related_lecture: e
summary: One CONTEXT.md to manage everything that enters the context window across seven layers — each with a budget and a caching strategy.
order: 3
---

> When a model underperforms, often it isn't a bad prompt — it's that what got fed into the window this turn was wrong: too much and drowning in noise, too little and missing key facts, the wrong stuff and misleading, no structure and uncacheable, uncontrolled and drifting every turn. context-engineering-kit uses one CONTEXT.md to turn "what's loaded into this single window" from implicit into auditable, reproducible engineering.

## What it solves

When the content entering the window goes uncontrolled, it fails in five ways:

| Failure mode | Consequence |
|---|---|
| Too much | Context rot — key info buried in noise |
| Too little | Missing key facts, the model guesses |
| Wrong stuff | Irrelevant content misleads judgment |
| No structure | Can't be layered or cached, both cost and latency spike |
| Uncontrolled | Content drifts each turn, behavior isn't reproducible |

## Core mechanism: a seven-layer model

CONTEXT.md sorts everything entering the window from "stable → volatile" into seven layers, each with a token budget and caching strategy:

| Layer | Content | Cache |
|---|---|---|
| L1 System instructions | role/rules | static cache |
| L2 Domain knowledge | business context | static cache |
| L3 Tool definitions | callable tools | static cache |
| L4 Memory | long-term lessons | static cache |
| L5 Retrieval | RAG results | rebuilt each turn |
| L6 Conversation history | multi-turn context | rebuilt each turn |
| L7 Current input | this turn's request | rebuilt each turn |

L1–L4 are stable and cacheable; L5–L7 are rebuilt each turn — separating stable from volatile is the precondition for caching to work at all.

The key distinction (the core selling point): **Prompt Engineering is the L1 subset of CE, RAG is the L5 layer of CE, Harness governs the project skeleton while CE governs the makeup of a single window.** They aren't competitors — they're different scales.

Four design principles: explicit over implicit / separate stable from volatile / auditable / reproducible. Three anti-patterns: dump everything (context rot), mix stable with volatile (caches all invalidate), retrieve without ranking (noise pollution).

## How to use

After git clone, follow the CONTEXT.md template and fill in, layer by layer, what your Agent loads into the window this turn, marking each layer's budget and caching strategy. It's both configuration and an auditable snapshot of what this window actually contained.

## In one line

Move "what exactly did I feed the model this time" out of your head and into a table you can review and reproduce.
