#!/usr/bin/env bash
set -euo pipefail
cd /workspace/vllm

# Idempotent: skip if already applied
grep -q '_has_chat_template' vllm/entrypoints/pooling/embed/io_processor.py && exit 0

# Apply the gold patch from PR #38362
curl -sL "https://github.com/vllm-project/vllm/pull/38362.patch" | git apply --3way - 2>/dev/null || {
    # Fallback: try cherry-pick
    git fetch origin fafca38adc1ce65d2c9e2857138c3c0d65b0905e --depth=1 2>/dev/null || true
    git cherry-pick --no-commit fafca38adc1ce65d2c9e2857138c3c0d65b0905e 2>/dev/null || {
        echo "WARN: auto-apply failed"
        exit 1
    }
}
