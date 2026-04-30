#!/usr/bin/env bash
set -euo pipefail

cd /workspace/docs

# Idempotency guard
if grep -qF "docs/AGENTS.md" "docs/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/AGENTS.md b/docs/AGENTS.md

PATCH

echo "Gold patch applied."
