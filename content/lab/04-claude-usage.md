---
title: claude-usage
nav: claude-usage
section: lab
status: open-source
repo: https://github.com/libaoming/claude-usage
slug: claude-usage
tags: [用量分析, CLI, 零依赖]
summary: 一条命令读本地 Claude Code 日志，把 token、成本、模型分布、缓存节省算清楚。
order: 4
---

> 用 Claude Code 用得越重，越说不清 token 和钱花在了哪：哪个项目最烧、Opus 和 Sonnet 各占多少、缓存到底省了多少。这些答案其实都躺在本地日志里，只是没人去读。claude-usage 把它读出来、算清楚。

## 它解决什么

账单是个总数，看不出结构。claude-usage 直接读 `~/.claude` 的本地日志，把用量拆开给你看：

| 维度 | 看清什么 |
|---|---|
| token / 成本 | 总量和按时间的趋势 |
| 模型分布 | Opus / Sonnet / Haiku 各占多少 |
| Top 项目 | 哪个项目最烧 token |
| 缓存命中 | prompt 缓存到底替你省了多少 |

## 核心机制

纯 Python 标准库，**零三方依赖**。解析本地日志、本地聚合、本地输出，不联网、不上传——你的用量数据不出本机。

## 怎么用

```
git clone https://github.com/libaoming/claude-usage
cd claude-usage && python3 usage.py
```

无需安装任何依赖，开箱即跑。

## 看我自己的用量

这套工具读的就是我本机的日志——[**打开作者本人的 Token 用量看板 →**](/usage/)（数据快照，每日使用、总量、模型分布；成本不外露）。

## 一句话

最小、最实用的一个：一条命令，把 Claude Code 这笔账从一个总数变成一张明细。
