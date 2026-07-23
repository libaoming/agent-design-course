---
title: openknowledge-py
nav: openknowledge-py
section: lab
status: open-source
repo: https://github.com/libaoming/openknowledge-py
slug: openknowledge-py
tags: [teaching rebuild, knowledge base, MCP]
summary: A from-scratch Python reproduction of inkeep/open-knowledge — a git-native markdown knowledge base for humans and AI agents. Understanding by rebuilding.
order: 9
---

> Reading a complex system's source and rebuilding it by hand teach you at depths an order of magnitude apart. openknowledge-py chose the latter: reproduce inkeep/open-knowledge — a git-native markdown knowledge base shared by humans and AI agents — from scratch in Python. The original is TypeScript; the reproduction deliberately mirrors the original's package topology (core → server → cli → app) so you can read them file by file, side by side. Only after hand-writing every subsystem — the markdown pipeline, search, CRDT collaboration, MCP — do you actually understand it.

## What it solves

| Goal | Approach |
|---|---|
| Truly understand each subsystem | Don't settle for skimming — rebuild until it runs |
| Cross-language comparative learning | Package topology mirrors the original: Zod→Pydantic, Orama→bm25s, Yjs→pycrdt, commander→typer |

## How it works: nine milestones

M0–M8, linearly: scaffolding → core (schema + markdown pipeline / BM25 search / git shadow repo + bridge diff/merge) → server (read-only MCP tools / write verbs / CRDT sync + file-watcher) → app (WYSIWYG editor — a thin Tiptap JS island wired up via pycrdt-websocket) → cli (init / seed / start). The backend mainline is complete: 29/29 features passing, 170 tests green. A desktop branch (Electron, one codebase, dual host) is in progress.

## How to use it

`uv sync --extra core --extra server` → `okpy init ~/my-notes` → optional `okpy seed` → `okpy start` — one process serves the editor UI, CRDT collaboration, and the agent-write HTTP API; open 127.0.0.1:1234 in a browser. MCP configuration for agents lives in examples/mcp.json.

## In one sentence

The best way to read source code is not to read it — rebuild it.
