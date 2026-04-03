#!/usr/bin/env bash
# Hook sourced at end of test.sh for LLM rubric judge

if [ "${LLM_JUDGE:-0}" = "1" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    log "=== Running LLM rubric judge ==="
    ICR=$(python3 /tests/judge.py /tests/rubric.yaml /workspace/vscode 2>/dev/null || echo "0.0")
    style_rubric=$(python3 -c "print(0.10 * float('$ICR'))")
    score=$(echo "$score + $style_rubric" | bc)
    log "Style rubric ICR: $ICR -> +$style_rubric"
    echo "$score" > "$REWARD_FILE"
    cat > "$REWARD_JSON" <<EOF
{"reward": $score, "behavioral": $behavioral, "structural": $structural, "config": $config_score, "style_rubric": $style_rubric}
EOF
fi
