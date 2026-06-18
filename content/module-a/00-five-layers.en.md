---
title: Why Understanding Agents Starts With Splitting Them Into Five Layers
module: a
order: 0
slug: five-layers
nav: The Five-Layer Foundation
summary: An Agent's capabilities and failures all grow on five foundational layers — Loop / Tool / Planning / Memory / Multi-Agent.
tags: [技术地基, 五层架构, MCP]
---

## The Target: Without Layers, You Apply the Wrong Fix at the Wrong Level

The first time most people encounter Agents, they get buried under a pile of jargon: Loop, tool calling, ReAct, memory, multi-agent, MCP… So they either treat it as "a chatbot that talks" or as "one giant prompt." Both of these mental models will come back to bite you when you actually build a product.

What happens when you don't think in layers? You'll mistake a problem that's really about "the model's planning ability isn't good enough" for "the prompt wasn't written well," and then endlessly tweak prompts. You'll misdiagnose "the tool description is so bad the model can't figure out how to call it" as "the model is too dumb," and go swap in a more expensive model. You'll force a multi-agent setup onto a task that needs no collaboration at all, adding nothing but communication distortion and cost. More dangerous still: when a production Agent breaks, you can't pinpoint which layer collapsed — was it errors cascading inside the loop, a tool called wrong, or memory holding onto things it never should have?

Splitting an Agent into five layers is, at its core, giving yourself a **failure-localization map** and a **capability map**. Each layer solves one clear problem, and each layer has its own typical failure signatures. Once you can read this map, you can speak to the point when talking with engineers, you know which layer to bet on when making technical choices, and you can lock onto the collapsed layer directly when investigating incidents. This is the foundation of Module A — every later discussion about failure points, error recovery, transparency, and boundary behavior stands on top of these five layers.

## The Framework: The Five-Layer Foundation in One Table

Bottom-up, the five layers stack one on top of the next. If a lower layer is shaky, everything above it falls apart — without a reliable Loop, even the most elegant planning won't run; without dependable tool calling, planning is just wishful thinking.

![The five-layer foundation of Agents: L1 Loop at the bottom, stacking up to L5 Multi-Agent, with MCP cutting across tool integration](../assets/diagrams/five-layers.svg)

| Layer | What Problem It Solves | Typical Capabilities | Failure Signatures |
|------|------------|---------|---------|
| L1 Agent Loop | Let the model "keep acting" instead of answering once | Think → Act → Observe loop; continue when `stop_reason==tool_use`, otherwise wrap up | Errors cascade and amplify inside the loop; stuck in infinite loops or terminating too early |
| L2 Tool Use | Let the model call on the capabilities of the outside world | The three essentials of name / description / inputSchema; parallel tool calls; Computer Use | The model doesn't call, calls the wrong thing, or fills in wrong parameters; a vague description drags down call success rate |
| L3 Planning | Let the model decompose and orchestrate complex tasks | Five workflows: Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Supervisor-Workers | Messy task decomposition, missed steps; using the wrong orchestration pattern |
| L4 Long-Term Memory | Let the Agent remember what it should across sessions | Rolling window / summary compression / key-information extraction; explicit vs. implicit preferences | Missing what should be remembered (poor Recall); recalling what shouldn't be recalled (poor Precision) |
| L5 Multi-Agent | Let multiple Agents collaborate on tasks a single one can't hold | Communication protocols to prevent distortion; three-tier subtask error handling: retry → degrade → escalate | Information distorted between agents; errors with no one to catch them; over-decomposition that just adds cost |

> [!NOTE]
> Key insight: Agency comes from the model's training itself, not from the orchestration framework. A hardcoded node-based workflow has a very low ceiling — it can't handle paths outside what was pre-set. The framework is just scaffolding; it determines how much the model can express, but the upper bound on that expression is set by the model.

There's one more thing that cuts across all five layers: **MCP (Model Context Protocol)**. It doesn't belong to any single layer; it's the standardized protocol for L2 tool integration — think of it as the "USB-C standard for plugging in tools." Three roles: Host / Client / Server; three capabilities: Tools (the most important) / Resources / Prompts; two transports: stdio (local) / SSE (remote). Its value is standardizing how tools get plugged in, so you don't rewrite a fresh batch of glue code for every Agent.

## Data / Cases: What the Five Layers Look Like in Real Products

The following are all real, anonymized scenarios, each illustrating the "feel of success and failure" for one layer:

- **L1 Loop cascade amplification (a voice recruiting Agent)**: In a real-time voice scenario, a single recognition error gets carried into the next round of reasoning, drifting further with each turn, until the whole conversation goes off-topic. The lesson: the loop must have a correction mechanism — you can't let errors propagate downstream undamped.
- **L2 Tool description makes or breaks it (a contract-review Agent)**: For the very same "extract clause" tool, after rewriting the description from a single sentence into a clear explanation with usage boundaries and examples, the model's call success rate rose markedly. The model didn't change, the tool description did, and the result changed — confirming that "description quality is the most important variable in L2."
- **L3 orchestration-pattern mismatch (a deep-research Agent)**: A research flow that needed dynamic subtask allocation was force-fit into linear Prompt Chaining, and it jammed the moment it hit a branch. It only ran smoothly after switching to Orchestrator-Workers (an orchestrator dynamically dispatching subtasks). Picking the right workflow pattern matters more than piling on prompts.
- **L4 the Precision vs. Recall trade-off (a long-term assistant Agent)**: A rolling window is easy but drops early information (poor Recall); key-information extraction is precise but requires first defining "what counts as important." You also have to distinguish explicit preferences (what the user states outright) from implicit preferences (inferred from behavior) — recording a wrongly-inferred implicit preference as fact is the textbook Precision failure.
- **L5 when to bring in multi-agent (a script-compliance scenario)**: Real-time compliance checking uses the Supervisor-Workers pattern — one Agent does the work, one Agent watches compliance in real time. But remember: L5 is only worth it when "the task is parallelizable / needs independent verification / can't fit in a single context"; otherwise the communication distortion and cost aren't worth it.

## Actionable Practices: How to Put This Layering to Work

**The PM lens — use it to judge and communicate:**

1. When you get an Agent requirement, first ask "which layer is this stuck on," rather than jumping straight to how to write the prompt.
2. When evaluating directions, locate your bets by layer: should you optimize the tool description (L2), switch the orchestration pattern (L3), or add a memory scheme (L4)?
3. Beware the "over-collaboration" impulse — if a single Agent plus good tools can solve it, don't reach for L5; every extra layer adds another helping of communication distortion and cost.
4. In incident retros, work through the layers against the "Failure Signatures" column, translating the vague "the Agent isn't working well" into exactly which layer collapsed.
5. When aligning with engineers, speak in layer numbers: "This is an L4 Precision problem" is far more efficient than "it keeps misremembering things."

**The engineering lens — use it to make architecture decisions:**

1. L1 — stabilize the loop skeleton first: define clear stop conditions, guard against infinite loops, and leave room for error correction; don't let errors cascade undamped.
2. L2 — treat the description as a first-class citizen and polish it, with clear boundaries and examples; use parallel tool calls for independent subtasks. Prefer MCP for tool integration to avoid reinventing glue.
3. L3 — pick the workflow by task shape: linear → Prompt Chaining, diverse inputs → Routing, independent subtasks → Parallelization, dynamic allocation → Orchestrator-Workers, real-time validation → Supervisor-Workers.
4. L4 — pick the memory scheme by scenario and explicitly define "what's worth remembering"; separate explicit from implicit preferences, be conservative with implicit inference, and prefer missing a record over recording a wrong one.
5. L5 — before going multi-agent, first settle the communication protocol and the three-tier error handling (retry → degrade → escalate); prove a single Agent genuinely can't hold it before you split.

## Wrap-Up

> The five layers aren't five separate parts; they're a failure-localization map: if a lower layer is shaky, everything above it falls apart. To locate a problem, first ask "which layer collapsed," then decide whether to change the prompt, change the tool, or change the architecture.
