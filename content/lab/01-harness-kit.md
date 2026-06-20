---
title: harness-kit
nav: harness-kit
section: lab
status: open-source
repo: https://github.com/libaoming/harness-kit
slug: harness-kit
tags: [项目脚手架, 工程方法论, Claude Code]
related_lecture: c
summary: 把「用 Claude Code 做长程任务」的工程方法，沉淀成一套可 clone 即用的项目骨架。
order: 1
---

> 长程 Agent 最大的敌人不是不够聪明，而是会在长任务里迷失——忘目标、丢进度、偏方向、做完无从验证。根子是把这些都托付给了模型不可靠的记忆。Harness 就是套在模型外面的一副挽具：一套确定性的工程结构，把目标、进度、验证标准迁到外部文件，让 Agent 每一步都重新锚定、不漂移。harness-kit 把「这副挽具该怎么搭」做成了可 clone 的方法论与模板。

## 它解决什么

用 Claude Code 做跨越多个会话的长程任务，你大概率撞过这四堵墙：

| 失败 | 症状 |
|---|---|
| 跨会话失忆 | 新开会话，Agent 忘了上次做到哪、为什么这么设计 |
| 进度漂移 | 说要做 A，做着做着偏到 B，没有单一事实源 |
| 验证缺位 | 声称「做完了」，但没有可复核的通过标准 |
| 上下文爆炸 | 材料一股脑塞进窗口，重要信息被淹没 |

根子是同一个：把业务规则、进度、验证标准托付给了不可靠的 LLM 记忆。harness-kit 把它们全迁到确定性文件。

## 核心机制：四层防御

| 层 | 作用 | 落地物 |
|---|---|---|
| L1 持久化 | 规则/进度落盘 | CLAUDE.md + STATUS.md + Auto Memory |
| L2 方法论 | 单一事实源 + 可验证切片 | features.json + 里程碑三件套 + fixture |
| L3 自动化钩子 | 确定性自动化 | hooks（Stop/SessionStart 进度追加） |
| L4 上下文隔离 | 脏活外包子 agent | 隔离纪律 + 专属子 agent |

落到五个核心组件：CLAUDE.md（项目宪法）、STATUS.md（单页状态）、features.json（原子任务事实源，pending/in_progress/failing/passing）、里程碑三件套（init.sh / AGENTS.md / PROGRESS.md）、fixture 先于代码。

## 怎么用

git clone 后两种用法：手动——复制 templates/ 11 个模板，填掉占位符即可开工；一键——装成 Claude Code 插件后 /harness-kit:harness-init，回答几个问题自动 scaffold 整套骨架。仓里带一个填好的 examples/demo-cli/ 最小示例和 docs/methodology.md 四层详解。

## 一句话

不是模板套娃，是把「这个项目还活着、做到哪了」这件事，从你的记性里搬进文件里。
