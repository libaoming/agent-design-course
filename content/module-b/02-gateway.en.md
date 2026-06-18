---
title: Why the First Thing to Break in Production Isn't the Model — It's the Plumbing
module: b
order: 2
slug: gateway
nav: Gateway Engineering
summary: The Agent Gateway — ingress, routing, persistence, reliable delivery, and concurrency that let an Agent truly live in production.
tags: [工程地基, Gateway, 生产化]
---

## Setting up the target: how a model wired straight to users dies

Let's start with the kind of code almost everyone writes for their first version — the minimal loop of an Agent:

```python
while True:
    user_input = input()
    messages.append({"role": "user", "content": user_input})
    response = client.messages.create(messages=messages)
    print(response.content[0].text)
```

In your own terminal, it runs beautifully. You ask, it answers, and it looks like "the Agent is done." But the moment you try to hand it to real users, the following things start happening, one after another:

- **One process restart and the memory is gone.** History only lives in the in-memory `messages` list. A server restart, a hot reload, even a single uncaught exception, and the entire conversation evaporates into thin air.
- **It only knows one entry point.** This code is hard-wired to `input()`. Today a user @-mentions you in some IM group, tomorrow it's a different collaboration platform — and every new platform you onboard means copying the whole loop over again.
- **One network hiccup and the message is lost.** A timeout, a 503 from the other side, the connection dropping at the exact moment you send — the message neither arrives nor gets retried. It's just gone.
- **Multiple people talking at once, fighting each other.** Two users share one `messages`; their contexts cross-contaminate and replies get misattributed.
- **Context piles up until a 400.** The conversation is never trimmed, so sooner or later it slams into the model's context limit, followed by a blunt error.
- **One rate-limited API Key takes down the whole line.** With no redundancy, the moment a provider throttles you, your Agent goes silent.

These problems share one thing in common: **none of them is a "the model isn't smart enough" problem — they're all "the Agent has no chassis" problems.** No matter how strong the model is, it needs a layer of infrastructure to connect it to the real world and absorb all the surprises of a production environment. That layer is the Gateway.

> [!NOTE] In one sentence: Harness engineering solves "can the Agent get it done"; Gateway engineering solves "once it's done, can the result be delivered, can it recover when it crashes, can it hold up when it scales." The Harness is the engine; the Gateway is the chassis.

## The framework: the Gateway's five core responsibilities

Flip that list of "how it dies" around, and you get the five things the Gateway must shoulder. They aren't five independent features — they're five capabilities an Agent must possess simultaneously in order to "live in production."

![The Gateway chassis sits between platform ingress and the Agent Loop, shouldering five responsibilities: multi-channel ingress, routing, persistence, reliable delivery, and concurrency](../assets/diagrams/gateway.svg)

| Responsibility | Problem it solves | Key design |
|------|------------|---------|
| **Multi-channel ingress** | Many platform entry points have different formats; you don't want to rewrite the loop for each | Normalize into a unified message format; each platform only implements `receive()` + `send()` |
| **Message routing** | A message comes in — which Agent / which config should handle it | Match in layers from "specific to coarse," from a particular user all the way down to a global default |
| **Session persistence** | History can't be lost after a restart, and context can't grow without bound | Append history to disk (JSONL), crash-safe; when it gets too long, tiered truncation + compression |
| **Reliable delivery** | On network timeouts or remote failures, messages mustn't be lost and must be retryable | Write-Ahead Queue — persist before delivering — with exponential backoff retries |
| **Concurrency control** | Multiple tasks and multiple users running at once must not interfere, with users taking priority | Separate queues per work type (Named Lanes), each serial, with user messages cutting to the front |

### The invariant: the loop you never change

The first discipline of Gateway engineering is: **the Agent Loop is an invariant — every later feature stacks on top of it without touching it.**

```python
while True:
    user_input = channel.receive()
    messages.append({"role": "user", "content": user_input})
    response = client.messages.create(messages=messages)
    if response.stop_reason == "end_turn":
        channel.send(response.content[0].text)
    elif response.stop_reason == "tool_use":
        ...  # 工具派发逻辑
```

It differs from the target-setting version by exactly one thing: `input()` / `print()` is replaced by `channel.receive()` / `channel.send()`. One abstraction, and the "hard-wired to a single entry point" problem is pried wide open. There's also a trap that's easy to fall into: **the result of a tool execution must be put back into the conversation as a `user`-role message** — this is a hard API requirement, and if you put it in the wrong role, the model can't read it.

### Multi-channel ingress: one dataclass that flattens every platform

No matter which platform a message comes from, converge it into a single structure:

```python
@dataclass
class InboundMessage:
    text: str
    sender_id: str
    channel: str   # 哪个平台来的
    scope: str     # 私聊还是群聊
```

To onboard each new platform, you only implement its `receive()` and `send()`. The loop itself, the routing, and the persistence all stay untouched.

### Message routing: five priority layers, from precise to fallback

A message comes in — which config does it use? Match layer by layer from highest priority to lowest, stopping on the first hit:

```
平台 + 类型 + 发送者   →  精确匹配（给特定用户的专属配置）
平台 + 类型            →  群组级
平台                   →  平台级
类型                   →  类型级（所有私聊 / 所有群聊）
*                      →  全局默认（兜底）
```

The vast majority of messages take the global default; you only override config for a specific platform, group, or VIP when you actually need to.

### Session persistence: persist to disk + three layers of overflow protection

Persistence uses JSONL: every incoming message appends a line. Appending is crash-safe — if it dies mid-write, you lose at most the last line. When context is about to burst, instead of erroring out directly, it does three layers of progressive degradation:

```
Attempt 0: 正常调用
Attempt 1: 截断过大的工具结果（往往是某次工具吐了一大坨）
Attempt 2: 用 LLM 把最旧的 50% 历史压缩成摘要，替换原文
```

Reach for the cheapest move first, escalate to the costly ones only when that's not enough — a classic "order by cost, escalate level by level" degradation approach.

### Reliable delivery: persist first, then deliver

This is the part of the whole Gateway that most embodies "production awareness":

```python
tmp.write_text(json.dumps(entry))  # 1. 先写临时文件
os.fsync(...)                      # 2. 强制刷盘，确保真落到磁盘
os.replace(tmp, final)             # 3. 原子重命名，入队成功
```

These three steps are called a Write-Ahead Queue. Even if the process crashes the instant before delivery, the message is already safely sitting on disk and can be fished out and re-delivered after a restart. On a delivery failure, it retries with exponential backoff (roughly `5s → 25s → 2min → 10min`), with an added ±20% jitter to keep multiple failed tasks from all retrying at the same instant. Full fault tolerance is three layers stacked together: delivery-queue retries (transient network / remote failures) → context truncation/compression (context overflow) → API Key rotation (one gets throttled, automatically switch to the next).

### Concurrency control: separate lanes, users always first

Split work into a few independent lanes by "work type" (Named Lanes), each serial internally:

```python
lanes = {
    "main":      LaneQueue(max_concurrency=1),  # 用户消息，阻塞等结果
    "heartbeat": LaneQueue(max_concurrency=1),  # 后台心跳，不阻塞用户
    "cron":      LaneQueue(max_concurrency=1),  # 定时任务
}
```

The point of separate lanes is **isolation**: no matter how long a scheduled task runs, it can't block a real person waiting for a reply — the user's lane always has priority. There's also one key detail: **a generation mechanism prevents zombie tasks** — after a process restart, an old task finds its generation number doesn't match the current one, realizes "I'm a task from a past life," and quietly exits.

## Case: an Agent that reaches out to you on its own

Merely "responding passively" doesn't count as truly living in production. Let the Agent **act on its own**: it has a background heartbeat thread that wakes up once a second to check "is there anything I should proactively do?"

```python
def heartbeat_thread():
    while True:
        if not lock.acquire(blocking=False):  # 用户正在对话，让路
            sleep(1); continue
        response = run_agent_turn(trigger="heartbeat")
        if "HEARTBEAT_OK" not in response:     # 有实质内容才推送
            output_queue.put(response)
```

These fewer-than-twenty lines of code hide the shadows of three Gateway designs:

1. **Concurrency isolation is at work.** The first thing the heartbeat does is try to grab the lock; if it can't, it immediately yields — this is the concrete embodiment of "users first" in Named Lanes.
2. **Proactivity is bounded by a convention.** When the Agent decides "nothing to do," it replies with `HEARTBEAT_OK`; the Gateway sees this marker and silently discards it, only pushing when there's genuine substance. One string convention blocks 99% of the noise.
3. **Scheduled tasks are driven by a config file.** A `CRON.json` supports three triggers: "run once at a given moment," "run every so often," and "cron expression."

Picture it in a real business: an operations-assistant Agent that answers during the day when someone asks (the main lane), checks via heartbeat when no one's around whether "the daily report is due" (the heartbeat lane), and is woken on the hour by a scheduled task to run an inspection sweep (the cron lane). The three lanes each run in their own track, and the moment a real person shows up, they yield. That's what an Agent that "lives in production, rather than lying in your terminal" looks like.

## Actionable approach: bolt a chassis onto your Agent

Add things "in the order the pain shows up" and you basically can't go wrong:

1. **Decouple the loop from the entry point first.** Replace every `input()`/`print()` with `channel.receive()`/`channel.send()`. Lowest cost, highest payoff.
2. **Persist conversation history as JSONL.** Solve "amnesia" first — the problem that most damages user trust.
3. **Add context-overflow protection.** Degrade in tiers: "truncate bloated tool results → compress the oldest history."
4. **Only abstract the channel when you onboard a second platform.** Don't abstract too early.
5. **Layer message routing as needed.** A global default alone is enough at the start; add rules on top only when special-config needs appear.
6. **Switch delivery to persist-then-send (WAQ).** Upgrade when message loss starts genuinely hurting users.
7. **Keep several API Keys on hand for rotation.** Turn "one gets throttled" from an outage into an automatic switch.
8. **When you need concurrency, split lanes by work type rather than spawning raw threads.** Use the generation mechanism to clean up zombie tasks after a restart.

> [!WARNING] A note on ordering: the above is sorted by "the order the pain shows up," not a to-do list to knock out all at once. Doing concurrency too early, or abstracting multi-channel too early, is just another form of over-engineering. Treat whatever hurts first, first.

## Wrapping up

> The Harness is the engine, the Gateway is the chassis — the model is responsible for how fast it runs, the Gateway for recovering when it crashes, re-delivering when it drops, and yielding when it's crowded. Before handing your Agent to real users, ask one question: does it have a chassis?
