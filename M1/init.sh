#!/bin/bash
# M1/init.sh — 环境自检（走完统一报告，不用 set -e）
# fixture 缺失只 WARN，依赖/env 缺失记 FAIL。

cd "$(dirname "$0")/.." || exit 1
WARN=0; FAIL=0
ok(){ echo "  ✅ $1"; }
warn(){ echo "  ⚠️  $1"; WARN=$((WARN+1)); }
fail(){ echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo "== 1. 依赖 =="
command -v python3 >/dev/null && ok "python3 $(python3 --version 2>&1 | awk '{print $2}')" || fail "python3 缺失"

echo "== 2. 内容源 =="
[ -d "$HOME/Documents/Obsidian Vault/wiki" ] && ok "vault wiki 可达" || warn "vault wiki 不可达（重写讲义时需要）"

echo "== 3. schema =="
[ -f features.json ] && python3 -c "import json;json.load(open('features.json'))" 2>/dev/null && ok "features.json 合法" || fail "features.json 非法"

echo "== 4. 内容结构 =="
[ -d content/module-a ] && [ -d content/module-b ] && ok "content/ 双模块目录就位" || fail "content/ 目录缺失"

echo "== 5. fixtures =="
[ -d fixtures/first-lecture ] && ok "第1讲 fixture 存在" || warn "fixtures/first-lecture 缺失（先造 fixture）"

echo "== 6. 端到端冒烟 =="
if [ -f scripts/build.py ]; then
  python3 scripts/build.py >/dev/null 2>&1 && [ -f site/index.html ] && ok "build 产出 site/index.html" || fail "build 失败或无产物"
else
  warn "scripts/build.py 未创建（F03 未做）"
fi

echo ""
echo "== 自检结果：FAIL=$FAIL WARN=$WARN =="
[ "$FAIL" -gt 0 ] && echo "🔴 有阻塞项，先修 FAIL 再开工" || echo "🟢 可开工（WARN 不阻塞）"
