---
title: Why the prompt file you're reading is often not the system the model actually receives
module: e
order: 1
slug: prompt-instruction-layers
nav: Prompts & Instruction Layers · L1/L2
summary: A single system message is usually stitched together from several sources; whether a rule belongs in a file or in code comes down to three tests—scope, priority, and robustness.
tags: [上下文工程, 系统提示, 指令, L1, L2, 暗物质]
---

## Setting the target: you audited the prompt file line by line, yet the same old bug still ships

You inherit a voice Agent that keeps throwing the same fault: after it calls the hang-up tool, it volunteers one more line—"Conversation complete, no reply needed"—dragging the call out with an awkward little tail. You open its system prompt file and read it three times cover to cover, and there it is, in plain language: "Do not speak after calling the end-of-call tool." The rule is right there, the wording is unambiguous, and yet in production it just won't listen.

What's stranger: the bug is intermittent. Ordinary calls are mostly fine, but the moment some "mode switch" action fires mid-call—say, it gets too noisy and the Agent upgrades to a noise-cancellation script—the fault springs right back to life.

You suspect the model is just weak, so you rewrite that rule harder, move it to the top of the section, and tack on three exclamation points. No effect.

The real problem isn't how that line is phrased—it's something you never realized: **the prompt file you're reading is simply not the system the model receives this turn.** The system message the model sees each turn is one whole string the framework stitches together for you from several sources—the wording in the file is only one piece; there are also iron rules hard-coded in code and force-appended every turn, plus fields filled in at runtime from the user profile. Auditing against the file alone, of course you can't find the problem: the one rule that actually makes the fault disappear isn't in the file at all—it's stitched in by code. And that "mode switch" action happens to drop it during the stitching.

This lecture makes two things crystal clear: who the model's system actually is this turn, where it lives, and how it gets stitched together; and whether a rule should go in the file (L1) or be appended by code (L2)—and by what test.

## The framework: who stitches a system together, and which layer a rule belongs in

First, let's calibrate the point that's easiest to confuse. Many frameworks call "the system prompt passed to the LLM" `instructions`—different name, but it's L1 system prompt at heart. The real trap is this: **L1 and L2 actually land in the same system message in the API**, and the model can't tell them apart when it sees them. Their difference isn't "where the model sees them," but "who maintains them, what scope, what priority."

The table below is the core framework of this lecture—the **"L1 / L2 Decision Table"**:

| Dimension | L1 system prompt | L2 instructions |
|------|-----------|---------|
| What it holds | Role, persona, behavioral norms, capability boundaries (relatively stable) | Task-specific rules, priority constraints, dynamically appended iron rules |
| Where it lives | Mostly a file on disk (the wording document) | Mostly stitched in code (constants, templates, runtime appends) |
| Who changes it | Product / ops hand-edit the file | Change the code logic |
| How it's fed | Carried fixed every turn | Some appended permanently, some replacing the whole, some bypassed for a single turn |
| Nature | Behavioral guidance | Plugging a stubborn fault, suppressing a model instinct |

Key insight: **the one system the model sees each turn is often stitched from three sources**—① the wording in the file (L1), ② fields filled in by `.format()` at runtime from the user profile (coming from L6 memory / profile, filled into L1), and ③ iron rules hard-coded and force-appended at the very end every turn (L2). Read the file alone, and you only see the first piece.

So should a rule stay in the L1 file, or be lifted into L2 and appended by code? Use the **three tests**:

| Test | Stays in L1 (file wording) | Lift to L2 (code append) |
|------|------------------|-------------------|
| Scope | May only apply to a certain stage / a certain path | Must be present across all paths, all stages |
| Priority | An ordinary rule the model is already happy to obey | Must sit at **the very end**, using recency to suppress the model's opposite instinct |
| Robustness | Occasionally ignored, no big deal | The moment it's lost, you get a system-level fault |

> [!NOTE]
> If any one of the three tests carries weight, you should lift that rule out of the L1 file and append it permanently to the end of the system by code. "Priority" here means **position**, not importance—the question is "do we need to rely on the end position to suppress an opposite instinct in the model," not "is this thing important to the business." Before judging this one, ask yourself: does the model have a spontaneous opposite tendency toward this rule? If yes, priority carries weight.

## Data / cases: three anonymized scenarios, three different feels

**Feel one: the same matter may have two sets of rules, each governing something different.** In one voice Agent, the rules around "hanging up" are actually two sets, governing completely different things. One is written in the L1 wording file and governs the business: when to end the call, how to say goodbye. The other is written in code and governs the mechanical timing: say the farewell first → call the end tool → after the call, no more characters of any kind. The latter isn't "generated"—it's a string constant hand-typed in the source, stitched fixed to the end of the system every time an Agent is created. The only difference between the two sets: one is in a file (humans edit), one is in code (force-appended every turn). **Treat them as one thing while auditing, and you'll miss the very set that actually plugs the fault.**

**Feel two: a stubborn fault is suppressed by end position, not by writing the line harder.** That "no characters after calling the tool" rule above—why must it be lifted out by code and nailed to the end of the system? Because engineering tests found that even with the requirement written into the tool description, the model still takes it upon itself to volunteer one more status note—it has a strong instinct to "honestly report to the user what I just did." Fighting that instinct isn't about harsher wording, it's about **position**: put the rule at the very end of the whole system, and use recency (the model is most sensitive to the most recent tokens) to suppress the instinct. This is the textbook case of all three tests carrying weight at once—scope spans all paths, priority must be at the end, robustness means a fault if lost—all three hit, so it must be L2.

**Feel three: switching modes by full replacement, but losing the iron rule at the end.** This is the nastiest flavor of dark matter. In one team's code, the system handed to the LLM at Agent creation is "file wording + end iron rule"—no problem. But it separately saved a "baseline instructions" for later mode switching, and what it saved was **the version before the iron rule was stitched on**. So when a noise-cancellation upgrade fires mid-call and the system needs full replacement, the code uses "baseline + new wording"—and the iron rule at the end is simply gone. The fault revives on the spot.

```text
system handed to LLM at creation   = file wording + end iron rule   ✅ has iron rule
separately saved "baseline"        = file wording                   ❌ no iron rule
full replacement on mode switch    = baseline + noise script = file wording + noise script   ❌ iron rule lost
```

These three feels point to the same sentence: **a rule being written does not mean it's actually stitched into the messages the model receives every turn.** You can't read this gap out of the file; you can only see it by chasing into the code and watching how the system is actually assembled turn by turn.

In passing, this also surfaces L2's three injection methods, each with a completely different effect on history—the mode-switch bug is rooted right in the "full replacement" one:

| Injection method | Behavior | Effect on history | Use for |
|---------|------|------------|------|
| Permanent append | Carried every turn, stitched fixed to the end | Stably resident | Cross-path, highest-priority iron rules |
| Full replacement | Swaps out the whole system | Rewrites the persistent system, easiest to lose things | Upgrades / mode switches |
| Single-turn bypass | Injected this turn only, never enters persistent history | Doesn't pollute history, doesn't accumulate tokens | One-off temporary wording |

## Actionable practices: the PM view and the engineering view

**PM view—use it to judge and communicate:**

1. When a "rule written but ignored" fault appears, don't immediately have the engineer write the prompt harder. First ask: "The system the model actually receives this turn—which sources is it stitched from? Is this rule really in there?"
2. When a new rule needs to land, run it through all three tests together: does scope span paths, is there a model instinct to suppress, does losing it cause a system-level fault? If any one carries weight, engineering should append it by code, not stuff it into the wording file.
3. Beware of "piling all important rules at the end." The end is the scarce high ground of recency; pile too much there and they dilute each other, and resident temporary wording pollutes behavior (e.g., a one-off prompt nailed in to be carried every turn, so the model harps on it for no reason).
4. Don't audit prompts by file alone. Have the engineer give you an "assembly diagram of which sources stitch this system together"—handing you the file alone isn't a delivery.

**Engineering view—use it for architecture decisions:**

1. Draw an instructions assembly dataflow for each Agent: from the file on disk, all the way to "the system sent to the LLM each turn," marking clearly who stitched in what at each step—file wording, profile `.format()` injection, code-appended iron rules—miss none of them.
2. To decide whether a rule goes L1 or L2, run the three tests. If none carries weight, keep it in the file; if any carries weight, append it permanently by code and nail it to the end of the system.
3. Route one-off temporary wording through single-turn bypass injection, never full replacement—the latter turns temporary wording into a resident system carried every turn thereafter.
4. Wherever you "save a baseline instructions for later replacement," make sure the baseline **always includes the end iron rule**; a sturdier approach is to re-stitch the iron rule onto the end at every replacement (baseline + new wording + iron rule), guaranteeing it's always last.
5. Don't dump the raw profile data wholesale into the system. Use `.format()` to fill only the necessary fields, avoiding large blocks of structured data crowding out L1.

## Wrapping up

> A stubborn rule isn't won by writing it harder, but by placing it later; and whether you can place it right depends first on seeing clearly who this turn's system is stitched from. Always audit the assembly before the wording—the file you read has only ever been one part of the system the model receives.
