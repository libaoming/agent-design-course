---
title: Delphi Clone · Digital Twin Platform
nav: Digital Twin
section: lab
status: in-production
slug: delphi-clone
tags: [digital twin, RAG, alignment flywheel]
summary: Distill a real person into a conversational digital twin — multi-source ingestion, adaptive interview drilling, grounded RAG answers, an alignment flywheel, and the person's own voice — a full pipeline built from scratch and running in production.
order: 11
---

> A domain expert's scarcest resource is time: they know a lot, but one-on-one answers don't scale, and their thinking is scattered across notes, articles, and audio where nobody can ask follow-ups. This project is a clean-room replica of delphi.ai — mechanism inspired, code 100% original — a "self-clone" digital twin platform: distill the person into a conversational twin that answers their audience 24/7, and hands the conversation back to the human when it can't answer. The full pipeline is closed-source, running in a private production environment; a complete public teardown deck is linked at the end.

## What it solves

| Pain point | Reality |
|---|---|
| Knowledge can't be queried | Thinking lives in notes / articles / audio — audiences can read, but can't ask |
| Time doesn't replicate | One-on-one Q&A has the highest quality, but there are only 24 hours in a day |
| Generic LLMs fabricate on your behalf | Point an LLM at your persona and it will confidently make things up where it doesn't know |

## Core mechanism: distill → answer → flywheel

**Distill**: multi-source ingestion (notes / URLs / PDF files) into one store, then an adaptive interview does three-level drilling — from seed opinions to counter-examples to boundaries — producing structured assertions rather than a pile of text chunks. The twin's resemblance comes from the assertion layer, not from raw corpus volume.

**Answer**: the audience chats in the browser with no login. Retrieval is vector recall + parent-chunk context + rerank, and every answer passes a three-state grounding check — answer with cited sources when the material supports it, plainly say "I don't know" when it doesn't, never fabricate. Replies can be spoken in the person's own cloned voice, and the page carries an explicit AI-twin disclosure.

**Flywheel**: holdout fidelity evals score each twin's alignment; a nightly offline reflection pass (Dreaming) clusters real conversations into frequent questions, hot-cited chunks, and blind spots; questions the twin can't answer go to an inbox and return to the human, whose approved replies are fed back into the knowledge base — the places where the twin fails are exactly the targets for the next round of distillation.

## Three hard-won engineering judgments

1. **Anti-fabrication is not a prompt, it's four layers** — retrieval threshold, three-state grounding, a refusal gate, and citation tracing, each backing up the last. Ablation showed all four are needed to stop "confident nonsense in the person's tone".
2. **Memory deletion must be end-to-end** — when an audience member clears their memory, you must delete not just the stored memories but also the queued reflection jobs, or deleted memories quietly resurrect via background workers. The right to deletion is a semantic guarantee, not a single DELETE statement.
3. **What the audience says never auto-enters the persona store** — every knowledge candidate arising from conversations requires the person's explicit approval before ingestion. This is the fidelity baseline: the twin represents the person, not "the person plus the internet".

## Companion teardown

A full product and architecture teardown of this project is public as a deck: [Delphi Clone Teardown](/delphi-interview/) — argued along the axis from "sounds like them" to "is actually true", covering distillation, retrieval, the alignment flywheel, and compliance design.

## In one sentence

Not a wrapper chatbot — a self-cloning pipeline where distillation, grounded answering, and alignment feedback grow as one system.
