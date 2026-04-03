#!/bin/bash
# Hook sourced at end of test.sh to run LLM rubric judge
# Only runs when LLM_JUDGE=1

if [ "${LLM_JUDGE:-0}" != "1" ]; then
    return 0
fi

if [ -f /tests/rubric.yaml ] && [ -d /workspace/vscode ]; then
    ICR=$(python3 /tests/judge.py /tests/rubric.yaml /workspace/vscode 2>/dev/null || echo "0.0")
    # Store ICR contribution (will be added to final score of 1.0 when test fully passes)
    echo "$ICR" > /logs/verifier/icr.txt
fi
