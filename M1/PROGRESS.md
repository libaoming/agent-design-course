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
### 2026-06-17（首页加微信收款码赞赏卡片）
- 发现上一轮遗留半成品：build.py 有 +21 行未提交改动（`SUPPORT` 字典 + `support_block()`，首页接入），但 CSS 缺失、图片不存在。
- 补齐 `.support-card / .support-head / .support-title / .support-note / .support-qr` CSS（96×96 二维码，对齐 author-card 橙皮风，移动端换行）。
- 复制微信收款码（¥36，Dereck，302KB）到 `assets/wechat-pay.png`，build copytree 自动带入 `site/`。
- build/verify FAIL=0 全绿，commit 4e4809b（三文件：build.py + orangebook.css + wechat-pay.png）。

### 2026-06-05（收尾：Module D 完整 + 配图 + 统计调整 + 根站简历）
- Module D 补齐 4 类盲区深入讲（反思推理/学习RAG/A2A/优先级探索），每讲对照本课呼应；派 4 子 agent 写。共 5 讲。
- Module D 配图 4 张（反思循环/RAG五步/A2A三编排/优先级四象限），全站图增至 18 张。
- 统计**每页显示**（讲义页右栏 TOC 下 / 模块页底 / 首页 hero）；修绿点与文字重叠 bug（block 下 gap 失效→改 dot margin-right）；按用户要求**去掉「次阅读」只留「已有 N 人学过」**，保持全站 TOTAL。
- Module D 加**参考来源**（模块导语 + 总览讲末尾，链 github.com/xindoo/agentic-design-patterns）。
- 答清统计原理（全站 TOTAL / localhost 不计 / 缓存延迟 / 8h session 去重）。
- 关联：libaoming.github.io 根站 2017 旧简历 → 换成跳转课程站的占位页（PUT index.html，commit 897dbf1a；另一仓库 libaoming/libaoming.github.io）。
- **本 session 收尾**：features.json 15 feature 全 passing；STATUS「下次入口」已更正（原误留 S3 Module B）。主体交付完成。

### 2026-06-05（Module D「21 设计模式」开工 + 统计上线）
- **统计闭环**：用户注册 GoatCounter（code=learn-agent-design）+ 开 Allow visitor counts + 填 GC_CODE 上线。截图核查首页绿点胶囊「已有 3 人学过 · 3 次阅读」已亮（真实 UV）。讲清 GoatCounter 去重=hash(IP+UA+每日盐)、不存IP不用cookie、8h session、隐私友好偏保守。F14 passing。
- **Module D 开工**：用户选「独立 Module D 21 设计模式」（源 Google Agentic Design Patterns / xindoo 中文）。定位=按「21 可复用实现模式」切，补前三模块盲区，不重复已讲。build.py 加 MODULES["d"] + 循环 ("a","b","c","d") + by_mod。
- 第 0 讲「21 模式全景地图」已写（21 行索引大表 + 6 组 + ✅🟡❌ 标注本课覆盖；本身是 Module D 的目录+路线图）。build 通过侧栏含第四模块。
- **下一步**：派子 agent 从 xindoo 仓库章节提炼 6 类盲区深入讲（反思/学习适应/RAG/A2A/推理/优先级探索），合并 4-5 讲。

### 2026-06-05（再补 6 图 + 访问统计框架）
- 补图至 14 张：边界4模式台阶/上下文稳定易变/Gateway五职责/框架光谱/指令文件柜/三层校验。截图核查台阶图无压线。覆盖几乎每讲。
- **访问统计**：用户要「多少人看过/正在学习」。交底=纯静态做不了真实时在线，不造假。定方案：GoatCounter（隐私友好，用户注册1次）+「正在学习」用真实近似「已有 N 人学过」(累计 UV)。
- build.py 加 GC_CODE 变量 + gc_tracking()（PV 统计 script）+ stats_block()（首页 hero 显示「已有 N 人学过 · M 次阅读」，fetch GoatCounter /counter/TOTAL.json）。**空 GC_CODE 优雅降级**：不渲染任何统计 UI、不接第三方脚本（已验证 0 命中）。CSS 加 .learn-stats 胶囊样式（绿点 + 橙底）。
- **待用户做**：注册 goatcounter.com（邮箱 libaoming2@gmail.com）→ Settings 勾「Allow adding visitor counts」→ 把 site code 给我填入 GC_CODE。

### 2026-06-05（配图：8 张手绘风 SVG 框架图）
- 用户要「多放图」，参考 X 文章 Anatoli「Claude Can Do All of This」的手绘线框示意图风格（chrome 截图确认=浅底+黑墨手绘线+标注+箭头+强调色）。
- 方案：内联/独立 SVG + `feTurbulence`+`feDisplacementMap` 滤镜做轻手绘抖动；零依赖、矢量、橙皮书配色统一。先做 1 张样板（五层架构）经用户确认风格=「就这个，轻手绘线框」+ 范围=核心讲精选约 8-10 张。
- build.py 加 `![alt](src)` 图片语法 → `<figure class="diagram">`；CSS 加 figure/diagram 样式。
- 画 8 张并嵌入：five-layers/task-path/failure-nodes/error-recovery/transparency（A）+ harness/multi-agent-platform（B）+ feature-state-machine（C）。截图核查 Harness 环绕图（最难布局）文字无压线、布局均衡。build+verify 全绿。

### 2026-06-05（Module C · Harness 工程 7 讲）
- 用户要把 walkinglabs《Harness Engineering》作为第三个讲义模块放进来，取向=融合作者实战方法论，精选核心 7 讲。
- build.py 加 MODULES["c"] + 4 处循环 ("a","b")→("a","b","c") + by_mod 加 c。
- 派 7 子 agent 融合写作：每个 prompt 自包含 walkinglabs 该讲框架要点 + 让子 agent 读**本项目自己的 harness 文件**（CLAUDE.md/STATUS/features.json/三件套/verify.sh，活样本）+ 用户方法论 memory。自指效果强。
- 7 讲：为何仍失败/Harness是什么(五子系统×四层防御对照)/仓库即事实源/指令拆分/跨会话连续/边界与featurelist/端到端与交接。build 19讲+3示例全绿。
- **配图需求待办**：用户要「内容多放图」，参考 X 文章 https://x.com/AnatoliKopadze/status/2057813254617858078 风格——需先确认风格再做（与之前「配图克制」设定有张力）。

### 2026-06-05（对齐学习体系：模块导语 + 实战示例区）
- 用户指出课程站缺了他学习体系里的「模块介绍」和「示例介绍」（学习路径文档=阶段→L章节→Q&A 案例的结构）。
- 加 **模块导语**：MODULES dict 加 intro 字段（定位/讲次编排/适合谁），module 页渲染成浅灰导语卡片。
- 加 **实战示例区**（独立第三区，仿 walkinglabs projects）：build.py 重写支持 content/examples/ + 侧栏第三分组（绿色「例」徽章）+ examples.html 列表 + 详情页（复用讲义模板）。
- 派 3 子 agent 从 vault syntheses 提炼实战示例：Claude Code（五层/透明度/上下文）、Cursor（上下文工程/diff 人在环）、垂直 AI-OS（Parrot+Lassie 对照，深井 vs 通吃）。
- build：12 讲 + 3 示例，verify 全绿；截图核查 module-a 导语 + 侧栏三区到位。

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
