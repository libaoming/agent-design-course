---
title: skill-catalog-pipeline
nav: skill-catalog-pipeline
section: lab
status: open-source
repo: https://github.com/libaoming/skill-catalog-pipeline
slug: skill-catalog-pipeline
tags: [数据管线, 语义检索, pgvector]
related_lecture: b
summary: 把 7.7 万条第三方技能包做成 500ms 语义检索技能库底座的工程方案——五层管线 + 17 条踩坑结晶。
order: 7
---

> 技能市场只给你一个分页 API，想自建一个「可语义检索、可装载」的技能库底座，中间隔着一整条工程管线：怎么抓全、怎么洗净、怎么存、怎么搜得快、怎么持续跟上游同步。skill-catalog-pipeline 把这条管线在 77,000+ 条真实技能包上跑通了一遍，然后把方案、脱敏参考实现和 17 条踩坑复盘一起开源——价值最高的不是代码，是那些「文档里不会写、只有踩过才知道」的坑。

## 它解决什么

| 环节 | 真实的坑 |
|---|---|
| 抓全 | 分页抖动会漏上千条，还会把在架技能误判成下架 |
| 清洗 | 七成条目分类为空，还混着 NUL 脏数据 |
| 检索 | 2048 维向量直接超出 pgvector 索引上限 |
| 同步 | `updated_at` 是个脏信号，靠它增量同步会漏更新 |

## 核心机制：五层管线

| 层 | 职责 | 关键设计 |
|---|---|---|
| FETCH 抓取 | 抓全 | 多轮并集 + 完整性闸门 |
| NORMALIZE 清洗 | 洗净 | 5 项硬条件校验，dry-run 幂等 |
| STORAGE 存储 | 存好 | Postgres + pgvector + 对象存储，资产四态 |
| RETRIEVAL 检索 | 搜快 | halfvec 余弦 + IVFFlat，带索引 ~500ms（无索引 130s，提速约 260 倍） |
| SYNC 同步 | 跟上 | 周度四态 diff，认 version 不认 updated_at |

## 怎么用

先读 docs/ 里的架构文档和 engineering-notes（17 条踩坑复盘），这是仓库的主体价值；src/ 是脱敏参考实现（16 个脚本 + SQL，凭证走环境变量），照着改造成你自己的底座，不是开箱即跑的产品。

## 一句话

一份「把别人的技能变成自己的可检索资产」的完整工程蓝图，坑都替你踩过了。
