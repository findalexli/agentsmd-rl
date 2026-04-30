#!/usr/bin/env bash
set -euo pipefail

cd /workspace/homebrew-cask

# Idempotency guard
if grep -qF ".github/copilot-instructions.md" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md

PATCH

echo "Gold patch applied."
