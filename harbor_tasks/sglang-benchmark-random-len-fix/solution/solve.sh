#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

# Idempotent: sed is a no-op if already applied
sed -i 's/input_lens\[i\] = max(0, input_lens\[i\] - num_special_tokens)/input_lens[i] = max(1, input_lens[i] - num_special_tokens)/' \
    python/sglang/benchmark/datasets/random.py
