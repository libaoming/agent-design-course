# CLAUDE.md — learn-agent-design

> 把本地 Obsidian wiki 的 Agent 学习材料，重写成 walkinglabs 式「问题驱动讲义体」的公开课——对外定位「构建 AI Agent / AI Agent 工程公开课」。纯静态 HTML 多页 + 轻构建脚本，橙研所橙皮书风，可推 GitHub Pages。Build in Public 作品（配合公众号「橙研所」）。

本项目采用 harness 方法论 + 4 层防御体系（Anthropic "Effective Harnesses for Long-Running Agents" + 得物 Harness 工程实践）。

## 入会顺序（每次新 session）
1. **先读 `STATUS.md`** —— 一句话状态 + 下次入口 + 踩坑清单
2. 再读 `PRD.md` / `SPEC.md` / `architecture.md` / `features.json`（三件套覆盖需求/方案/切片）
3. 开工前跑 `bash M1/init.sh` 确认环境全绿

> 🤖 **增量流水合并（每次启动先做）**：若 `M1/PROGRESS.md` 有「🤖 增量流水（待整理）」块（Stop hook 每轮自动追加的原始请求），**先合并进正式 Session Log、清空该块，再开工**。

## 仓库结构
```
learn-agent-design/
  CLAUDE.md              本文件（L1 持久化 + L4 隔离纪律）
  STATUS.md              新 session 入口（L1）
  PRD.md / SPEC.md / architecture.md   文档先行三件套（L2 输入源）
  features.json          原子 feature 单一事实源（L2）
  M1/                    里程碑三件套（init.sh / AGENTS.md / PROGRESS.md）
  fixtures/              fixture（先于代码，含 README 索引）
  content/              讲义 markdown 源（module-a / module-b）
  assets/               视觉系统 CSS、line-SVG 图标
  scripts/build.py      构建脚本：markdown → 多页静态 HTML
  site/                 build 产物（不入 git）
  .claude/agents/        项目专属子 agent（L4 脏活隔离）
```

## 内容约定（这个项目的核心）
- **一讲 = 一个 markdown 文件**，放 `content/module-a/` 或 `content/module-b/`，带 YAML frontmatter（见 SPEC.md「讲义文件 schema」）。
- **讲义体硬规矩**：每讲是「问题驱动」叙事，不是笔记搬运。结构 = 立靶（失败模式/为什么重要）→ 给框架（表格/MECE）→ 上数据/case → 可操作做法 → 一句话收口。标题用「为什么 Agent 会 X / 为什么 X 重要」句式。
- **视觉**：橙研所橙皮书风（橙色品牌渐变 + 卡片排版）。**禁 emoji**，图标一律 line-SVG。文字为绝对主体，配图克制（每讲 ≤ 3-5 张，分散嵌入）。
- **内容来源**：`~/Documents/Obsidian Vault/wiki/`（concepts/ + syntheses/ + memory 里的 L3 五维）。**重写不是复制**——派子 agent 读原始笔记，回提炼后的讲义草稿，主 context 不整篇 Read 笔记原文。

---

## 4 层防御体系（本项目的工程底座）

### L1 持久化层
业务语义 / 规则 / 进度从不可靠的 LLM 记忆迁到确定性文件：`CLAUDE.md`（规则）+ `STATUS.md`（进度，每次 session 收尾必更新）+ Auto Memory（跨会话）。

### L2 方法论层（开发纪律）
- `features.json` 是**单一事实源**：status ∈ {pending, in_progress, failing, passing}，**verify 真跑通才能改 passing**
- 🚦 **verifier 硬闸门**：feature 的 `verify` 字段为空 = **不准开工**。每讲的成功信号 = build 产出对应 HTML 且关键章节标题出现 + 无 emoji + 导航可达
- 🧭 **三段式关联**：每个 feature 填 `related`/`affected`/`out_of_scope`
- **线性切片**推进：S1 先把骨架+1讲端到端跑通，再逐讲填充。不一次堆 20 讲
- **fixture 先于代码**：第 1 讲 markdown 是 build 脚本的 fixture，先写讲义再写脚本

### L3 自动化钩子层
确定性自动化放项目级 `.claude/settings.local.json`（local 不入 git）。**已内置**：Stop hook（每轮把用户请求增量追加到 `M1/PROGRESS.md` 的「增量流水」区）。

### L4 上下文隔离层 ⭐
把"吃大量 context 的脏活"派给子 agent（**Agent 工具**或 `.claude/agents/learn-agent-design-ops.md`）在独立 context 跑完，**只回结论**。

**本项目必须隔离的脏活**
- **批量读 vault 笔记重写讲义**：派子 agent 读 `~/Documents/Obsidian Vault/wiki/` 下指定笔记，回**提炼后的讲义草稿**（按讲义体结构），主 context 绝不整篇 Read 原始笔记
- 大文档检索：PRD/SPEC/大 features.json → 子 agent 只回相关切片
- build 长日志 / 产物核查 → 子 agent 只回结论

**留主线（不外包）**：讲义体最终定稿润色、视觉/CSS 决策、build 脚本架构、verify 判定、跟用户对话

**🚨 子 agent 铁律**
1. prompt **完全自包含**：写死 vault 路径（`/Users/baomingli/Documents/Obsidian Vault/wiki/`）、要读的笔记文件名、要回的讲义结构
2. **只读**：子 agent 对 vault 只读不写；改 content/ 由主 agent 定稿
3. **回草稿不回原文**：子 agent 返回结构化讲义草稿（含立靶/框架/数据/做法），不把笔记原文贴回

---

## verify 纪律
- **开工闸门**：`verify` 字段为空的 feature 不准动
- `features.json` status：草稿写完只到 `in_progress`；**build 产出正确 HTML 且过检查清单才能改 `passing`**
- 每讲 verify 检查清单：① build 无报错 ② 产出对应 `.html` ③ 关键章节标题出现在 HTML ④ 全文无 emoji（`grep` 检测）⑤ 从导航可点达
- 🖼️ **框架图 SVG 必须渲染逐张肉眼看，禁止只靠估算**：改完/新出 SVG（尤其多语言版本），用 `qlmanage -t -s 1480 x.svg -o /tmp/...` 渲染成 PNG **逐张 Read 看**。XML 合法 + 无文本残留只是结构验证，**看不出文字撞框/重叠/溢出**——这要渲染才知道。教训（2026-06-19 英文化 18 张图）：子 agent 自报「已防溢出」是靠字符数估算的，**6/6 都误判**（英文比中文宽，居中标签撞框、行标撞列、长行出框）。修法 = 精简文案 / 单行降字号，**列坐标与几何元素一律不动**。

## 命名约定
- 讲义文件：`content/module-{a,b}/{NN}-{slug}.md`（NN 两位序号）
- git branch：`feat/{feature_id}`
- 代码注释用中文；用户可见站点文案用中文
