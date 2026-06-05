#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — 把 content/**/*.md 渲染成 site/ 下的纯静态 HTML 多页站。
左侧边栏导航 + 右侧本页目录，Claude Code 文档式调性。零三方依赖。"""

import os, re, shutil, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
ASSETS = os.path.join(ROOT, "assets")
SITE = os.path.join(ROOT, "site")

SITE_TITLE = "Learn Agent Design"
SITE_TAGLINE = "把 Agent 学习笔记，重写成一门可讲、可查、可分享的公开课"
MODULES = {
    "a": {"name": "Agent 产品与能力设计",
          "desc": "以 L3 五维能力为主轴（任务路径 / 失败节点 / 错误恢复 / 透明度 / 边界行为），技术地基五层做底座。讲「怎么设计与评估一个 Agent」。"},
    "b": {"name": "Agent 工程地基",
          "desc": "Harness 工程、Gateway 工程、上下文工程七维、评测体系、框架选型。讲「怎么让 Agent 可靠地跑起来」。"},
}

# ----------------------------------------------------------------------------
# frontmatter 解析（YAML 子集）
# ----------------------------------------------------------------------------
def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in block.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [i.strip() for i in val[1:-1].split(",") if i.strip()]
        else:
            meta[key] = val
    return meta, body

# ----------------------------------------------------------------------------
# 行内
# ----------------------------------------------------------------------------
def inline(text):
    codes = []
    def stash(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return "\x00%d\x00" % (len(codes) - 1)
    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)
    return text

def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]

# ----------------------------------------------------------------------------
# 块级 markdown → HTML，附带 h2 目录（TOC）收集
# ----------------------------------------------------------------------------
def render_md(md):
    lines = md.splitlines()
    out, toc, i, n, sec = [], [], 0, len(lines), 0
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            buf, i = [], i + 1
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i])); i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        if not line.strip():
            i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1)); txt = m.group(2).strip()
            if lvl == 2:
                sec += 1; hid = "sec-%d" % sec
                toc.append((txt, hid))
                out.append('<h2 id="%s">%s</h2>' % (hid, inline(txt)))
            else:
                out.append("<h%d>%s</h%d>" % (lvl, inline(txt), lvl))
            i += 1; continue
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:?\-|]+\|?\s*$", lines[i + 1]) and "-" in lines[i + 1]:
            header = split_row(line); i += 2; body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(split_row(lines[i])); i += 1
            t = ["<table><thead><tr>"] + ["<th>%s</th>" % inline(c) for c in header] + ["</tr></thead><tbody>"]
            for row in body:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in row) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t)); continue
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip()); i += 1
            cls = ""
            m2 = re.match(r"^\[!(\w+)\]\s*(.*)$", buf[0]) if buf else None
            if m2:
                cls = ' class="callout callout-%s"' % m2.group(1).lower(); rest = m2.group(2)
                buf = ([rest] if rest else []) + buf[1:]
            out.append("<blockquote%s><p>%s</p></blockquote>" % (cls, inline(" ".join(buf))))
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items, base_indent = [], None
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                indent = len(lines[i]) - len(lines[i].lstrip())
                if base_indent is None:
                    base_indent = indent
                content = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                content = re.sub(r"^\[[ xX]\]\s+", "", content)
                if indent > base_indent and items:
                    items[-1].setdefault("sub", []).append(content)
                else:
                    items.append({"text": content, "sub": []})
                i += 1
            buf = ["<%s>" % tag]
            for it in items:
                buf.append("<li>" + inline(it["text"]))
                if it["sub"]:
                    buf.append("<ul>" + "".join("<li>%s</li>" % inline(s) for s in it["sub"]) + "</ul>")
                buf.append("</li>")
            buf.append("</%s>" % tag)
            out.append("".join(buf)); continue
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|>|```|\s*([-*]|\d+\.)\s)", lines[i]) \
                and not ("|" in lines[i] and i + 1 < n and "-" in (lines[i + 1] if i + 1 < n else "") and re.match(r"^\s*\|?[\s:?\-|]+\|?\s*$", lines[i + 1])):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out), toc

# ----------------------------------------------------------------------------
# 侧边栏 + 页面外壳
# ----------------------------------------------------------------------------
def sidebar(by_mod, prefix, active_slug="", active_mod="", home=False):
    s = [f'<aside class="sidebar"><div class="sidebar-scroll">']
    s.append(f'<a class="sidebar-brand{" active" if home else ""}" href="{prefix}index.html"><span class="brand-dot"></span><span>{SITE_TITLE}</span></a>')
    s.append('<nav class="sidebar-nav">')
    for mod in ("a", "b"):
        amod = " active" if active_mod == mod else ""
        s.append(f'<div class="nav-section">')
        s.append(f'<a class="nav-section-title{amod}" href="{prefix}module-{mod}.html"><span class="mod-badge">{mod.upper()}</span>{html.escape(MODULES[mod]["name"])}</a>')
        if by_mod[mod]:
            s.append("<ul>")
            for lec in by_mod[mod]:
                act = " active" if lec["slug"] == active_slug else ""
                label = html.escape(lec.get("nav", lec["title"]))
                s.append(f'<li><a class="{act.strip()}" href="{prefix}module-{mod}/{lec["slug"]}.html">{label}</a></li>')
            s.append("</ul>")
        else:
            s.append('<ul><li><span class="soon">筹备中</span></li></ul>')
        s.append("</div>")
    s.append("</nav></div></aside>")
    return "".join(s)

def shell(title, body, by_mod, prefix="", active_slug="", active_mod="", home=False, toc=None):
    toc_html = ""
    main_cls = "main-inner"
    if toc:
        main_cls = "main-inner with-toc"
        items = "".join('<li><a href="#%s">%s</a></li>' % (hid, html.escape(t)) for t, hid in toc)
        toc_html = f'<nav class="toc"><div class="toc-title">本讲目录</div><ul>{items}</ul></nav>'
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{prefix}assets/orangebook.css">
</head><body>
<div class="layout">
{sidebar(by_mod, prefix, active_slug, active_mod, home)}
<main class="main"><div class="{main_cls}">
<div class="content">{body}</div>
{toc_html}
</div></main>
</div>
</body></html>'''

# ----------------------------------------------------------------------------
def collect():
    lectures = []
    for mod in ("a", "b"):
        d = os.path.join(CONTENT, "module-" + mod)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if not fn.endswith(".md"):
                continue
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                meta, body = parse_frontmatter(f.read())
            if not meta.get("title"):
                continue
            meta["module"] = meta.get("module", mod)
            meta["order"] = int(meta.get("order", 999))
            meta["_body"] = body
            lectures.append(meta)
    lectures.sort(key=lambda x: (x["module"], x["order"]))
    return lectures

def lecture_card(lec, prefix=""):
    mod = lec["module"]
    return f'''<a class="card" href="{prefix}module-{mod}/{lec['slug']}.html">
      <span class="card-no">第 {lec['order']} 讲</span>
      <h3>{html.escape(lec['title'])}</h3>
      <p>{html.escape(lec.get('summary',''))}</p>
    </a>'''

def write(relpath, content):
    full = os.path.join(SITE, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

# ----------------------------------------------------------------------------
def build():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE)
    shutil.copytree(ASSETS, os.path.join(SITE, "assets"))

    lectures = collect()
    by_mod = {"a": [], "b": []}
    for lec in lectures:
        by_mod[lec["module"]].append(lec)

    # 首页
    home = [f'''<div class="hero">
      <span class="eyebrow">A Course on Building Agents</span>
      <h1>学会<em>设计</em>与<em>工程化</em>一个 Agent</h1>
      <p class="lead">{html.escape(SITE_TAGLINE)}。两条主线：把 Agent 当产品来设计，把 Agent 当系统来交付。</p>
    </div>''']
    for mod in ("a", "b"):
        info = MODULES[mod]; count = len(by_mod[mod])
        home.append(f'<h2 class="home-sec"><span class="mod-badge">{mod.upper()}</span>{html.escape(info["name"])}<span class="sec-count">{count} 讲</span></h2>')
        home.append(f'<p class="home-desc">{html.escape(info["desc"])}</p>')
        if by_mod[mod]:
            home.append('<div class="card-list">')
            for lec in by_mod[mod]:
                home.append(lecture_card(lec, prefix=""))
            home.append("</div>")
        else:
            home.append('<p class="soon-note">本模块讲次筹备中。</p>')
    write("index.html", shell(SITE_TITLE, "\n".join(home), by_mod, prefix="", home=True))

    # 模块页
    for mod in ("a", "b"):
        info = MODULES[mod]
        page = [f'<div class="page-head"><span class="mod-badge big">{mod.upper()}</span><h1>{html.escape(info["name"])}</h1><p class="lead">{html.escape(info["desc"])}</p></div>']
        if by_mod[mod]:
            page.append('<div class="card-list">')
            for lec in by_mod[mod]:
                page.append(lecture_card(lec, prefix=""))
            page.append("</div>")
        else:
            page.append('<p class="soon-note">本模块讲次筹备中，敬请期待。</p>')
        write("module-%s.html" % mod, shell(info["name"], "\n".join(page), by_mod, prefix="", active_mod=mod))

    # 讲义页
    for lec in lectures:
        mod = lec["module"]; siblings = by_mod[mod]; pos = siblings.index(lec)
        prev_lec = siblings[pos - 1] if pos > 0 else None
        next_lec = siblings[pos + 1] if pos < len(siblings) - 1 else None
        body_html, toc = render_md(lec["_body"])
        summary = html.escape(lec.get("summary", ""))
        art = [f'<article class="lecture">',
               f'<div class="breadcrumb"><a href="../index.html">首页</a><span>/</span><a href="../module-{mod}.html">{html.escape(MODULES[mod]["name"])}</a></div>',
               f'<h1>{html.escape(lec["title"])}</h1>']
        if summary:
            art.append(f'<p class="summary">{summary}</p>')
        art.append(f'<p class="meta">Module {mod.upper()} · 第 {lec["order"]} 讲</p>')
        art.append(body_html)
        pager = ['<div class="pager">']
        pager.append(f'<a class="prev" href="{prev_lec["slug"]}.html"><span class="dir">← 上一讲</span><span class="ttl">{html.escape(prev_lec.get("nav", prev_lec["title"]))}</span></a>' if prev_lec else '<span class="spacer"></span>')
        pager.append(f'<a class="next" href="{next_lec["slug"]}.html"><span class="dir">下一讲 →</span><span class="ttl">{html.escape(next_lec.get("nav", next_lec["title"]))}</span></a>' if next_lec else '<span class="spacer"></span>')
        pager.append("</div>")
        art.append("".join(pager)); art.append("</article>")
        write(os.path.join("module-%s" % mod, lec["slug"] + ".html"),
              shell(lec["title"], "\n".join(art), by_mod, prefix="../", active_slug=lec["slug"], active_mod=mod, toc=toc))

    print("build done: %d lectures, site/ ready" % len(lectures))
    return len(lectures)

if __name__ == "__main__":
    build()
