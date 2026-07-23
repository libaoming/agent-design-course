---
title: superagent-from-scratch
nav: superagent-from-scratch
section: lab
status: open-source
repo: https://github.com/libaoming/superagent-from-scratch
slug: superagent-from-scratch
tags: [教学复刻, agent loop, 零框架]
related_lecture: c
summary: 千行级、零框架、教学优先的 SuperAgent harness 复刻——从 18.5 万行的 deer-flow 里蒸馏出 agent 核心，一个下午读完。
order: 6
---

> 想搞懂现代 Agent 框架的内核，你有两条路都走不通：头部开源学不动——deer-flow（76k star）backend 18.5 万行，2,300 行 agent 核心埋在产品壳里；教程又太浅——停在 function calling，够不着上下文管理、防御 middleware、子 agent 隔离。superagent-from-scratch 走第三条路：把 deer-flow 的核心架构蒸馏成一个零框架、src/ 不到 700 行的教学实现，`messages → LLM → tools → append` 这个循环第一次裸露在你眼前。

## 它解决什么

| 障碍 | 症状 |
|---|---|
| 头部开源学不动 | 18.5 万行代码里找 2,300 行核心，先淹死在产品壳里 |
| 教程太浅 | 讲到 function calling 就停，middleware / 子 agent / 长任务全缺席 |
| 框架遮蔽本质 | LangChain 一行黑盒，看不到循环本体长什么样 |

## 核心机制：五个线性切片

每个切片一个 git tag（sfs-s1…s5），配离线测试和「why 先行」的拆解笔记：

| 切片 | 内容 |
|---|---|
| S1 | agent 循环 + LLM 接缝 + 3 个真实工具 |
| S2 | middleware 管线（before_model / after_model / wrap_tool_call） |
| S3 | task 工具 + subagent 委派——上下文隔离，只回结论 |
| S4 | skills 系统（SKILL.md 发现 + 斜杠激活） |
| S5 | 长任务（write_todos + goal 续跑闭环 + HITL 中断） |

测试跑在录制好的 LLM fixture 上，从不 mock.patch——62 条离线测试全绿，运行时依赖只有 anthropic + pyyaml。

## 怎么用

`git clone` → `uv sync` → `uv run pytest -q`。全程离线，不需要 API key。按切片顺序读代码 + 拆解笔记，一个下午过完。

## 一句话

不是又一个 Agent 框架，是把「框架里到底发生了什么」摊开在千行代码里给你看。
