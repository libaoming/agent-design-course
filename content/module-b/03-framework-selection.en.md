---
title: Why You Should Pick an Agent Framework Based on Need, Not Default to LangGraph
module: b
order: 3
slug: framework-selection
nav: Framework Selection
summary: A decision tree and trade-off table that make clear when to reach for LangGraph / Checkpoint / Map-Reduce / Multi-Agent—and when not to.
tags: [工程地基, 框架选型, LangGraph]
---

## Setting the target: both picking the wrong framework and adopting one too early are expensive

Let's start with a common scenario. A team sets out to build "automated document review," and in the very first week they wire up the full stack: LangGraph, a vector store, multi-agent orchestration. Two weeks later they realize the thing actually blocking progress isn't orchestration at all—it's that the prompts aren't tuned yet and single-step output still isn't stable. They paid the cost of framework complexity up front, while the business value stays out of reach.

Three hidden costs of adopting a framework too early:

- **The abstraction hides observability.** The framework packs "call the model → parse → route" into a black box, so when a step gets slow or its output goes bad, you can't see it. The first principle of Agent debugging is that "every step's I/O, latency, and tokens must be visible"—install the framework too early and you've already lost that.
- **Complexity mismatch.** A requirement that is fundamentally "single-step Q&A" gets wrapped in a node graph, a state machine, and Checkpoints, multiplying maintenance cost several times over—when it doesn't need conditional flow at all.
- **Lock-in cost.** Once a framework's core abstractions seep into your business code, switching frameworks means a rewrite.

But the reverse is also costly: **choosing "no framework" can be just as wrong.** For a production task that genuinely has complex conditional branches, needs resume-from-checkpoint, and needs human-in-the-loop (HITL), forcing it through a bare SDK with hand-rolled state management eventually produces a worse, less maintainable "homemade LangGraph."

So the target of this lecture isn't "is the framework good or not," but rather: **where exactly on the complexity spectrum does your requirement sit, and what is the matching tool.**

## Frameworks: the capabilities and trade-offs of four classes of tools

The common options aren't four parallel brands—they're tools covering different tiers of the "complexity spectrum."

![Framework selection complexity spectrum: bare SDK → LangChain → LangGraph → AutoGen, matched to requirement complexity](../assets/diagrams/framework-selection.svg)

| Framework | Core abstraction | Where it fits | Trade-off |
|------|---------|---------|------|
| Bare SDK | None (you call the model yourself) | Simple single-step Agent | Most transparent, most controllable; but you hand-roll all complex flow |
| LangChain | Chain / Agent / Memory | Rapid prototyping | Quick to start, many components; abstraction is on the heavy side, production observability needs extra work |
| LangGraph | Node graph (Node + Edge + State) | Production-grade complex single-task Agent | Explicit state machine, supports Checkpoint; steep learning curve, overkill for simple tasks |
| AutoGen | Multi-Agent conversation | Agents need to discuss with each other | Good for collaborative reasoning; high communication overhead, results hard to control |

The essential difference between their core abstractions: **the bare SDK has no state machine, LangGraph makes the state machine explicit, and AutoGen treats "the conversation among multiple Agents" as a first-class citizen.** Framework selection is just judging which layer your requirement needs made explicit.

Around the LangGraph layer, there are three "capabilities" you must understand (they determine production-readiness; they aren't separate frameworks):

| Capability | What problem it solves | When you need it |
|------|------------|---------|
| State / Node / Edge trio | Explicitly model a complex flow as a shared dict + function nodes + fixed/conditional edges | When there are conditional branches inside a single task |
| Checkpoint (state persistence) | Don't rerun from scratch on mid-way failure; supports HITL, audit trail, resume-from-checkpoint | When the task is long, needs human intervention, or needs traceability |
| Map-Reduce | Split a big task into N parallel subtasks, then aggregate | When subtasks have no dependencies and you want to compress runtime |

Checkpoint's three storage backends escalate with deployment scale—don't reach for the heaviest one right away: MemorySaver (dev and debugging only) → SqliteSaver (single-machine production) → PostgresSaver (distributed).

## Case: the evolution path of a contract review task

Requirement: **review commercial contracts, identify risky clauses, and hand high-risk ones to a human for review.**

**Version 1 (a single contract)** has the right shape of a LangGraph node graph, because internally it genuinely has conditional branches:

```
[input] → [parse] → Checkpoint
       → [Map: parallel review ×4 (payment / breach / confidentiality / disputes)] → individual Checkpoints
       → [Reduce: aggregate and dedupe] → Checkpoint
       → conditional edge: high risk?
           yes → [HITL Node] ← Checkpoint persistent wait
           no → [report generation] → [output]
```

Each capability maps to a real need: the four review dimensions have no data dependency on one another, so they go through **Map-Reduce parallelism**, cutting runtime from 4x down to roughly 1x; the task chain is long, so every step writes a **Checkpoint** and a failure doesn't force a rerun from scratch; high risk needs a human, so we use a **conditional edge + HITL Node**, relying on Checkpoint to persistently suspend state and resume once the person returns.

**Version 2 (1,000 independent contracts)** is a high-frequency pitfall. The intuition is "just orchestrate the batch processing into LangGraph too," but that's wrong. The 1,000 contracts are independent of one another; there's no conditional flow. The real bottleneck is concurrency control and failure retries, not the state machine. The right shape is layered:

```
Outer: asyncio controls concurrency (guard against API rate limits) + task queue
Inner: each contract still uses LangGraph to handle its own single-task flow
Global: support resume-from-checkpoint + independent retry per failed contract
```

In one line: **"complexity inside a single task" is solved with LangGraph; "batching and concurrency across tasks" is solved with queues and async—don't conflate the two.**

Only if this escalates further to "multiple Agents discussing and adjudicating the risk level among themselves" does it become time to consider multi-Agent conversation frameworks like AutoGen. And multi-Agent isn't free—it amounts to stacking another layer on top of the full single-Agent capability set:

```
Single Agent  = Tool Use + Context management + HITL + safety + idempotency + error retry
Multi-Agent = Single Agent × N + state persistence + three-tier error handling + parallel optimization + communication protocol + Orchestrator
```

Once you see this chain of plus signs clearly, you won't casually reach for multi-Agent just because it "sounds advanced."

## Actionable approach: a selection decision tree + an engineering checklist

**Step 1: run through the selection decision tree.**

```
Q1: Does a single task have complex conditional flow inside it (branches / loops / human intervention)?
    yes → LangGraph     no → bare SDK
Q2: Are there dependencies among multiple tasks?
    dependencies → coordinate with an Orchestrator
    no dependencies → parallel batch processing (asyncio + queue), don't cram it into LangGraph
```

**Step 2: confirm whether you actually need these three capabilities—adopt only when you need them, don't prepay.**

- Task chain is long, may fail mid-way / needs audit / needs resume-from-checkpoint → add Checkpoint (MemorySaver for dev, Sqlite for single-machine, Postgres only when distributed)
- N mutually independent subtasks and you want to compress runtime → add Map-Reduce
- Need a human gate to release → add a HITL Node, relying on Checkpoint for persistent suspension

**Step 3: if you decide to wrap a framework, hold to three principles.**

- Only wrap the stable parts (prompts change often—don't wrap them in)
- The wrapper must not hide observability (every step's I/O / latency / tokens must be visible)
- Use an isolation layer to guard against abstraction leakage (your own interface → adapter → framework, so switching frameworks doesn't touch business code)

**Step 4: the moment you go Multi-Agent, this "four-piece set" is the engineering baseline—miss one and you'll crash in production.**

- **Three-tier error handling**: automatic retry (exponential backoff, 2-3 times) → graceful degradation → escalate to a human
- **Idempotency**: bind write operations to a unique operation ID, and check before executing whether it has already run (single Agents need this too)
- **State persistence**: write each step's result to storage (associated with a pipeline_id), and resume from checkpoint on restart
- **Parallel optimization**: data dependencies go sequential; only run in parallel when there are no dependencies

## Wrap-up

> First ask "which layer is my complexity at," then decide "whether to adopt a framework, and which layer of capability to adopt"; hand the complexity inside a single task to LangGraph, hand the batching across tasks to a queue, and the advanced-sounding multi-Agent is always the last card you play. One degree too much is a liability; one degree too little is hand-rolling.
