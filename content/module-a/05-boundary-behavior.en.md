---
title: Why an Agent That Can't Respect Boundaries Becomes a Dangerous "Overconfident Assistant"
module: a
order: 5
slug: boundary-behavior
nav: Boundary Behavior
summary: Break down 4 boundary types × 4 behavior modes into a designable, measurable boundary-behavior system.
tags: [L3, 边界行为, 维度5]
---

## Setting the Target: What Damage Can an Agent That Ignores Boundaries Cause

Let's start with three things that really do happen.

The first is **acting out of scope**. You tell a customer-service Agent, "Please refund this order for me." It doesn't have refund permission—but it doesn't know it doesn't. So it generates a reply: "Your refund has been initiated and should arrive in 3–5 business days." Confident tone, polished format. The customer leaves happy, no money is refunded, and complaints double three days later. Outside its permission boundary, the Agent pretended it had done the job.

The second is **hallucinating a hard answer**. You ask a legal Agent, "What are the latest jurisdiction rules in California for this kind of dispute?" Its training data has a cutoff and simply doesn't cover the latest statute—but instead of saying "I'm not sure," it follows the inertia of its corpus and fabricates something that looks a lot like a real statute. The user is a lawyer, and writes this "answer" into a legal opinion for their client. This is hallucination outside the data boundary, and the output flows straight into a downstream decision chain.

The third is **failing to refuse when it should**. You ask a medical-consultation Agent, "What dosage of this drug should I take for my symptom?" This is outside the compliance/ethics boundary—it should not be giving a specific diagnosis or dosage, but it answers anyway, and answers very professionally. This isn't "can't do it," it's "shouldn't do it" but did it anyway.

What these three disasters have in common: the Agent never realized it was standing outside some boundary, so it used "pretending to complete the task" to paper over "I can't / I'm not able to / I shouldn't." **Boundary-behavior design is about turning "how an Agent should behave when it hits a boundary" into a designable, measurable product decision—rather than leaving it to fate.**

## The Framework: 4 Boundary Types × 4 Behavior Modes

Step one: cut "why it can't do this" into 4 MECE categories. Note the axis you cut on—not by business domain, but by the **root cause of why it can't**:

| Boundary Type | Meaning | Nature |
|---|---|---|
| Capability | Technically can't do it, or can't do it accurately | Not yet supported |
| Data | Knowledge cutoff, not covered in training | Not yet supported |
| Permission | Operations outside the authorized scope | Not yet supported |
| Compliance/Ethics | Not permitted by law or morality | Must not do |

The MECE sanity check on this split is crucial, and two comparisons verify it: Capability vs. Data—the difference is "**can it be learned**" (Capability is something the model architecture itself can't do; Data is something the model could learn but just wasn't fed); Capability vs. Compliance—the difference is "**should it be learned**" (Capability is wanting to do it but being unable; Compliance is being able to do it but not allowed to).

This leads to the first key distinction of the whole lecture: **the first 3 types are "not yet supported," the 4th is "must not do."** The first 3 can be dissolved as models improve, data is added, and authorization expands; the 4th must never be crossed no matter how strong the technology gets.

Step two: rank an Agent's behavior when it hits a boundary into 4 modes, from worst to best:

![A ladder of the 4 boundary-behavior modes from worst to best: A pretend-completion < B blunt error < C honest disclosure < D prevention-layer interception, with B>C flipping in compliance scenarios](../assets/diagrams/boundary-behavior.svg)

| Mode | Name | Rating | Description |
|---|---|---|---|
| A | Pretend completion (hallucination) | Worst | Outside the boundary but faking that it got it done—packaging "I can't" as "I can" |
| B | Blunt error (technical error) | Second worst | Throws a technical error/stack trace/status code—honest but bad UX, exposes internal details |
| C | Honest disclosure | Standard | Frankly states it's beyond its capability/data range and offers a suggestion—honest and friendly |
| D | Prevention-layer interception (boundary detection) | Optimal | Detects and intercepts at the ingest stage, so it never even enters the generation step |

**A counterintuitive point: A < B < C < D is not absolute.** The ordering holds in most scenarios, but it flips in **compliance boundary** scenarios—there, B (blunt error) is actually better than C (honest disclosure). The judgment criterion is just one sentence:

> Will the pretend-completion output be used as the basis for a downstream decision? Yes (a lawyer uses a rating to write an opinion, a doctor uses a description to make a diagnosis) → better to hard-error and keep people out, B > C; No (the user is just browsing or chatting) → friendly disclosure makes for better UX, C > B.

Remember: whether a behavior mode is good or bad isn't fixed—it depends on "boundary type + whether the output will be trusted downstream."

## 5 Anti-Patterns and One Real Case

Flip the framework above around and you get the 5 most commonly stepped-on traps:

1. **Pretend-completion hallucination**—the king of anti-patterns, faking "I got it done," with the greatest harm.
2. **Tail-end interception**—catching the out-of-scope request only after generation finishes, or even after output. It should be caught at the ingest stage.
3. **Not distinguishing capability boundary vs. compliance boundary**—treating "must not do" as "not yet supported," or vice versa.
4. **Out-of-boundary errors that expose technical details**—dumping stack traces, internal interface names, model versions—unprofessional and a security risk.
5. **Not reporting boundary-detection accuracy to a KPI**—without measurement, boundary behavior can't be managed or improved.

**Anonymized case: jurisdiction boundary in a legal AI.** A legal-domain AI assistant once faced this class of request: a user asks how to handle a cross-jurisdiction dispute, where the specific jurisdiction rules touch both the data boundary (the latest statute isn't covered) and the compliance boundary (giving a specific legal opinion requires a license). The early version behaved like the classic Mode A—following the corpus to fabricate a jurisdiction conclusion that looked reasonable. The problem: legal output **will enter a downstream decision**. By the criterion above, this scenario must flip to "better to over-flag than to miss"—prefer B over A, and ideally achieve D: at the moment the request comes in, recognize "this is a compliance-boundary request needing a licensed legal opinion + jurisdiction determination," intercept it directly, guide the user to consult a practicing lawyer, and write the interception into the compliance audit.

## Actionable Practices

**How to design boundary behavior:**

1. **First do a 4-type boundary inventory**: classify each out-of-scope request the Agent might face into one of capability/data/permission/compliance, and use the two rulers "can it be learned" and "should it be learned" to self-check for MECE.
2. **Assign a target behavior mode to each boundary type**: default to pursuing C (honest disclosure); pursue D (ingest-stage interception) for high-value/high-risk scenarios. For compliance boundaries, prefer D, then B, and **never allow A**.
3. **Move detection forward to the ingest stage**: do boundary recognition before the request enters the generation pipeline, rather than patching it up after generation.
4. **De-technicalize error copy**: say "I can't handle this kind of request; I suggest you…" rather than throwing technical errors or internal details.
5. **Flip the trade-off by scenario:**

| Scenario | Trade-off Bias | Threshold Reference |
|---|---|---|
| Medical / Legal / Financial ratings | Better to over-flag than to miss | Pretend-completion rate ≤ 0.5% |
| Customer-service FAQ / Chat | Better to miss than to over-flag | False-positive rate ≤ 3% |
| AI recruiting phone calls (two-way dialogue) | Tight control on both sides | ≤ 5% on each side |
| Security audit | Better to over-flag than to miss | Pretend-completion rate ≤ 0.1% |

High-risk scenarios tolerate "wrongly intercepting some legitimate requests" (false positives) but never tolerate "missing a single out-of-scope request" (a miss); low-risk chat scenarios are the reverse.

**How to define metrics:** boundary behavior that doesn't make it into a KPI is the same as not being designed. The North Star is the **pretend-completion rate** (number of times it's outside the boundary but still outputs a result / number of out-of-boundary inputs sampled in QA), not "boundary-recognition accuracy"—because the harm users actually feel is "is the AI making things up?" Accuracy is the means; pretend-completion rate is the user-perspective outcome. Pair it with boundary-recognition recall and guidance-conversion rate; for process cost, look at false-positive rate / post-interception retention rate / boundary-recognition latency. Compliance boundaries also need their own audit fields (interception reason / model version / prompt hash / input hash / manual review time), with TTL set per applicable regulation.

Finally, boundary behavior isn't isolated—a miss turns into a hallucination; a false positive sends the Agent down the wrong recovery path; recognizing it correctly but not telling the user turns into a transparency problem. So boundary-detection accuracy itself must also be brought into monitoring.

## Wrap-Up

> Get the 4 boundary types straight—capability, data, and permission are "not yet supported," while compliance is "must not do"; among the 4 behaviors, pretend completion is the most damnable, because it disguises "I can't" as "I can." The North Star isn't whether detection is accurate, but that one thing the user feels: this AI—is it making things up or not?
