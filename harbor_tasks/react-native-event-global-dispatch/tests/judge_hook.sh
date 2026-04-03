#!/usr/bin/env bash
# LLM rubric judge hook — sourced by test.sh
if [ "${LLM_JUDGE:-0}" = "1" ] && [ -f /tests/judge.py ]; then
    python3 /tests/judge.py \
        --task /home/agent/task \
        --agent-output /home/agent/output \
        --output /logs/verifier/judge.json 2>&1 || true
fi
