---
title: agent-memory-kit
nav: agent-memory-kit
section: lab
status: open-source
repo: https://github.com/libaoming/agent-memory-kit
slug: agent-memory-kit
tags: [Agent 记忆, 运行时, 闭环]
summary: 给你正在构建的产品 Agent 装一层运行时记忆——四个角色把经验沉淀成可复用的教训。
order: 2
---

> 一个无状态的 Agent 不会从自己的历史里学到任何东西：同一个坑反复踩，用户上次纠正过的偏好这次又忘。它缺的不是智力，是一条把「干过、错过、被纠正过」沉淀下来、下次还能取回的回路。agent-memory-kit 给在建的产品 Agent 装上这条回路。

## 它解决什么

这是给**你正在构建的产品 Agent**用的运行时记忆，不是 Claude Code 自己的开发记忆——两者别混。它针对的是这些症状：

| 症状 | 根因 |
|---|---|
| 同类任务一错再错 | 失败没有被记录，更没有被复盘 |
| 用户纠正过的偏好又忘 | 纠正只活在当次对话，没落盘 |
| 经验无法跨会话迁移 | 没有「取回相关教训」的检索环节 |

## 核心机制：四角色闭环

| 角色 | 职责 |
|---|---|
| Doer | 产品 Agent 干活，留下执行 trace |
| Reflector | 第二个 Agent 独立评估这次干得对不对 |
| Store | 把提炼出的教训持久化成 markdown |
| 检索注入 | 下次任务开始前，把相关教训检索回 Doer |

关键是 Doer 与 Reflector 分离：干活的和评判的不是同一个上下文，避免自我背书。教训以人类可读的 md 落盘，可审计、可手改。

## 怎么用

git clone 后，把四角色接口接到你的 Agent：Doer 是你已有的执行体，挂上 trace 钩子；Reflector / Store / 检索注入按模板填。仓里给了检索注入与闭环优化两块现成实现，Reflector / Librarian 留接口占位。

## 一句话

让 Agent 把「上次这么干栽了」记成一条下次取得回来的教训，而不是每次从零开始。
