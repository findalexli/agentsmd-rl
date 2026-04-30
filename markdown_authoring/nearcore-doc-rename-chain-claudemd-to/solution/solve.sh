#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nearcore

# Idempotency guard
if grep -qF "chain/chain/AGENTS.md" "chain/chain/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/chain/chain/AGENTS.md b/chain/chain/AGENTS.md

PATCH

echo "Gold patch applied."
