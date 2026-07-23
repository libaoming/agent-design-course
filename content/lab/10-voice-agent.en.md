---
title: Blue-collar Recruiting Voice Agent
nav: Voice Agent
section: lab
status: in-production
repo: https://github.com/libaoming/livekit-voice-agent-demo
slug: voice-agent
tags: [realtime voice, phone agent, production system]
related_lecture: a
summary: An end-to-end phone pipeline — realtime voice conversations, call persistence, and an LLM grading loop — running in a real recruiting business.
order: 10
---

> Blue-collar recruiting runs on a fact that white-collar hiring doesn't: candidates don't write resumes or browse job posts — the most effective touchpoint is a phone call. But human calls are expensive, inconsistent, and impossible to review. This project turns "calling candidates about jobs" into a realtime voice Agent system — from carrier lines dialing in and out, to voice chat inside WeChat, to automatic grading of every call — all running in production. It's the only project in this section marked "In Production" rather than purely open source: the minimal runnable phone pipeline has been extracted into a public demo, while the business system itself stays closed.

## What it solves

| Pain | Reality |
|---|---|
| Wrong channel | Blue-collar candidates don't submit resumes; text job posts barely reach them — the phone is the main channel |
| Human calls don't scale | A recruiter makes a few dozen calls a day, script quality varies, and peak season is simply unwinnable |
| Calls are a black box | Once a call ends, it's gone — no record, no grading, no way to learn from bad calls |

## How it works: one pipeline, four endpoints

The skeleton is "one voice pipeline + multiple endpoints":

| Endpoint | Form |
|---|---|
| Phone | Carrier SIP lines, inbound and outbound — the Agent makes and takes real calls |
| Web | Realtime voice conversation in the browser (WebSocket relay) |
| WeChat Mini Program | Voice entry point on the candidate side, verified on real devices |
| Grading | Every conversation is persisted and scored by an LLM-as-judge across five dimensions |

The pipeline itself: SIP/client ingress → realtime voice conversation (orchestrated with LiveKit; ASR/TTS/end-to-end speech models from domestic cloud vendors) → call persistence (audio + transcript + structured outcome) → grading feedback. The grading step closes the loop — bad calls no longer vanish; they become input for iterating scripts and prompts.

## Three hard-earned engineering lessons

A realtime voice Agent and a text Agent are different species. What this project learned the hard way:

1. **Pipeline prompts can't be reused for end-to-end speech models** — JSON output and tool_call conventions get read out loud on a realtime voice link; you need a separate override layer.
2. **A sentence is not a turn** — the ASR emitting a sentence doesn't mean the user finished talking; without debouncing, the Agent constantly interrupts.
3. **Never switch state before audio finishes playing** — if the state machine follows the text instead of the playback, users hear half a sentence.

## How to use it

The business system is closed, but the minimal runnable phone skeleton is open-sourced as a demo: a Chinese-language phone Agent built on LiveKit + domestic SIP access + a cloud vendor speech stack. Clone it, fill in your line and model credentials per the README, and place your first call.

## In one sentence

Not "a bot that can voice-chat" — a production pipeline where everything from the phone line to the grading report grows as one piece.
