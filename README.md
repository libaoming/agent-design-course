# 构建 AI Agent

> 从能力设计到生产交付，一门问题驱动的 AI Agent 工程公开课。两条主线：把 Agent 当产品来设计，把 Agent 当系统来交付。

一门问题驱动讲义体的 AI Agent 工程公开课，纯静态站点，零运行时依赖。

## 课程结构

**Module A · Agent 产品与能力设计**
1. 为什么搞懂 Agent，要先把它拆成五层来看（技术地基）
2. 为什么 Agent 接到任务后，第一步不该是动手（任务完成路径）
3. 为什么 Agent 失败不能笼统归因，必须按节点拆开（失败节点）
4. 为什么没有错误恢复策略的 Agent 会一错就崩（错误恢复 4+1）
5. 为什么 Agent 的透明度不是越多越好（透明度）
6. 为什么 Agent 不会守边界就会成为危险的「瞎自信助手」（边界行为）

**Module B · Agent 工程地基**
1. 为什么换更强的模型救不了你的 Agent，先修 Harness
2. 为什么管不好上下文窗口，再聪明的 Agent 也会变蠢（上下文工程七维）
3. 为什么 Agent 上了生产，先崩的不是模型而是那层管道（Gateway 工程）
4. 为什么 Agent 框架要按需求选，而不是默认上 LangGraph（框架选型）
5. 为什么没有评测体系的 Agent 只能靠拍脑袋迭代（评测与 Benchmark）
6. 为什么多 Agent 平台不能一步到位，而要分四阶段长出来（平台架构）

## 本地预览

```bash
python3 scripts/build.py          # 构建到 site/
cd site && python3 -m http.server 8765   # 浏览器打开 http://localhost:8765
```

构建脚本是纯 Python 标准库（`scripts/build.py`），把 `content/**/*.md` 渲染成多页静态站，零三方依赖。

## 部署

push 到 `main` 由 GitHub Actions 自动构建并发布到 GitHub Pages（见 `.github/workflows/deploy.yml`）。

## 许可

内容 © baomingli。
