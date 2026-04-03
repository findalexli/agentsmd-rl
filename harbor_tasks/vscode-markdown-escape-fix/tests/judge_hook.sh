#!/bin/bash
# Hook for LLM rubric judge
# Sourced at end of test.sh when LLM_JUDGE=1

if [[ "${LLM_JUDGE:-0}" == "1" && -f /tests/rubric.yaml ]]; then
    # rubric.yaml rules are evaluated by judge.py
    # output captured but not directly used in score for this task
    python3 /tests/judge.py /tests/rubric.yaml /workspace/vscode 2>/dev/null || true
fi
