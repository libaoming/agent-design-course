---
title: Your Static Prefix Has a Cache Marker — So Why Are You Paying for It Every Turn
module: e
order: 5
slug: cache-engineering
nav: Cache Engineering · Prefixes and Thresholds
summary: Cache is a byte-for-byte prefix match — one byte off and everything after it is wasted. Marking is not caching; count your tokens first to see if you clear the model's threshold.
tags: [上下文工程, prompt-caching, 前缀匹配, cache经济学]
---

## The Target: You Think It's Frozen, but the Bill Says It's Rewritten Every Turn

In a multi-turn conversational Agent, the persona, the tool descriptions, the all-phase instructions — that chunk of thousands of tokens of static prefix — gets re-read by the model on every single turn. It's identical byte for byte, so why pay for it every turn? So you slap a cache marker on it and figure you're saving money now.

After it goes live you check the bill, and the savings never showed up. You print per-turn usage and see `cache_read` is 0 from start to finish — the cache never hit at all, and that static prefix is being rewritten at full price every turn. What's even sneakier: it throws no error. You think it's frozen; the framework quietly re-bills it every turn, and nobody warns you.

This is the problem Cache engineering exists to solve. It's a **cross-cutting layer** within context engineering — the static layers like L1 system prompt, L4 structured IO, and L5 tool integration all depend on it to avoid paying twice. But cache has its own temperament: it's not a "flip the marker and it works" switch, but a mechanism with strict preconditions. You have to first understand what it matches on and when it gets silently thawed, or you'll end up in the most confusing state of all — "marker's on, still paying."

## The Framework: One Invariant That Grows Into the Whole Playbook

The entirety of Cache engineering follows from a single sentence:

> **Prompt caching is a prefix match. Any single byte change in the prefix invalidates all cache from that point onward.**

The cache key is the rendered prompt — the **exact bytes** from the start up to each `cache_control` breakpoint. If one byte differs at position N, all cache for every breakpoint after N is voided. The render order is ironclad law: `tools` → `system` → `messages`. So tool definitions come first (position 0); touch one tool and the entire cache collapses from the top. Putting `cache_control` on the last system block caches tools + system together. And anything that changes every turn — timestamps, current state — must come **after** the last breakpoint.

Given a prompt, the first move is always to ask: "From start to finish, which segment is identical on every turn?" That segment, and only that segment, qualifies for the cache prefix.

### Two Blocks: Separate What Changes From What Doesn't

The most common cache anti-pattern in multi-turn conversations is mixing the persona + tools + phase instructions together with the current state + filled slots in the same block. The consequence: the moment any runtime field changes (say, the phase jumps from S4 to S5), the entire block prefix changes, all cache is invalidated, the same persona gets rewritten every turn, and `cache_read` stays 0 forever.

The fix is to split into two independent blocks:

| Block | What it holds | cache_control | Behavior |
|-------|--------|:----------------:|------|
| Stable block | Persona + tool descriptions + all-phase instructions + output format constraints | Yes | Unchanged for the session; written turn 1, read turns 2..N |
| Volatile block | Current state / filled slots / next-step hints | No | Changes every turn but very short; not cached, cost stays manageable |

The key is the order: the Stable block goes first and gets marked; the Volatile block goes **after** the breakpoint and stays unmarked. The changing stuff is small, so not caching it costs nothing; the unchanging stuff is heavy, so caching it saves the lion's share. This split alone often cuts the input cost of a multi-turn conversation by more than half.

### The Model's Minimum Threshold: Even With a Marker, It May Silently Not Cache

This is the most counterintuitive rule. **A prefix shorter than the threshold is silently not cached** — no error, just `cache_creation_input_tokens` permanently at 0. And this threshold **varies by model** — it's an official, lookup-able fact:

| Model family | Minimum cacheable tokens |
|----------|:----------------:|
| Claude Opus 4.x / Haiku 4.5 | 4096 |
| Claude Sonnet 4.6 / early Haiku | 2048 |
| Early Sonnet (4.5 / 4 / 3.7, etc.) | 1024 |

The fatal corollary: suppose your static block is ~3k tokens and the marker is placed correctly, but you're running on an Opus or Haiku 4.5 endpoint — 3k is less than 4096, so **it won't cache at all**. Switch to Sonnet 4.6 (threshold 2048) and only then does it cache. So between "I set cache_control" and "I actually save money" there's a gate you have to clear first: count the tokens, then talk about cache.

### Cache Economics: Don't Guess How Much You Save

A cache write costs more than full price, a cache read costs less than full price — so cache is a ledger with a payback period:

| Item | Price (relative to uncached input) |
|----|:------------------------:|
| cache write (short TTL) | ~1.25× |
| cache write (long TTL) | ~2× |
| cache read | ~0.1× |
| Miss (uncached) | 1× |

Break-even is easy to compute: under short TTL, you recoup it on the second request (1.25 + 0.1 = 1.35 < 2). Long TTL costs twice as much to write, so it takes at least three requests to recoup — but the upside is it survives traffic lulls, holding up even when the gap exceeds the short TTL.

A back-of-envelope template (assume 30 turns, a 5000-token static block, short TTL):

- No cache: 30 × 5000 × 1 = 150,000 units
- With cache: turn 1 is 5000 × 1.25 (write) + 29 × 5000 × 0.1 (read) + a little volatile ≈ 6250 + 14500 ≈ 20,750 units
- Saving ≈ (150000 − 20750) / 150000 ≈ **86%**

This derivation is itself the best language for aligning PM and engineering: instead of "cache saves a bit of money," say "this path, costed at 1.25× write and 0.1× read, breaks even in two requests and saves 80% over 30 turns."

### Invalidation Tiers and the Lookback Window: Not Every Change Wipes Everything

Cache splits into three tiers — tools / system / messages — and a single change invalidates only its own tier and everything after it:

| Change | tools cache | system cache | messages cache |
|------|:-----------:|:------------:|:--------------:|
| Add/remove a tool / reorder tools / switch model | Voided | Voided | Voided |
| system content changes | Kept | Voided | Voided |
| tool_choice / image / thinking toggle | Kept | Kept | Voided |
| message content changes | Kept | Kept | Voided |

The practical corollary: `tool_choice` and the `thinking` toggle can change every turn without losing the tools + system cache; only touching tool definitions or switching models forces a full rebuild.

There's also an easily overlooked **lookback window**: each breakpoint walks back at most ~20 content blocks to find old cache. In an agentic loop, if a single turn packs in more than 20 tool_use / tool_result pairs, the next turn's breakpoint can't find the previous turn's cache and silently misses. The fix: in long turns, insert an intermediate breakpoint roughly every 15 blocks.

## Data / Cases: How Cache Bites You in the Real World

- **Mixed block makes cache_read permanently 0 (a support Agent)**: the system block stuffed persona + tools + current order status all into one block and marked it. After launch, `cache_read` stayed 0. Root cause: the current order status changed every turn, polluting the entire prefix and rewriting the persona each turn. After splitting into stable (persona + tools) + volatile (order status), `cache_read` finally went positive from turn 2 onward.
- **The endpoint + threshold double trap (a voice Agent audit)**: while drawing up the context ledger for a real-time voice Agent, two hazards turned out to be stacked — first, the endpoint it connected to directly might not support cache_control at all; second, its static block was ~3k tokens, below the 4096 threshold of Opus / Haiku 4.5. Either trap alone makes "marked but still no savings," so each must be verified independently — never assume. Later, on a different endpoint where the static block was fattened to over 5000 tokens, one team measured `cache_read` staying reliably above 0 from turn 2 onward, saving ~80% of input cost over a 30-turn call — confirming that "clears the threshold + endpoint supports it" are two prerequisites, neither of which can be missing.
- **Dynamically assembling tool sets, not a single hit across users (a common pitfall)**: someone "assembled the tool set dynamically per user preference, and set cache_control to save money." The problem: tools sit at position 0, and a tool set that varies by user = every user is a different prefix, so not a single cache hits across users — and instead they pay the write fee every time. The right approach is to freeze the tool set as a stable full set (sorted by name, deterministically serialized), and use `tool_choice` or message content to control "which one to use this turn" — rather than mutating the tools definition.

All three cases point to the same sentence: **a persistent `cache_read` of 0 means there's a silent killer hiding in the prefix** — maybe runtime state that snuck in, maybe a prefix below threshold, maybe a tool set that varies by user.

## Actionable Practice: How to Put This to Work

**PM lens — use it to make judgments and reconcile the bill:**

1. Before any "cache optimization" conversation, demand two numbers: the static block's real token count, and which model the target endpoint runs. The former decides whether you clear the threshold, the latter decides what the threshold is — missing either makes it impossible to judge whether you can save.
2. Speak in payback periods, not "saves a bit": "this path breaks even in two requests and saves 80% over N turns" is a promise engineering can verify.
3. Write "after launch, `cache_read` must be > 0 from turn 2 onward" into the acceptance criteria. A reading of zero isn't waved away as "didn't take effect" — you diff the rendered bytes of two requests to catch the silent killer.
4. Beware the temptation of the verb "freeze": cache savings tempt you to cram things that should change into the stable block. Once a date, a username, or state sneaks in, you not only stop saving — you throw away the write fee too.

**Engineering lens — use it to make implementation decisions:**

1. Before launch, count tokens first, then check the model threshold table. If the static block is shorter than the threshold, don't bother marking it — that's a write fee you pay for nothing, with no savings. If you can't clear it, fatten the stable block, or switch to a lower-threshold endpoint.
2. Split the static layer into two blocks, stable / volatile: persona + tools + all-phase instructions go in stable and get `cache_control`; current state + filled slots go in volatile, placed after the breakpoint, unmarked.
3. Clean the silent killers out of the prefix: `datetime.now()` in system, an early `uuid4()` / request_id, an unsorted `json.dumps()`, a per-user f-string-concatenated id, conditional concatenation like `if flag: system += ...`, a tool set that varies by user — every one of these zeroes out `cache_read`. The general fix: move dynamic fragments after the last breakpoint / make them deterministic / delete them if not needed.
4. In an agentic loop, when a single turn's block count approaches 20, insert an intermediate breakpoint roughly every 15 blocks to avoid exceeding the lookback window and silently missing on the next turn.
5. Add observability: print three numbers every turn — `input` / `cache_creation` / `cache_read`. True total = input + cache_creation + cache_read; seeing only a small input and assuming it's cheap is an illusion. `cache_read` going positive from turn 2 onward is the only sign the cache truly took effect.

## Wrap-Up

> Setting cache_control does not mean the cache took effect. First count tokens to see whether you clear the model threshold, then freeze the static prefix into a byte-for-byte unchanging stable block, and after launch always check that `cache_read` is > 0 from turn 2 onward — give the model the ability to save you money, and it turns around and demands you prove that this prefix really didn't change.
