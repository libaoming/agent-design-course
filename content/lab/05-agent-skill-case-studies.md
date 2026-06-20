---
title: agent-skill-case-studies
nav: agent-skill-case-studies
section: lab
status: open-source
repo: https://github.com/libaoming/agent-skill-case-studies
slug: agent-skill-case-studies
tags: [Agent Skills, 案例研究, 设计模式]
summary: 把设计精良的 Claude Agent Skills 当教材拆开，提炼可复用的设计模式。
order: 5
---

> 怎么设计一个好的 Agent Skill，目前几乎没有系统参考——大家都在凭感觉写。但优秀的 Skill 本身就是最好的教材：它的结构怎么搭、提示词怎么组织、工具怎么定义，拆开看全是可复用的决策。agent-skill-case-studies 就是把这些好 Skill 一个个拆开看。

## 它解决什么

写 Skill 时常见的困惑：结构该怎么分、提示词写多详细、工具粒度多大、什么时候该拆子 agent。没有范例时只能试错。这个仓库把答案沉淀成案例：

| 拆解维度 | 看什么 |
|---|---|
| 结构 | Skill 怎么组织文件与触发条件 |
| 提示词策略 | 指令怎么写才稳、才不啰嗦 |
| 工具设计 | 工具粒度、输入输出怎么定 |

## 核心机制

挑 Anthropic 官方 + 社区里设计精良的 Claude Agent Skills（chess / pptx / pdf / artifacts-builder 等），逐个拆结构、提示词策略、工具设计，再横向提炼出可复用的设计模式。是拆解向的内容合集，契合「把好东西拆开看」的调性。

## 怎么用

git clone 或直接在 GitHub 上读。按案例索引挑一个感兴趣的 Skill，跟着拆解走一遍，把其中的设计决策搬到自己的 Skill 里。

## 一句话

不教你从零发明，教你把别人验证过的好设计看懂、拿走。
