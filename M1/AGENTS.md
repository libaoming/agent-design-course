# M1 Session Kickoff（开新会话先读这份）

> 接班说明：不靠任何人讲背景，10 分钟内选到正确的下一件事干。
> 依据：Anthropic "Effective Harnesses for Long-Running Agents"。

## 0. 一句话定位
把本地 Obsidian wiki 的 Agent 学习材料，重写成 walkinglabs 式「问题驱动讲义体」的公开课。纯静态 HTML + 轻构建脚本，橙皮书风。

## 1. Session 启动 5 步
1. `cat M1/PROGRESS.md` → 看 active_feature / blockers / next_candidates
2. 读 `../STATUS.md` → 一句话状态 + 踩坑
3. `bash M1/init.sh` → 环境全绿才开工
4. 按"选 feature 算法"挑下一件事
5. 动手 → 收尾更新 PROGRESS.md + STATUS.md

## 2. 选 feature 算法
1. 优先 `status=failing` 且 `blocking` 已全 passing 的最低编号 feature
2. 没有则取 `pending` 且依赖已 passing 的
3. 同一 slice 内做完再进下一 slice（S1→S2→S3→S4，不跳）

## 3. 4 条硬规矩
1. **fixture 先于代码**：第1讲 markdown 是 build 的 fixture，先写讲义再调脚本
2. **build 过检查清单才改 passing**：草稿写完只到 in_progress（检查清单见 CLAUDE.md verify 纪律）
3. **不跳 slice**：S1 没端到端跑通不开 S2
4. **收尾必更新 PROGRESS.md + STATUS.md**

## 4. 讲义体写作铁律（这个项目的灵魂）
- 标题用「为什么 Agent 会 X / 为什么 X 重要」句式
- 结构：立靶（失败模式）→ 框架（表格/MECE）→ 数据/case → 可操作做法 → 一句话收口
- **重写不是搬运**：派子 agent 读 vault 笔记回草稿，主 context 不整篇 Read 原文
- 禁 emoji，图标用 line-SVG，配图每讲 ≤ 3-5 张

## 5. commit 规范
`{feat|fix|refactor|docs|content}(feature_id): 描述`

## 6. 反模式
过早宣布胜利 / 一次堆 20 讲 / 笔记直接粘贴当讲义 / 环境不可复现 / 缺端到端 build 验证。
