#!/usr/bin/env bash
set -euo pipefail

cd /workspace/brew

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md

PATCH

echo "Gold patch applied."
