---
title: meet-scribe
nav: meet-scribe
section: lab
status: open-source
repo: https://github.com/libaoming/meet-scribe
slug: meet-scribe
tags: [meeting minutes, local transcription, unattended]
summary: Automatic minutes for offline meetings — record → local transcription + speaker diarization → claude-generated minutes → Obsidian, fully unattended.
order: 8
---

> Online meetings have had auto-minutes for years; offline meetings are still stuck at "reconstruct from memory afterwards". Sending recordings to a cloud ASR brings two discomforts: your meeting content leaves the machine, and transcription bills by the minute. meet-scribe moves the whole pipeline back on-device: the moment a recording lands on disk, launchd takes over — WhisperX local transcription, pyannote speaker diarization, minutes via `claude -p`, written into your Obsidian vault. Audio never leaves the machine, zero marginal cost, no daemon, no database.

## What it solves

| Pain | Answer |
|---|---|
| Offline meeting minutes are handwritten | Recordings become structured, speaker-attributed minutes automatically |
| Cloud ASR privacy and cost | Models run fully local — audio stays on-device, zero marginal cost |
| No appetite for resident services | No daemon, no database — launchd WatchPaths triggers on file arrival |

## How it works: directories are the state machine

Two entry points: on the Mac, `meet start/stop` controls recording; on the iPhone, record with Voice Memos and it flows in automatically via an iCloud MeetInbox folder. From there, everything is file-driven —

Audio lands → launchd WatchPaths fires → `bin/pipeline.sh`, a single seam with four steps: ffmpeg to 16kHz wav → whisperx Chinese transcription + speaker diarization → fill the prompt and call `claude -p` for minutes → write to Obsidian and archive. The directories themselves are the state machine: inbox / processing / archive / error — one glance shows where every recording stands. Humans do only three things: start/stop and name the meeting, correct speaker names, and act on the TODOs.

## How to use it

`bin/meet start <name>` to record, `bin/meet stop` to finish — or drop any audio file into `~/Meetings/inbox/` for automatic processing. New machine setup: uv venv + pull models from ModelScope (1.5GB transcription model + 1.2GB Chinese alignment model) + `M1/init.sh` self-check + load the launchd plist.

## In one sentence

Permanently cross "write up the minutes" off your todo list — for free.
