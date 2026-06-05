# STATUS — learn-agent-design

> 每次 session 第一个读的文件。收尾必更新本文件。

## 一句话状态
2026-06-05 **S1+S2+S3 ✅**：两个模块共 **12 讲** 全部就位（Module A 产品/能力设计 6 讲 + Module B 工程地基 6 讲），侧边栏导航 + Claude doc 风 + 代码块/表格/callout 全渲染，build+verify 全绿，截图核查通过。内容主体完成。下一步 S4（可选）：部署 GitHub Pages + 首页打磨 + 资料库/技能区。

## 预览方式
- 本地：`cd site && python3 -m http.server 8765` → 浏览器开 `http://localhost:8765`
- 重新构建：`python3 scripts/build.py`
- 全量验证：`bash scripts/verify.sh`

## 下次入口
1. 读本文件 → 读 `M1/PROGRESS.md`
2. 跑 `bash M1/init.sh` 确认环境（需 python3）
3. 当前应做：**S3 — Module B 工程地基讲义**。候选讲：Harness 工程 / Gateway 工程 / 上下文工程七维 / 评测体系与 Benchmark / 框架选型 / 多Agent平台四阶段。vault 概念页齐全（concepts/Agent-Harness工程.md、Agent-Gateway工程.md、Agent上下文引擎-七维拆解透镜.md、Agent-评测体系与Benchmark.md、Agent-框架选型.md、多Agent平台架构四阶段模式.md）。派子 agent 提炼草稿，主线定稿，写入 content/module-b/NN-slug.md，build + verify。

## 关键技术事实
- 技术栈：Python 3 标准库写 `scripts/build.py`（markdown→HTML，零三方依赖优先；若用 markdown 库需 requirements.txt）
- 部署目标：GitHub Pages（build 产物在 `site/`）
- 内容源：`/Users/baomingli/Documents/Obsidian Vault/wiki/`（concepts/ + syntheses/ + L3 五维 memory）
- 视觉基准：橙研所橙皮书风（橙色渐变 + 卡片），参考 vault 里的 PDF 报告模板 + mz-visual-system.css；禁 emoji，line-SVG 图标

## 文档地图
- 需求：`PRD.md`　方案：`SPEC.md`　架构：`architecture.md`　切片：`features.json`
- 里程碑三件套：`M1/`　fixture：`fixtures/`
- 脏活隔离子 agent：`.claude/agents/learn-agent-design-ops.md`（批量读 vault 笔记重写讲义）

## 踩坑清单
- （随项目积累）
