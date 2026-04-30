#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opensre

# Idempotency guard
if grep -qF "tests/AGENTS.md" "tests/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tests/AGENTS.md b/tests/AGENTS.md

PATCH

echo "Gold patch applied."
