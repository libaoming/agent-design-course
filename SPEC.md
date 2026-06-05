# SPEC — learn-agent-design

> LLM-native 技术规范：结构化 schema + 显式约束 + 反模式。

## 讲义文件 schema

每讲是 `content/module-{a,b}/{NN}-{slug}.md`，**带 YAML frontmatter + markdown 正文**。

```yaml
---
title: 为什么 Agent 的透明度不是越多越好     # 必填，讲义体句式
module: a                                    # a | b
order: 4                                      # 模块内排序（两位以内整数）
slug: transparency                            # 文件名用，URL 用
summary: 透明度不是标量而是「对象×粒度×传达路径」的矩阵；给错对象 = 负价值。  # 一句话，首页/模块页卡片用
tags: [L3, 透明度, 反模式]                     # 可选
source_notes: [learning_l3_dim4_transparency] # 可选，溯源（不渲染，仅记录）
---

正文 markdown……
```

### frontmatter 字段约束
| 字段 | 必填 | 类型 | 约束 |
|---|---|---|---|
| title | 是 | str | 「为什么…」句式优先；禁 emoji |
| module | 是 | enum | `a` / `b` |
| order | 是 | int | 模块内唯一，决定排序与上一讲/下一讲 |
| slug | 是 | str | kebab-case，URL 安全 |
| summary | 是 | str | ≤ 60 字，卡片展示 |
| tags | 否 | list | |
| source_notes | 否 | list | 溯源用，不渲染 |

### 正文讲义体结构（软约束，写作纪律）
1. **立靶**：对治的失败模式 / 为什么重要。
2. **框架**：核心 MECE / 表格（至少一个 markdown 表格）。
3. **数据 / case**：数字、真实案例（脱敏）。
4. **可操作做法**：清单。
5. **一句话收口**：记忆锚点 / 金句，用 `> ` 引用块。

## 支持的 markdown 子集（build 脚本必须解析）
| 语法 | 说明 |
|---|---|
| `# ~ ####` 标题 | h1 作页面主标题来源（或用 frontmatter title）；正文用 h2/h3 |
| 段落 | 空行分段 |
| 表格 | GFM 管道表格（**必须支持**，讲义体核心） |
| 无序/有序列表 | `- ` / `1. `，支持一层嵌套 |
| `> ` 引用块 | 收口金句用 |
| `**粗体**` / `` `代码` `` | 行内 |
| ` ```代码块``` ` | 围栏代码块 |
| 链接 `[t](url)` | 站内相对链接 + 外链 |

> 解析策略见 architecture.md「关键技术决策」——优先标准库手写极简解析器，覆盖以上子集即可，不追求 CommonMark 全集。

## 视觉系统（assets/orangebook.css）
- **配色**：品牌主色橙 `--brand: #E8651E`（橙皮书橙）；辅助 `--brand-soft`、渐变 `--brand-grad: linear-gradient(135deg,#F59E0B,#E8651E)`；中性 `--ink:#1f2328` 正文、`--muted:#5b6370`、`--bg:#fffdfa` 暖白、`--card:#ffffff`、`--line:#f0e8de`。
- **字体**：正文系统无衬线（`-apple-system, "PingFang SC", "Microsoft YaHei", sans-serif`）；标题可加重字重；代码用等宽。
- **排版**：正文最大宽度 ~720px 居中、行高 1.8、字号 17px；表格斑马纹 + 橙色表头；卡片圆角 14px + 轻阴影 + 左侧橙色色条。
- **禁止**：emoji（一律 line-SVG）；花哨动画；正文图片喧宾夺主。
- **图标**：内联 line-SVG（stroke 风格，1.5px），放 `assets/`，build 时内联或引用。

## 构建脚本（scripts/build.py）
- 入口：`python3 scripts/build.py`。
- 流程：① 读 `content/**/*.md` 解析 frontmatter+正文 → ② markdown→HTML → ③ 套页面模板（首页/模块页/讲义页）→ ④ 写入 `site/`，拷贝 `assets/` 到 `site/assets/`。
- 导航：从所有讲义的 frontmatter 自动生成模块讲次列表 + 讲义页上一讲/下一讲。
- 幂等：重复跑结果一致；先清 `site/` 再生成。

## 页面类型
| 页面 | 路径 | 内容 |
|---|---|---|
| 首页 | `site/index.html` | 课程一句话定位 + Module A/B 双卡片 + 各模块讲次入口 |
| 模块页 | `site/module-a.html` / `module-b.html` | 该模块讲次列表（卡片，含 summary） |
| 讲义页 | `site/{module}/{slug}.html` | 讲义正文 + 顶部导航 + 上一讲/下一讲 |

## 反模式（禁止）
| 反模式 | 为什么禁 |
|---|---|
| 笔记原文直接粘贴当讲义 | 违背「问题驱动讲义体」，沦为搬运 |
| 用 emoji 当图标/装饰 | 违背橙皮书克制调性 |
| 引入前端框架/Tailwind/Node 构建链 | 违背"纯静态+零依赖"约束 |
| 一次构建堆 20 讲 | 违背线性切片，先 S1 端到端跑通 |
| 泄露未公开项目内部细节 | vault 是私人材料，对外需脱敏 |
| build 产物 `site/` 提交进 git | 产物应 gitignore，只提交源 |

## 切片关联 — Related Context
### S1（骨架跑通）
- **Related**：本 SPEC 全文 + architecture.md + 第1讲 fixture。
- **Affected**：build 脚本、视觉 CSS、三类页面模板、第1讲内容。
- **Out of scope**：S2/S3 的其余讲次、搜索、暗黑模式、资料库/技能区、部署。
