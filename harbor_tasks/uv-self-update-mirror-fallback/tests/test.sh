#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/workspace/uv"
FILE="crates/uv-bin-install/src/lib.rs"
TOTAL=0.0

add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

cd "$REPO_DIR"

# ── GATE: file exists and is valid UTF-8 ──
# [pr_diff] (0): Syntax gate — abort if target file is missing or corrupt
if ! python3 -c "open('$FILE', encoding='utf-8').read()" 2>/dev/null; then
    echo "GATE FAILED: $FILE is missing or not valid UTF-8"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

set +e

# ── Helper: strip Rust comments from source text ──
# Returns source with // line comments and /* block comments */ removed
strip_comments() {
    python3 -c "
import re, sys
src = sys.stdin.read()
# Remove block comments (non-greedy, handles multiline)
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
# Remove line comments
src = re.sub(r'//[^\n]*', '', src)
print(src)
"
}

# ── Helper: extract a function body from the Rust source (comments stripped) ──
# Justification for structural checks: Rust code requires full workspace
# compilation (~30 min + toolchain) which is impractical in the test env.
extract_fn() {
    python3 -c "
import re, sys
src = open('$FILE').read()
# Strip comments first to prevent gaming
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
src = re.sub(r'//[^\n]*', '', src)
# Find function and extract its body using brace counting
pat = re.compile(r'fn\s+${1}\s*[\(<]')
m = pat.search(src)
if not m:
    sys.exit(1)
start = src.index('{', m.start())
depth = 0
for i in range(start, len(src)):
    if src[i] == '{': depth += 1
    elif src[i] == '}': depth -= 1
    if depth == 0:
        print(src[m.start():i+1])
        break
"
}

# ── Behavioral 1: Binary::Uv includes mirror URL ──
# [pr_diff] (0.20): Binary::Uv should fetch from VERSIONS_MANIFEST_MIRROR
UV_ARM=$(extract_fn manifest_urls | python3 -c "
import sys
src = sys.stdin.read()
idx = src.find('Self::Uv')
if idx < 0:
    sys.exit(1)
# Find the next match arm or closing brace
rest = src[idx:]
depth = 0
for i, c in enumerate(rest):
    if c == '{': depth += 1
    elif c == '}': depth -= 1
    if depth < 0:
        print(rest[:i])
        break
else:
    print(rest)
" 2>/dev/null) || UV_ARM=""

if echo "$UV_ARM" | grep -q 'VERSIONS_MANIFEST_MIRROR'; then
    add 0.20
    echo "PASS (0.20): Binary::Uv includes VERSIONS_MANIFEST_MIRROR"
else
    echo "FAIL (0.20): Binary::Uv does not include VERSIONS_MANIFEST_MIRROR"
fi

# ── Behavioral 2: Binary::Uv has two URLs (mirror first, then canonical) ──
# [pr_diff] (0.15): Uv arm should have mirror before canonical, matching Ruff pattern
if echo "$UV_ARM" | grep -q 'VERSIONS_MANIFEST_MIRROR' && echo "$UV_ARM" | grep -q 'VERSIONS_MANIFEST_URL'; then
    MIRROR_POS=$(echo "$UV_ARM" | grep -n 'VERSIONS_MANIFEST_MIRROR' | head -1 | cut -d: -f1)
    CANON_POS=$(echo "$UV_ARM" | grep -n 'VERSIONS_MANIFEST_URL' | head -1 | cut -d: -f1)
    if [ -n "$MIRROR_POS" ] && [ -n "$CANON_POS" ] && [ "$MIRROR_POS" -lt "$CANON_POS" ]; then
        add 0.15
        echo "PASS (0.15): Binary::Uv has mirror before canonical URL"
    else
        echo "FAIL (0.15): Binary::Uv has URLs in wrong order (mirror should come first)"
    fi
else
    echo "FAIL (0.15): Binary::Uv does not have both mirror and canonical URLs"
fi

# ── Behavioral 3: ManifestParse triggers fallback ──
# [pr_diff] (0.15): should_try_next_url must return true for ManifestParse
FALLBACK_FN=$(extract_fn should_try_next_url 2>/dev/null) || FALLBACK_FN=""

if echo "$FALLBACK_FN" | grep -qE 'ManifestParse'; then
    PARSE_CONTEXT=$(echo "$FALLBACK_FN" | grep -A3 'ManifestParse')
    if echo "$PARSE_CONTEXT" | grep -q 'true'; then
        add 0.15
        echo "PASS (0.15): ManifestParse triggers URL fallback"
    else
        echo "FAIL (0.15): ManifestParse found but does not map to true"
    fi
else
    echo "FAIL (0.15): ManifestParse not handled in should_try_next_url"
fi

# ── Behavioral 4: ManifestUtf8 triggers fallback ──
# [pr_diff] (0.15): should_try_next_url must return true for ManifestUtf8
if echo "$FALLBACK_FN" | grep -qE 'ManifestUtf8'; then
    UTF8_CONTEXT=$(echo "$FALLBACK_FN" | grep -A3 'ManifestUtf8')
    if echo "$UTF8_CONTEXT" | grep -q 'true'; then
        add 0.15
        echo "PASS (0.15): ManifestUtf8 triggers URL fallback"
    else
        echo "FAIL (0.15): ManifestUtf8 found but does not map to true"
    fi
else
    echo "FAIL (0.15): ManifestUtf8 not handled in should_try_next_url"
fi

# ── Regression 1: Binary::Ruff still has both URLs ──
# [pr_diff] (0.10): Ruff arm must still have mirror + canonical
RUFF_ARM=$(extract_fn manifest_urls | python3 -c "
import sys
src = sys.stdin.read()
idx = src.find('Self::Ruff')
if idx < 0:
    sys.exit(1)
rest = src[idx:]
depth = 0
for i, c in enumerate(rest):
    if c == '{': depth += 1
    elif c == '}': depth -= 1
    if depth < 0:
        print(rest[:i])
        break
else:
    print(rest)
" 2>/dev/null) || RUFF_ARM=""

if echo "$RUFF_ARM" | grep -q 'VERSIONS_MANIFEST_MIRROR' && echo "$RUFF_ARM" | grep -q 'VERSIONS_MANIFEST_URL'; then
    add 0.10
    echo "PASS (0.10): Binary::Ruff still has both mirror and canonical URLs"
else
    echo "FAIL (0.10): Binary::Ruff is missing mirror or canonical URL"
fi

# ── Regression 2: Download and ManifestFetch still trigger fallback ──
# [pr_diff] (0.10): Existing fallback triggers must not be removed
PASS_R2=true
if ! echo "$FALLBACK_FN" | grep -q 'Download'; then
    echo "FAIL (0.10): Download removed from should_try_next_url"
    PASS_R2=false
fi
if ! echo "$FALLBACK_FN" | grep -q 'ManifestFetch'; then
    echo "FAIL (0.10): ManifestFetch removed from should_try_next_url"
    PASS_R2=false
fi
if [ "$PASS_R2" = true ]; then
    add 0.10
    echo "PASS (0.10): Download and ManifestFetch still trigger fallback"
fi

# ── Config-derived: No panic!/unreachable! in manifest_urls ──
# [agent_config] (0.05): "AVOID using panic!, unreachable!" — CLAUDE.md:7 @ 7228ad62
MANIFEST_FN=$(extract_fn manifest_urls 2>/dev/null) || MANIFEST_FN=""
if echo "$MANIFEST_FN" | grep -qE '\bpanic!\b|\bunreachable!\b'; then
    echo "FAIL (0.05): manifest_urls contains panic! or unreachable!"
else
    add 0.05
    echo "PASS (0.05): No panic!/unreachable! in manifest_urls"
fi

# ── Anti-stub: manifest_urls Uv arm has actual vec!/array construction ──
# [pr_diff] (0.05): Uv arm must have actual URL construction, not a stub
UV_ARM_LINES=$(echo "$UV_ARM" | grep -cE '\S' 2>/dev/null || echo 0)
HAS_VEC=$(echo "$UV_ARM" | grep -cE 'vec!|Vec::|\[' 2>/dev/null || echo 0)
if [ "$UV_ARM_LINES" -ge 3 ] && [ "$HAS_VEC" -ge 1 ]; then
    add 0.05
    echo "PASS (0.05): Binary::Uv arm is substantial (${UV_ARM_LINES} non-blank lines, has collection construction)"
else
    echo "FAIL (0.05): Binary::Uv arm looks like a stub (${UV_ARM_LINES} lines, vec/array: ${HAS_VEC})"
fi

# ── Write results ──
echo ""
echo "Total: $TOTAL / 1.0"
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
import json
total = $TOTAL
json.dump({
    'reward': total,
    'behavioral': round(min(0.65, total), 4),
    'regression': round(max(0, min(0.20, total - 0.65)), 4),
    'config': round(max(0, min(0.05, total - 0.85)), 4),
    'structural': round(max(0, min(0.05, total - 0.90)), 4)
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
