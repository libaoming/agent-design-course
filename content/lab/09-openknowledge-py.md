---
title: openknowledge-py
nav: openknowledge-py
section: lab
status: open-source
repo: https://github.com/libaoming/openknowledge-py
slug: openknowledge-py
tags: [教学复刻, 知识库, MCP]
summary: 用 Python 从零复刻 inkeep/open-knowledge——人与 AI agent 共用的 git-native markdown 知识底座，「通过重建来拆解」。
order: 9
---

> 读一个复杂系统的源码，和亲手把它重建一遍，学到的深度差一个量级。openknowledge-py 选了后者：把 inkeep/open-knowledge——一个人与 AI agent 共用的 git-native markdown 知识底座——用 Python 从零复刻。原版是 TypeScript，复刻版的包布局刻意镜像原版拓扑（core → server → cli → app），可以逐文件对照着读；每个子系统（markdown 管线、搜索、CRDT 协同、MCP）都亲手写过一遍之后，才算真的懂了。

## 它解决什么

| 目标 | 做法 |
|---|---|
| 真正理解每个子系统 | 不读懂拉倒，重建到跑通为止 |
| 跨语言对照学习 | 包拓扑镜像原版，Zod→Pydantic、Orama→bm25s、Yjs→pycrdt、commander→typer 逐项映射 |

## 核心机制：九个里程碑

M0–M8 线性推进：脚手架 → core（schema + markdown 管线 / BM25 搜索 / git shadow repo + bridge diff/merge）→ server（MCP 只读工具 / 写动词 / CRDT 同步 + file-watcher）→ app（WYSIWYG 编辑器，Tiptap 薄 JS 孤岛经 pycrdt-websocket 连通）→ cli（init / seed / start）。后端主线已完成：29/29 features passing，170 条测试全绿。桌面支线（Electron 一份代码双 host）进行中。

## 怎么用

`uv sync --extra core --extra server` → `okpy init ~/my-notes` → 可选 `okpy seed` → `okpy start`——一个进程里同时起编辑器 UI、CRDT 协同和 agent-write HTTP 接口，浏览器打开 127.0.0.1:1234 即用。给 agent 接 MCP 的配置见 examples/mcp.json。

## 一句话

最好的源码阅读方式是不读——把它重建出来。
