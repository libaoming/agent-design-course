---
title: context-engineering-kit
nav: context-engineering-kit
section: lab
status: open-source
repo: https://github.com/libaoming/context-engineering-kit
slug: context-engineering-kit
tags: [上下文工程, CONTEXT.md, 缓存]
related_lecture: e
summary: 用一张 CONTEXT.md，把进入上下文窗口的每样东西按七层管理起来——每层带预算和缓存策略。
order: 3
---

> 模型表现差，很多时候不是 prompt 不够好，是这一轮喂进窗口的东西不对：塞太多被噪声淹没、塞太少缺关键事实、塞错了误导、没结构无法缓存、不可控每次都飘。context-engineering-kit 用一张 CONTEXT.md，把单次窗口里装了什么这件事，从隐式变成可审计、可复现的工程。

## 它解决什么

进入上下文窗口的内容失控时，会以五种方式失败：

| 失败模式 | 后果 |
|---|---|
| 塞太多 | context rot，关键信息被噪声淹没 |
| 塞太少 | 缺关键事实，模型靠猜 |
| 塞错了 | 不相关内容误导判断 |
| 没结构 | 无法分层缓存，成本与延迟双高 |
| 不可控 | 每轮内容飘，行为不可复现 |

## 核心机制：七层模型

CONTEXT.md 把进入窗口的东西按「稳定 → 易变」分七层，每层带 token 预算 + 缓存策略：

| 层 | 内容 | 缓存 |
|---|---|---|
| L1 系统指令 | 角色/规则 | 静态缓存 |
| L2 领域知识 | 业务背景 | 静态缓存 |
| L3 工具定义 | 可调工具 | 静态缓存 |
| L4 记忆 | 长期教训 | 静态缓存 |
| L5 检索内容 | RAG 召回 | 每轮重建 |
| L6 对话历史 | 多轮上下文 | 每轮重建 |
| L7 当前输入 | 本轮请求 | 每轮重建 |

L1-L4 稳定可缓存、L5-L7 每轮重建——稳定与易变分离，是缓存能生效的前提。

辨析（这套模型的核心卖点）：**Prompt Engineering 是 CE 的 L1 子集，RAG 是 CE 的 L5 一层，Harness 管的是项目骨架、CE 管的是单次窗口构成**。三者不是竞品，是不同尺度。

四条设计原则：显式优于隐式 / 稳定易变分离 / 可审计 / 可复现。三条反模式：全塞（context rot）、稳定易变混放（缓存全失效）、检索不排序（噪声污染）。

## 怎么用

git clone 后照 CONTEXT.md 模板，把你的 Agent 这一轮要进窗口的内容逐层填进去，标好每层预算与缓存策略。它既是配置，也是这次窗口装了什么的可审计快照。

## 一句话

把「这次到底喂了模型什么」从你脑子里搬到一张能 review、能复现的表里。
