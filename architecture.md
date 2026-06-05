# Architecture — learn-agent-design

> 文档先行。设计原则 + 系统图 + 模块职责 + 数据流 + 关键决策。

## 设计原则
1. **内容与呈现分离**：讲义是纯 markdown（可移植、易写、可溯源到 vault）；样式集中在一份 CSS；脚本只做"内容→HTML"。
2. **零依赖优先**：标准库能做就不引三方库；产物是纯静态文件，无运行时。
3. **重写不搬运**：内容经子 agent 从 vault 提炼成讲义体，主线只做定稿。
4. **线性切片**：先一讲端到端跑通，再规模化填充。
5. **可验证**：每个 feature 有 build/grep 级别的客观成功信号。

## 系统总览
```
  Obsidian vault wiki (私人材料源, 只读)
            │  子 agent 读 + 重写（脱敏）
            ▼
  content/module-{a,b}/*.md   ← 讲义源（frontmatter + 讲义体正文）
            │
            ▼
  scripts/build.py            ← 解析 md → 套模板 → 生成 HTML + 导航
        │        │
        │        └── assets/orangebook.css（+ line-SVG 图标）
        ▼
  site/  index.html / module-*.html / {module}/{slug}.html
            │
            ▼
  GitHub Pages（相对路径，纯静态托管）
```

## 模块职责
| 模块 | 职责 | 不负责 |
|---|---|---|
| `content/` | 讲义源（唯一内容事实源） | 不含样式/脚本 |
| `scripts/build.py` | 解析 + 渲染 + 导航生成 + 拷资源 | 不写内容、不做服务端 |
| `scripts/verify.sh` | 端到端验证（build + 标题 + 无 emoji + 链接） | 不改文件 |
| `assets/` | 视觉系统 CSS + 图标 | 不含内容 |
| `site/` | build 产物（gitignore） | 手改无效，下次 build 覆盖 |
| `.claude/agents/*-ops` | 从 vault 提炼讲义草稿（脏活隔离） | 不定稿（主线定稿） |

## 数据流
1. 主 agent 决定要写哪一讲 → 派子 agent 读 vault 指定笔记 → 子 agent 回讲义体草稿。
2. 主 agent 定稿润色 → 写入 `content/module-x/NN-slug.md`（带 frontmatter）。
3. `build.py` 扫描 `content/` → 解析 → 按 module/order 排序生成导航 → 渲染三类页面 → 写 `site/`。
4. `verify.sh` 跑 build + 检查清单 → 通过则 feature 可标 passing。
5. 推 `site/` 到 GitHub Pages。

## 关键技术决策
| 决策 | 备选 | 为什么选它 |
|---|---|---|
| 极简手写 markdown 解析器（标准库） | 引 `markdown`/`mistune` 库 | 满足 SPEC 的子集即可，保零依赖、可控、易部署；若子集不够再降级引库并记 requirements |
| 一份 CSS 全站复用 | 每页内联样式 | 改样式一处生效，符合橙皮书统一调性 |
| frontmatter 驱动导航 | 手维护导航列表 | 新增讲义自动进导航，杜绝漏挂 |
| `site/` gitignore | 提交产物 | 产物可复现，避免脏 diff；GitHub Pages 可用 Actions 构建或推 gh-pages 分支 |
| Python 而非 Node | Node SSG | 用户环境有 python3，且避免 Node 构建链复杂度（SPEC 反模式） |

## 风险与对策
- **markdown 子集不够用** → 先覆盖 SPEC 列出的子集；遇到不支持语法，要么改写讲义，要么补解析器，要么降级引库（记 requirements.txt）。
- **vault 脱敏遗漏** → 子 agent 重写时显式去标识；主线定稿再过一遍。
- **配图喧宾夺主** → CSS 限制图片最大宽度 + 讲义体以文字与表格为主。
