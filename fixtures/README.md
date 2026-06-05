# fixtures 索引

verify 引用的 fixture 都在此。**fixture 先于代码**：feature 的 verify 指向的 fixture 不存在 → 先造，不许 mock。

| fixture | 状态 | 用途 / 喂哪些 feature |
|---|---|---|
| `first-lecture/` | 待造 | F05_first_lecture（第1讲样板 markdown）+ F03_build_script（build 的输入）+ F06_e2e_verify |

## first-lecture 设计
- 选题：Module A 开篇实质讲，材料最全、最能展示「问题驱动讲义体」的丰富度。
- 候选：「为什么 Agent 的透明度不是越多越好」（L3 维度4，含三层 MECE 框架 + 5 反模式 + 2 case + 面试金句）。
- 作用：一份 fixture 养活三条 feature——它既是样板内容（F05），又是 build 脚本的真实输入（F03），又是端到端验证的检查对象（F06）。
