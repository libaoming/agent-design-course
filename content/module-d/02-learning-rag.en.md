---
title: "Learning & Adaptation + RAG: So Your Agent Stops Starting From Scratch — and Stops Making Things Up"
module: d
order: 2
slug: learning-rag
nav: Learning & RAG
summary: Learning lets an Agent improve its strategy from feedback; RAG lets it plug into your private knowledge — both work at the context layer.
tags: [设计模式, 学习适应, RAG, 盲区]
---

## Setting the Target: Two Flaws That Keep Your Agent From Ever Growing Up

Start with two real scenarios.

First: you give the Agent a data-cleaning task, and the first time it gets the date format wrong. You correct it. The next day, same task — it makes the same mistake, in the same spot. The day after, again. It isn't dumb; it simply **has no learning mechanism**. Every conversation is a blank slate, so the pit it fell into yesterday it falls into again today. Correct it a hundred times and nothing sticks. This is "starting from scratch every time."

Second: you ask the Agent, "In our company's expense policy, above what amount does a flight require second-level approval?" It hands you an answer that looks supremely confident, neatly formatted, even with a specific number. The problem is — it made that number up. It has never seen your company's expense handbook, but it won't say "I don't know." It will stitch together something that looks like the most expense-policy-shaped thing in its training data. This is "without RAG, all it can do is make things up."

These two flaws map to the two blind-spot patterns this lecture fills in: **Learning and Adaptation** solves "starting from scratch every time," letting the Agent improve its strategy from interactions and feedback; **Retrieval (RAG)** solves "making things up," letting the Agent look up your private knowledge before generating. They look like two separate things, but at the core they're the same problem: **the model's weights are frozen and its knowledge has a cutoff — so how do you make a "frozen brain" behave as if it's continuously growing, and as if it knows things it originally didn't?** The answer in neither case is to change the weights (too heavy). It's to **change the context it receives each time** — a thread that runs through this whole lecture.

## Framework One: The Three Paths of Learning & Adaptation

"Letting an Agent learn" isn't a single action — it's three paths with completely different costs and payoffs. Remember one line first: **the further down you go, the heavier it gets, but the more durable it is.**

| Path | What changes | How | Durability | Cost | Typical scenario |
|------|--------------|-----|------------|------|------------------|
| ① In-context learning | No weight change, only context | Put experience/examples/corrections into the prompt or conversation history | Current session only | Very low | Few-shot examples; paste the error back and let it fix |
| ② Memory-driven adaptation | No weight change; change external memory | Write successful cases/user preferences into long-term memory, recall by relevance next time | Persistent across sessions | Medium | Remember "this user wants ISO 8601 dates," apply it automatically next time |
| ③ Fine-tuning / RLHF | Change the weights | Retrain on labeled data / reinforcement learning from human preferences | Permanent | High (iteration measured in weeks) | Burn stable domain-specific behavior into the model |

The three paths form a **staircase**, not a pick-one. The vast majority of Agent products rely on ① and ②, and almost never touch ③: both ① and ② change only the context, can be adjusted any time, and take effect the same day; ③ once burned into the weights is hard to undo and slow to iterate. **Default engineering order: if in-context can solve it, don't reach for memory; if memory can solve it, don't reach for fine-tuning.**

One key distinction — **explicit vs. implicit feedback**: explicit feedback is the user telling you outright what's right or wrong (strong signal, low noise — store it in memory with high weight); implicit feedback is inferred from behavior (copying your output = useful; rewriting it immediately = missed the mark; asking three times = didn't hit the point — weak signal but high volume, and it doesn't bother the user). A mature learning Agent uses both. **The most common rookie mistake is wiring up only explicit feedback** — but users rarely correct you proactively, and most of the valuable signal is hidden in behavior.

## Framework Two: The Five Steps of RAG

RAG (Retrieval-Augmented Generation) in one line: **before generating, go fetch relevant content from an external knowledge base, stuff it into the context, and then let the model answer based on that content.** It splits into two stages and five steps — the first three build the index offline, the last two run the query online:

![The five-step RAG pipeline: chunking → embedding → vector store (offline indexing) → retrieve Top-K → inject + generate (online query)](../assets/diagrams/learning-rag.svg)

| Step | Stage | What it does | Engineering key point |
|------|-------|--------------|------------------------|
| 1. Chunking | Offline | Cut long documents into small chunks | Chunk granularity: too large → imprecise retrieval, wasted budget; too small → broken semantics. Cutting on semantic boundaries (paragraphs/headings) beats hard-cutting on a fixed character count |
| 2. Embedding | Offline | Turn each chunk into a vector | Pick the right embedding model; for Chinese, test it empirically above all |
| 3. Store in vector DB | Offline | Store vectors + source text in a vector database | Build the index well, support fast similarity retrieval |
| 4. Retrieve Top-K | Online | Embed the query, fetch the k most similar chunks | Recall vs. precision: k too small misses key info, k too large pulls in noise and squeezes the budget; often paired with a rerank step |
| 5. Inject + generate | Online | Splice retrieved chunks into the prompt and hand them to the model along with the question | Injection budget: rank and truncate; citation traceability: mark which chunk each sentence came from, so it's traceable and verifiable |

RAG precisely solves three problems the model can't solve on its own: **knowledge cutoff** (let it read today's documents), **private/domain knowledge** (your expense handbook, codebase, product docs that the model has never seen), and **reduced hallucination** (answers grounded in evidence and required to cite sources, so the room to make things up gets squeezed).

## Case: The Evolution of a Customer-Support Agent

**Day 0 (nothing in place)**: a user asks, "How many team members does the Pro plan support?" The Agent guesses "10" from training data. Wrong — it's actually 5. The user complains.

**Add RAG (solving the made-up answers)**: chunk the product docs, pricing page, and FAQ into the index. Ask again, and the Agent first retrieves the "Pro plan: 5 seats" chunk, injects it into context, and answers "5" with a source link attached. The hallucination is gone.

**Add learning (solving starting from scratch)**: a longtime user keeps emphasizing, "I only care about API questions — skip the UI walkthroughs." The first time this is **explicit feedback**, and the Agent writes it into that user's long-term memory (path ②). After that it automatically recalls this preference and leads with API. Meanwhile, in the background, it notices that "answers about webhook retries" have a low copy rate and a high follow-up rate (**implicit feedback**); ops uses this to rewrite the docs and re-index them — another round of learning, this one happening on the RAG side.

**RAG owns "knowing it right," learning owns "understanding you better and better"**: one manages knowledge correctness, the other manages strategy adaptation. Neither touches the weights; both work purely at the context layer — which is exactly why they can iterate fast and ship the same day.

## Actionable Practices

**Learning & Adaptation**: ① exhaust in-context first, then consider memory, and only then touch fine-tuning; ② always capture explicit feedback and store it with high weight (a user actively correcting you is the most expensive signal); ③ design at least one implicit-feedback collector (pick one of copy rate / rewrite rate / follow-up rate and instrument it first); ④ memory must be recallable and forgettable (stale preferences need to be updatable and retirable); ⑤ advanced: automate the learning loop (let evaluation scores drive prompt rewrites, forming a closed loop).

**RAG**: ① chunk on semantic boundaries first, then tune the character count; ② retrieval quality comes before everything — evaluate it on its own (poor generation is eight-times-out-of-ten a retrieval miss, so unit-test recall first); ③ leave a budget for injection, rank and truncate (retrieving 20 chunks doesn't mean stuffing all of them in); ④ enforce citation traceability (squeezes hallucination + makes it debuggable); ⑤ for Chinese, you must empirically test the embedding and chunking (default configs are mostly tuned for English).

**Meta-principle**: both patterns are "change the context," not "change the model." When you want the Agent to be "smarter," your first instinct shouldn't be "swap in a bigger model" or "go fine-tune" — it should be "in the context I'm giving it, which piece of experience (learning) or which piece of knowledge (RAG) is missing?"

## Weaving It Into the Course

**Learning & Adaptation ↔ Module A's five layers, L4 Memory + the harness's autoevolve.** Path ②, memory-driven adaptation, is exactly the implementation of layer L4 Memory in Module A's five layers — long-term memory isn't about storing data, it's about letting the Agent "remember how to do things." And **autoevolve (automatic prompt evolution)** in the harness methodology is essentially automating this "feedback → improve strategy" learning loop: letting evaluation results turn around and rewrite the prompt. Learning isn't a capability unique to models — engineering scaffolding can "learn" just as well.

**RAG ↔ Module B's Context Engineering (the Cursor case study) + L4 in the five layers.** RAG is the standard implementation of context engineering in the "external knowledge" dimension. Remember the codebase-index retrieval in the Cursor case study? Cursor chunks, embeds, and indexes the entire repo, and when you ask a question it first retrieves the relevant snippets and then injects them — **that's a RAG built for code.** Retrieved knowledge and long-term memory share the same L4 slot; the only difference is that memory stores "experience" and the RAG store holds "knowledge."

## Wrap-Up

> An Agent doesn't automatically get smarter because the model is bigger — it gets smarter because the context you give it is more correct. Learning & adaptation carry yesterday's lessons into today; RAG plugs the knowledge it never had right in front of it — neither touches the weights, both work at the context layer. So this lecture is the two most important downstreams of Module B's Context Engineering: one accrues experience internally, the other connects to knowledge externally.
