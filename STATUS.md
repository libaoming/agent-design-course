# STATUS — learn-agent-design

> 每次 session 第一个读的文件。收尾必更新本文件。

## 一句话状态（2026-06-16 新增 Module E · 上下文工程）
**5 讲义模块 31 讲**（A 产品能力 6 / B 工程地基 6 / C Harness 工程 7 / D 设计模式 5 / **E 上下文工程 7**）+ 3 实战示例 + 18 张轻手绘 SVG 框架图 + 每页「已有 N 人学过本课程」统计（GoatCounter）。模块导语 + GitHub Actions 自动部署。**（⚠️ 2026-06-19 已改版为「橙研所」博客流：侧栏导航→顶部 nav、课程→博客、「N 人学过」已删，详见下方「网站改版」段）**

**2026-06-16 新增 Module E · Context Engineering 上下文工程**：与 A（产品能力）/ C（Harness）并列的第三大支柱，源自 CE 7 单元自学体系。S5 切片，**第 0 讲「CE 总览·七层与暗物质」已上线**（七层次表 + 暗物质 + CE/PE/Harness 辨析，五段式）。**全程脱敏**：私人项目写成「某语音 agent / 某成熟产品」，build 后跑 grep 闸门确认零命中（妙招/豆包/ECS/评级等）。**E01-E06（U2-U7 各层深入讲）于 2026-06-16 全部完稿上线**：prompt 分层 / 结构化 IO+工具 / 记忆+RAG / 历史+压缩 / cache 工程 / 可观测+eval，均「为什么 X」立靶句式 + 五段式，build/verify 全绿、脱敏 grep 干净。features.json 全 22 feature passing。

> 早期状态（2026-06-05 主体完成）：4 模块 24 讲全 passing，Module C 融合 walkinglabs + 本项目实战方法论（自指），Module D 源 Google《Agentic Design Patterns》/xindoo 仓库。
关联：libaoming.github.io 根站 2017 旧简历已换成跳转课程站的占位页（另一仓库 libaoming/libaoming.github.io，旧源码在 git 历史可恢复）。

## 🎨 网站改版（2026-06-19，方向 B：从「在线课程」→「橙研所」个人 IP 博客流，对标 claude.com/blog）
**动机**：原站太像在线课程（左侧课程目录 sidebar + 模块/讲/「N 人学过本课程」），定位应是个人 Build in Public 思想阵地。**已上线**：
- **骨架**：左 sidebar → **顶部横向 nav**（橙研所品牌 + 5 主线 + 实战 + 主题/语言），全宽布局；shell 全站统一（`topnav()`/`site_footer()`，旧 `sidebar()` 保留未用）。
- **首页**：博客 hero（左定位 + 右 5 主线大字入口，serif）+ 作者卡 + **每主线精选 3 篇卡片网格 + 「查看全部 N 篇 →」**（不再全量铺开）。
- **卡片**：竖卡（封面 banner + 分类 + 标题 + 摘要），3 列 grid（`lecture_card`/`example_card` 改造）。
- **封面**：柔和粉彩 5 色板（A 陶土 / B sage / C 淡紫 / D 玫瑰 / E 雾蓝）+ 黑色线条图标（`MOD_ICON` 模块级）+ 去网格纹理，暗色降饱和适配。
- **去课程化文案**：站名「构建 AI Agent」→**「橙研所」**（en「ChengYanSuo」）；「讲」→「篇」、「Lecture」→「Post」；title 带「· 橙研所」后缀。
- **serif**：零加载系统衬线栈（Georgia + 宋体）；英文站标题全衬线、中文 hero 大标题宋体。
- 改动集中在 `scripts/build.py` + `assets/orangebook.css`，讲义内容一字未动。

**🔴 下一轮待办（用户明确要）**：**每篇封面图标做成不同的**——现在同主线 6-7 张卡共用一个图标（`MOD_ICON` 模块级），重复。要按 slug 给 31 讲 + 3 实战各配独特 line-art（清单已在 2026-06-19 session 拉取，见 `content/module-*/`）。更进一步可走 AI 生图做 claude 那种叙事插画。
**可选**：分类筛选交互、精选条横排、中文 serif 是否扩到正文标题（现仅 hero）。

## ✅ 已收口（2026-06-19）：英文版 i18n 全量翻译已上线 + 国内备案待排

**背景**：站点托管 GitHub Pages，国内访问长期被污染/限速。确定方向 = **出海·面向英文开发者**（GitHub Pages 对海外无障碍），做英文版；国内访问问题单独走备案另排。

**① 英文版 i18n（✅ 完成 2026-06-18，已部署）**：全量 34 篇（31 讲 + 3 实战）译文落地，commit `0948ba7` 已 push，GitHub Actions「Deploy site to GitHub Pages」run = success。英文站 `chengyansuo.com/en/` 上线。实现回顾（决策记录留存）：
- URL：`/en/` 子目录（中文留根 `chengyansuo.com/`，英文 `chengyansuo.com/en/`）。GitHub Pages 单仓库唯一干净方案。
- build.py：UI 串抽成 `STRINGS[lang]` 字典，`build()` 跑两遍（zh→根 / en→/en/），侧栏加语言切换器，`<html lang>` 跟随。
- 内容：每篇 `NN-slug.md` 配兄弟文件 `NN-slug.en.md`（自带英文 frontmatter，译 title/nav/summary + 正文）；`collect()` 找 `.en.md`，缺失则该语言跳过该讲（允许渐进翻译）。
- 范围：**全量 34 篇**（31 讲 + 3 实战），译文派子 agent 并行（L4 隔离）。
- ✅ 框架图英文化（2026-06-19 完成）：18 张 `assets/diagrams/*.svg` 各出英文版 `x.en.svg`（派 4 子 agent 并行翻译内嵌中文，主线 qlmanage 逐张渲染核查、修了 6 张英文变长导致的溢出/重叠）。机制 = build.py 复制 en assets 后用 `x.en.svg` 覆盖同名 `x.svg`，中英两站各用各的图，markdown 零改动。验证：英文站 18 张全英文、中文站 18 张未损、产物无 `.en.svg` 残留。

**② 国内备案（待办·排期，需用户本人办）**：
- 目的：让国内读者也能访问 chengyansuo.com（与英文版正交，解的是「国内打不开」）。
- 路径：买国内云服务器/静态托管（腾讯云 COS / 阿里云 OSS + CDN）→ 域名实名认证 → **工信部 ICP 备案**（云厂商代提交，周期约 2-3 周）→ 把静态产物 `site/` 同步上去（或国内镜像）。
- 现状：**未启动**。GNAME 注册的 chengyansuo.com 需先做域名实名。备案是用户本人走云厂商流程，Claude 不能代办，此处仅记录排期。
- 备选（免备案缓解）：Cloudflare 代理 / Vercel，能改善但国内仍不稳，备案才是根治。

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
- **跨 session 工具返回污染（2026-06-17）**：多个 Claude Code session 并发运行时，工具（Bash/Read）的返回结果出现重复行、隐藏 Unicode 双向控制字符（U+202E 等）、以及假的「Wasted call / file unchanged / file does not exist」拦截。**根因（经 Explore 子 agent 调查更正）**：全局 `~/.claude/settings.json` 里**没有任何 PostToolUse hook**；曾怀疑的两个 async Stop/SessionEnd hook（`ccclub sync --silent`、`sync-memory-to-obsidian.py`）在当前配置下**都不向 stdout 打印**（前者 silent 禁 console.log，后者无 --verbose），故**不是**串流来源——"async hook 嫌疑"已被否定。真正根因更可能在 **harness 自身**：多 session 并发时共享的转录缓冲区 / 流处理，**非配置可改项**。**有效缓解**：① 别让多个 session 同时频繁结束回合；② 完全退出进程重开（`/exit`，不是 /clear）。**注**：禁用那两个 async hook 只解决"共享文件被并发无锁写坏"这个*另一个*问题（写 Obsidian vault / ccclub JSON / 日志均无锁），与本串流无关；禁用影响很小（仅失去 ccclub 排行榜同步 + Obsidian 记忆镜像，记忆本体仍在 `~/.claude/.../memory/`）。**铁律：在此环境写任何文件，写完立刻 `git diff` 校验，发现污染（重复/隐藏字符）立即 `git checkout -- <file>` 回滚，绝不留下被污染的文件。**
