# M1 PROGRESS

| 字段 | 值 |
|---|---|
| active_feature | （S1 完成，待开 S2） |
| slice | S1 ✅ → S2 |
| 更新 | 2026-06-05 |

## Next Candidates
- S2：Module A 维度1 任务路径讲
- S2：维度2 失败节点讲
- S2：维度3 错误恢复（4+1）讲
- S2：维度5 边界行为（4类4模式）讲
- S2：技术地基五层（Loop/Tool/Planning/Memory/Multi-Agent）讲

## Blockers
- （无）

## Session Log（倒序）
### 2026-06-05（S4：上线 GitHub Pages）
- 创建 public 仓库 github.com/libaoming/agent-design-course，git init+commit+push（main）。
- GitHub Actions（.github/workflows/deploy.yml）自动 build+deploy，run 27000151884 成功（build 9s + deploy 10s）。
- 线上 https://libaoming.github.io/agent-design-course/ HTTP 200，首页+讲义页抽查正常。
- .gitignore 排除 site/ 与 .claude/settings.local.json；source 入库、产物 CI 生成。
- 唯一警告：Actions 用 Node20（2026-06-16 后强制 Node24），后续可升级 action 版本。

### 2026-06-05（S3：Module B 完成）
- **Module B 6 讲全部就位**：Harness 工程 / 上下文工程七维 / Gateway 工程 / 框架选型 / 评测与 Benchmark / 多 Agent 平台四阶段。
- 同模式：并行派 6 个 general-purpose 子 agent 从 vault 概念页提炼讲义体草稿，主线定稿（去中文序号、加 frontmatter+nav、统一层级）。
- build.py callout 升级支持类型标签（注/警/提示），CSS 加 callout-warning 样式。
- 全站 12 讲 build 通过，verify 6 项全绿。截图核查 gateway 篇：代码块、行内 code、警示框、侧栏双模块全满、TOC 均到位。

### 2026-06-05（视觉重构）
- **布局改左侧边栏导航**（仿 learn-harness-engineering）+ **风格转向 Claude Code 文档调性**：暖白底、陶土橙(#C15F3C)强调、文档式卡片、右侧「本讲目录」TOC、侧栏当前讲高亮。
- build.py 重写渲染层：sidebar() / shell() 三栏 + render_md 收集 h2 生成 TOC + 标题锚点 + scroll-margin。
- 6 篇加 nav 短标题（侧栏用）。orangebook.css 全量重写为侧栏布局+doc 调性。
- 浏览器截图**亲眼核查通过**：首页（hero+模块卡片）、讲义页（侧栏高亮+TOC+橙摘要框+浅灰表头表格+灰色「注」callout）均到位。verify 6 项全绿。

### 2026-06-05
- **S1 端到端跑通 ✅**：F01..F06 全 passing。`verify.sh` 6 项全绿（build / 双模块 / 讲义渲染 / 表格 / 无 emoji / 导航）。
- 产物：site/index.html + module-a.html + module-b.html + module-a/transparency.html。
- 第1讲样板 = 「为什么 Agent 的透明度不是越多越好」（透明度材料脱敏重写成讲义体）。
- build.py 为标准库手写 md 解析器（标题/段落/GFM表格/列表/引用/代码/行内/链接），零三方依赖。
- 浏览器截图预览受扩展权限阻断，改为本地 http server 预览（:8765），客观验证以 verify.sh 为准。
- 脚手架完成（4 层骨架）。PRD/SPEC/architecture 已填实（信息足够，未停下反问用户）。

## 如果…就…
- 如果不知道做什么 → 按 AGENTS.md「选 feature 算法」
- 如果 fixture 缺 → 先造第1讲 markdown，不许 mock
- 如果要批量读 vault 笔记重写讲义 → 派 `.claude/agents/learn-agent-design-ops.md` 或 general-purpose 子 agent，主 context 不拉原文

## 🤖 增量流水（待整理）
（Stop hook 自动追加区，下次启动先合并进 Session Log 再清空）
