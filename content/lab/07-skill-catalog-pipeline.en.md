---
title: skill-catalog-pipeline
nav: skill-catalog-pipeline
section: lab
status: open-source
repo: https://github.com/libaoming/skill-catalog-pipeline
slug: skill-catalog-pipeline
tags: [data pipeline, semantic search, pgvector]
related_lecture: b
summary: An engineering blueprint for turning 77k third-party skill packs into a semantically searchable (500ms) skill catalog foundation — a five-layer pipeline plus 17 hard-earned lessons.
order: 7
---

> A skill marketplace hands you nothing but a paginated API. Between that and a "semantically searchable, loadable" skill catalog foundation lies an entire engineering pipeline: fetching everything, cleaning it, storing it, searching it fast, and staying in sync with upstream. skill-catalog-pipeline ran that pipeline end to end on 77,000+ real skill packs, then open-sourced the blueprint, a redacted reference implementation, and 17 postmortem lessons — the highest-value part isn't the code, it's the pitfalls no documentation warns you about.

## What it solves

| Stage | The real pitfall |
|---|---|
| Fetch | Pagination jitter silently drops thousands of entries and mislabels live skills as delisted |
| Normalize | 70% of entries have empty categories, with NUL bytes mixed in |
| Retrieval | 2048-dimension vectors exceed pgvector's index limit outright |
| Sync | `updated_at` is a dirty signal — incremental sync based on it misses updates |

## How it works: a five-layer pipeline

| Layer | Job | Key design |
|---|---|---|
| FETCH | Get everything | Multi-round union + completeness gate |
| NORMALIZE | Get it clean | 5 hard validation conditions, idempotent dry-run |
| STORAGE | Keep it well | Postgres + pgvector + object storage, four asset states |
| RETRIEVAL | Search fast | halfvec cosine + IVFFlat — ~500ms with index (130s without, ~260× speedup) |
| SYNC | Stay current | Weekly four-state diff; trust version, never updated_at |

## How to use it

Start with the architecture doc and engineering-notes (17 postmortem lessons) in docs/ — that's the repo's main value. src/ is a redacted reference implementation (16 scripts + SQL, credentials via environment variables): adapt it into your own foundation; it is not a turnkey product.

## In one sentence

A complete engineering blueprint for turning other people's skills into your own searchable asset — with the pitfalls already stepped on for you.
