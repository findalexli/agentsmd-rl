#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next-browser

# Idempotency guard
if grep -qF "skills/next-browser/SKILL.md" "skills/next-browser/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/next-browser/SKILL.md b/skills/next-browser/SKILL.md

PATCH

echo "Gold patch applied."
