#!/bin/bash
# scripts/verify.sh — S1 端到端验证：build 通过 + 关键标题 + 无 emoji + 链接可达
cd "$(dirname "$0")/.." || exit 1
FAIL=0
ok(){ echo "  ✅ $1"; }
bad(){ echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo "== 1. build =="
python3 scripts/build.py && [ -f site/index.html ] && ok "build 产出 site/index.html" || { bad "build 失败"; exit 1; }

echo "== 2. 双模块 + 侧边栏出现在首页 =="
grep -q "Agent 产品与能力设计" site/index.html && grep -q "Agent 工程地基" site/index.html && grep -q 'class="sidebar"' site/index.html && ok "首页含双模块 + 侧边栏" || bad "首页缺模块或侧边栏"

echo "== 3. 第1讲渲染 =="
LEC=site/module-a/transparency.html
[ -f "$LEC" ] && ok "讲义页生成" || bad "讲义页缺失"
while IFS= read -r h; do
  [ -z "$h" ] && continue
  grep -qF "$h" "$LEC" && : || bad "缺标题: $h"
done < fixtures/first-lecture/expected-headings.txt
[ "$FAIL" -eq 0 ] && ok "全部期望标题命中"

echo "== 4. 表格渲染（讲义体核心）=="
grep -q "<table>" "$LEC" && ok "含渲染后的表格" || bad "表格未渲染"

echo "== 5. 全站无 emoji =="
if grep -rlP '[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}]' site/ >/dev/null 2>&1; then
  bad "检测到 emoji"; grep -rlP '[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}]' site/
else
  ok "无 emoji"
fi

echo "== 6. 导航链接可达 =="
grep -q 'href="../module-a.html"' "$LEC" && grep -q 'orangebook.css' "$LEC" && ok "导航+样式引用就位" || bad "导航/样式链接缺失"

echo ""
echo "== verify 结果：FAIL=$FAIL =="
[ "$FAIL" -gt 0 ] && { echo "🔴 未通过"; exit 1; } || echo "🟢 S1 端到端通过"
