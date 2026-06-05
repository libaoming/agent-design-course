# STATUS — learn-agent-design

> 每次 session 第一个读的文件。收尾必更新本文件。

## 一句话状态
2026-06-05 **已上线**：3 讲义模块共 **19 讲**（A 产品/能力 6 + B 工程地基 6 + **C Harness 工程 7**）+ 3 篇实战示例。Module C 融合 walkinglabs《Harness Engineering》框架 + 本项目自己的实战方法论（自指：这门课本身就是用这套方法做的）。侧栏四区 + 模块导语 + Claude doc 风。**已配 14 张轻手绘风 SVG 框架图**（feTurbulence 滤镜做手绘抖动）覆盖几乎每讲：A 6 讲全有图 + B 5 讲（Harness/上下文稳定易变/Gateway/框架光谱/多Agent）+ C 3 讲（指令文件柜/feature状态机/三层校验）。build.py 支持 `![]()` 语法。**统计已上线 ✅**：GoatCounter（code=learn-agent-design，需在 Settings 开 Allow visitor counts，已开）接入，全站 PV/UV tracking + 首页绿点胶囊「已有 N 人学过本课程 · M 次阅读」（截图核查 3 人/3 阅读已亮，真实数据不造假）。**Module D 完成 ✅**：5 讲（全景地图 + 反思推理 / 学习RAG / A2A / 优先级探索 4 类盲区深入），每讲都对照本课呼应（织进整门课，不孤立罗列）。**全站现状**：4 讲义模块共 **24 讲**（A6+B6+C7+D5）+ 3 实战示例 + 14 张框架图 + 每页访问统计。**剩余可选**：Module D 配图（21模式地图/状态机类）/ 资料库·技能区 / 首页缘起文案。

## 线上 / 仓库
- 站点：https://libaoming.github.io/agent-design-course/
- 仓库（public）：https://github.com/libaoming/agent-design-course
- 部署：push main → GitHub Actions（.github/workflows/deploy.yml）自动 build + deploy，site/ 由 CI 生成不入库

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
