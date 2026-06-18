---
title: What the model actually sees each turn was never the prompt you wrote
module: e
order: 0
slug: context-engineering-overview
nav: CE Overview — Seven Layers and Dark Matter
summary: The context the model receives each turn is one big blob the framework assembled for you; only after all seven layers are 100% visible can you talk about optimizing.
tags: [上下文工程, 七层次, 暗物质, CONTEXT.md]
---

## Setting the target: you edit a prompt, but the model eats a whole blob of context

Most people optimize an Agent with only two moves: when it's slow, swap in a pricier model; when it misbehaves, make the system prompt longer and more detailed. You push the prompt to three thousand words and the model is still hit-or-miss, so you start to wonder, "maybe the model just isn't good enough."

The real problem usually isn't in that prompt at all. It's in something you never noticed: **you have no idea which tokens the model actually received this turn.** You think it saw the words you wrote, but what it actually received is one big blob the framework assembled for you — your system prompt, plus default config the SDK quietly loaded, plus conversation history accumulated all along the way, plus a user profile injected somewhere, plus the schema description of every tool. These "I thought I didn't add them, but they're in there" tokens are the **dark matter** of context.

This is the dividing line between Prompt Engineering and Context Engineering. **PE optimizes "that one passage" itself** — wording, structure, how the examples are given. **CE optimizes "how the entire turn's context gets assembled"** — where each of the seven layers comes from, how many tokens each takes, which should be cached, which should be compressed. No matter how well you write a long, detailed system prompt, that's still PE. What actually decides whether an Agent is stable, cheap, and controllable is whether you've taken charge of how that whole turn is assembled.

This is the foundation for the entire Module E: every later lecture — prompts and instructions, structured IO and tools, memory and RAG, history and compression, cache and observability — unfolds on this single "seven-layer assembly map."

## Framework: break every turn's context into seven layers

In any LLM application, the context the model sees each turn can be broken into these seven layers. Top to bottom, the earlier ones lean static (barely change turn to turn), the later ones lean dynamic (grow each turn).

| Layer | What this layer holds | Typical source | Static / Dynamic |
|------|------------|---------|---------|
| L1 System prompt | Role definition, behavioral rules, capability boundaries | system prompt, framework preset | Static |
| L2 Instructions | Task flow, priorities, single-turn constraints | rules baked into the system, hard rules appended in code | Mostly static |
| L3 User input | What the user said this turn | this turn's user message | Dynamic |
| L4 Structured IO | The output's format contract | JSON schema, response_format | Static |
| L5 Tool integration | Which external capabilities the model can call | tool schema, MCP server | Static |
| L6 RAG and memory | Retrieved snippets, long-term memory, user profile | vector store, memory files, user records | Dynamically injected |
| L7 State and history | Conversation history, task / user state | session history, stage trackers | Dynamically accumulated |

> [!NOTE]
> For every layer, ask the same four questions: **what's the content / who fills it / how many tokens / how to cache and compress.** If you can't answer even one for a layer, that layer is in the "framework decides for you" state — and the framework's defaults are almost never optimized for your scenario.

The most dangerous are L1, L6, and L7: many SDKs silently stuff them into the context. For instance, some agent SDKs default to loading a global config file as the system prompt — you didn't write a single word, yet it takes up over a thousand tokens. **The first step of CE isn't optimizing, it's making the content of all seven layers 100% visible** — light up the dark matter first.

CE isn't an isolated technique. It's one of three orthogonal "visibility" engineering disciplines:

| Dimension | What it optimizes | In one line |
|------|---------|--------|
| Prompt Engineering | The single prompt itself | Write "that passage" well |
| Context Engineering | How the whole blob the model sees each turn is assembled | Assemble "that whole turn" well and balance the books |
| Harness | Code state and handoff across turns and sessions | Make long tasks finish and resume |

Harness manages "code-state visibility" (which task actually passed, how the next session picks up); CE manages "context-composition visibility" (what the model actually saw each turn, where the dark matter is). The two complement each other — a reliable long-running Agent needs to manage a single source of truth, progress, handoffs, and a **CONTEXT.md**, all together.

Boiled down to principles, CE has five, but they all grow from one sentence — **the seven layers are interconnected; you can't optimize one in isolation**: changing the system prompt may break a tool, adding RAG may wash out the instructions in the system prompt. So every change should run against a baseline and watch the numbers (token / latency / cache / completion rate) rather than going by feel; design around the real workflow rather than letting the model answer garbage just to push tokens down; hold up under tenfold complexity; and maintain CONTEXT.md as a living document, not a one-off artifact.

## Data / case: how the seven layers bite in real scenarios

Below is the de-identified real feel of it, each mapping to a typical "dark-matter incident":

- **An agent SDK's implicit default (an AI tooling team)**: an Agent's responses were inexplicably slow; checking the model and the network led nowhere. Only after printing the real input tokens per turn did it surface: an inconspicuous SDK config option defaulted to loading a roughly 17k-token global config file into the system prompt. Nobody wrote it, nobody reviewed it, nobody needed it. Once turned off, latency on plain-text turns was nearly halved. **This optimization should have been done before the first line of code, not as a fire drill after launch.**
- **A voice Agent's layer-by-layer audit**: while drawing the CONTEXT.md for a real-time voice Agent, two pieces of dark matter showed up — first, framework-managed conversation history, invisible in the code, where input tokens per turn rose linearly with turn count and a long session crept toward the limit unnoticed; second, a static prefix of several thousand tokens that could have been cached once, but because there was no layering it was resent in full every turn. Neither was "written wrong" — they were "unmanaged," the textbook absence of CE.
- **A mature product's real ledger (a team's self-audit)**: after summing up all historical session usage for a mature Agent product, it turned out the token count shown on the commonly used dashboard only took the smallest one or two fields, underestimating real traffic by nearly two orders of magnitude. **When you report a token number, first report which definition it's under** — this gets fully explained in this module's cache and observability lectures.

All three cases point to the same thing: the context problem is almost never in "the part you wrote," but in "the part the framework quietly assembled in that nobody reconciled."

## Actionable practice: how to put this to work

**The PM lens — use it to judge and communicate:**

1. When an Agent request or fault lands on you, first ask "which of the seven layers is this stuck on" instead of jumping to how to change the prompt.
2. When aligning with engineers, talk in layer numbers: "this is L7 history bloat," "this is L6 injecting the wrong memory" — far more precise than "it keeps messing up."
3. Before discussing any "context optimization," first ask for a CONTEXT.md — without it, the team is still at the design-mockup stage and any so-called optimization is guesswork.
4. Beware of "sacrificing experience for a metric": squeezing the system prompt down to 100 tokens does save money, but if the model starts answering garbage, that's fake savings.

**The engineering lens — use it for architecture decisions:**

1. Before the first line of SDK config, draw a CONTEXT.md at the project root: split into a static table (fixed each turn, label source / token / cache strategy) and a dynamic table (changes each turn, label increment / compression strategy).
2. Audit the framework's implicit defaults — config-loading options, history-truncation strategies, presets containing dynamic info are all common sources of dark matter; before using any field, check its default and its impact on the seven layers.
3. Make the static layers' (L1 / L2 / L4 / L5) prefix byte-for-byte stable with near-100% cache hits, and always place the dynamic layers (L3 / L7) after the static ones.
4. Add observability: print input / cache / history tokens each turn, so CONTEXT.md, the "design ledger," and the runtime logs, the "reconciliation statement," can be matched up — and any gap that doesn't match is the next piece of dark matter to investigate.

## Closing

> The first step of CE is never optimizing — it's making the seven layers 100% visible. You can't optimize a blob of context you can't see; light up the dark matter and balance the books first, then talk about how to save and how to stabilize.
