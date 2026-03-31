#!/usr/bin/env bash
set +e

REPO_DIR="/repo"
cd "$REPO_DIR"

TOTAL=0
add_score() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

FILE="crates/uv/src/commands/tool/list.rs"

###############################################################################
# GATE: Syntax check — file must compile
###############################################################################
# [pr_diff] (gate): Modified file must be valid Rust
echo "=== GATE: cargo check ==="
if ! cargo check -p uv --quiet 2>&1; then
    echo "GATE FAILED: cargo check failed"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE passed."

###############################################################################
# FAIL-TO-PASS: Integration test — exclude-newer respected per tool (0.55)
###############################################################################
# [pr_diff] (0.55): tool_list_outdated_respects_exclude_newer — tools installed
# with --exclude-newer must not be flagged outdated against absolute latest
echo "=== F2P: integration test ==="
if cargo test --test tool_list -- tool_list_outdated_respects_exclude_newer --exact 2>&1; then
    echo "PASS: tool_list_outdated_respects_exclude_newer"
    add_score 0.55
else
    echo "FAIL: tool_list_outdated_respects_exclude_newer"
fi

###############################################################################
# PASS-TO-PASS: Existing tool_list tests (0.20)
###############################################################################
# [pr_diff] (0.10): tool_list_show_paths must still pass
echo "=== P2P: tool_list_show_paths ==="
if cargo test --test tool_list -- tool_list_show_paths --exact 2>&1; then
    echo "PASS: tool_list_show_paths"
    add_score 0.10
else
    echo "FAIL: tool_list_show_paths"
fi

# [pr_diff] (0.10): tool_list_outdated must still pass
echo "=== P2P: tool_list_outdated ==="
if cargo test --test tool_list -- tool_list_outdated --exact 2>&1; then
    echo "PASS: tool_list_outdated"
    add_score 0.10
else
    echo "FAIL: tool_list_outdated"
fi

###############################################################################
# STRUCTURAL: Anti-stub (0.10)
###############################################################################
# [pr_diff] (0.05): LatestClient must still be constructed (not removed/stubbed)
echo "=== STRUCTURAL: anti-stub ==="
STRUCT_SCORE=0
if grep -q 'LatestClient' "$FILE"; then
    STRUCT_SCORE=$(python3 -c "print($STRUCT_SCORE + 0.05)")
    echo "PASS: LatestClient still present"
else
    echo "FAIL: LatestClient missing — likely stubbed out"
fi

# [pr_diff] (0.05): The outdated section must have non-trivial implementation.
# Any valid fix adds per-tool client construction, increasing the section size.
# Buggy code has ~20 lines between 'if outdated' and 'buffer_unordered'.
# A valid fix needs at least ~25 lines for per-tool construction logic.
OUTDATED_START=$(grep -n 'if outdated' "$FILE" | head -1 | cut -d: -f1)
BUFFER_LINE=$(grep -n 'buffer_unordered' "$FILE" | head -1 | cut -d: -f1)
if [ -n "$OUTDATED_START" ] && [ -n "$BUFFER_LINE" ]; then
    SECTION_LEN=$((BUFFER_LINE - OUTDATED_START))
    if [ "$SECTION_LEN" -ge 30 ]; then
        STRUCT_SCORE=$(python3 -c "print($STRUCT_SCORE + 0.05)")
        echo "PASS: outdated section has $SECTION_LEN lines (non-trivial)"
    else
        echo "FAIL: outdated section only $SECTION_LEN lines (likely not per-tool)"
    fi
else
    echo "SKIP: couldn't locate outdated section boundaries"
fi

add_score "$STRUCT_SCORE"

###############################################################################
# CONFIG-DERIVED: CLAUDE.md rules (0.15)
###############################################################################
# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap()" — CLAUDE.md:8 @ c1cd212
echo "=== CONFIG: no unwrap/panic ==="
OUTDATED_START=$(grep -n 'if outdated' "$FILE" | head -1 | cut -d: -f1)
BUFFER_LINE=$(grep -n 'buffer_unordered' "$FILE" | head -1 | cut -d: -f1)
if [ -n "$OUTDATED_START" ] && [ -n "$BUFFER_LINE" ]; then
    SECTION=$(sed -n "${OUTDATED_START},${BUFFER_LINE}p" "$FILE")
    if echo "$SECTION" | grep -qE '\.unwrap\(\)|panic!\(|unreachable!\(\)'; then
        echo "FAIL: unwrap/panic found in outdated section"
    else
        echo "PASS: no unwrap/panic in outdated section"
        add_score 0.05
    fi
else
    echo "SKIP: couldn't locate outdated section"
fi

# [agent_config] (0.05): "PREFER top-level imports over local imports" — CLAUDE.md:15 @ c1cd212
echo "=== CONFIG: top-level imports ==="
FUNC_START=$(grep -n 'pub(crate) async fn list' "$FILE" | head -1 | cut -d: -f1)
if [ -n "$FUNC_START" ]; then
    FUNC_BODY=$(sed -n "${FUNC_START},\$p" "$FILE")
    LOCAL_IMPORTS=$(echo "$FUNC_BODY" | tail -n +3 | grep -c '^\s*use ' || true)
    if [ "$LOCAL_IMPORTS" -eq 0 ]; then
        echo "PASS: no local imports inside function"
        add_score 0.05
    else
        echo "FAIL: found $LOCAL_IMPORTS local import(s) inside function"
    fi
else
    echo "SKIP: couldn't locate list function"
fi

# [agent_config] (0.05): "PREFER if let / let chains for fallibility" — CLAUDE.md:9 @ c1cd212
# Check for bare .expect() calls in the modified section (same spirit as no unwrap)
echo "=== CONFIG: prefer if-let for fallibility ==="
if [ -n "$OUTDATED_START" ] && [ -n "$BUFFER_LINE" ]; then
    SECTION=$(sed -n "${OUTDATED_START},${BUFFER_LINE}p" "$FILE")
    if echo "$SECTION" | grep -qE '\.expect\(' ; then
        echo "FAIL: .expect() found in outdated section — use ? or if let"
    else
        echo "PASS: no .expect() in outdated section"
        add_score 0.05
    fi
else
    echo "SKIP: couldn't locate outdated section"
fi

###############################################################################
# FINAL SCORE
###############################################################################
echo ""
echo "=== TOTAL SCORE: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
import json
total = $TOTAL
print(json.dumps({'reward': total}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
