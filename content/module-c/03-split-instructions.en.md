---
title: Why One Giant Instruction File Drags Down Your Agent
module: c
order: 3
slug: split-instructions
nav: Splitting Instructions
summary: A 600-line CLAUDE.md is a self-reinforcing failure loop; the cure is splitting it into an entry file plus topic modules.
tags: [Harness, 指令拆分, 上下文工程]
---

## Setting the Target: The Bigger the File, the Dumber the Agent — and It's a Self-Reinforcing Loop

You wrote a `CLAUDE.md` for your Agent. In week one it was 80 lines and ran great. So you kept adding to it: hit a new pitfall, add a line; settled on a convention, add a line; reached a conclusion in some design discussion, jot it down too. Three months later it's 600 lines — and then you notice the Agent starting to ignore the hard constraints you spelled out in black and white.

This isn't your imagination. It's a **self-reinforcing failure loop**:

- The bigger the file → the more context budget it eats → the less attention left for the actual task → the worse the Agent performs
- The worse the Agent performs → the more you think "one more line of explanation and it'll get it" → the file keeps growing → performance keeps degrading

walkinglabs' Harness Engineering calls out this loop directly: **cramming every instruction into one giant file is the most common — and most insidious — anti-pattern in beginner Agent engineering.** It's insidious because it's completely harmless at small scale, and by the time you notice something's wrong, the file is already too big to dare touch.

## Framework: The Four Failure Mechanisms of a Giant Instruction File

Put them side by side and you'll see these four problems feed each other — they're not four independent bugs, but four faces of the same disease.

| Mechanism | Symptom | Why It's Fatal |
|---|---|---|
| ① Context budget exhaustion | A bloated file eats 10–20K tokens, reloaded every single conversation turn | These tokens are a fixed cost every turn, squeezing out room for the task, retrieval results, and conversation history |
| ② Lost in the middle | The middle of long text is utilized far less than the beginning and end | A critical hard constraint buried at line 300 is technically readable but effectively "invisible" — the model prioritizes the head and tail, and the middle gets systematically diluted |
| ③ Priorities mashed together | Hard constraints, design suggestions, and historical notes all laid out in the same format | The model can't tell "absolutely must not violate" from "feel free to consult" — an ironclad rule and a casually jotted TODO look identical |
| ④ Maintenance rot | Adding a line costs nothing, deleting one carries risk (fear of deleting the wrong thing), so the file only grows | Entropy increases monotonically. A file nobody dares delete from eventually becomes an "archaeological stratum" that no one reads and the Agent can't take in either |

The combined effect: ① shrinks the effective attention, ②③ ensure the remaining attention is still misapplied, and ④ guarantees things only get worse. This is why "just add one more line" never cures the disease — you're pouring water on someone who's already drowning.

## Framework: The Filing Cabinet — Entry File + Topic Modules

walkinglabs' cure is an everyday metaphor: **the filing cabinet.** You wouldn't dump your underwear, toiletries, documents, and medicine all into one box and then dig to the bottom every time you need something. You use drawers. Your Agent's instructions should be the same — **the entry file holds only what "must always be seen," and topic modules are pulled in on demand.**

![Instruction filing cabinet: the entry file AGENTS.md (≤200 lines, always resident) links to topic modules under docs, pulled in on demand](../assets/diagrams/split-instructions.svg)

| Tier | File | Lines | What Goes In | What Stays Out |
|---|---|---|---|---|
| Entry (the cabinet's labels) | `AGENTS.md` / `CLAUDE.md` | 50–200 | Project overview + startup commands + ≤15 hard constraints + links to the modules | Detailed plans, historical decisions, long lists |
| Topic module (each drawer) | Each file under `docs/` | 50–150 | Details on a single topic (e.g., deployment, data model, a subsystem's conventions) | Anything unrelated to this topic |

Two numeric disciplines are key: **entry ≤ 200 lines, hard constraints ≤ 15.** Going over means you've stuffed something into the entry that doesn't belong there. The entry file's job isn't to "explain everything" — it's to "tell the Agent where to go to find everything explained."

This dovetails neatly with the context engineering view: the entry file is the part loaded fixed on every turn, the part that should hit the prompt cache 100% of the time; topic modules are more like retrieval/memory pulled in on demand, not part of the fixed per-turn budget. Stuffing a module back into the entry is converting something that should be lazy into something eager — burning per-turn tokens for nothing.

## Case: A Real Entry File That "Doesn't Pile Everything Together"

This very public course project uses a filing-cabinet entry file. It doesn't pile requirements, plans, architecture, and progress all into `CLAUDE.md`; it does two things instead:

**First, replace "recite everything" with an "onboarding order."** The entry file doesn't open with a long string of rules, but with a read-order checklist:

> 1. First read `STATUS.md` (one-line status + entry point for next time + list of pitfalls)
> 2. Then read `PRD.md` / `SPEC.md` / `architecture.md` / `features.json`
> 3. Before starting work, run `bash M1/init.sh` to confirm the environment is all green

This is like writing the drawers' "opening order" on the cabinet door. The Agent doesn't need to read requirement details in the entry file; it just needs to know "requirements live in `PRD.md`, go pull them from there." Requirements, plans, and architecture are each their own module (the trio), progress is another module (`STATUS.md`), and none of them contaminate the others.

**Second, the entry keeps only "hard constraints needed every turn," with all details linked out.** The visual spec in the entry is a single line — "orange-book style + no emoji + line-SVG icons" — while the full visual system lives in the CSS under `assets/`; the hard rules of the lecture format get one line in the entry, with schema details in `SPEC.md`.

Map this against the four failure mechanisms and you defuse each one in turn: for ①, the entry is short, so the fixed per-turn cost is small; for ②, hard constraints are concentrated in a short file, so there's no "middle" to bury them in; for ③, whatever appears in the entry *is* a hard constraint, which formally distinguishes it from the suggestions/details in the modules; for ④, deleting a detail from a module has its blast radius locked inside that module — so you dare to delete.

A cautionary counter-example: a certain SDK defaults to `setting_sources=['user','project']`, which **silently** injects `~/.claude/CLAUDE.md` (about 17K tokens of dark matter) into every turn. This is the stealth version of "giant file failure" — your entry file looks perfectly clean, but the framework is piling a 600-liner in behind your back. After setting `setting_sources=[]`, a plain-text turn dropped from 4.5s to 2.4s. **Mechanism ① comes not only from the files you write, but also from the files the SDK loads on your behalf.**

## Actionable Practices: A Migration Checklist from Giant File to Filing Cabinet

1. **Measure first, then split.** Before splitting, run a "context checkup": print how many tokens the entry file actually consumes, and while you're at it audit whether the SDK is sneaking things in (dark defaults like `setting_sources`). No numbers, no splitting by gut feel.
2. **Draw a context composition table.** Tag every section of the entry file with three columns: `source | must-read every turn? | belongs in entry or module?` Keep "hard constraints that must be read every turn" in the entry; mark everything else for relocation.
3. **Split modules by topic, 50–150 lines each.** The criterion is "would you look for this kind of info together?" — what you'd look for together goes in one module, what you wouldn't gets split apart.
4. **Slim the entry to ≤200 lines, ≤15 hard constraints.** For anything over, ask yourself: is this "an ironclad rule to follow every turn" or "a detail to look up when needed"? The latter always gets linked out.
5. **Replace "list everything" with "read order."** Open the entry with an onboarding checklist that tells the Agent what to read first and where to pull details from.
6. **Give hard constraints a visual anchor.** Concentrate the ≤15 hard constraints into a single marked list so they're formally, obviously distinct from suggestions.
7. **Set a maintenance discipline to counter mechanism ④**: adding module details requires no caution, but anything entering the entry must pass through a gate of "does this need to be seen every turn?" Convert "deletion is risky" into "entry has a threshold."

## Closing

The failure of a giant instruction file isn't because you wrote too little — it's precisely because you wrote too much. **An Agent's attention is a fixed budget; every extra line you stuff into the entry is a line stolen from the task.**

> Good instruction architecture is a clearly labeled filing cabinet, not a stuffed box. The entry only answers "where to find it"; topic modules answer "how exactly to do it."
