#!/usr/bin/env bash
set -euo pipefail

cd /workspace/detekt

# Idempotency guard
if grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md

PATCH

echo "Gold patch applied."
