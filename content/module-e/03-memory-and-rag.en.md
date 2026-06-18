---
title: Why the Model Misuses Memory Even After You "Injected" It
module: e
order: 3
slug: memory-and-rag
nav: Memory & RAG · L6
summary: Whether to inject memory, how much, and what to do when it goes wrong—use the seven-dimension lens to decide, three layers of division of labor to avoid re-feeding, and the opposite instinct to stop treating memory as gospel.
tags: [上下文工程, RAG, 记忆, 用户画像, 注入决策]
---

## Setting up the target: you think injecting memory means you're done, but the model insists on misusing it

When building an Agent with memory, the most intuitive idea is: look up the user's history, splice it into the prompt, and the model naturally "remembers" this person. So you write some loading logic, `.format()` the user profile into the system prompt, run a self-test—and sure enough, the Agent greets the user by name and picks up last time's topic. Looks smart.

But once it's been live for a while, three kinds of incidents start showing up one after another.

The first: **injecting the wrong person**. Two users' identifiers get crossed, so A's profile gets injected for B, and the Agent opens with "Last time you said you wanted to switch cities, right?"—leaving B baffled. This is worse than not injecting at all, because the model believes it and acts on the wrong information. The second: **re-feeding**. Information already asked this round gets asked again next round, or the user's entire history gets stuffed verbatim into the context—tokens blow up, latency spikes, and the model still can't grasp the point. The third is the most insidious: **it got injected, but the model clings stubbornly to old preferences**. The profile says "last time wanted a driver role," but this call the user clearly says they want to change direction—yet the model won't let go of "driver." You assumed "remembering" was a good thing, but the model treats historical memory as an inviolable commandment.

What this lecture sets out to solve is the single core problem behind all three: **this round, should we feed the model a piece of external knowledge or historical memory that "it doesn't inherently know, but might need this round"? Which piece, how much, when, and what to do when it's wrong?** This is L6 in the seven-layer assembly diagram—RAG and memory.

## Framework: first understand what L6 is, then use the seven-dimension lens to decide

L6 holds **"knowledge or memory retrieved for the current user and current round that isn't inherently in the model's head."** Two subtypes:

| Subtype | What it is | Typical scenarios |
|---|---|---|
| RAG (retrieval-augmented) | Fetch relevant snippets from a knowledge base | FAQ base, doc base, dynamically recalled by query |
| Memory | Cross-session / cross-round user state | User profile, where we left off, long-term preferences |

### Crux one: layers are split by "content origin," not by "where it's physically spliced"

This is L6's most counterintuitive and most easily misjudged point. Suppose some user profile ends up `.format()`-ed into the string that becomes the system prompt—physically it lives in L1's text, but its logical attribution is still L6.

Why? Because layering looks at **how this content came to be**:

- **L1 system prompt**: static persona, identical for every user and every round, available without retrieving anything.
- **L6 memory**: available only after retrieving a user's profile based on "who this person is"; the injected content differs per user.

The fact that it ends up spliced into L1's string ≠ it is L1. **Physical location ≠ logical attribution.** When auditing context, trace content's **origin chain**, not just which block of text it lands in. A companion quick check: **was this piece of information produced this round, or carried over from a previous round / from the base?**—produced-this-round counts as L7 (state and history), carried-over counts as L6. L7 accumulates within this session, is framework-managed, and grows automatically every round; L6 is retrieved cross-session and injected relatively statically at the opening.

### Crux two: the seven-dimension lens for the "injection decision"

Injecting memory is essentially answering one sentence: "At the right moment, with the right judgment, within budget, put the right knowledge in—without putting in the wrong thing." Break that sentence into seven dimensions and you get a decision table you can fill in item by item:

| Dimension | Question to answer | Typical answer for memory scenarios |
|---|---|---|
| When to inject | Which node of the loop injects | Inject once at session start, not retrieve every round |
| Signal (what triggers) | What signal decides which piece to inject | Strong identifier (e.g. unique ID) hits a user's profile / hits last round's breakpoint |
| Rank (how to order multiple) | How to order and select among candidates | Not relevant for simple profiles; only real RAG with multi-snippet recall needs it |
| Budget (token budget) | How many tokens injection takes, how to compress | Compress into a structured summary rather than full history; consider cache for those going into the static prefix |
| Guardrail (how to prevent errors) | How to prevent wrong injection / over-injection | Identity verification to prevent mix-ups; accept that "wrong injection > no injection," when unsure don't inject |
| State | Whether injection depends on session state | Resuming a breakpoint needs reading session state; pure profile is weaker |
| Observe (observability) | Is what was injected, and whether it was used right, visible? | Print injected memory tokens each round, reconcile |

The main act for memory scenarios is **When + Budget + Guardrail**: inject once at the opening (When), compress instead of dumping everything (Budget), wrong injection is worse than no injection (Guardrail). Rank / State / Observe are weak in simple profile scenarios and only become heavyweight in real, RAG-heavy scenarios.

### Crux three: the three-layer division of labor for memory, to avoid re-feeding

"Re-feeding" keeps happening because memory wasn't split by who manages which time scale. Slice memory into three layers, each managing one stretch, and the problem disappears on its own:

| Layer | What it stores | Role |
|---|---|---|
| Within-session | Slots collected so far | Don't re-ask what's been asked this round |
| Session end | One-line summary + next-time resume hint (heavily compressed) | No need to probe from scratch next time |
| Cross-session | Long-term profile | Returning users get injected directly, no rebuild |

In one sentence: **within-session relies on current slots to avoid re-asking; between sessions relies on the hint to avoid re-probing; long-term relies on the profile to avoid rebuilding.** With each of the three layers guarding one time scale, re-feeding has nowhere to stand.

### Crux four: inject by freshness tiers

A returning user ≠ inject the full profile, because **memory goes stale, and the older it is the less trustworthy.** The right approach is to tier by time since last interaction:

| Time since last | Strategy | What to inject |
|---|---|---|
| Recent (e.g. ≤ N days) | Resume directly | Skip the self-intro; memory is fresh and trustworthy |
| Semi-recent (e.g. ≤ M days) | Inject but confirm first | Inject the profile but verify identity first; memory may be stale |
| Too long ago | Treat as a new user | Inject almost nothing, re-probe |

The mnemonic: **memory isn't all-or-nothing; tier it by freshness—the fresher, the bolder to use; the older, the more you confirm or discard.** This is really a fusion of two dimensions: Budget (don't waste budget injecting stale memory) and Guardrail (old memory may be wrong, confirm first to prevent wrong injection). The overall criterion for injection granularity is **"just enough for this round"**—a super-old user with dozens of accumulated interactions gets a compressed profile + the most recent hint injected, not a verbatim record.

### Crux five: the opposite instinct—injected ≠ the model will use it appropriately

This is the one most worth burning into reflex in the whole lecture. You stuff memory into the context, subconsciously assuming the model will "refer to it in moderation," but the model has an **opposite instinct: it over-uses injected memory.** The profile says the user last wanted a driver role; this call the user says they want to change direction, and the model will very likely cling stubbornly to "driver."

The defense is two-pronged: ① **explicitly state priority** in the prompt—"the profile is a historical reference; the current round's user intent is authoritative; on conflict, follow this round"; ② use **down-weighted phrasing** when injecting—"previously mentioned…, please re-confirm this time," so injected memory is a reference, not gospel.

> [!NOTE]
> This instinct doesn't only appear at the memory layer. Whenever you "stuff X into the context / give the model a capability," immediately ask: **does the model have an opposite instinct to misuse it? On conflict, whom should it follow, or should both coexist?** Handing out a capability and using it correctly are two different things.

## Data / cases: three incidents, three fixes

Below are the typical, de-identified feel of it, mapping to the three incidents in the target setup:

- **Wrong injection is worse than no injection (a voice Agent, identity mix-up)**: an Agent matched user profiles by some identifier; one data mix-up injected A's profile for B. The Agent opened with "You wanted a driver last time, right?"—B never said that, and both experience and trust collapsed. Whereas if nothing had been injected, the Agent would just normally ask "What are you looking for?"—no harm at all. Conclusion: a memory system's Guardrail stance should be **conservative**, when unsure don't inject; and the Signal must use a strong identifier + identity verification.

- **Re-retrieving every round drags down latency (a real-time Agent, mistimed injection)**: one version changed the profile to "retrieve and inject in real time every round based on what the user just said," and three costs hit at once: an extra retrieval per round = latency (the red line for real-time scenarios), repeatedly injecting similar content = wasted duplicate tokens, and content that jitters every round = broken cache and a confused model. Fix: the profile is **cross-session static memory**; injecting once at the opening is enough. The criterion is clear—**static memory is injected once at the opening; only knowledge that changes with the query (real RAG) is worth retrieving every round.**

- **Static profile not in cache, re-sent at full price every round (an Agent, a Budget hidden ledger)**: once the profile is `.format()`-ed into L1, it becomes—along with the system persona—a **static prefix re-sent every round.** The longer the profile, the more tokens are re-sent each round, quietly pushing up per-call cost. This is the same dark matter as tool schemas and the L1 persona: **all memory that is "injected at the opening and unchanged for the whole call" belongs to the static prefix, and should go into the prompt cache to be sent once and then hit the cache afterward.** If someone stuffs dozens of histories verbatim into the profile, not only might tokens blow past the limit, but the cache can't save a prefix that large either—the only way out is to compress into a structured summary.

The three cases point to one sentence: the hard part of memory isn't "being able to find it," it's **"when to inject, how much, whether it'll be injected wrong, and whether the model will use it wrong."**

## Actionable practices: how to put this to use

**PM lens—use it to judge and communicate:**

1. When reviewing a memory feature, walk through the seven-dimension lens item by item first: When does it inject? What Signal does it rely on? How many Budget tokens, compress or not? **How does the Guardrail prevent wrong injection?** Whichever dimension you can't answer is where the design isn't finished.
2. Align with engineers using layer numbers: "this is L6 injecting the wrong memory," "this is L7 history bloat"—far more precise than "it keeps going wrong."
3. Hold the line on the "wrong injection > no injection" value stance: in experience reviews, rank "mix-ups" as a higher-priority defect than "didn't remember."
4. Require every memory feature to answer "did you tier by freshness?"—don't let the team default to "returning users get the full profile injected."

**Engineering lens—use it for architecture decisions:**

1. Implement memory in **three layers**: within-session slots (no re-asking), session-end summary + hint (no re-probing), cross-session profile (no rebuilding)—each managing one time scale.
2. **Static memory is injected once at the opening**; only knowledge that changes with the query and can't be fully injected up front goes through per-round retrieval (real RAG).
3. Memory like profiles—"injected at the opening, unchanged for the whole call"—goes into the **static prefix for caching** alongside the L1 persona and tool schema: byte-stable, aiming for high hit rates.
4. Make injection granularity **"just enough for this round"**: the profile stores a distilled picture + the most recent hint, not a pile of verbatim history; tier by freshness, the older the briefer or dropped.
5. **Explicitly write priority** in the prompt—"injected memory is a reference; this round is authoritative"—plus down-weighted phrasing, to stop the model from clinging to old preferences.
6. Add observability: print which memory was injected each round and how many tokens it took, so the "design ledger" and the "runtime log" can be reconciled.

## Closing

> [!NOTE]
> What's truly hard about a memory system was never "being able to find it," but "when to inject, how much, whether it'll be injected wrong, and whether the model will use it wrong." Injected ≠ the model will use it appropriately—write "this round is authoritative" for injected memory so it stays a reference, not gospel.
