#!/bin/bash
# Hook for LLM rubric judge - sourced at end of test.sh

if [[ "${LLM_JUDGE:-0}" == "1" ]] && [[ -f /tests/rubric.yaml ]]; then
    echo ""
    echo "=== LLM RUBRIC JUDGE ==="
    ICR=$(python3 /tests/judge.py /tests/rubric.yaml /workspace/react 2>/dev/null || echo "0.5")
    echo "ICR (Individual Config Rule) score: $ICR"

    # Add weighted ICR to score (max 0.10 for style/config rubric)
    STYLE_SCORE=$(python3 -c "print(0.10 * float('$ICR'))")
    SCORE=$(python3 -c "print(min(1.0, $SCORE + $STYLE_SCORE))")

    echo "Final score with rubric: $(printf "%.2f" "$SCORE")"
    echo "$SCORE" > /logs/verifier/reward.txt
fi
