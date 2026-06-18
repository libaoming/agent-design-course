---
title: Why this turn's output shouldn't have to "both speak and be parsed"
module: e
order: 2
slug: structured-io-and-tools
nav: Structured IO and Tools
summary: Whether a chunk of output should speak plain language or spit out JSON has one and only one criterion—"who consumes it"; whether a tool should be eager or deferred comes down to the latency red line times the number of tools.
tags: [上下文工程, 结构化输出, 工具集成, eager-deferred, 暗物质]
---

## Setting up the target: one turn of output, saddled with two conflicting jobs

You're building a voice Agent. Product files a request: during the call, persist the candidate's profile into the database in real time—easy, right? Just have the LLM in that conversational turn spit out a chunk of JSON on the side.

So you change the prompt, telling the model to "first answer the user normally, then append a structured profile at the end." You ship it, try it, and disaster strikes: halfway through speaking, the voice starts reading out "left curly brace, quote, name colon," the conversational rhythm falls apart, and the user hears what sounds like a robot stuttering.

The problem isn't that the model is bad. It's that **you made one turn of output carry two jobs at once**: one chunk needs to be fed straight to TTS and spoken to a human, the other needs to be parsed by a program and stored in a database. These two things have opposite requirements for "what the output should look like"—humans want fluent speech, programs want stable fields. Force-merge them and you please neither.

This is the most common trap in the two layers of the seven-layer context model: L4 (structured IO) and L5 (tool integration). Both look like they govern "what the model's output should look like and what actions it can trigger," but what they really answer are two independent yet intertwined questions: **should this chunk of output be schema-driven or come out as natural language? Should these tools all be handed over up front, or loaded on demand?** Get either one wrong and either the speech breaks, the token count explodes, or the user hears a dead patch of silence.

## Framework: two criteria plus one layering mantra

First, keep the two layers straight. The most confusing point is this: a tool's parameters are also a chunk of schema, so does it count as L4 or L5?

The answer is **it lands in both layers, no contradiction**. It's just a matter of which angle you look from:

| | L4 Structured IO | L5 Tool Integration |
|---|---|---|
| Governs what | "**What the output/call structure looks like**, who parses it" | "**Whether this action exists**, whether the model will initiate a call" |
| Direction | Mainly governs output (the response format contract) | Governs output (model initiates a call) + input (tool result flows back) |
| Who consumes | A downstream program parses / stores / renders | An external system executes a side effect (hang up, query DB, send message) |
| Static/dynamic | Static (schema fixed every turn) | Static (tool list fixed every turn) |

> [!NOTE]
> **Layering mantra**: L5 governs "whether this action exists," L4 governs "what that structure looks like." A single tool lands in both layers—it's both "an L5 action" and carries "an L4 parameter structure." To decide which layer a tool primarily belongs to, first ask whether it is essentially an **action** or a **format constraint**: if it can initiate a call and trigger a side effect, L5 is the main body; the parameter schema is just the L4 face it carries along. Don't jump to L4 just because it "returns structured data."

**L4's one and only criterion: who is this output meant to be consumed by.**

| Output consumer | Choice | Reason |
|---|---|---|
| For a human / spoken by TTS | Natural language, straight out | You want fluent speech; JSON can't be read aloud, and force-stuffing a schema chokes the tone |
| For a downstream program to parse / store / score / trigger an action | Schema-driven (JSON / tool_call) | Programs need stable fields; parsing natural language is unreliable |
| Both spoken and grabbed by a program | Split into two calls: the conversation stream speaks plain language + a side path does one schema extraction | Don't make one output carry two jobs |

**L5's criterion: latency red line × number of tools.** Eager means writing all tool schemas into the context up front, so the model sees every signature each turn; deferred means schemas aren't preloaded—when the model wants one it "searches/fetches" first, then calls (a typical implementation is some kind of ToolSearch or MCP lazy loading).

| | Eager (hand it all over up front) | Deferred (load on demand) |
|---|---|---|
| Mechanism | Tool schemas written into the `tools` field, present every turn | Schemas not preloaded; search/fetch when needed, then call |
| Latency | Low (signature already present, call directly) | First use +several hundred ms to several seconds (must load the schema first) |
| Token | Resends all tool schemas every turn (part of the static prefix) | Saves: unused tools never enter the context |
| Scale | Optimal when there are few tools; too many disrupts selection + blows up the token count | Only pays off at dozens to hundreds of tools |

> [!WARNING]
> Deferred is not a free token-saving miracle. Every deferred tool **incurs a round-trip cost on first use**—the model has to send one turn to "fetch" the schema, then another turn for the real call. In a low-latency scenario, that's a patch of silence the user hears. So the criterion isn't "many tools means deferred," it's "can the latency tolerate this first-use round-trip."

## Data / cases: two IO setups, one tool upgrade, one black-box collapse

**Case A conversational interaction vs Case B offline analysis (same business, two paths).** Imagine a voice recruiting Agent:

| | Case A conversational interaction (real-time path) | Case B offline analysis (side path / after the fact) |
|---|---|---|
| LLM output | Natural language straight out, also caps max output tokens to force short, spoken phrasing | Structured JSON: multi-dimensional scoring / multiple profile fields |
| Why | Output is immediately fed to some voice endpoint to speak to the user → must be plain speech | Output goes to a program to store / score / render a card → must be stable fields |
| L4 choice | Almost no structure (natural language straight out) | Schema-driven, runs LLM-as-judge |
| Path | On the call's critical path (TTS every turn) | Not on the call's critical path (runs asynchronously after the fact) |

The elegance is entirely in "separation of duties": during the call, **never** let the LLM spit out JSON (it stalls TTS and breaks the spoken rhythm); if you want a structured profile, push it to **a separate LLM call after the call** that extracts with a schema. Back to that opening request—"persist the profile in real time during the call"—the correct answer is not to change the conversation stream to spit out JSON, but to **start a separate side path**: feed the speech transcription stream asynchronously to another pipeline LLM that extracts and writes to the DB, while the main conversation chain isn't touched at all. Conversation is conversation, extraction is extraction.

**One tool upgrade.** A voice Agent starts with just 1 tool (a single "hang up the call" action), using eager—with only 1 tool and a latency-red-line scenario, eager is mandatory. Later product wants to grow it to 20 tools (query, booking, send notification…). Keep everything eager? Full eager resends 20 schemas every turn (token explosion) + the model easily picks wrong among 20. But pure deferred won't work either—in a voice scenario, the silence on a deferred tool's first use is an experience red line. The pragmatic answer is **layering**: keep high-frequency core tools (like hang-up) eager for low latency, and route the long-tail low-frequency tools through deferred. Switch to an ordinary text chatbot, without the "perceived silence" constraint, and you can go more aggressively full deferred.

**One black-box collapse.** When you switch the voice Agent from the "pipeline path" (one chat completion per turn) to the "end-to-end realtime path" (a speech-to-speech black-box session), you'll find L4/L5 directly **collapse and vanish**: a realtime session injects instructions only once at the session level, there's no "turn" boundary, the provider doesn't expose tool-call hooks, and compression is black-box self-managed. The whole capability of structured output and tool calling has no foothold left.

> [!WARNING]
> The trade-off implication of the realtime collapse is hard: **if you want to add structured output / tool-calling capability to a voice Agent, you have to stay on the pipeline path** (one chat completion per turn—only then can tools/schemas attach). Once you go to an end-to-end realtime black box, the L4/L5 capability is essentially **ceded to the provider**, in exchange for end-to-end low latency. If you want to have your cake and eat it too, the only compromise is a side path: feed a transcription stream asynchronously into a pipeline for structured extraction, while the main chain stays realtime and untouched.

There's also a piece of dark matter that's easy to miss: **a tool's description is static token that's resent every turn**. A tool's schema plus a few-hundred-word description gets fully resent every turn along with the `tools` field, yet it never appears in your system prompt file—an audit that only reads the prompt file misses those few hundred words (same root cause as "written isn't the same as in effect, you have to trace the code"). And the tool schema belongs to the **static prefix**, which should go into the prompt cache together with L1 and be sent only once. Without caching, in eager mode the more tools there are, the bigger this invisible token cost gets.

## Actionable practices: two tracks, PM and engineering

**PM perspective—use it to make judgments and communicate:**

1. When you get a request to "have the model also output some structured data on the side," first ask "who ultimately consumes this output." Spoken to a human → natural language; for a program → structured; both spoken and parsed → explicitly split into two calls, don't make one turn carry two jobs.
2. When discussing tool experience, align on "latency red line × number of tools": low-latency scenarios (voice, real-time) default to eager—don't get swept away by "deferred saves tokens"; only talk deferred once tools pile up to dozens, and factor in the experience cost of the first-use round-trip.
3. Beware the intuition that "structured output is more advanced"—force-stuffing JSON into the conversation stream is an experience disaster. Structure is a means, not an end.
4. Before choosing a real-time architecture, ask clearly: does this product line need tool calling / fine-grained structuring in the future? If so, don't lightly adopt an end-to-end realtime black box, or you're effectively ceding that layer of capability.

**Engineering perspective—use it to make architecture decisions:**

1. Split paths by "who consumes the output": real-time conversation stays conversation (natural language straight out, cap the output length to force short speech), structured extraction goes to a side path (an after-the-fact / async schema call), physically separated into two.
2. Tier tool selection by "latency red line × count": keep high-frequency core tools eager, route long-tail low-frequency ones through deferred; voice / low-latency scenarios default to eager as a backstop.
3. Treat the tool schema as a static prefix—put it into the prompt cache together with L1, don't let a few-hundred-word description get fully resent every turn.
4. Audit the "actually-running path," not the design doc: a complete JSON schema or stage output contract drawn in the design document doesn't mean it's actually enabled in production; auditing L4/L5 means looking at which path the code actually takes.
5. Before going realtime, keep an escape route to the pipeline path: either keep the main chain on pipeline, or feed a transcription stream into a pipeline on a side path for structured extraction—don't wait until the collapse to discover the tool capability has nowhere to attach.

## Closing

> L4 governs what the output looks like, L5 governs what actions can be called; a single tool landing in both layers is no contradiction. Schema or natural language depends only on who consumes the output; eager or deferred is just the latency red line times the number of tools. Don't make one output both speak and be parsed—split into two calls: conversation is conversation, extraction is extraction.
