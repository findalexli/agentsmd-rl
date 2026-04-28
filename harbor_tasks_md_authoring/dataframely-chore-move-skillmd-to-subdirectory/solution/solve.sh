#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dataframely

# Idempotency guard
if grep -qF "skills/SKILL.md" "skills/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/SKILL.md b/skills/SKILL.md

PATCH

echo "Gold patch applied."
