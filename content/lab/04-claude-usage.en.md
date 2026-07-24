---
title: claude-usage
nav: claude-usage
section: lab
status: open-source
repo: https://github.com/libaoming/claude-usage
slug: claude-usage
tags: [usage analytics, CLI, zero-dependency]
summary: One command reads your local Claude Code logs and works out tokens, cost, model split, and cache savings.
order: 4
---

> The more heavily you use Claude Code, the harder it is to say where the tokens and money went: which project burns the most, how much is Opus vs. Sonnet, how much the cache actually saved. The answers all sit in local logs — nobody just reads them. claude-usage reads them out and does the math.

## What it solves

A bill is one number; it shows no structure. claude-usage reads the local logs under `~/.claude` and breaks usage open for you:

| Dimension | What you see |
|---|---|
| Tokens / cost | Totals and trends over time |
| Model split | How much is Opus / Sonnet / Haiku |
| Top projects | Which project burns the most tokens |
| Cache hits | How much prompt caching actually saved you |

## Core mechanism

Pure Python standard library, **zero third-party dependencies**. It parses local logs, aggregates locally, and outputs locally — no network, no upload. Your usage data never leaves your machine.

## How to use

```
git clone https://github.com/libaoming/claude-usage
cd claude-usage && python3 usage.py
```

No dependencies to install — runs out of the box.

## My own usage

This tool reads the logs on my own machine — [**open the author's Token usage dashboard →**](/usage/) (a data snapshot: daily usage, totals, per-model split; cost withheld).

## In one line

The smallest, most practical one: a single command that turns your Claude Code bill from one number into an itemized breakdown.
