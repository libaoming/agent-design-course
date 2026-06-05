#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — content/**/*.md → site/ 纯静态多页站。
左侧边栏导航（模块讲义 + 实战示例）+ 右侧 TOC，Claude Code 文档调性。零三方依赖。"""

import os, re, shutil, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
ASSETS = os.path.join(ROOT, "assets")
SITE = os.path.join(ROOT, "site")

SITE_TITLE = "Learn Agent Design"
SITE_TAGLINE = "把 Agent 学习笔记，重写成一门可讲、可查、可分享的公开课"

MODULES = {
    "a": {
        "name": "Agent 产品与能力设计",
        "desc": "以 L3 五维能力为主轴，技术地基五层做底座。讲「怎么设计与评估一个 Agent」。",
        "intro": (
            "本模块回答一个问题：**怎么把一个 Agent 当成产品来设计和评估？**\n\n"
            "主轴是评估一个 Agent 能力的五个维度——任务完成路径、失败节点、错误恢复、透明度、边界行为；"
            "底座是理解 Agent 怎么跑起来的技术地基五层（Loop / Tool / Planning / Memory / Multi-Agent）。"
            "学完你会拿到一套**可拆分、可埋点、可定 KPI** 的语言：把模糊的「这个 Agent 好不好用」拆成具体维度，逐项设计、逐项度量。\n\n"
            "**讲次编排**：先用第 0 讲的五层架构建立底座（定位问题在哪一层），再沿五维逐讲展开——前四维层层递进（能不能做完 → 在哪失败 → 失败怎么恢复 → 过程透不透明），最后落到边界行为（该不该做）。\n\n"
            "**适合**：想转型 / 进阶到 Agent 方向的产品经理、模型策略 PM，以及想要「产品评估视角」的工程师。"
        ),
    },
    "b": {
        "name": "Agent 工程地基",
        "desc": "Harness、Gateway、上下文工程、评测、框架选型。讲「怎么让 Agent 可靠地跑起来」。",
        "intro": (
            "本模块回答另一个问题：**怎么让一个 Agent 在生产环境里可靠地跑起来？**\n\n"
            "核心理念一句话——模型是司机，工程基础设施才是车。模型能力商品化之后，护城河上移到 Harness、上下文工程和数据飞轮。"
            "本模块从 Harness 总纲出发，依次讲上下文工程（最稀缺的资源怎么管）、Gateway（生产底盘）、框架选型（别默认上 LangGraph）、评测体系（别拍脑袋迭代）、多 Agent 平台（按瓶颈而非想象演进）。\n\n"
            "**讲次编排**：第 0 讲 Harness 是总纲（先修车再换司机），其后五讲分别对应一个工程子系统，每讲都遵循「不修这块会怎样 → 框架 → 怎么落地」。\n\n"
            "**适合**：做 Agent 应用的工程师、独立开发者，以及想补「工程地基认知」的 PM。"
        ),
    },
    "c": {
        "name": "Harness 工程",
        "desc": "让 Agent 可靠地跑完长任务的工程方法论。以 walkinglabs《Harness Engineering》为骨架，融合一套真实项目里跑出来的实战做法。",
        "intro": (
            "本模块回答最后一个问题：**怎么让一个 Agent 可靠地跑完一个需要很多步、跨很多次会话的长任务？**\n\n"
            "核心命题是——模型能力是常数，能不能交付是 harness 的函数。同一个模型，裸跑失败，套上完整 harness 就成功；成功率能从两成爬到接近满分，而模型一行没动。"
            "本模块以 walkinglabs《Harness Engineering》的框架为骨架，融合一套在真实项目里跑出来的实战方法论：features.json 单一事实源、STATUS + 里程碑三件套、线性切片、fixture 先于代码、4 层防御体系、上下文隔离子 agent。\n\n"
            "**讲次编排**：先立靶（为什么能力强的 Agent 仍失败）→ 给定义（harness 到底是什么）→ 逐个子系统展开（仓库即事实源 / 指令拆分 / 跨会话连续 / 边界与 feature list / 端到端验证与干净交接）。\n\n"
            "**适合**：要让 Agent 干真活、跑长任务的工程师和 PM——其实你正在读的这门课，本身就是用这套方法论做出来的。"
        ),
    },
    "d": {
        "name": "Agent 设计模式（21 式）",
        "desc": "Google《Agentic Design Patterns》21 个核心模式的中文精炼。一本「遇到这类问题用哪个套路」的模式食谱，补全前三个模块的盲区。",
        "intro": (
            "前三个模块分别按「能力维度」「工程地基」「harness 方法论」切；本模块换一把刀——按 **21 个可复用的实现模式**切，是一本「遇到这类问题，用哪个套路」的食谱。\n\n"
            "来源是 Google 的《Agentic Design Patterns》（Antonio Gulli），这里取其中文精炼（参考 xindoo 的翻译项目）。21 个模式可归成 6 组：基础执行 / 质量与安全 / 记忆与知识 / 协作与互联 / 控制与治理 / 推理与探索。\n\n"
            "**讲次编排**：第 0 讲是**全景地图**——把 21 个模式一次铺开、归组、并标注「本课前三模块讲过没」；其后几讲**只深入前三模块的盲区模式**（反思、学习与适应、知识检索 RAG、智能体间通信 A2A、推理技术、优先级与探索），不重复已讲的工具/规划/记忆/异常/安全/评测。\n\n"
            "**适合**：想要一份「招式速查」的人——知道遇到某类问题，业界有哪些成型套路可选。"
        ),
    },
}

EXAMPLES_TITLE = "实战示例"
EXAMPLES_INTRO = (
    "光有框架还不够。这一区用前两个模块的框架，去**拆解真实的 Agent 产品**——"
    "看抽象的五维、五层、Harness，在 Claude Code、Cursor 这些产品里到底长什么样。"
    "每个示例都是一次「拿着透镜看真实世界」的练习：框架是怎么从一个真实产品里被验证、被修正的。"
)

# 访问统计（GoatCounter）——goatcounter.com 注册后把站点 code 填进 GC_CODE（如 "learn-agent-design"）。
# 留空 = 不渲染任何统计 UI / 不接入任何第三方脚本，站点照常工作。
GC_CODE = "learn-agent-design"

def gc_tracking():
    return ('<script data-goatcounter="https://%s.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>' % GC_CODE) if GC_CODE else ""

def stats_block():
    if not GC_CODE:
        return ""
    return ('<div class="learn-stats" id="learnStats" hidden>'
            '<span class="dot"></span>已有 <strong id="gcU">·</strong> 人学过本课程 · <span id="gcV">·</span> 次阅读</div>'
            '<script>fetch("https://%s.goatcounter.com/counter/TOTAL.json")'
            '.then(function(r){return r.ok?r.json():Promise.reject()})'
            '.then(function(d){document.getElementById("gcU").textContent=d.count_unique;'
            'document.getElementById("gcV").textContent=d.count;'
            'document.getElementById("learnStats").hidden=false})'
            '.catch(function(){})</script>') % GC_CODE

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
    lines = md.splitlines(); out, toc, i, n, sec = [], [], 0, len(lines), 0
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

# ---------------------------------------------------------------- sidebar / shell
def sidebar(by_mod, examples, prefix, active_slug="", active_mod="", home=False):
    s = ['<aside class="sidebar"><div class="sidebar-scroll">']
    s.append(f'<a class="sidebar-brand{" active" if home else ""}" href="{prefix}index.html"><span class="brand-dot"></span><span>{SITE_TITLE}</span></a>')
    s.append('<nav class="sidebar-nav">')
    for mod in ("a", "b", "c", "d"):
        amod = " active" if active_mod == mod else ""
        s.append('<div class="nav-section">')
        s.append(f'<a class="nav-section-title{amod}" href="{prefix}module-{mod}.html"><span class="mod-badge">{mod.upper()}</span>{html.escape(MODULES[mod]["name"])}</a>')
        s.append("<ul>")
        for lec in by_mod[mod]:
            act = " active" if lec["slug"] == active_slug else ""
            s.append(f'<li><a class="{act.strip()}" href="{prefix}module-{mod}/{lec["slug"]}.html">{html.escape(lec.get("nav", lec["title"]))}</a></li>')
        s.append("</ul></div>")
    # 实战示例区
    aex = " active" if active_mod == "examples" else ""
    s.append('<div class="nav-section">')
    s.append(f'<a class="nav-section-title{aex}" href="{prefix}examples.html"><span class="mod-badge ex">例</span>{EXAMPLES_TITLE}</a>')
    if examples:
        s.append("<ul>")
        for ex in examples:
            act = " active" if ex["slug"] == active_slug else ""
            s.append(f'<li><a class="{act.strip()}" href="{prefix}examples/{ex["slug"]}.html">{html.escape(ex.get("nav", ex["title"]))}</a></li>')
        s.append("</ul>")
    else:
        s.append('<ul><li><span class="soon">筹备中</span></li></ul>')
    s.append("</div>")
    s.append("</nav></div></aside>")
    return "".join(s)

def shell(title, body, by_mod, examples, prefix="", active_slug="", active_mod="", home=False, toc=None):
    main_cls, toc_html, stats_in_content = "main-inner", "", ""
    if toc:
        main_cls = "main-inner with-toc"
        items = "".join('<li><a href="#%s">%s</a></li>' % (hid, html.escape(t)) for t, hid in toc)
        toc_html = f'<nav class="toc"><div class="toc-title">本页目录</div><ul>{items}</ul>{stats_block()}</nav>'
    elif not home:
        stats_in_content = stats_block()
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{prefix}assets/orangebook.css">
{gc_tracking()}
</head><body>
<div class="layout">
{sidebar(by_mod, examples, prefix, active_slug, active_mod, home)}
<main class="main"><div class="{main_cls}">
<div class="content">{body}{stats_in_content}</div>
{toc_html}
</div></main>
</div>
</body></html>'''

# ---------------------------------------------------------------- collect
def _collect_dir(path, default_mod=None):
    items = []
    if not os.path.isdir(path):
        return items
    for fn in os.listdir(path):
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        with open(os.path.join(path, fn), encoding="utf-8") as f:
            meta, body = parse_frontmatter(f.read())
        if not meta.get("title"):
            continue
        if default_mod:
            meta["module"] = meta.get("module", default_mod)
        meta["order"] = int(meta.get("order", 999))
        meta["_body"] = body
        items.append(meta)
    items.sort(key=lambda x: x["order"])
    return items

def collect():
    lectures = []
    for mod in ("a", "b", "c", "d"):
        lectures += _collect_dir(os.path.join(CONTENT, "module-" + mod), default_mod=mod)
    lectures.sort(key=lambda x: (x["module"], x["order"]))
    examples = _collect_dir(os.path.join(CONTENT, "examples"))
    return lectures, examples

def lecture_card(lec, prefix=""):
    mod = lec["module"]
    return f'''<a class="card" href="{prefix}module-{mod}/{lec['slug']}.html">
      <span class="card-no">第 {lec['order']} 讲</span>
      <h3>{html.escape(lec['title'])}</h3>
      <p>{html.escape(lec.get('summary',''))}</p>
    </a>'''

def example_card(ex, prefix=""):
    tgt = html.escape(ex.get("target", "")) if ex.get("target") else ""
    badge = f'<span class="card-no">{tgt}</span>' if tgt else '<span class="card-no">实战示例</span>'
    return f'''<a class="card" href="{prefix}examples/{ex['slug']}.html">
      {badge}
      <h3>{html.escape(ex['title'])}</h3>
      <p>{html.escape(ex.get('summary',''))}</p>
    </a>'''

def write(relpath, content):
    full = os.path.join(SITE, relpath); os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def article_page(item, kind, siblings, by_mod, examples):
    """渲染讲义页 / 示例详情页（同模板）。kind: 'lecture' | 'example'"""
    pos = siblings.index(item)
    prev_it = siblings[pos - 1] if pos > 0 else None
    next_it = siblings[pos + 1] if pos < len(siblings) - 1 else None
    body_html, toc = render_md(item["_body"])
    summary = html.escape(item.get("summary", ""))
    if kind == "lecture":
        mod = item["module"]
        crumb = f'<a href="../index.html">首页</a><span>/</span><a href="../module-{mod}.html">{html.escape(MODULES[mod]["name"])}</a>'
        meta_line = f'Module {mod.upper()} · 第 {item["order"]} 讲'
        active_mod = mod; subdir = "module-%s" % mod
    else:
        crumb = f'<a href="../index.html">首页</a><span>/</span><a href="../examples.html">{EXAMPLES_TITLE}</a>'
        meta_line = "实战示例" + (f' · 拆解对象：{html.escape(item["target"])}' if item.get("target") else "")
        active_mod = "examples"; subdir = "examples"
    art = ['<article class="lecture">', f'<div class="breadcrumb">{crumb}</div>', f'<h1>{html.escape(item["title"])}</h1>']
    if summary:
        art.append(f'<p class="summary">{summary}</p>')
    art.append(f'<p class="meta">{meta_line}</p>')
    art.append(body_html)
    pager = ['<div class="pager">']
    pager.append(f'<a class="prev" href="{prev_it["slug"]}.html"><span class="dir">← 上一篇</span><span class="ttl">{html.escape(prev_it.get("nav", prev_it["title"]))}</span></a>' if prev_it else '<span class="spacer"></span>')
    pager.append(f'<a class="next" href="{next_it["slug"]}.html"><span class="dir">下一篇 →</span><span class="ttl">{html.escape(next_it.get("nav", next_it["title"]))}</span></a>' if next_it else '<span class="spacer"></span>')
    pager.append("</div>"); art.append("".join(pager)); art.append("</article>")
    write(os.path.join(subdir, item["slug"] + ".html"),
          shell(item["title"], "\n".join(art), by_mod, examples, prefix="../", active_slug=item["slug"], active_mod=active_mod, toc=toc))

# ---------------------------------------------------------------- build
def build():
    if os.path.isdir(SITE): shutil.rmtree(SITE)
    os.makedirs(SITE); shutil.copytree(ASSETS, os.path.join(SITE, "assets"))

    lectures, examples = collect()
    by_mod = {"a": [], "b": [], "c": [], "d": []}
    for lec in lectures:
        by_mod[lec["module"]].append(lec)

    # 首页
    home = [f'''<div class="hero">
      <span class="eyebrow">A Course on Building Agents</span>
      <h1>学会<em>设计</em>与<em>工程化</em>一个 Agent</h1>
      <p class="lead">{html.escape(SITE_TAGLINE)}。两条主线：把 Agent 当产品来设计，把 Agent 当系统来交付。</p>
      {stats_block()}
    </div>''']
    for mod in ("a", "b", "c", "d"):
        info = MODULES[mod]; count = len(by_mod[mod])
        home.append(f'<h2 class="home-sec"><span class="mod-badge">{mod.upper()}</span>{html.escape(info["name"])}<span class="sec-count">{count} 讲</span></h2>')
        home.append(f'<p class="home-desc">{html.escape(info["desc"])}</p>')
        home.append('<div class="card-list">')
        for lec in by_mod[mod]:
            home.append(lecture_card(lec, prefix=""))
        home.append("</div>")
    home.append(f'<h2 class="home-sec"><span class="mod-badge ex">例</span>{EXAMPLES_TITLE}<span class="sec-count">{len(examples)} 篇</span></h2>')
    home.append(f'<p class="home-desc">{html.escape("用框架拆解真实 Agent 产品")}</p>')
    if examples:
        home.append('<div class="card-list">')
        for ex in examples:
            home.append(example_card(ex, prefix=""))
        home.append("</div>")
    else:
        home.append('<p class="soon-note">实战示例筹备中。</p>')
    write("index.html", shell(SITE_TITLE, "\n".join(home), by_mod, examples, prefix="", home=True))

    # 模块页（含模块导语）
    for mod in ("a", "b", "c", "d"):
        info = MODULES[mod]
        intro_html, _ = render_md(info.get("intro", ""))
        page = [f'<div class="page-head"><span class="mod-badge big">{mod.upper()}</span><h1>{html.escape(info["name"])}</h1><p class="lead">{html.escape(info["desc"])}</p></div>']
        if intro_html:
            page.append(f'<div class="module-intro">{intro_html}</div>')
        page.append('<h2 class="list-head">讲次</h2><div class="card-list">')
        for lec in by_mod[mod]:
            page.append(lecture_card(lec, prefix=""))
        page.append("</div>")
        write("module-%s.html" % mod, shell(info["name"], "\n".join(page), by_mod, examples, prefix="", active_mod=mod))

    # 实战示例列表页
    intro_html, _ = render_md(EXAMPLES_INTRO)
    exp = [f'<div class="page-head"><span class="mod-badge big ex">例</span><h1>{EXAMPLES_TITLE}</h1></div>',
           f'<div class="module-intro">{intro_html}</div>']
    if examples:
        exp.append('<h2 class="list-head">示例</h2><div class="card-list">')
        for ex in examples:
            exp.append(example_card(ex, prefix=""))
        exp.append("</div>")
    else:
        exp.append('<p class="soon-note">实战示例筹备中，敬请期待。</p>')
    write("examples.html", shell(EXAMPLES_TITLE, "\n".join(exp), by_mod, examples, prefix="", active_mod="examples"))

    # 讲义详情
    for lec in lectures:
        article_page(lec, "lecture", by_mod[lec["module"]], by_mod, examples)
    # 示例详情
    for ex in examples:
        article_page(ex, "example", examples, by_mod, examples)

    print("build done: %d lectures + %d examples, site/ ready" % (len(lectures), len(examples)))
    return len(lectures), len(examples)

if __name__ == "__main__":
    build()
