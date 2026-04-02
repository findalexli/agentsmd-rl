#!/bin/bash
# judge_hook.sh - Sourced at end of test.sh to run LLM rubric judge

if [ "${LLM_JUDGE:-0}" = "1" ] && [ -f /tests/judge.py ]; then
    python3 /tests/judge.py 2>/dev/null || true
fi
