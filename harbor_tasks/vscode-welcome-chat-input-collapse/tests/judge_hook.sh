#!/bin/bash
# Judge hook - sourced at end of test.sh when LLM_JUDGE=1

if [ "${LLM_JUDGE:-0}" != "1" ]; then
    exit 0
fi

if [ -f /tests/judge.py ]; then
    echo "Running LLM rubric judge..."
    JUDGE_RESULT=$(python3 /tests/judge.py 2>/dev/null || echo '{"score": 0}')
    JUDGE_SCORE=$(echo "$JUDGE_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total',0))" 2>/dev/null)

    # Read current reward
    CURRENT=$(cat /logs/verifier/reward.txt 2>/dev/null || echo "0")

    # Add rubric score (10% weight)
    NEW_REWARD=$(python3 -c "print(min(1.0, $CURRENT + $JUDGE_SCORE * 0.10))" 2>/dev/null)

    echo "$NEW_REWARD" > /logs/verifier/reward.txt
    echo "LLM Judge score: $JUDGE_SCORE, updated reward: $NEW_REWARD"
fi
