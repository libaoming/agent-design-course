---
title: "Reflection and Reasoning: Letting an Agent Go Back and Fix Its Work, and Think More Deeply"
module: d
order: 1
slug: reflection-reasoning
nav: Reflection & Reasoning
summary: A one-pass output can be wrong without the Agent knowing it; Reflection adds critique-driven, targeted revision; Reasoning makes the thinking explicit so the Agent thinks more deeply.
tags: [设计模式, 反思, 推理, 盲区]
---

## Setting the Target: One-Pass Output, Wrong but Oblivious

Let's start with two scenarios that genuinely go off the rails.

First, ask an Agent to write a slightly complex piece of code. It generates it in one breath, hands it over directly, you run it, and it errors out. You paste the error back, it fixes it; errors again, fixes again. It takes three or four rounds before it's right. Where's the problem? **When a model generates, it moves "linearly forward"—it never looks back at what it just wrote before handing it over.** It's not that it can't fix things; it was simply never given the chance to "fix."

Second, ask a question that needs a few steps of reasoning: "A room has 3 switches that control 3 lamps in the next room. You can only enter the next room once. How do you figure out which switch controls which lamp?" If the model blurts out an answer right away, it often misses "the bulb heats up"—the key intermediate quantity. **Because it compressed thinking that should have been unfolded into a one-shot intuitive leap.** When the answer is wrong, it doesn't even know which step was wrong—because there were no "steps" at all.

These two targets map to the two patterns of this lecture: the first ailment—not looking back—is cured by **Reflection**: treat the output as a draft, find your own mistakes, and revise. The second ailment—thinking too shallowly—is cured by **Reasoning techniques**: lay the thinking process out explicitly, even try multiple paths in parallel and allow backtracking. They are a complementary pair of "thinking more correctly" and "thinking more deeply."

## The Framework: Reflection's Generator-Critic + Four Reasoning Techniques

### Reflection—The Generate, Critique, Revise Loop

The core structure of Reflection is called **Generator-Critic**. In one sentence: have the same (or another) model act first as the author, then as the reviewer. The standard loop has three steps and can run multiple rounds:

![Reflection's Generator-Critic loop: generate a draft → critique and find mistakes → targeted revision; if not good enough, run another round with the critique; if good enough, stop](../assets/diagrams/reflection-reasoning.svg)

1. **Generate**: produce the first version of the output. This version is explicitly defined as a "draft," not the final piece.
2. **Critique**: examine the draft from a different angle—what's wrong, what's missing, what could be better. The critique must be specific and actionable; it can't just say "this is poorly written."
3. **Refine**: armed with the critique, make targeted edits to the draft and produce the second version.

Then decide whether to run another round (good enough / hit the round limit / stop when it stops improving). Here we have to nail down the most easily confused point: **Reflection ≠ Retry.**

| Dimension | Plain Retry | Reflection |
|------|------------------|-------------------|
| Second input | A prompt almost identical to the first | The first output + a specific critique of it |
| Mechanism of improvement | Change the random seed, try your luck | Targeted edits guided by diagnostic feedback |
| Does information accumulate | No accumulation, starts from zero each time | Accumulates; each version stands on the shoulders of the last |
| Fitting scenarios | Output itself is random, just re-sample | Output has clearly critiquable quality dimensions |

Retry is "rolling the dice again"; Reflection is "marking up an essay with a red pen." The cost of Reflection must also be laid out: **one extra round of critique + one round of revision means 2-3x the tokens and latency.** So it's not a default switch—you turn it on per scenario.

### Reasoning—Four Techniques for Making Thinking Explicit

Reasoning techniques solve "not thinking deeply enough." The core idea is unified: **don't let the model jump straight from the question to the answer; let the intermediate thinking process unfold explicitly and consumably.** Four techniques, in increasing complexity:

| Technique | Mechanism in one sentence | Shape | Fits | Cost |
|------|-----------|------|------|------|
| CoT (Chain-of-Thought) | "Think step by step," write out the reasoning chain before giving the answer | A single straight line | Multi-step arithmetic, logic, commonsense reasoning | Low |
| Self-Consistency | Sample multiple CoT paths, vote on the answer and take the majority | Multiple parallel lines + voting | Questions with a unique, easily aggregated answer | Medium (N× sampling) |
| ToT (Tree-of-Thoughts) | Break thinking into nodes, branch exploration + evaluation + backtracking | A tree (backtrackable) | Questions needing search / trial-and-error / planning | High |
| ReAct | Reasoning and action interleaved: think a step → call a tool → see the result → think again | A loop | Tasks needing external info / tools | Medium-high |

How the four relate: CoT is "write one line of thought clearly"; Self-Consistency is "write the same question several times and take the consensus"; ToT is "if halfway through you realize it's wrong, you can turn around and switch paths"; ReAct is "when you can't think it through, go look it up, go try it, bring back real feedback and keep thinking." The first three happen inside the model's head (pure text reasoning); ReAct is the only one that pulls "action / tools" into the reasoning loop—which is also why it's most tightly tied to Agents.

## Case: The Same Task, How Much Difference These Two Patterns Make

The task: have the Agent write a short explainer "explaining what a vector database is to a non-technical reader."

**Bare run (no reflection, no explicit reasoning)**: the model does one pass and writes a chunk of text stuffed with "embedding space," "cosine similarity," and "approximate nearest neighbor." Jargon piled on; a non-technical reader can't understand a word of it, yet the model hands it over with full confidence. Wrong but oblivious.

**With Reflection**: Generate, same as above; Critique (have it review from the angle of "a reader with zero technical background") is very specific—"the second paragraph has three unexplained terms; missing an everyday analogy; the opening doesn't make clear what problem this thing solves"; Refine takes those three points and edits, and the second version's opening adds the analogy "like a library shelving books by similar content," with all the jargon backstopped by plain language first. Quality clearly improves, at the cost of one extra round.

**With Reasoning (ReAct)**: if the task becomes "explain and compare the three current mainstream products," relying purely on the model's memory easily goes stale or gets fabricated. ReAct will: think ("I need to look up the latest product comparison") → act (call the retrieval tool) → observe (get the real material) → think again ("the material says product X's pricing changed") → integrate the output. **Reasoning determines "whether the content is correct and deep"; Reflection determines "whether the finished product is good and on-point." One governs the process, the other governs the final closing.**

## Actionable Practice: When to Turn It On, and Which One

**When to turn on Reflection**—signals: the output has clearly critiquable quality dimensions (you can only critique what you can describe); the task is open-ended generation (code, long-form writing, plans); the cost of one mistake > the cost of one or two extra rounds. Not worth it: simple factual Q&A, format conversion, latency-critical real-time scenarios. Two key points: ① keep critique and generation in different perspectives or different agents as much as possible—don't let the author praise their own work; ② set a stopping condition (fixed rounds / stop when it stops improving), otherwise endless polishing burns tokens.

**How to pick a Reasoning technique**—choose by the shape of the task, don't reach for the heaviest one by default: multi-step reasoning with a unique answer → CoT (cheapest); CoT occasionally wrong but votes can aggregate → Self-Consistency; needs search / trial-and-error / turning around → ToT (most expensive, use last); depends on external info or tools → ReAct. One-sentence decision: **first ask "does this question need to interact with the external world"—if yes, ReAct; if no, then pick within CoT / SC / ToT by complexity, from light to heavy.**

## Weaving It Into the Course: These Two Patterns Aren't New

**Reflection ↔ Module C's "end-to-end and handoff," the "separation of planning / generation / evaluation into three agents."** Module C covered how mature multi-agent systems split planning, generation, and evaluation across different agents—that **evaluation agent is essentially Reflection "externalized."** The naive form of Reflection is the same model writing first then self-evaluating, but self-evaluation tends to give itself high marks; the evaluation agent fully separates the "critic" into another agent that doesn't participate in generation. So the two are two concentrations of the same idea: **make the judge independent of the generator.**

**Reasoning ↔ Module A's "five layers of the technical foundation," L1 Loop + L3 Planning.** ReAct is the reasoning form of the L1 Loop—L1 is the "perceive → decide → act → observe" loop, and ReAct writes the "decide" stage explicitly as natural-language reasoning; ReAct = Loop + explicit thinking. ToT's "branch exploration + backtracking" corresponds to L3 Planning's search strategy. So Module D isn't teaching something brand new—it's filling in, for the earlier foundation, "what they look like inside a single agent's thinking layer."

## Closing

> A one-pass Agent is wrong but oblivious; a shallow-thinking Agent just guesses when things get hard. Reflection makes it go back and fix; Reasoning makes it think deeply—the former governs "whether the closing is correct," the latter "whether the process is deep." Neither is a default switch; they're knobs you turn on by hand, looking at the shape of the task and weighing the cost.
