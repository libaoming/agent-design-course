#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — content/**/*.md → site/ 纯静态多页站（中英双语 i18n）。
左侧边栏导航（模块讲义 + 实战示例）+ 右侧 TOC，Claude Code 文档调性。零三方依赖。

i18n：中文渲染到 site/ 根，英文渲染到 site/en/。每篇 NN-slug.md 可配兄弟文件
NN-slug.en.md（自带英文 frontmatter + 正文）；缺失则英文版跳过该篇（允许渐进翻译）。
UI chrome 全在 STRINGS[lang]；MODULES/AUTHOR/SITE 等字段值用 {"zh","en"} 形式，
缺英文回退中文。assets 给每种语言各复制一份，避免相对前缀复杂化。"""

import os, re, shutil, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
ASSETS = os.path.join(ROOT, "assets")
SITE = os.path.join(ROOT, "site")

LANGS = ["zh", "en"]  # zh → site/ 根；en → site/en/

def tr(val, lang):
    """字段值可以是普通字符串，或 {"zh":..., "en":...}。缺该语言回退 zh。"""
    if isinstance(val, dict):
        return val.get(lang) or val.get("zh") or ""
    return val

# 自定义域名（GitHub Pages）：仅写一次到 site/CNAME。留空则不写。
SITE_DOMAIN = "chengyansuo.com"

SITE_TITLE = {"zh": "橙研所", "en": "ChengYanSuo"}
SITE_TAGLINE = {
    "zh": "从能力设计到生产交付，一门问题驱动的 AI Agent 工程公开课",
    "en": "From capability design to production delivery — a problem-driven open course on AI Agent engineering",
}

# UI chrome 文案表
STRINGS = {
    "zh": {
        "html_lang": "zh-CN",
        "toc_title": "本页目录",
        "theme_toggle": "切换深色模式",
        "lang_switch": "EN",
        "lang_switch_title": "Switch to English",
        "soon": "筹备中",
        "soon_note": "实战示例筹备中。",
        "examples_soon": "实战示例筹备中，敬请期待。",
        "build_in_public": "Build in Public",
        "foot_wechat": "公众号「橙研所」 · ",
        "github": "GitHub",
        "lecture_no": "第 %d 篇",
        "example_tag": "实战示例",
        "minutes": "约 %d 分钟",
        "sec_count_lec": "%d 篇",
        "see_all": "查看全部 %d 篇 &#8594;",
        "sec_count_ex": "%d 篇",
        "sec_count_lab": "%d 个项目",
        "see_all_lab": "查看全部 %d 个项目 &#8594;",
        "lab_soon": "实验室项目筹备中，敬请期待。",
        "meta_lab": "实验室",
        "lab_links_title": "项目链接",
        "lab_related": "配套讲义",
        "lab_repo": "GitHub 仓库",
        "home_ex_desc": "用框架拆解真实 Agent 产品",
        "list_head": "篇目",
        "crumb_home": "首页",
        "meta_lecture": "Module %s · 第 %d 篇",
        "meta_example": "实战示例",
        "meta_example_target": "实战示例 · 拆解对象：%s",
        "prev": "← 上一篇",
        "next": "下一篇 →",
        "stats": '已有 <strong id="gcU">·</strong> 人读过',
        "landing_eyebrow": "橙研所 · Build in Public",
        "landing_h1": "把 Agent 当<em>产品</em>设计，当<em>系统</em>交付",
        "landing_lead": "我是橙研所，一个 AI 产品经理。这里是我边做边写的 Agent 工程笔记——从产品能力、工程地基，到 Harness、设计模式与上下文工程。问题驱动，持续生长。",
        "start_here": "从这里开始",
        "start_desc": "五条主线，每条都是一组问题驱动的深度笔记。挑一条切进去。",
        "hero_eyebrow": "A Course on Building Agents",
        "hero_h1": "学会<em>设计</em>与<em>工程化</em>一个 AI Agent",
        "hero_lead_suffix": "。两条主线：把 Agent 当产品来设计，把 Agent 当系统来交付。",
    },
    "en": {
        "html_lang": "en",
        "toc_title": "On this page",
        "theme_toggle": "Toggle dark mode",
        "lang_switch": "中文",
        "lang_switch_title": "切换到中文",
        "soon": "Coming soon",
        "soon_note": "Case studies coming soon.",
        "examples_soon": "Case studies are in the works — stay tuned.",
        "build_in_public": "Build in Public",
        "foot_wechat": "WeChat: ChengYanSuo · ",
        "github": "GitHub",
        "lecture_no": "Post %d",
        "example_tag": "Case Study",
        "minutes": "%d min read",
        "sec_count_lec": "%d posts",
        "see_all": "See all %d posts &#8594;",
        "sec_count_ex": "%d studies",
        "sec_count_lab": "%d projects",
        "see_all_lab": "See all %d projects &#8594;",
        "lab_soon": "Lab projects coming soon — stay tuned.",
        "meta_lab": "Lab",
        "lab_links_title": "Project links",
        "lab_related": "Related course",
        "lab_repo": "GitHub repo",
        "home_ex_desc": "Real Agent products, dissected with the frameworks",
        "list_head": "Posts",
        "crumb_home": "Home",
        "meta_lecture": "Module %s · Post %d",
        "meta_example": "Case Study",
        "meta_example_target": "Case Study · Subject: %s",
        "prev": "← Previous",
        "next": "Next →",
        "stats": '<strong id="gcU">·</strong> readers so far',
        "landing_eyebrow": "ChengYanSuo · Build in Public",
        "landing_h1": "Design the Agent as a <em>product</em>, ship it as a <em>system</em>",
        "landing_lead": "I'm an AI product manager writing in the open. These are my Agent engineering notes — from product capability and engineering foundations to harnesses, design patterns, and context engineering. Problem-driven, always growing.",
        "start_here": "Start here",
        "start_desc": "Five threads, each a set of problem-driven deep notes. Pick one and dive in.",
        "hero_eyebrow": "A Course on Building Agents",
        "hero_h1": "Learn to <em>design</em> and <em>engineer</em> an AI Agent",
        "hero_lead_suffix": ". Two threads: design the Agent as a product, and deliver the Agent as a system.",
    },
}

def S(lang, key):
    return STRINGS[lang][key]

# 作者 / 引流条（Build in Public）。links 里 url 为空 = 渲染成文字标签。
# TODO（待用户补）：X / 即刻 / 小红书的真实链接，补进 AUTHOR["links"] 即可。
AUTHOR = {
    "name": {"zh": "橙研所", "en": "ChengYanSuo"},
    "by": {"zh": "作者", "en": "By"},
    "avatar": "橙",
    "bio": {
        "zh": "AI 产品经理 · Build in Public。这门课配合公众号「橙研所」边做边写，把 Agent 学习笔记重写成讲义体。",
        "en": "AI product manager · Build in Public. This course is written in the open alongside my Chinese newsletter, turning Agent study notes into structured lectures.",
    },
    "links": [
        ({"zh": "GitHub", "en": "GitHub"}, "https://github.com/libaoming"),
        ({"zh": "公众号 · 橙研所", "en": "Newsletter · ChengYanSuo"}, ""),
    ],
}

def author_block(lang):
    links = []
    for label, url in AUTHOR["links"]:
        lbl = html.escape(tr(label, lang))
        if url:
            links.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, lbl))
        else:
            links.append('<span class="lk">%s</span>' % lbl)
    return ('<div class="author-card">'
            '<span class="author-avatar">%s</span>'
            '<span class="author-meta">'
            '<span class="author-name"><span class="by">%s</span>%s</span>'
            '<p class="author-bio">%s</p>'
            '<span class="author-links">%s</span>'
            '</span></div>') % (
        html.escape(AUTHOR["avatar"]), html.escape(tr(AUTHOR["by"], lang)),
        html.escape(tr(AUTHOR["name"], lang)), html.escape(tr(AUTHOR["bio"], lang)), "".join(links))

# 微信收款码（赞赏 / 请作者喝杯咖啡）。
SUPPORT = {
    "title": {"zh": "请作者喝杯咖啡", "en": "Buy me a coffee"},
    "note": {"zh": "讲义对你有用的话，微信扫码赞赏一杯。备注一句话，我会很开心。",
             "en": "If the course helped, scan with WeChat to tip a coffee. A note makes my day."},
    "img": "assets/wechat-pay.png",
    "alt": {"zh": "微信收款码 · 橙研所", "en": "WeChat payment QR · ChengYanSuo"},
}

def support_block(lang, prefix=""):
    return (
        '<button class="support-btn" onclick="document.getElementById(\'support-modal\').style.display=\'flex\'">'
        '%s'
        '</button>'
        '<div id="support-modal" class="support-modal" onclick="if(event.target===this)this.style.display=\'none\'">'
        '<div class="support-modal-box">'
        '<button class="support-modal-close" onclick="document.getElementById(\'support-modal\').style.display=\'none\'">&#215;</button>'
        '<p class="support-modal-note">%s</p>'
        '<img src="%s%s" alt="%s">'
        '</div>'
        '</div>'
    ) % (
        html.escape(tr(SUPPORT["title"], lang)), html.escape(tr(SUPPORT["note"], lang)),
        prefix, SUPPORT["img"], html.escape(tr(SUPPORT["alt"], lang)))

MODULES = {
    "a": {
        "name": {"zh": "Agent 产品与能力设计",
                 "en": "Agent Product & Capability Design"},
        "desc": {"zh": "以 L3 五维能力为主轴，技术地基五层做底座。讲「怎么设计与评估一个 Agent」。",
                 "en": "Centered on the five capability dimensions, with the five-layer technical foundation as the base. How to design and evaluate an Agent."},
        "intro": {
            "zh": (
                "本模块回答一个问题：**怎么把一个 Agent 当成产品来设计和评估？**\n\n"
                "主轴是评估一个 Agent 能力的五个维度——任务完成路径、失败节点、错误恢复、透明度、边界行为；"
                "底座是理解 Agent 怎么跑起来的技术地基五层（Loop / Tool / Planning / Memory / Multi-Agent）。"
                "学完你会拿到一套**可拆分、可埋点、可定 KPI** 的语言：把模糊的「这个 Agent 好不好用」拆成具体维度，逐项设计、逐项度量。\n\n"
                "**讲次编排**：先用第 0 讲的五层架构建立底座（定位问题在哪一层），再沿五维逐讲展开——前四维层层递进（能不能做完 → 在哪失败 → 失败怎么恢复 → 过程透不透明），最后落到边界行为（该不该做）。\n\n"
                "**适合**：想转型 / 进阶到 Agent 方向的产品经理、模型策略 PM，以及想要「产品评估视角」的工程师。"
            ),
            "en": (
                "This module answers one question: **how do you design and evaluate an Agent as a product?**\n\n"
                "The main thread is the five dimensions for assessing an Agent's capability — task-completion path, failure nodes, error recovery, transparency, and boundary behavior; "
                "the base is the five-layer technical foundation for understanding how an Agent runs (Loop / Tool / Planning / Memory / Multi-Agent). "
                "By the end you'll own a vocabulary that is **decomposable, instrumentable, and KPI-ready**: turning the vague \"is this Agent any good?\" into concrete dimensions you design and measure one by one.\n\n"
                "**Lecture order**: Lecture 0 sets the base with the five-layer architecture (locate which layer a problem lives on), then the five dimensions unfold one per lecture — the first four build on each other (can it finish → where does it fail → how does it recover → is the process transparent), ending on boundary behavior (should it act at all).\n\n"
                "**For**: product managers moving into or leveling up on Agents, model-strategy PMs, and engineers who want a \"product evaluation\" lens."
            ),
        },
    },
    "b": {
        "name": {"zh": "Agent 工程地基",
                 "en": "Agent Engineering Foundations"},
        "desc": {"zh": "Harness、Gateway、上下文工程、评测、框架选型。讲「怎么让 Agent 可靠地跑起来」。",
                 "en": "Harness, Gateway, context engineering, evaluation, framework selection. How to make an Agent run reliably."},
        "intro": {
            "zh": (
                "本模块回答另一个问题：**怎么让一个 Agent 在生产环境里可靠地跑起来？**\n\n"
                "核心理念一句话——模型是司机，工程基础设施才是车。模型能力商品化之后，护城河上移到 Harness、上下文工程和数据飞轮。"
                "本模块从 Harness 总纲出发，依次讲上下文工程（最稀缺的资源怎么管）、Gateway（生产底盘）、框架选型（别默认上 LangGraph）、评测体系（别拍脑袋迭代）、多 Agent 平台（按瓶颈而非想象演进）。\n\n"
                "**讲次编排**：第 0 讲 Harness 是总纲（先修车再换司机），其后五讲分别对应一个工程子系统，每讲都遵循「不修这块会怎样 → 框架 → 怎么落地」。\n\n"
                "**适合**：做 Agent 应用的工程师、独立开发者，以及想补「工程地基认知」的 PM。"
            ),
            "en": (
                "This module answers another question: **how do you make an Agent run reliably in production?**\n\n"
                "The core idea in one line — the model is the driver, the engineering infrastructure is the car. Once model capability is commoditized, the moat moves up to the Harness, context engineering, and the data flywheel. "
                "Starting from the Harness overview, this module covers context engineering (managing the scarcest resource), the Gateway (the production chassis), framework selection (don't default to LangGraph), the evaluation system (don't iterate on gut feel), and multi-Agent platforms (evolve by bottleneck, not by imagination).\n\n"
                "**Lecture order**: Lecture 0 (Harness) is the overview — fix the car before swapping the driver — then five lectures each map to one engineering subsystem, all following \"what breaks without it → framework → how to ship it.\"\n\n"
                "**For**: engineers and indie developers building Agent applications, and PMs who want to fill in the \"engineering foundations\" mental model."
            ),
        },
    },
    "c": {
        "name": {"zh": "Harness 工程",
                 "en": "Harness Engineering"},
        "desc": {"zh": "让 Agent 可靠地跑完长任务的工程方法论。以 walkinglabs《Harness Engineering》为骨架，融合一套真实项目里跑出来的实战做法。",
                 "en": "The engineering methodology for getting an Agent to finish long tasks reliably. Built on walkinglabs' Harness Engineering, fused with practices forged in real projects."},
        "intro": {
            "zh": (
                "本模块回答最后一个问题：**怎么让一个 Agent 可靠地跑完一个需要很多步、跨很多次会话的长任务？**\n\n"
                "核心命题是——模型能力是常数，能不能交付是 harness 的函数。同一个模型，裸跑失败，套上完整 harness 就成功；成功率能从两成爬到接近满分，而模型一行没动。"
                "本模块以 walkinglabs《Harness Engineering》的框架为骨架，融合一套在真实项目里跑出来的实战方法论：features.json 单一事实源、STATUS + 里程碑三件套、线性切片、fixture 先于代码、4 层防御体系、上下文隔离子 agent。\n\n"
                "**讲次编排**：先立靶（为什么能力强的 Agent 仍失败）→ 给定义（harness 到底是什么）→ 逐个子系统展开（仓库即事实源 / 指令拆分 / 跨会话连续 / 边界与 feature list / 端到端验证与干净交接）。\n\n"
                "**适合**：要让 Agent 干真活、跑长任务的工程师和 PM——其实你正在读的这门课，本身就是用这套方法论做出来的。"
            ),
            "en": (
                "This module answers the last question: **how do you get an Agent to reliably finish a long task that takes many steps across many sessions?**\n\n"
                "The core thesis — model capability is a constant; whether it delivers is a function of the harness. The same model fails bare and succeeds wrapped in a full harness; success rates climb from ~20% to near-perfect without changing a single line of the model. "
                "This module uses walkinglabs' Harness Engineering as the skeleton, fused with a battle-tested methodology from real projects: features.json as the single source of truth, the STATUS + milestone triad, linear slicing, fixtures before code, the four-layer defense system, and context-isolated sub-agents.\n\n"
                "**Lecture order**: set the target (why capable Agents still fail) → give the definition (what a harness actually is) → unfold each subsystem (repo as source of truth / instruction splitting / cross-session continuity / boundaries and the feature list / end-to-end verification and clean handoff).\n\n"
                "**For**: engineers and PMs who need an Agent to do real work on long tasks — in fact, the course you're reading was itself built with this methodology."
            ),
        },
    },
    "d": {
        "name": {"zh": "Agent 设计模式（21 式）",
                 "en": "Agent Design Patterns (21)"},
        "desc": {"zh": "Google《Agentic Design Patterns》21 个核心模式的中文精炼。一本「遇到这类问题用哪个套路」的模式食谱，补全前三个模块的盲区。",
                 "en": "A distilled take on the 21 core patterns from Google's Agentic Design Patterns. A \"which pattern for which problem\" cookbook that fills the blind spots of the first three modules."},
        "intro": {
            "zh": (
                "前三个模块分别按「能力维度」「工程地基」「harness 方法论」切；本模块换一把刀——按 **21 个可复用的实现模式**切，是一本「遇到这类问题，用哪个套路」的食谱。\n\n"
                "来源是 Google 的《Agentic Design Patterns》（Antonio Gulli），这里取其中文精炼，参考 [xindoo 的中文翻译项目](https://github.com/xindoo/agentic-design-patterns)。21 个模式可归成 6 组：基础执行 / 质量与安全 / 记忆与知识 / 协作与互联 / 控制与治理 / 推理与探索。\n\n"
                "**讲次编排**：第 0 讲是**全景地图**——把 21 个模式一次铺开、归组、并标注「本课前三模块讲过没」；其后几讲**只深入前三模块的盲区模式**（反思、学习与适应、知识检索 RAG、智能体间通信 A2A、推理技术、优先级与探索），不重复已讲的工具/规划/记忆/异常/安全/评测。\n\n"
                "**适合**：想要一份「招式速查」的人——知道遇到某类问题，业界有哪些成型套路可选。"
            ),
            "en": (
                "The first three modules cut along \"capability dimensions,\" \"engineering foundations,\" and \"harness methodology.\" This module picks up a different knife — cutting along **21 reusable implementation patterns**, a cookbook of \"which pattern for which problem.\"\n\n"
                "The source is Google's Agentic Design Patterns (Antonio Gulli); this is a distilled Chinese-to-English rendering, referencing [xindoo's translation project](https://github.com/xindoo/agentic-design-patterns). The 21 patterns group into 6 clusters: core execution / quality & safety / memory & knowledge / collaboration & interop / control & governance / reasoning & exploration.\n\n"
                "**Lecture order**: Lecture 0 is the **panorama** — laying out all 21 patterns at once, grouping them, and marking \"covered in the first three modules or not\"; the later lectures **dive only into the blind-spot patterns** (reflection, learning & adaptation, knowledge retrieval / RAG, agent-to-agent communication / A2A, reasoning techniques, prioritization & exploration), without repeating tools/planning/memory/exception/safety/evaluation already covered.\n\n"
                "**For**: anyone who wants a \"move cheat-sheet\" — knowing, for a given class of problem, which established patterns are on the menu."
            ),
        },
    },
    "e": {
        "name": {"zh": "Context Engineering 上下文工程",
                 "en": "Context Engineering"},
        "desc": {"zh": "模型每轮实际看到的上下文怎么拼、怎么省、怎么验。以 7 层次为主轴，把 CE 从「读过方法论」练成「能拆、能埋点、能算账」。",
                 "en": "How the context the model actually sees each turn is assembled, trimmed, and verified. Anchored on the 7 layers, turning CE from \"read the theory\" into \"can decompose, instrument, and account for it.\""},
        "intro": {
            "zh": (
                "本模块回答一个被严重低估的问题：**模型这一轮，到底看到了什么 token？是谁替你决定的？**\n\n"
                "你写的那段 prompt，从来不是模型实际收到的全部。框架默认值、对话历史、注入的记忆、工具 schema 都会被悄悄拼进去——这些「你以为没塞、实际塞了」的 token，就是上下文里的**暗物质**。Context Engineering（CE）不是把 system prompt 写长写细（那还是 Prompt Engineering），而是**优化模型每一轮看到的整坨上下文怎么装配**。\n\n"
                "主轴是 **7 层次**：把模型每轮的上下文拆成系统提示、指令、结构化 IO、工具、记忆、历史等层，外加 cache 与可观测两道横切。学完你会拿到一套能力——**让 7 层 100% 可见，再用一张 CONTEXT.md 把「设计账本」和「运行期对账单」对上，差额就是要排查的暗物质**。\n\n"
                "**讲次编排**：第 0 讲先建总览框架（7 层次 + 暗物质 + CE/PE/Harness 辨析），其后逐层深入——提示与指令、结构化 IO 与工具、记忆与 RAG、历史与压缩，最后两道横切（cache 工程、可观测与评估）收口。\n\n"
                "**适合**：要把 LLM agent 做稳、做省、做得可验证的工程师与 PM——尤其是被「换了更强的模型还是不稳」「token 成本算不清」困住的人。"
            ),
            "en": (
                "This module answers a badly underrated question: **what tokens did the model actually see this turn — and who decided that for you?**\n\n"
                "The prompt you wrote is never all the model receives. Framework defaults, conversation history, injected memory, and tool schemas all get quietly assembled in — these \"you thought you didn't include them, but you did\" tokens are the **dark matter** of context. Context Engineering (CE) is not writing a longer, finer system prompt (that's still Prompt Engineering); it is **optimizing how the entire blob of context the model sees each turn is assembled**.\n\n"
                "The main thread is the **7 layers**: decomposing each turn's context into system prompt, instructions, structured IO, tools, memory, history, and more — plus two cross-cutting concerns, cache and observability. By the end you'll own a capability — **make all 7 layers 100% visible, then use a single CONTEXT.md to reconcile the \"design ledger\" against the \"runtime statement\"; the gap is the dark matter to investigate**.\n\n"
                "**Lecture order**: Lecture 0 builds the overview (7 layers + dark matter + distinguishing CE/PE/Harness), then drills in layer by layer — prompts & instructions, structured IO & tools, memory & RAG, history & compaction — closing on the two cross-cutting concerns (cache engineering, observability & evaluation).\n\n"
                "**For**: engineers and PMs who need their LLM agent stable, cheap, and verifiable — especially anyone stuck on \"swapped in a stronger model and it's still flaky\" or \"can't account for the token cost.\""
            ),
        },
    },
}

EXAMPLES_TITLE = {"zh": "实战示例", "en": "Case Studies"}
EXAMPLES_INTRO = {
    "zh": (
        "光有框架还不够。这一区用前两个模块的框架，去**拆解真实的 Agent 产品**——"
        "看抽象的五维、五层、Harness，在 Claude Code、Cursor 这些产品里到底长什么样。"
        "每个示例都是一次「拿着透镜看真实世界」的练习：框架是怎么从一个真实产品里被验证、被修正的。"
    ),
    "en": (
        "Frameworks alone aren't enough. This section uses the frameworks from the earlier modules to **dissect real Agent products** — "
        "seeing what the abstract five dimensions, five layers, and Harness actually look like inside products like Claude Code and Cursor. "
        "Each study is an exercise in \"looking at the real world through the lens\": how a framework gets validated and corrected against a real product."
    ),
}

LAB_TITLE = {"zh": "实验室", "en": "Lab"}
LAB_INTRO = {
    "zh": (
        "讲义是想明白的，实战是拆解过的，实验室是**做出来的**——这一区陈列我自己造的项目：多数已开源，也有跑在生产里的系统。"
        "都是为了同一件事造的工具：让 Agent 在长任务里不漂移、有记忆、上下文可控、用量看得清。"
        "每个项目一页，固定结构：解决什么 → 核心机制 → 怎么用。"
    ),
    "en": (
        "Lectures are what I've thought through, case studies are what I've taken apart, and the Lab is what I've **actually built** — "
        "this section lists projects I made myself: most are open source, some run in production. They're all tools made for the same goal: keeping Agents from drifting on long tasks, "
        "giving them memory, keeping context under control, and making usage legible. One page per project: what it solves, how it works, how to use it."
    ),
}
# 项目状态徽章（canonical key → 双语标签）。实验室可容纳不同成熟度。
STATUS_LABEL = {
    "open-source": {"zh": "已开源", "en": "Open Source"},
    "experimental": {"zh": "试验中", "en": "Experimental"},
    "local-only": {"zh": "本地未推", "en": "Local Only"},
    "in-production": {"zh": "生产中", "en": "In Production"},
}

# 访问统计（GoatCounter）。留空 = 不接入任何第三方脚本。
GC_CODE = "learn-agent-design"

# 主题切换：head 防闪烁 + body 末尾点击切换逻辑
THEME_HEAD_JS = '<script>(function(){try{var t=localStorage.getItem("cys-theme");if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}})();</script>'
THEME_BODY_JS = '<script>document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("#themeToggle");if(!b)return;var d=document.documentElement,c=d.getAttribute("data-theme");var sys=window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches;var n=c?(c==="dark"?"light":"dark"):(sys?"light":"dark");d.setAttribute("data-theme",n);try{localStorage.setItem("cys-theme",n);}catch(e){}});</script>'

def gc_tracking():
    return ('<script data-goatcounter="https://%s.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>' % GC_CODE) if GC_CODE else ""

def stats_block(lang):
    if not GC_CODE:
        return ""
    return ('<div class="learn-stats" id="learnStats" hidden>'
            '<span class="dot"></span>%s</div>'
            '<script>fetch("https://%s.goatcounter.com/counter/TOTAL.json")'
            '.then(function(r){return r.ok?r.json():Promise.reject()})'
            '.then(function(d){document.getElementById("gcU").textContent=d.count_unique;'
            'document.getElementById("learnStats").hidden=false})'
            '.catch(function(){})</script>') % (S(lang, "stats"), GC_CODE)

# ---------------------------------------------------------------- frontmatter
def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n"); body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in block.splitlines():
        if not line.strip() or ":" not in line:
            continue
        k, v = line.split(":", 1); k, v = k.strip(), v.strip()
        meta[k] = [i.strip() for i in v[1:-1].split(",") if i.strip()] if (v.startswith("[") and v.endswith("]")) else v
    return meta, body

# ---------------------------------------------------------------- 阅读时长估算
def estimate_minutes(body):
    text = re.sub(r"[#>*`\-\|\[\]\(\)!]", "", body)
    cjk = len(re.findall(r"[一-鿿]", text))
    words = len(re.findall(r"[A-Za-z0-9]+", text))
    return max(1, round(cjk / 400.0 + words / 200.0))

# ---------------------------------------------------------------- inline
def inline(text):
    codes = []
    def stash(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>"); return "\x00%d\x00" % (len(codes) - 1)
    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)
    return text

def split_row(line):
    line = line.strip()
    if line.startswith("|"): line = line[1:]
    if line.endswith("|"): line = line[:-1]
    return [c.strip() for c in line.split("|")]

# ---------------------------------------------------------------- block md → html + toc
def render_md(md):
    lines = md.splitlines(); out, toc, i, n, sec = [], [], 0, len(md.splitlines()), 0
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            buf, i = [], i + 1
            while i < n and not lines[i].startswith("```"): buf.append(html.escape(lines[i])); i += 1
            i += 1; out.append("<pre><code>" + "\n".join(buf) + "</code></pre>"); continue
        if not line.strip(): i += 1; continue
        mi = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
        if mi:
            alt, src = mi.group(1), mi.group(2)
            cap = ('<figcaption>%s</figcaption>' % inline(alt)) if alt else ""
            out.append('<figure class="diagram"><img src="%s" alt="%s">%s</figure>' % (src, html.escape(alt), cap))
            i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1)); txt = m.group(2).strip()
            if lvl == 2:
                sec += 1; hid = "sec-%d" % sec; toc.append((txt, hid))
                out.append('<h2 id="%s">%s</h2>' % (hid, inline(txt)))
            else:
                out.append("<h%d>%s</h%d>" % (lvl, inline(txt), lvl))
            i += 1; continue
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:?\-|]+\|?\s*$", lines[i + 1]) and "-" in lines[i + 1]:
            header = split_row(line); i += 2; body = []
            while i < n and "|" in lines[i] and lines[i].strip(): body.append(split_row(lines[i])); i += 1
            t = ["<table><thead><tr>"] + ["<th>%s</th>" % inline(c) for c in header] + ["</tr></thead><tbody>"]
            for row in body: t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in row) + "</tr>")
            t.append("</tbody></table>"); out.append("".join(t)); continue
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"): buf.append(lines[i].lstrip(">").strip()); i += 1
            cls = ""; m2 = re.match(r"^\[!(\w+)\]\s*(.*)$", buf[0]) if buf else None
            if m2:
                cls = ' class="callout callout-%s"' % m2.group(1).lower(); rest = m2.group(2)
                buf = ([rest] if rest else []) + buf[1:]
            out.append("<blockquote%s><p>%s</p></blockquote>" % (cls, inline(" ".join(buf)))); continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line)); tag = "ol" if ordered else "ul"
            items, base = [], None
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                indent = len(lines[i]) - len(lines[i].lstrip())
                if base is None: base = indent
                c = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]); c = re.sub(r"^\[[ xX]\]\s+", "", c)
                if indent > base and items: items[-1].setdefault("sub", []).append(c)
                else: items.append({"text": c, "sub": []})
                i += 1
            b = ["<%s>" % tag]
            for it in items:
                b.append("<li>" + inline(it["text"]))
                if it["sub"]: b.append("<ul>" + "".join("<li>%s</li>" % inline(s) for s in it["sub"]) + "</ul>")
                b.append("</li>")
            b.append("</%s>" % tag); out.append("".join(b)); continue
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|>|```|\s*([-*]|\d+\.)\s)", lines[i]) \
                and not ("|" in lines[i] and i + 1 < n and "-" in (lines[i + 1] if i + 1 < n else "") and re.match(r"^\s*\|?[\s:?\-|]+\|?\s*$", lines[i + 1])):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out), toc

# ---------------------------------------------------------------- 跨语言切换 href
def lang_switch_href(lang, prefix, rel):
    """当前 lang 的页面 rel（相对本语言根），切到另一语言的同名页面。
    zh→en：prefix + 'en/' + rel；en→zh：prefix + '../' + rel。"""
    other = "en" if lang == "zh" else "zh"
    hop = "en/" if other == "en" else "../"
    return prefix + hop + rel

# ---------------------------------------------------------------- 顶部导航 / 页脚 / shell
# 顶部横向导航用的主线短名（侧栏全称太长，横排放不下）
NAV_SHORT = {
    "a": {"zh": "产品能力", "en": "Product"},
    "b": {"zh": "工程地基", "en": "Foundations"},
    "c": {"zh": "Harness", "en": "Harness"},
    "d": {"zh": "设计模式", "en": "Patterns"},
    "e": {"zh": "上下文工程", "en": "Context"},
}

def topnav(lang, prefix, rel, active_mod=""):
    s = ['<header class="topnav"><div class="topnav-inner">']
    s.append(f'<a class="brand" href="{prefix}index.html"><span class="brand-dot"></span><span class="brand-name">{html.escape(tr(SITE_TITLE, lang))}</span></a>')
    s.append('<nav class="topnav-links">')
    for mod in MODULES:
        amod = " active" if active_mod == mod else ""
        s.append(f'<a class="tn-link{amod}" href="{prefix}module-{mod}.html">{html.escape(tr(NAV_SHORT[mod], lang))}</a>')
    aex = " active" if active_mod == "examples" else ""
    s.append(f'<a class="tn-link{aex}" href="{prefix}examples.html">{"实战" if lang=="zh" else "Cases"}</a>')
    alab = " active" if active_mod == "lab" else ""
    s.append(f'<a class="tn-link{alab}" href="{prefix}lab.html">{html.escape(tr(LAB_TITLE, lang))}</a>')
    s.append('</nav>')
    s.append('<div class="topnav-tools">')
    s.append(f'<button class="theme-toggle" id="themeToggle" type="button" aria-label="{S(lang,"theme_toggle")}" title="{S(lang,"theme_toggle")}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg></button>')
    s.append(f'<a class="lang-switch" href="{lang_switch_href(lang, prefix, rel)}" title="{S(lang,"lang_switch_title")}">{S(lang,"lang_switch")}</a>')
    s.append('</div></div></header>')
    return "".join(s)

def site_footer(lang):
    return ('<footer class="site-foot"><div class="site-foot-inner">'
            '<span class="sf-name">%s</span> · %s'
            '<span class="sf-links">%s<a href="https://github.com/libaoming" target="_blank" rel="noopener">%s</a></span>'
            '</div></footer>') % (
        html.escape(tr(AUTHOR["name"], lang)), S(lang, "build_in_public"),
        S(lang, "foot_wechat"), S(lang, "github"))

# ---------------------------------------------------------------- sidebar（保留：暂未使用，文章页系列内导航备用） / shell
def sidebar(lang, by_mod, examples, prefix, rel, active_slug="", active_mod="", home=False):
    s = ['<aside class="sidebar"><div class="sidebar-scroll">']
    s.append(f'<a class="sidebar-brand{" active" if home else ""}" href="{prefix}index.html"><span class="brand-dot"></span><span>{html.escape(tr(SITE_TITLE, lang))}</span></a>')
    s.append('<div class="sidebar-tools">')
    s.append(f'<button class="theme-toggle" id="themeToggle" type="button" aria-label="{S(lang,"theme_toggle")}" title="{S(lang,"theme_toggle")}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg></button>')
    s.append(f'<a class="lang-switch" href="{lang_switch_href(lang, prefix, rel)}" title="{S(lang,"lang_switch_title")}">{S(lang,"lang_switch")}</a>')
    s.append('</div>')
    s.append('<nav class="sidebar-nav">')
    for mod in MODULES:
        amod = " active" if active_mod == mod else ""
        s.append('<div class="nav-section">')
        s.append(f'<a class="nav-section-title{amod}" href="{prefix}module-{mod}.html"><span class="mod-badge">{mod.upper()}</span>{html.escape(tr(MODULES[mod]["name"], lang))}</a>')
        s.append("<ul>")
        for lec in by_mod[mod]:
            act = " active" if lec["slug"] == active_slug else ""
            s.append(f'<li><a class="{act.strip()}" href="{prefix}module-{mod}/{lec["slug"]}.html">{html.escape(fld(lec, "nav", lang) or fld(lec, "title", lang))}</a></li>')
        s.append("</ul></div>")
    aex = " active" if active_mod == "examples" else ""
    s.append('<div class="nav-section">')
    s.append(f'<a class="nav-section-title{aex}" href="{prefix}examples.html"><span class="mod-badge ex">{"例" if lang=="zh" else "EX"}</span>{html.escape(tr(EXAMPLES_TITLE, lang))}</a>')
    if examples:
        s.append("<ul>")
        for ex in examples:
            act = " active" if ex["slug"] == active_slug else ""
            s.append(f'<li><a class="{act.strip()}" href="{prefix}examples/{ex["slug"]}.html">{html.escape(fld(ex, "nav", lang) or fld(ex, "title", lang))}</a></li>')
        s.append("</ul>")
    else:
        s.append(f'<ul><li><span class="soon">{S(lang,"soon")}</span></li></ul>')
    s.append("</div>")
    s.append("</nav>")
    s.append('<div class="sidebar-foot"><span class="sf-name">%s</span> · %s<br>%s<a href="https://github.com/libaoming" target="_blank" rel="noopener">%s</a></div>'
             % (html.escape(tr(AUTHOR["name"], lang)), S(lang, "build_in_public"), S(lang, "foot_wechat"), S(lang, "github")))
    s.append("</div></aside>")
    return "".join(s)

def shell(lang, title, body, by_mod, examples, prefix="", rel="index.html", active_slug="", active_mod="", home=False, toc=None):
    main_cls, toc_html, stats_in_content = "main-inner", "", ""
    _site = tr(SITE_TITLE, lang)
    full_title = _site if title == _site else f"{title} · {_site}"
    if toc:
        main_cls = "main-inner with-toc"
        items = "".join('<li><a href="#%s">%s</a></li>' % (hid, html.escape(t)) for t, hid in toc)
        toc_html = f'<nav class="toc"><div class="toc-title">{S(lang,"toc_title")}</div><ul>{items}</ul>{stats_block(lang)}</nav>'
    elif not home:
        stats_in_content = stats_block(lang)
    return f'''<!DOCTYPE html>
<html lang="{S(lang,"html_lang")}"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
{THEME_HEAD_JS}
<link rel="stylesheet" href="{prefix}assets/orangebook.css">
{gc_tracking()}
</head><body>
{topnav(lang, prefix, rel, active_mod)}
<main class="main"><div class="{main_cls}">
<div class="content">{body}{stats_in_content}</div>
{toc_html}
</div></main>
{site_footer(lang)}
{THEME_BODY_JS}
</body></html>'''

# ---------------------------------------------------------------- collect
def fld(item, key, lang):
    """取 item 的某字段（zh 直取；非 zh 取 item['i18n'][lang][key]，缺则空）。"""
    if lang == "zh":
        return item.get(key, "")
    return item.get("i18n", {}).get(lang, {}).get(key, "")

def body_of(item, lang):
    if lang == "zh":
        return item["_body"]
    return item.get("i18n", {}).get(lang, {}).get("_body", "")

def minutes_of(item, lang):
    if lang == "zh":
        return item.get("minutes", 0)
    return item.get("i18n", {}).get(lang, {}).get("minutes", 0)

def has_lang(item, lang):
    return lang == "zh" or lang in item.get("i18n", {})

def _collect_dir(path, default_mod=None):
    items = []
    if not os.path.isdir(path):
        return items
    for fn in os.listdir(path):
        if not fn.endswith(".md") or fn.startswith("_") or fn.endswith(".en.md"):
            continue
        with open(os.path.join(path, fn), encoding="utf-8") as f:
            meta, body = parse_frontmatter(f.read())
        if not meta.get("title"):
            continue
        if default_mod:
            meta["module"] = meta.get("module", default_mod)
        meta["order"] = int(meta.get("order", 999))
        meta["_body"] = body
        meta["minutes"] = estimate_minutes(body)
        # 兄弟英文文件 NN-slug.en.md
        meta["i18n"] = {}
        en_path = os.path.join(path, fn[:-3] + ".en.md")
        if os.path.isfile(en_path):
            with open(en_path, encoding="utf-8") as f:
                en_meta, en_body = parse_frontmatter(f.read())
            if en_meta.get("title"):
                meta["i18n"]["en"] = {
                    "title": en_meta.get("title", ""),
                    "nav": en_meta.get("nav", ""),
                    "summary": en_meta.get("summary", ""),
                    "target": en_meta.get("target", meta.get("target", "")),
                    "_body": en_body,
                    "minutes": estimate_minutes(en_body),
                }
        items.append(meta)
    items.sort(key=lambda x: x["order"])
    return items

def collect():
    lectures = []
    for mod in MODULES:
        lectures += _collect_dir(os.path.join(CONTENT, "module-" + mod), default_mod=mod)
    lectures.sort(key=lambda x: (x["module"], x["order"]))
    examples = _collect_dir(os.path.join(CONTENT, "examples"))
    labs = _collect_dir(os.path.join(CONTENT, "lab"))
    return lectures, examples, labs

def card_tags(item, lang):
    parts = []
    lv = fld(item, "level", lang) or item.get("level", "")  # level 暂不区分语言
    if lv:
        parts.append('<span class="tag-pill tag-level">%s</span>' % html.escape(lv))
    if minutes_of(item, lang):
        parts.append('<span class="tag-pill tag-time">%s</span>' % (S(lang, "minutes") % minutes_of(item, lang)))
    return ('<span class="card-tags">%s</span>' % "".join(parts)) if parts else ""

# 每条主线一个线条图标（封面用，白描边）；同主线讲义共用图标，靠角标编号区分
MOD_ICON = {
    "a": '<circle cx="12" cy="12" r="9"/><path d="M12 12l4.5-5-2.2 6.5-6.5 2.2z"/>',
    "b": '<path d="M3 8l9-4 9 4-9 4z"/><path d="M3 12l9 4 9-4"/><path d="M3 16l9 4 9-4"/>',
    "c": '<circle cx="12" cy="12" r="3.4"/><path d="M12 3.2v3M12 17.8v3M3.2 12h3M17.8 12h3M5.9 5.9l2.1 2.1M15.9 15.9l2.1 2.1M18.1 5.9l-2.1 2.1M7.9 15.9l-2.1 2.1"/>',
    "d": '<rect x="4" y="4" width="7" height="7" rx="1.3"/><rect x="13" y="4" width="7" height="7" rx="1.3"/><rect x="4" y="13" width="7" height="7" rx="1.3"/><rect x="13" y="13" width="7" height="7" rx="1.3"/>',
    "e": '<rect x="3.5" y="5" width="17" height="14" rx="2"/><path d="M3.5 9.2h17"/>',
    "ex": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>',
    "lab": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5-9V3"/><path d="M7.5 14h9"/>',
}

# 每篇一个独特线条图标（按 slug，贴合该篇主题）；缺失回退模块级 MOD_ICON
SLUG_ICON = {
    # A 产品能力
    "five-layers": '<path d="M4 5h16M4 8.75h16M4 12.5h16M4 16.25h16M4 20h16"/>',
    "task-path": '<circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/><path d="M6.8 12h3.4M13.8 12h3.4"/>',
    "failure-nodes": '<circle cx="5" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/><path d="M6.8 12h3M14.2 12h3M10.4 9.5l3.2 5M13.6 9.5l-3.2 5"/>',
    "error-recovery": '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M17.5 3.5v3.5h-3.5"/>',
    "transparency": '<path d="M2.5 12s3.6-6 9.5-6 9.5 6 9.5 6-3.6 6-9.5 6-9.5-6-9.5-6z"/><circle cx="12" cy="12" r="2.4"/>',
    "boundary-behavior": '<path d="M12 3l7.5 3v6c0 4.3-3.2 6.9-7.5 8.5-4.3-1.6-7.5-4.2-7.5-8.5V6z"/>',
    # B 工程地基
    "harness": '<rect x="3.5" y="6" width="17" height="10" rx="2"/><circle cx="8" cy="18.5" r="1.6"/><circle cx="16" cy="18.5" r="1.6"/><path d="M4 11h16"/>',
    "context-engineering": '<path d="M4 5h16l-5.5 7v6.5l-5-2.5V12z"/>',
    "gateway": '<path d="M5 20V8a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v12"/><path d="M4 20h16M10 20v-5a2 2 0 0 1 4 0v5"/>',
    "framework-selection": '<circle cx="7" cy="5" r="1.6"/><circle cx="17" cy="5" r="1.6"/><circle cx="12" cy="20" r="1.6"/><path d="M12 18.4V12M12 12l-4.3-4.3M12 12l4.3-4.3"/>',
    "evaluation": '<path d="M4 20h16"/><rect x="5" y="12" width="3.5" height="6"/><rect x="10.25" y="7" width="3.5" height="11"/><rect x="15.5" y="14" width="3.5" height="4"/>',
    "multi-agent-platform": '<circle cx="12" cy="5" r="1.9"/><circle cx="5" cy="18" r="1.9"/><circle cx="19" cy="18" r="1.9"/><circle cx="12" cy="13" r="1.9"/><path d="M12 6.9v4.2M10.4 14.3L6.4 16.6M13.6 14.3l4 2.3"/>',
    # C Harness
    "why-agents-fail": '<path d="M12 3.5L3 19.5h18z"/><path d="M12 10v4.5M12 17v.4"/>',
    "what-is-harness": '<circle cx="12" cy="12" r="3.4"/><path d="M12 3.2v3M12 17.8v3M3.2 12h3M17.8 12h3M5.9 5.9l2.1 2.1M15.9 15.9l2.1 2.1M18.1 5.9l-2.1 2.1M7.9 15.9l-2.1 2.1"/>',
    "repo-source-of-truth": '<ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6v12c0 1.5 3.1 2.6 7 2.6s7-1.1 7-2.6V6"/><path d="M5 12c0 1.5 3.1 2.6 7 2.6s7-1.1 7-2.6"/>',
    "split-instructions": '<rect x="3.5" y="4.5" width="9" height="12" rx="1.5"/><path d="M15 9h5.5v10.5h-9V17"/>',
    "cross-session": '<rect x="3" y="9" width="9.5" height="6" rx="3"/><rect x="11.5" y="9" width="9.5" height="6" rx="3"/>',
    "wip-and-features": '<path d="M10 6h10M10 12h10M10 18h10"/><path d="M3.5 5.5l1.4 1.4 2.3-2.4M3.5 17.5l1.4 1.4 2.3-2.4M4 11.5h3.5"/>',
    "verify-and-handoff": '<path d="M3.5 12l3.2 3.2 5.3-6.4"/><path d="M13 9.5h7M20 9.5l-2.6-2.6M20 9.5l-2.6 2.6"/>',
    # D 设计模式
    "overview": '<rect x="4" y="4" width="6.5" height="6.5" rx="1.2"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.2"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.2"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.2"/>',
    "reflection-reasoning": '<path d="M18.5 11a6.5 6.5 0 1 0-1.8 5.2"/><path d="M16.5 13v3.5H20"/>',
    "learning-rag": '<rect x="4" y="5" width="9" height="12" rx="1"/><path d="M4 8h9"/><circle cx="16.5" cy="14.5" r="3.2"/><path d="M18.8 16.8L21 19"/>',
    "a2a": '<path d="M5 9h11M16 9l-3-2.5M16 9l-3 2.5"/><path d="M19 15H8M8 15l3-2.5M8 15l3 2.5"/>',
    "prioritization-exploration": '<path d="M5 6h15M5 12h10M5 18h5"/>',
    # E 上下文工程
    "context-engineering-overview": '<rect x="4" y="5" width="16" height="5.5" rx="1.2"/><rect x="4" y="13" width="16" height="5.5" rx="1.2" stroke-dasharray="2.5 2.5"/>',
    "prompt-instruction-layers": '<rect x="4" y="4.5" width="16" height="3.6" rx="1"/><rect x="4" y="10.2" width="16" height="3.6" rx="1"/><rect x="4" y="15.9" width="16" height="3.6" rx="1"/>',
    "structured-io-and-tools": '<path d="M9.5 4c-2.2 0-2 3.3-2 4.5S7.3 12 5.5 12c1.8 0 2 2.3 2 3.5s-.2 4.5 2 4.5"/><path d="M14.5 4c2.2 0 2 3.3 2 4.5s.2 3.5 2 3.5c-1.8 0-2 2.3-2 3.5s.2 4.5-2 4.5"/>',
    "memory-and-rag": '<rect x="6.5" y="6.5" width="11" height="11" rx="2"/><path d="M9.5 3v3.5M14.5 3v3.5M9.5 17.5V21M14.5 17.5V21M3 9.5h3.5M3 14.5h3.5M17.5 9.5H21M17.5 14.5H21"/>',
    "history-and-compaction": '<path d="M4 7h16M4 17h16"/><path d="M8.5 3.5l3.5 3.5 3.5-3.5M8.5 20.5l3.5-3.5 3.5 3.5"/>',
    "cache-engineering": '<path d="M13 3L5 13.5h5.5L9.5 21l8-11h-5.5z"/>',
    "observability-and-eval": '<path d="M4 4v16h16"/><path d="M7.5 14.5l3.5-4.5 3 2 4.5-6.5"/>',
    # 实战示例
    "claude-code": '<path d="M9 8l-4 4 4 4M15 8l4 4-4 4M13 6l-2 12"/>',
    "cursor": '<path d="M5 3.5l5.5 15.5 2.2-6.4 6.4-2.2z"/>',
    "vertical-aios": '<path d="M12 3v13M7.5 11.5L12 16l4.5-4.5M6 20h12"/>',
    # 实验室
    "harness-kit": '<rect x="3.5" y="6" width="17" height="9" rx="2"/><circle cx="8" cy="17.5" r="1.7"/><circle cx="16" cy="17.5" r="1.7"/><path d="M4 10.5h16"/>',
    "agent-memory-kit": '<path d="M5.5 8.5a7 7 0 0 1 12-1.5"/><path d="M18.5 15.5a7 7 0 0 1-12 1.5"/><path d="M17.5 3v3.5H14M6.5 21v-3.5H10"/>',
    "context-engineering-kit": '<rect x="4" y="4.5" width="16" height="4.3" rx="1.2"/><rect x="4" y="11" width="16" height="3" rx="1" stroke-dasharray="2.5 2.5"/><rect x="4" y="16" width="16" height="3" rx="1" stroke-dasharray="2.5 2.5"/>',
    "claude-usage": '<path d="M4 16.5a8 8 0 0 1 16 0"/><path d="M12 16.5l4.5-4"/><circle cx="12" cy="16.5" r="1.2"/>',
    "agent-skill-case-studies": '<rect x="4" y="4" width="16" height="13" rx="1.5"/><path d="M4 8h16"/><circle cx="11" cy="12.5" r="2.6"/><path d="M13 14.5L15.5 17"/>',
    "superagent-from-scratch": '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M17.5 3.5v3.5H14"/><rect x="9.4" y="9.4" width="5.2" height="5.2" rx="1"/>',
    "skill-catalog-pipeline": '<path d="M4 4.5h16L14.5 11v6.5l-5 3V11z"/><path d="M8 7.5h8"/>',
    "meet-scribe": '<rect x="9" y="3.5" width="6" height="10" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0"/><path d="M12 17.5V21M8.5 21h7"/>',
    "openknowledge-py": '<path d="M12 6.5C10 4.8 7.2 4.2 4 4.5v14c3.2-.3 6 .3 8 2 2-1.7 4.8-2.3 8-2v-14c-3.2-.3-6 .3-8 2z"/><path d="M12 6.5v14"/>',
    "voice-agent": '<path d="M6.8 3.5c.6 0 1.1.4 1.3 1l1 3.2c.2.6 0 1.2-.5 1.6l-1.5 1.2a12.5 12.5 0 0 0 6.4 6.4l1.2-1.5c.4-.5 1-.7 1.6-.5l3.2 1c.6.2 1 .7 1 1.3v2.3c0 .8-.6 1.4-1.4 1.4A16.5 16.5 0 0 1 3.5 5v-.1c0-.8.6-1.4 1.4-1.4z"/><path d="M15 7.5c1 .4 1.8 1.2 2.2 2.2M15.5 4a7 7 0 0 1 4.5 4.5"/>',
}

def icon_for(slug, mod):
    return SLUG_ICON.get(slug, MOD_ICON.get(mod, ""))

def _cover(cls, badge, inner):
    return (f'<span class="card-cover {cls}"><span class="cover-badge">{badge}</span>'
            f'<svg class="cover-icon" viewBox="0 0 24 24" fill="none" stroke="#262420" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round">{inner}</svg></span>')

def lecture_card(lec, lang, prefix=""):
    mod = lec["module"]
    return f'''<a class="card card-v" href="{prefix}module-{mod}/{lec['slug']}.html">
      {_cover(f"thumb-{mod}", f"{mod.upper()} · {lec['order']}", icon_for(lec['slug'], mod))}
      <span class="card-body">
      <span class="card-no">{html.escape(tr(NAV_SHORT[mod], lang))} · {S(lang,"lecture_no") % lec['order']}</span>
      <h3>{html.escape(fld(lec,'title',lang))}</h3>
      <p>{html.escape(fld(lec,'summary',lang))}</p>
      {card_tags(lec, lang)}
      </span>
    </a>'''

def example_card(ex, lang, prefix="", idx=0):
    tgt = html.escape(fld(ex, "target", lang) or ex.get("target", "")) if (ex.get("target") or fld(ex, "target", lang)) else ""
    label = tgt if tgt else S(lang,"example_tag")
    return f'''<a class="card card-v" href="{prefix}examples/{ex['slug']}.html">
      {_cover("thumb-ex", f'{"例" if lang=="zh" else "EX"} · {idx + 1}', icon_for(ex['slug'], "ex"))}
      <span class="card-body">
      <span class="card-no">{label}</span>
      <h3>{html.escape(fld(ex,'title',lang))}</h3>
      <p>{html.escape(fld(ex,'summary',lang))}</p>
      {card_tags(ex, lang)}
      </span>
    </a>'''

def lab_card(lab, lang, prefix="", idx=0):
    st = lab.get("status", "")
    st_label = tr(STATUS_LABEL[st], lang) if st in STATUS_LABEL else st
    return f'''<a class="card card-v" href="{prefix}lab/{lab['slug']}.html">
      {_cover("thumb-lab", f'{"研" if lang=="zh" else "LAB"} · {idx + 1}', icon_for(lab['slug'], "lab"))}
      <span class="card-body">
      <span class="card-no">{html.escape(st_label)}</span>
      <h3>{html.escape(fld(lab,'title',lang))}</h3>
      <p>{html.escape(fld(lab,'summary',lang))}</p>
      {card_tags(lab, lang)}
      </span>
    </a>'''

def out_path(lang, relpath):
    return relpath if lang == "zh" else os.path.join("en", relpath)

def write(lang, relpath, content):
    full = os.path.join(SITE, out_path(lang, relpath)); os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def article_page(lang, item, kind, siblings, by_mod, examples):
    """渲染讲义页 / 示例详情页（同模板）。kind: 'lecture' | 'example'"""
    pos = siblings.index(item)
    prev_it = siblings[pos - 1] if pos > 0 else None
    next_it = siblings[pos + 1] if pos < len(siblings) - 1 else None
    body_html, toc = render_md(body_of(item, lang))
    summary = html.escape(fld(item, "summary", lang))
    if kind == "lecture":
        mod = item["module"]
        crumb = f'<a href="../index.html">{S(lang,"crumb_home")}</a><span>/</span><a href="../module-{mod}.html">{html.escape(tr(MODULES[mod]["name"], lang))}</a>'
        meta_line = S(lang, "meta_lecture") % (mod.upper(), item["order"])
        active_mod = mod; subdir = "module-%s" % mod
    elif kind == "example":
        crumb = f'<a href="../index.html">{S(lang,"crumb_home")}</a><span>/</span><a href="../examples.html">{html.escape(tr(EXAMPLES_TITLE, lang))}</a>'
        tgt = fld(item, "target", lang) or item.get("target", "")
        meta_line = (S(lang, "meta_example_target") % html.escape(tgt)) if tgt else S(lang, "meta_example")
        active_mod = "examples"; subdir = "examples"
    else:  # lab
        crumb = f'<a href="../index.html">{S(lang,"crumb_home")}</a><span>/</span><a href="../lab.html">{html.escape(tr(LAB_TITLE, lang))}</a>'
        st = item.get("status", ""); st_label = tr(STATUS_LABEL[st], lang) if st in STATUS_LABEL else st
        meta_line = ("%s · %s" % (S(lang, "meta_lab"), html.escape(st_label))) if st_label else S(lang, "meta_lab")
        active_mod = "lab"; subdir = "lab"
    art = ['<article class="lecture">', f'<div class="breadcrumb">{crumb}</div>', f'<h1>{html.escape(fld(item,"title",lang))}</h1>']
    if summary:
        art.append(f'<p class="summary">{summary}</p>')
    badges = ""
    lv = item.get("level", "")
    if lv:
        badges += '<span class="tag-pill tag-level">%s</span>' % html.escape(lv)
    if minutes_of(item, lang):
        badges += '<span class="tag-pill tag-time">%s</span>' % (S(lang, "minutes") % minutes_of(item, lang))
    art.append(f'<p class="meta">{meta_line}{badges}</p>')
    if kind == "lab":
        links = []
        repo = item.get("repo", "")
        if repo:
            links.append(f'<a class="lab-link" href="{html.escape(repo)}" target="_blank" rel="noopener">{S(lang,"lab_repo")} &#8599;</a>')
        rl = item.get("related_lecture", "")
        if rl and rl in MODULES:
            links.append(f'<a class="lab-link" href="../module-{rl}.html">{S(lang,"lab_related")} · {html.escape(tr(MODULES[rl]["name"], lang))}</a>')
        if links:
            art.append(f'<div class="lab-links"><span class="lab-links-t">{S(lang,"lab_links_title")}</span>{"".join(links)}</div>')
    art.append(body_html)
    pager = ['<div class="pager">']
    pager.append(f'<a class="prev" href="{prev_it["slug"]}.html"><span class="dir">{S(lang,"prev")}</span><span class="ttl">{html.escape(fld(prev_it,"nav",lang) or fld(prev_it,"title",lang))}</span></a>' if prev_it else '<span class="spacer"></span>')
    pager.append(f'<a class="next" href="{next_it["slug"]}.html"><span class="dir">{S(lang,"next")}</span><span class="ttl">{html.escape(fld(next_it,"nav",lang) or fld(next_it,"title",lang))}</span></a>' if next_it else '<span class="spacer"></span>')
    pager.append("</div>"); art.append("".join(pager)); art.append("</article>")
    rel = "%s/%s.html" % (subdir, item["slug"])
    write(lang, rel,
          shell(lang, fld(item, "title", lang), "\n".join(art), by_mod, examples, prefix="../", rel=rel, active_slug=item["slug"], active_mod=active_mod, toc=toc))

# ---------------------------------------------------------------- build
def build_lang(lang, lectures, examples, labs):
    # 按语言过滤：只渲染有该语言版本的讲义/示例/实验室项目
    by_mod = {m: [] for m in MODULES}
    langs_lectures = [l for l in lectures if has_lang(l, lang)]
    for lec in langs_lectures:
        by_mod[lec["module"]].append(lec)
    langs_examples = [e for e in examples if has_lang(e, lang)]
    langs_labs = [x for x in labs if has_lang(x, lang)]

    # 首页（博客流：hero 双栏[左定位 + 右主线入口] + 按主线分组的卡片网格）
    home = [f'''<section class="bloghero">
      <div class="bloghero-l">
        <span class="eyebrow">{S(lang,"landing_eyebrow")}</span>
        <h1>{S(lang,"landing_h1")}</h1>
        <p class="lead">{S(lang,"landing_lead")}</p>
        <div class="hero-actions">{support_block(lang, "")}</div>
      </div>
      <nav class="bloghero-r">''']
    for mod in MODULES:
        home.append(f'<a class="thread-link" href="module-{mod}.html">{html.escape(tr(MODULES[mod]["name"], lang))}<span class="arr">&#8594;</span></a>')
    home.append(f'<a class="thread-link" href="examples.html">{html.escape(tr(EXAMPLES_TITLE, lang))}<span class="arr">&#8594;</span></a>')
    home.append(f'<a class="thread-link" href="lab.html">{html.escape(tr(LAB_TITLE, lang))}<span class="arr">&#8594;</span></a>')
    # 独立板块入口（standalone/，只在根域名下，故用绝对路径兼容 /en/）
    learn_ai_label = "Learn AI · 模型硬功底" if lang == "zh" else "Learn AI · Model Fundamentals (Chinese)"
    ai_bible_label = "AI 圣经 · 18 篇论文精读" if lang == "zh" else "AI Bible · 18 Papers (Chinese)"
    home.append(f'<a class="thread-link" href="/learn-ai/">{learn_ai_label}<span class="arr">&#8594;</span></a>')
    home.append(f'<a class="thread-link" href="/ai-bible/">{ai_bible_label}<span class="arr">&#8594;</span></a>')
    home.append('</nav></section>')
    home.append(author_block(lang))
    for mod in MODULES:
        info = MODULES[mod]; count = len(by_mod[mod])
        home.append(f'<h2 class="home-sec"><span class="mod-badge">{mod.upper()}</span>{html.escape(tr(info["name"], lang))}<span class="sec-count">{S(lang,"sec_count_lec") % count}</span></h2>')
        home.append('<div class="card-grid">')
        for lec in by_mod[mod][:3]:
            home.append(lecture_card(lec, lang, prefix=""))
        home.append("</div>")
        if count > 3:
            home.append(f'<a class="see-all" href="module-{mod}.html">{S(lang,"see_all") % count}</a>')
    home.append(f'<h2 class="home-sec"><span class="mod-badge ex">{"例" if lang=="zh" else "EX"}</span>{html.escape(tr(EXAMPLES_TITLE, lang))}<span class="sec-count">{S(lang,"sec_count_ex") % len(langs_examples)}</span></h2>')
    if langs_examples:
        home.append('<div class="card-grid">')
        for i, ex in enumerate(langs_examples):
            home.append(example_card(ex, lang, prefix="", idx=i))
        home.append("</div>")
    else:
        home.append(f'<p class="soon-note">{S(lang,"soon_note")}</p>')
    # 首页 · 实验室精选（克制：精选前 3 + 全部）
    home.append(f'<h2 class="home-sec"><span class="mod-badge lab">{"研" if lang=="zh" else "LAB"}</span>{html.escape(tr(LAB_TITLE, lang))}<span class="sec-count">{S(lang,"sec_count_lab") % len(langs_labs)}</span></h2>')
    if langs_labs:
        home.append('<div class="card-grid">')
        for i, lab in enumerate(langs_labs[:3]):
            home.append(lab_card(lab, lang, prefix="", idx=i))
        home.append("</div>")
        if len(langs_labs) > 3:
            home.append(f'<a class="see-all" href="lab.html">{S(lang,"see_all_lab") % len(langs_labs)}</a>')
    else:
        home.append(f'<p class="soon-note">{S(lang,"lab_soon")}</p>')
    write(lang, "index.html", shell(lang, tr(SITE_TITLE, lang), "\n".join(home), by_mod, langs_examples, prefix="", rel="index.html", home=True))

    # 模块页（含模块导语）
    for mod in MODULES:
        info = MODULES[mod]
        intro_html, _ = render_md(tr(info.get("intro", ""), lang))
        page = [f'<div class="page-head"><span class="mod-badge big">{mod.upper()}</span><h1>{html.escape(tr(info["name"], lang))}</h1><p class="lead">{html.escape(tr(info["desc"], lang))}</p></div>']
        if intro_html:
            page.append(f'<div class="module-intro">{intro_html}</div>')
        page.append(f'<h2 class="list-head">{S(lang,"list_head")}</h2><div class="card-grid">')
        for lec in by_mod[mod]:
            page.append(lecture_card(lec, lang, prefix=""))
        page.append("</div>")
        rel = "module-%s.html" % mod
        write(lang, rel, shell(lang, tr(info["name"], lang), "\n".join(page), by_mod, langs_examples, prefix="", rel=rel, active_mod=mod))

    # 实战示例列表页
    intro_html, _ = render_md(tr(EXAMPLES_INTRO, lang))
    exp = [f'<div class="page-head"><span class="mod-badge big ex">{"例" if lang=="zh" else "EX"}</span><h1>{html.escape(tr(EXAMPLES_TITLE, lang))}</h1></div>',
           f'<div class="module-intro">{intro_html}</div>']
    if langs_examples:
        exp.append(f'<h2 class="list-head">{S(lang,"list_head") if lang=="en" else "示例"}</h2><div class="card-grid">')
        for i, ex in enumerate(langs_examples):
            exp.append(example_card(ex, lang, prefix="", idx=i))
        exp.append("</div>")
    else:
        exp.append(f'<p class="soon-note">{S(lang,"examples_soon")}</p>')
    write(lang, "examples.html", shell(lang, tr(EXAMPLES_TITLE, lang), "\n".join(exp), by_mod, langs_examples, prefix="", rel="examples.html", active_mod="examples"))

    # 实验室列表页
    intro_html, _ = render_md(tr(LAB_INTRO, lang))
    labp = [f'<div class="page-head"><span class="mod-badge big lab">{"研" if lang=="zh" else "LAB"}</span><h1>{html.escape(tr(LAB_TITLE, lang))}</h1></div>',
            f'<div class="module-intro">{intro_html}</div>']
    if langs_labs:
        labp.append(f'<h2 class="list-head">{S(lang,"list_head") if lang=="en" else "项目"}</h2><div class="card-grid">')
        for i, lab in enumerate(langs_labs):
            labp.append(lab_card(lab, lang, prefix="", idx=i))
        labp.append("</div>")
    else:
        labp.append(f'<p class="soon-note">{S(lang,"lab_soon")}</p>')
    write(lang, "lab.html", shell(lang, tr(LAB_TITLE, lang), "\n".join(labp), by_mod, langs_examples, prefix="", rel="lab.html", active_mod="lab"))

    # 讲义详情
    for lec in langs_lectures:
        article_page(lang, lec, "lecture", by_mod[lec["module"]], by_mod, langs_examples)
    # 示例详情
    for ex in langs_examples:
        article_page(lang, ex, "example", langs_examples, by_mod, langs_examples)
    # 实验室详情
    for lab in langs_labs:
        article_page(lang, lab, "lab", langs_labs, by_mod, langs_examples)

    return len(langs_lectures), len(langs_examples), len(langs_labs)

def build():
    if os.path.isdir(SITE): shutil.rmtree(SITE)
    os.makedirs(SITE)
    # assets 给每种语言各复制一份（en 放 site/en/assets），避免相对前缀复杂化
    shutil.copytree(ASSETS, os.path.join(SITE, "assets"))
    shutil.copytree(ASSETS, os.path.join(SITE, "en", "assets"))

    # 框架图英文化：源 assets/diagrams/x.en.svg = 英文版。
    # 英文站用 x.en.svg 覆盖同名 x.svg；中英两站都删掉 .en.svg 源（无人引用，避免冗余）。
    en_dg = os.path.join(SITE, "en", "assets", "diagrams")
    if os.path.isdir(en_dg):
        for fn in os.listdir(en_dg):
            if fn.endswith(".en.svg"):
                shutil.copyfile(os.path.join(en_dg, fn), os.path.join(en_dg, fn[:-7] + ".svg"))
    for d in (os.path.join(SITE, "assets", "diagrams"), en_dg):
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".en.svg"): os.remove(os.path.join(d, fn))

    lectures, examples, labs = collect()
    counts = {}
    for lang in LANGS:
        counts[lang] = build_lang(lang, lectures, examples, labs)

    # GitHub Pages 自定义域名：仅根目录写一次 CNAME
    if SITE_DOMAIN:
        with open(os.path.join(SITE, "CNAME"), "w", encoding="utf-8") as f:
            f.write(SITE_DOMAIN + "\n")

    # 独立板块：standalone/<name>/ 整目录原样发布到 site/<name>/（= chengyansuo.com/<name>/）。
    # 绕开 markdown 渲染，用于「Learn AI」等自带交互(playground/quiz)的成品 HTML 课线。
    # 注意：site 在 build 开头已 rmtree，这里在最后复制，故 standalone 内容不会被清掉。
    STANDALONE = os.path.join(ROOT, "standalone")
    if os.path.isdir(STANDALONE):
        for name in sorted(os.listdir(STANDALONE)):
            src = os.path.join(STANDALONE, name)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(SITE, name))
                print("standalone published: site/%s/" % name)

    for lang in LANGS:
        print("build done [%s]: %d lectures + %d examples + %d labs" % (lang, counts[lang][0], counts[lang][1], counts[lang][2]))
    print("site/ ready (zh → /, en → /en/)")
    return counts

if __name__ == "__main__":
    build()
