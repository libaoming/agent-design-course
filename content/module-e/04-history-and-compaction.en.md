---
title: Why Your Conversation History Quietly Balloons Where You Can't See It
module: e
order: 4
slug: history-and-compaction
nav: History and Compaction
summary: Conversation history grows quietly every turn, usually managed for you by the framework and invisible in your code—only a measured growth curve shows you how close it is to the limit.
tags: [上下文工程, 对话历史, 压缩, 暗物质, 增长曲线]
---

## Setting the target: the system prompt is only 3,000 words, so why does a long session still blow up?

A common illusion: "My system prompt is only 3,000 words, nowhere near the model's limit—no need to worry about tokens."

That's only half right. What the model actually ingests each turn isn't just that static system prompt—it's also **all the conversation history accumulated along the way**. The system prompt is static; once written, it doesn't move. But history is dynamic: **every additional turn stacks another layer on top of the previous one**. Over a few-minute voice call of fifteen or twenty turns, each turn re-feeds the contents of all previous turns once more. What actually bites you was never that 3,000-word system prompt—it's this history that climbs linearly with turn count.

What makes it worse: this rising curve is mostly **invisible** in your code. Many frameworks manage conversation history for you—you just `append` a message, and the framework decides behind the scenes how much history to feed the LLM each turn. There's no variable in your code tracking "how big is the history now," so when it silently climbs toward the limit and starts getting slower, more expensive, or even truncated, you often only find out in production.

This is the dark matter from the previous lecture, in its typical form at the conversation-history layer. This lecture answers three questions: **Who actually owns the conversation history? How do you see it growing before it blows up? And when should you take over compaction yourself?**

## Framework: figure out who's managing history before you talk about compaction

Before doing anything, draw a conceptual distinction. A single "state" actually holds three things with completely different lifecycles, and talking about optimization with them lumped together is bound to miss.

| | Conversation history (history) | Task state (state) | Long-term memory (memory) |
|---|---|---|---|
| Lifecycle | Accumulates within a single session | Advances within a single session | Persists across sessions |
| Who manages it | Mostly framework-managed (dark-matter hot zone) | Maintained by your own code | Persisted by you (profile / summary) |
| Blowup risk | Grows linearly with turn count | Barely grows | One-time at injection |

In one line: when this layer breaks, it's almost always history—the framework assembles it behind the scenes and you can't see it grow; state and memory are usually controlled by your own code and visible. Pouring your optimization energy into state, which barely grows tokens, is the most common misdirected effort at this layer.

**So who owns history? There are three management modes, and the mode determines whether you can control it.**

| Mode | Who assembles history | Can you control it? | Typical form |
|---|---|---|---|
| A · Fully framework-managed | You only `append`; the framework decides how much to feed the LLM each turn | Invisible; controllable only after measuring | Some fully managed Agent frameworks; certain Assistants-style APIs (retain all by default) |
| B · Self-managed | You maintain the message array yourself and decide when to compact | Fully visible and controllable | Writing your own session loop, storing your own summary |
| C · Vendor black box | The end-to-end session manages history internally; you can't touch it | Completely uncontrollable | Certain end-to-end voice realtime sessions |

When you pick up a project, the first move is to ask: **is this project's history mode A, B, or C?** That single question directly determines three things downstream—whether you must measure the growth curve (A: mandatory), whether you can write compaction yourself (only A/B leave you room), or whether to simply give up on optimizing this layer (C is a black box; there's nothing to write).

Mode A is the most dangerous, because its default is often "retain everything"—the framework won't proactively compact for you; it just faithfully carries all history forward, turn after turn, until it hits the limit. **"The framework will handle it for me" is the most expensive wishful thinking at this layer.**

**If you land on A or B, you have to design for compaction. Compaction isn't a switch—it's five elements:**

| Element | What it must answer | Common pitfall |
|---|---|---|
| Watermark | What threshold triggers it (e.g., history exceeds some token count / transcript exceeds some character count) | Guessing by feel, not benchmarking against the model's limit |
| What to compact | Summarize old turns, externalize large tool_results into references, keep only summaries of retrieved documents | Blanket-compacting away a critical slot |
| Who compacts | Write the compaction logic yourself, or delegate to the framework runtime | Thinking you delegated when the path was never actually wired |
| Session kickoff continuation | Persist a summary at session end, inject it at next startup to pick up where you left off | Compacting without continuation, so the next session starts from zero |
| Rules ≠ implementation | You wrote a compaction-rules doc—but does the live path actually wire it in? | The doc just sits there; the path never calls it |

The last one deserves its own spotlight, because it's the most insidious trap at this layer: **writing a compaction rule doesn't mean the path you actually run implements it.** The rules can look beautiful on the design doc, but if the pipeline path simply doesn't wire up that logic, history is still handed wholesale to the framework black box—you think you compacted, but nothing was compacted at all. This is the same disease as "design doc vs. live run": the rule is in the doc, the implementation isn't in the path.

## Data / case: the shape of the growth curve will speak for you

The only reliable way to measure this layer isn't reading code and guessing—it's to **plot a "turn count → input token" growth curve**. There are just four concrete steps: run one complete real session → at every LLM call, dump that turn's actual `input_tokens` → record by turn count and plot it → benchmark against the model's context limit and extrapolate by slope to see how far you are from the ceiling.

The shape of the curve tells you straight away what state this layer is in—more honestly than any code comment:

| Curve shape | What history is doing | What to do |
|---|---|---|
| Linear rise | No compaction; all history retained every turn | Extrapolate by slope, calculate how many turns until you hit the limit |
| Sawtooth (rises to a point, then drops) | Compaction is running; it shaves once at the watermark | Verify the watermark is set reasonably |
| Step (one turn jumps sharply) | Some turn poured in a big chunk (e.g., a long document / large tool_result) | Locate that chunk, consider externalizing it as a reference |
| Flat (barely rises) | Fixed-window strategy, keeping only the last N turns | Confirm no critical info was dropped in the discarded old turns |

Three anonymized cases, matching three typical incidents:

- **A voice Agent's invisible accumulation**: while drawing the context-composition table for a realtime voice Agent, we found that conversation history was fully managed by the framework (mode A), with no variable in the code recording its size. A compaction rule was written in the design doc, but the live pipeline path simply didn't wire it in—history was in fact handed entirely to the framework black box. The conclusion: before any optimization, you first have to dump the per-turn input tokens of a real call, plot the growth curve, and only then know whether a few-minute session will approach the model's limit. **Between "the rule is written" and "the path implements it" lies an entire measured curve.**

- **A hypothetical state tracker took the blame**: a team suspected that "phase switching" was dragging down tokens, and spent effort optimizing the phase-tracking logic. The measured curve showed that phase tracking contributed almost no token growth—it's just a one-way advancing marker, and it doesn't switch the system prompt. What actually rose linearly was history. **Failing to tell apart "state that barely grows" from "history that grows linearly" leads you to systematically misdirect optimization effort.** (Conversely, watch out for another pattern: if phase switching re-sends the entire system prompt, then it's no longer cheap—every switch is a full re-send, and that bill has to be reckoned too.)

- **A mature product's uncontrollable end-to-end session**: a product running an end-to-end voice session (mode C) keeps history entirely inside the vendor; the code can't touch the message array, and there's no "one chat completion per turn" boundary to insert compaction. It avoids blowing up thanks to the vendor's session-level built-in compaction, but you can neither see it nor tune it. The only road to control is to fall back to a pipeline architecture where you can see each call. **A black box not blowing up isn't the same as a black box being controllable—invisible is invisible.**

There's also a positive reference from a public product: a desktop client turned all this into a live panel that shows, right in the context window, how many tokens "conversation messages" occupy—refresh and you can watch it climb with the turn count. The hand-drawn "turn count → token growth curve" became their official dashboard. Most projects don't have this panel, which is all the more reason to dump it yourself—by comparison, you'll understand better why you must measure.

## Actionable practice: get this layer under control

**PM perspective—use it to judge and communicate:**

1. When you hear "long sessions get slow / expensive / truncated," your first reaction should be to ask "who manages history—A, B, or C?", not to rush into swapping models or rewriting the prompt.
2. Don't be soothed by "we set up a compaction rule"—follow up with "is that rule actually wired into the path you run, and have you measured the growth curve?" A rules doc is not an implementation.
3. Before discussing any "long-session optimization," first demand a "turn count → token growth curve" from a real session. Without it, the team is still at the design-doc stage, and so-called optimization is all gut feel.
4. Be wary of treating something like state tracking—which "barely grows"—as a cost driver to optimize; first have engineering use the curve to point out exactly which column is growing.

**Engineering perspective—use it for architecture decisions:**

1. When you take over a project, first determine the mode: is history fully framework-managed, self-managed, or a vendor black box? Mode A must be measured—you can't assume the framework will compact.
2. The measurement for mode A is a fixed four steps: run one complete session → dump each turn's real input tokens at the LLM call → plot the growth curve → extrapolate by slope and benchmark against the model's limit. Read the shape to judge the nature: linear = no compaction, sawtooth = compacting, step = a big chunk got poured in, flat = fixed window.
3. If you really self-manage compaction (mode B), don't skip any of the five elements: set the watermark, decide what to compact, decide who compacts, do session-kickoff continuation, and confirm the rule is actually called in the path.
4. **Always inject single-turn ad-hoc instructions out-of-band; never mix them into persistent history.** A one-off line like "Are you still there?" should go through a single-turn injection entry point (effective only this turn, not entering history), rather than being `append`ed in as a formal turn. Otherwise these ad-hoc lines accumulate permanently as formal turns—polluting history and bloating tokens for nothing. Stuffing them into the system prompt is worse, since then they're carried every turn.

## Closing

> Don't measure this layer by reading code and guessing—measure it by plotting a "turn count → token" growth curve. The shape will speak for you: linear means no compaction, and the slope tells you how many turns until you hit the wall. History you can't see won't stop growing just because you're not watching it.
