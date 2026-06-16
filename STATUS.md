# STATUS — learn-agent-design

> 每次 session 第一个读的文件。收尾必更新本文件。

## 一句话状态（2026-06-16 新增 Module E · 上下文工程）
**5 讲义模块 31 讲**（A 产品能力 6 / B 工程地基 6 / C Harness 工程 7 / D 设计模式 5 / **E 上下文工程 7**）+ 3 实战示例 + 18 张轻手绘 SVG 框架图 + 每页「已有 N 人学过本课程」统计（GoatCounter）。侧栏导航 + 模块导语 + Claude doc 风 + GitHub Actions 自动部署。

**2026-06-16 新增 Module E · Context Engineering 上下文工程**：与 A（产品能力）/ C（Harness）并列的第三大支柱，源自 CE 7 单元自学体系。S5 切片，**第 0 讲「CE 总览·七层与暗物质」已上线**（七层次表 + 暗物质 + CE/PE/Harness 辨析，五段式）。**全程脱敏**：私人项目写成「某语音 agent / 某成熟产品」，build 后跑 grep 闸门确认零命中（妙招/豆包/ECS/评级等）。**E01-E06（U2-U7 各层深入讲）于 2026-06-16 全部完稿上线**：prompt 分层 / 结构化 IO+工具 / 记忆+RAG / 历史+压缩 / cache 工程 / 可观测+eval，均「为什么 X」立靶句式 + 五段式，build/verify 全绿、脱敏 grep 干净。features.json 全 22 feature passing。

> 早期状态（2026-06-05 主体完成）：4 模块 24 讲全 passing，Module C 融合 walkinglabs + 本项目实战方法论（自指），Module D 源 Google《Agentic Design Patterns》/xindoo 仓库。
关联：libaoming.github.io 根站 2017 旧简历已换成跳转课程站的占位页（另一仓库 libaoming/libaoming.github.io，旧源码在 git 历史可恢复）。

## 线上 / 仓库
- 站点（主域名）：https://chengyansuo.com/（2026-06-16 购入并接 GitHub Pages，CNAME 由 build.py 的 SITE_DOMAIN 常量写入 site/CNAME；GNAME 注册，apex 4 条 A 记录→GitHub IP + www CNAME→libaoming.github.io）
- 站点（旧地址，自动跳转新域名）：https://libaoming.github.io/agent-design-course/
- 仓库（public）：https://github.com/libaoming/agent-design-course（仓库名未改，仅站内文案升级为「构建 AI Agent」）
- 部署：push main → GitHub Actions（.github/workflows/deploy.yml）自动 build + deploy，site/ 由 CI 生成不入库

## 预览方式
- 本地：`cd site && python3 -m http.server 8765` → 浏览器开 `http://localhost:8765`
- 重新构建：`python3 scripts/build.py`
- 全量验证：`bash scripts/verify.sh`

## 下次入口
1. 读本文件 → 读 `M1/PROGRESS.md`（倒序 Session Log 看全程）
2. 跑 `bash scripts/verify.sh` 确认环境与 build 全绿
3. **Module E 已完整 7 讲（2026-06-16 收口，全 passing）**。可选下一步：① 补配图（七层次/双 block 等 line-SVG）② 各讲质量复训抽查。下为当初逐讲方法（已全执行完，留作复用模板）：源 CE 自学体系 U2-U7。每讲一个切片，派子 agent 读 `~/ObsidianVault/notes/claude-memory-sync/learning_ce_uN_*.md` 回**脱敏**讲义草稿 → 主线五段式定稿 → build + verify + 脱敏 grep 闸门 → push。slug 已在 features.json 预定（prompt-instruction-layers / structured-io-and-tools / memory-and-rag / history-and-compaction / cache-engineering / observability-and-eval）。范例照 `content/module-a/00-five-layers.md` + `content/module-e/00-context-engineering-overview.md`。
4. 旧的可选项（没有也是完整作品）：
   - ① 资料库·技能区（仿 walkinglabs /resources /skills，放 [[project_harness_kit_oss]] 模板）
   - ② 首页「课程缘起」文案（强化 Build in Public）
   - ③ 每讲阅读时长
   - ④ GitHub Actions 升级 Node20→Node24（2026-06-16 后强制，到时升 action 版本）
   - ⑤ 配套发布推文（橙研所拆解调性）
- 改内容/视觉流程：编辑 content/*.md 或 assets/orangebook.css → `python3 scripts/build.py` → `bash scripts/verify.sh` → commit push（Actions 自动部署）
- 新讲义图：写 SVG 到 assets/diagrams/（feTurbulence 手绘滤镜 + 陶土橙），markdown 里 `![alt](../assets/diagrams/x.svg)` 引用
- 加新模块：build.py 的 MODULES dict + 4 处 `("a","b","c","d")` 循环 + by_mod

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
