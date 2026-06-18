---
title: Why a Multi-Agent Platform Can't Be Built in One Shot — It Has to Grow in Four Stages
module: b
order: 5
slug: multi-agent-platform
nav: Multi-Agent Platform
summary: The four-stage evolution from a single Agent to a multi-Agent platform, plus the three new costs it introduces — handoff, sharing, and aggregation.
tags: [工程地基, 多Agent, 平台架构]
---

## Setting the target: the "Multi-Agent" you imagine vs. what it actually costs

A lot of teams decide to build a "multi-Agent platform" on a whim. The pitch sounds beautiful: one foundation that hosts countless digital employees — recruiting, insurance, education, all jammed in — with marginal cost approaching zero.

In practice, two failure modes show up over and over:

The first is **stage-skipping**. You have exactly one single Agent that works, yet you go straight for the end-state architecture — multi-tenancy, automatic routing, an industry template library — and scaffold all of it up front. The result: before a second real business is even running, you're already carrying a pile of abstraction costs paid for an *imagined* scale. Registry, routing layer, isolation layer — all built, but with not a single stream of real traffic to validate whether any of them were designed correctly.

The second is **underestimating the hidden costs**. In the single-Agent era there's only one actor in the system; data, configuration, and pipelines are all "singular." The moment you go multi-Agent, three kinds of cost that didn't exist before appear out of nowhere:

- **Handoff cost**: which Agent should a given request route to? The mapping among entry points, rules, and workers — who maintains it?
- **Sharing cost**: which capabilities are common to all Agents (pipeline, runtime, post-processing), and which must be customized per Agent? Cut the boundary wrong and you either reinvent the wheel or force-fit reuse into coupling.
- **Aggregation cost**: monitoring, auditing, billing. You used to look at one number; now you have to slice by Agent and then re-aggregate, or it all turns to mush.

These three costs don't vanish just because you "went platform" — they only shift from hidden to visible. **The question isn't whether to pay, but in what order and at which stage you pay.** That's exactly the point of evolving in four stages: each stage unlocks only the capabilities it needs, and pays off each corresponding cost only when it actually shows up.

## Framework: the four-stage evolution from single Agent to platform

There are three core premises: **backward-compatible architecture** (your existing single-Agent system is the starting point of stage one — no rip-and-replace), **incremental expansion** (each stage unlocks one set of new capabilities, and you can stop and use it after finishing a stage), and **shared-layer reuse** (the underlying pipeline, runtime abstraction, and post-processing pipeline can be shared across Agents — this is where the work savings come from).

The four stages map onto the three costs becoming visible step by step:

![Four-stage evolution of a multi-Agent platform: A multi-instancing → B routing layer → C multi-tenant isolation → D template library, advanced by bottleneck](../assets/diagrams/multi-agent-platform.svg)

| Stage | Core characteristic | When to enter | Main risk |
|---|---|---|---|
| **A · Multi-instancing** | Make the system support multiple independent Agents, each with its own manifest, directory, and worker name; isolate data/config per Agent | You have one working single Agent, and a second real business need has genuinely appeared | Turning hardcoded paths into parameters — do it incompletely and you leave hidden coupling; this stage still has no routing and no isolation guarantees |
| **B · Routing layer** | Different entry points auto-route to the right Agent's worker, sharing one resource pool, with independent stats — **handoff cost is paid off here** | You have 2-3 Agents that need to serve externally in parallel, and manually switching traffic has become a bottleneck | The entry↔Agent↔worker mapping table is a new single point; maintain it wrong and lines get crossed |
| **C · Multi-tenant isolation** | The database enforces per-Agent filtering, storage is isolated, API auth is scoped per Agent — **aggregation and compliance costs are paid off here** | You're going production-grade for external tenants, and data must never cross | Any query that misses a filter condition is a privilege breach; incomplete isolation is the same as none |
| **D · Template library** | Distill industry templates so a new Agent shrinks from "fully custom" to "copy a template and tweak config" | You have 3+ homogeneous Agents, new industries launch frequently, and customization cost has become the new bottleneck | Abstract the template too early and it ossifies; too late and you miss the reuse dividend |

Note one key judgment call: **the threshold between A and B is "is there a second real business," between B and C is "do you serve externally / touch compliance," and between C and D is "how high is the launch frequency."** You don't advance on a timeline — you advance by bottleneck. Only once the current stage's capability is no longer the bottleneck does the next stage make sense.

## Case: a recruiting voice Agent that wants to grow into a "digital employee platform"

One team had a working blue-collar recruiting voice Agent (single Agent, single entry, single business) and wanted to expand it into a platform that "sells out-of-the-box digital employees by industry," with insurance and education as candidate verticals. They didn't scaffold the end state directly; instead they did an honest inventory of what they already had, sorting existing capabilities into three tiers:

- **Out-of-the-box (directly shareable)**: the call pipeline, the dual-runtime abstraction, the ASR/TTS clients, the unified worker entry, post-processing recording and transcription — these have zero coupling to any specific business, and any similar Agent can use them.
- **Reusable with minor rework**: the manifest and directory structure (hardcoded paths need to be parameterized) and database queries (need per-Agent filter conditions added) — these are what gets gradually reworked across stages A through C.
- **Completely missing, must be built**: the Agent registry, entry-pool routing, per-Agent audit pipelines, and the industry template library — exactly the pieces you only need once handoff/aggregation costs become visible.

How much Agents differ across industries directly drives "what can be shared vs. what must be customized per Agent":

| Dimension | Recruiting Agent | Insurance Agent | Education Agent |
|---|---|---|---|
| Number of dialogue stages | 14 | 18-20 | 12 |
| Average call duration | 3-8 min | 8-15 min | 5-10 min |
| Core tools | look up jobs / save summary / transfer to human | look up policy / calculate premium / verify eligibility | list courses / check schedule / submit enrollment |
| Customer profile fields | job type / salary / region / shift | age / health / family / assets / policy | grade / scores / interests / parent expectations |
| Compliance constraints | no discrimination | regulatory "no exaggeration" | no promising admission |

You can see it: the pipeline and runtime are shared, but the persona, stages, tools, and compliance scripting must each be customized — and that boundary is exactly where the "sharing cost" has to be cut precisely. Cut it wrong, and you either make the shared layer too narrow or jam proprietary logic into the shared layer. The final tab: building a multi-Agent platform from scratch was estimated to take several months plus a sizable budget; evolving on top of the existing architecture through the four stages took a fraction of that in time and resources. The gap doesn't come from writing faster — it comes from **not paying ahead of time for an imagined scale**. Every bit of abstraction corresponds to a real bottleneck that has already appeared.

## Actionable approach: figure out which stage you're in right now

**Step 1: Identify your current stage (self-check)**

- The system has only one Agent, and data and config are "singular" structures → you're **before A**; don't rush to touch the platform.
- Multiple Agents can coexist, but you rely on manual traffic switching / manual assignment → you're at **A**.
- Entry points auto-route to the correct Agent, and stats can be viewed separately per Agent → you're at **B**.
- Database queries enforce per-Agent filtering, storage and auth are isolated, and you pass a privilege-breach audit → you're at **C**.
- A new Agent can launch in 1-2 days by copying a template and tweaking config → you're at **D**.

**Step 2: Decide whether to enter the next stage (the threshold is the trigger condition)**

- Condition for entering A: a **second real business** has appeared (not "might exist someday"). With only one business, stay on a single Agent.
- Condition for entering B: you have 2-3 Agents and **manual traffic switching has become the bottleneck**. While Agents are still few, manual switching is plenty — don't build routing early.
- Condition for entering C: you need to **serve externally or touch a compliance red line**, where crossed data would cause an incident. Purely internal, low-sensitivity scenarios can wait.
- Condition for entering D: **new-Agent launch frequency is high** enough that customization cost becomes the bottleneck. With fewer than 3 homogeneous Agents, a template is premature abstraction.

**Step 3: Each time you enter a stage, first answer who pays its corresponding cost.** Before B, think through the handoff cost (who maintains the mapping table, how to troubleshoot when it breaks); before C, think through the aggregation cost (how to slice monitoring/audit/billing by Agent and re-aggregate); throughout, keep an eye on the sharing cost (with every Agent you add, first ask "is this capability something the shared layer should provide, or is it proprietary to this Agent").

**Anti-pattern cheat sheet:** building multi-tenant scaffolding with only one business (paying ahead for an imagined scale); jamming industry-proprietary logic into the shared layer (the sharing boundary is cut wrong, polluting the shared layer); adding Agents without touching monitoring and continuing to stare at a single aggregated number (aggregation cost unpaid, problems masked); advancing stages on a timeline rather than by bottleneck (paying cost where no bottleneck has appeared).

## Wrap-up

> A multi-Agent platform isn't built — it's grown: each stage unlocks only the capabilities the current bottleneck demands, paying off the three costs — handoff, sharing, aggregation — only when they actually appear. Advance by bottleneck, not by imagination.
