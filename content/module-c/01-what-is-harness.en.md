---
title: Same Model, Wildly Different Results — The Harness Is the Real Variable
module: c
order: 1
slug: what-is-harness
nav: What Is a Harness
summary: The Harness is all of the engineering infrastructure outside the model weights — the Five Subsystems are its components, the Four Layers of Defense are how you ship it.
tags: [Harness, 五子系统, 四层防御]
---

## The Setup: Same Model Swapped In — Why Does One Team Crash and the Other Soar

Same Opus, same task. Team A's agent runs all night and wraps up on its own; Team B's agent starts hallucinating by step three, loses context, breaks the code, and can never recover. The model weights on both sides are identical. The variable that makes the difference — walkinglabs gave it a name: **the Harness**.

It's far too easy to pin an agent's capability on the model itself: "How much stronger is Opus than Sonnet?" "Would a different model fix this?" But in an agent product that actually gets work done, the model is just the engine; how far it can go depends on **the whole car around that engine**: how you organize its instructions, whether the tools are both sufficient and restrained, whether the environment is reproducible, where the progress of a long task gets recorded, and how it knows it did the right thing. All of this together is the Harness — and it's routinely dismissed as "engineering details" and slapped together carelessly.

walkinglabs' core claim is blunt: **Agency (the capacity to perceive, reason, and act) comes from model training, but how much of that capacity gets realized is decided by the Harness.** The model is the driver; the Harness is the car. No matter how good the driver, a car with no steering wheel, no dashboard, and no brakes still ends up in the ditch. This lecture first breaks the "car" down into parts, then looks at how one real project assembles those parts.

## Framework One: The Five Subsystems of a Harness

walkinglabs breaks "everything outside the model weights" into five subsystems. Note that they aren't optional — drop any one and you get a whole class of failure mode:

| Subsystem | What it governs | What happens without it | Minimal shipping form |
|--------|---------|-----------|------------|
| ① Instructions | Encodes task rules, style, and boundaries into a structured document | The agent guesses the rules from scratch every time; behavior drifts | `AGENTS.md` / `CLAUDE.md`, around 100 lines |
| ② Tools | The interfaces through which the agent takes action | It can't do what it should, or has too much power and wreaks havoc | A sufficient, least-privilege tool set |
| ③ Environment | Locked dependencies and a reproducible runtime | "Works on my machine"; on the agent's side it's all red | A dependency lockfile + a one-command init script |
| ④ State | Persists progress and decisions to files | One interruption in a long task and it's amnesiac, can't resume | A progress file / task graph |
| ⑤ Feedback | Explicit verification commands so the agent can self-check | The agent feels great about itself and doesn't know it's wrong | An executable verify command |

Three accompanying design principles decide what these five subsystems should look like:

- **A map beats a manual**: instructions should be concise (a main document of around 100 lines), with details split into companion files loaded on demand, rather than handing the model a thousand-line "complete operations encyclopedia" to flip through itself. The main document is a map — it tells the model "where to look it up."
- **Constrain, don't micromanage**: write **executable rules** ("a task whose verify field is empty may not be started"), not an imperative play-by-play ("step one do X, step two do Y"). Rules set boundaries and let the model decide for itself within them; micromanagement uses prompts to simulate if-else, degrading the agent into a puppet on strings.
- **Quantify by ablation**: to learn which subsystem actually matters, **fix the model, remove subsystems one at a time, and measure each one's marginal contribution.** A gut feeling that "instructions are probably important" isn't engineering. Running it once with State and once without and seeing how much the success rate differs — that's data.

## Framework Two: Mapping the Five Subsystems ↔ the Four Layers of Defense

The Five Subsystems answer "what components does a Harness have," but not "how do you assemble them in a real project, and who governs what." This course's own project (a static site that rewrites learning material into a public-course lecture format) runs a set of **Four Layers of Defense** — which happens to be the shipping skeleton for the Five Subsystems. Looking at the two frameworks side by side, you see they relate as "parts list" and "assembly diagram":

| Four Layers of Defense | What it does | Which subsystems it absorbs | This project's concrete carrier |
|---------|-------|------------------|----------------|
| **L1 Persistence Layer** | Migrates business semantics / rules / progress from LLM memory to deterministic files | ① Instructions + ④ State | `CLAUDE.md` (rules) + `STATUS.md` (progress, updated at every wrap-up) + cross-session Memory |
| **L2 Methodology Layer** | Development discipline: single source of truth + linear slicing + fixtures first | ④ State + ⑤ Feedback | `features.json` (status machine) + verify hard gate + the PRD/SPEC/architecture trio |
| **L3 Automation-Hook Layer** | Deterministic automation, not reliant on the model's self-discipline | ③ Environment + ⑤ Feedback | The Stop hook in `.claude/settings.local.json` (auto-appends each round's request into the progress file) + init script |
| **L4 Context-Isolation Layer** | Dispatches context-eating grunt work to a subagent that runs to completion in an isolated context and returns only the conclusion | ② Tools (a subagent is itself a kind of tool) | Project-specific subagents in `.claude/agents/`; the main thread takes only conclusions, never reads the source |

The key to reading this table isn't the one-to-one "who maps to whom," but two things:

First, **the Five Subsystems are a classification view (sliced by function); the Four Layers of Defense are a stratification view (sliced by reliability).** The same `CLAUDE.md` is Instructions in the Five Subsystems and belongs to L1 in the Four Layers — because its core value is "moving rules out of hallucination-prone memory into files that don't change." The extra hidden thread the Four Layers add is **increasing reliability**: L1 turns the volatile into the persistent, L2 turns verbal agreements into hard gates backed by a state machine, L3 turns "remember to do it" into "do it automatically," and L4 turns "context explosion" into "isolated, non-contaminating."

Second, **State and Feedback are repeatedly emphasized by both frameworks at once.** In the Five Subsystems they're ④ and ⑤; in the Four Layers, L1 governs State, L2 governs Feedback, and L3 further hardens Feedback. This is no coincidence: when a long-task agent crashes, nine times out of ten it falls on these two things — "forgot the progress" and "didn't know it was wrong."

## Case Study: How This Project Avoids Crashing on State + Feedback

This course's source material is a personal knowledge base of over a hundred pages. If you let the main agent read the notes end to end and rewrite the lectures directly, two bad things happen: the main context gets blown out by the source text, and there's no mechanism at all to judge "did this lecture actually get written correctly." Here's how the Four Layers catch that:

- **L4 isolates the grunt work**: bulk-reading the knowledge-base notes is context-eating work, so it's dispatched to a project-specific subagent whose prompt is fully self-contained. The subagent reads it all in an isolated context and **returns only the distilled lecture draft — it does not paste the source text back to the main thread.**
- **L2's verify hard gate**: every lecture has a `verify` field in `features.json`, with the rule "empty field = may not be started." Once a draft is written it can only be marked `in_progress`; only when the build produces correct HTML, the key headings appear, `grep` finds no emoji, and the navigation is reachable is it allowed to flip to `passing`. Feedback isn't "I think it's fine," it's a check command that actually runs.
- **L1's STATUS resume**: every work session begins by reading `STATUS.md` (one-line status + next entry point + pitfalls) and must update it at wrap-up. Even if a session gets interrupted, the next one can pick up right at the breakpoint.
- **L3's Stop hook**: at the end of every conversation round, the hook automatically appends the user's request into the "incremental log" section of the progress file — not relying on the agent to record it conscientiously.

Note one counterintuitive point worth stealing (from the practice of self-improving harnesses): **putting a hard character cap on persistence files is a feature, not a bug.** For example, compressing the user-profile file to around 500 tokens and the main memory file to around 800 tokens forces it to keep only relevant information. Otherwise the files pile up endlessly, future sessions get dragged down by ever-heavier context, and it gets dumber the longer it runs. What State wants is "precise and few," not "complete and many."

## Actionable Practice: Install a Minimal Harness in Your Own Project

You don't have to deploy all four layers from day one — fill them in by order of reliability:

1. **Write Instructions first (half of L1)**: create a main instruction document of around 100 lines. The principle is a map beats a manual. Over 150 lines and you should split into companion files.
2. **Add State (④ / the other half of L1)**: create a `STATUS.md` and enforce "update at every wrap-up." For long tasks, add a task-list file backed by a state machine.
3. **Add Feedback (⑤ / L2)**: write each task **a verify command that actually runs.** Establish the iron rule — empty verify, no start. This single rule stops losses better than any amount of prompt tuning.
4. **Automate what should be automatic (L3)**: turn "must remember to do it every time" into a hook or script; don't count on the model to be conscientious every round.
5. **Add isolation only when context is about to blow (L4)**: when some class of work eats a lot of context, dispatch a self-contained subagent to run it in an isolated context and return only the conclusion.
6. **To learn whether it's worth it, ablate**: fix the model, turn off one layer, run it once, and see how far the success rate drops.

## Closing

> The model decides the ceiling of capability; the Harness decides how much of that ceiling you actually get. The Five Subsystems tell you what parts the car has; the Four Layers of Defense tell you how to assemble those parts, by reliability, into a car that can run long distances — and what decides life or death first is always those two most humble parts: does it remember where it got to (State), and does it know whether it did it right (Feedback).
