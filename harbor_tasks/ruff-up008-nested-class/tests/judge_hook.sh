#!/usr/bin/env bash
#
# LLM rubric judge hook. Source this at the end of test.sh:
#
#   source /tests/judge_hook.sh
#
# Controlled by env vars:
#   LLM_JUDGE=1           — enable the judge (set by --with-judge flag)
#   ANTHROPIC_API_KEY=... — required for API calls
#   JUDGE_WEIGHT=0.15     — weight of the judge score (default 0.15)
#
# When disabled: deterministic score is used as-is.
# When enabled: score = (1 - JUDGE_WEIGHT) * deterministic + JUDGE_WEIGHT * ICR
#

JUDGE_WEIGHT="${JUDGE_WEIGHT:-0.15}"

RUBRIC_PATH="/tests/rubric.yaml"
[ -f "$RUBRIC_PATH" ] || RUBRIC_PATH="/rubric.yaml"

if [ "${LLM_JUDGE:-0}" = "1" ] && [ -n "${ANTHROPIC_API_KEY:-}" ] && [ -f "$RUBRIC_PATH" ] && [ -f /tests/judge.py ]; then
    # Check if rubric has any rules (no yaml dependency — just grep)
    HAS_RULES=$(grep -c '^\s*- rule:' "$RUBRIC_PATH" 2>/dev/null || echo "0")

    if [ "$HAS_RULES" != "0" ]; then
        echo ""
        echo "=== LLM Rubric Judge ==="
        # Get workspace dir (first dir in /workspace/)
        WORKSPACE=$(ls -d /workspace/*/ 2>/dev/null | head -1)
        if [ -z "$WORKSPACE" ]; then
            WORKSPACE="/workspace"
        fi

        ICR=$(python3 /tests/judge.py "$RUBRIC_PATH" "$WORKSPACE" 2>&1 | tail -1)
        echo "  ICR score: $ICR"

        # Recompute: blend deterministic score with judge
        CURRENT=$(cat /logs/verifier/reward.txt 2>/dev/null || echo "0")
        BLENDED=$(python3 -c "
det = float('$CURRENT')
icr = float('$ICR')
w = float('$JUDGE_WEIGHT')
blended = (1.0 - w) * det + w * icr
print(f'{min(1.0, max(0.0, blended)):.4f}')
" 2>/dev/null || echo "$CURRENT")

        echo "  Deterministic: $CURRENT"
        echo "  Blended: $BLENDED (det=$(python3 -c "print(1-$JUDGE_WEIGHT)") + judge=$JUDGE_WEIGHT)"
        echo "$BLENDED" > /logs/verifier/reward.txt
    else
        echo ""
        echo "=== LLM Judge: skipped (no rules in rubric) ==="
    fi
fi
