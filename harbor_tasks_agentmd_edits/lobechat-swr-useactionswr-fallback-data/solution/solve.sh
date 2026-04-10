#!/usr/bin/env bash
set -euo pipefail
cd /workspace/lobe-chat
python3 /solution/apply_fix.py
# Run prettier to ensure the SWR file is properly formatted
npx prettier --write src/libs/swr/index.ts 2>/dev/null || true
