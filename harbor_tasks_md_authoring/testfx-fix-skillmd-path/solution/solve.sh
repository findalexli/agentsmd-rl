#!/usr/bin/env bash
set -euo pipefail

cd /workspace/testfx

# Idempotency guard
if grep -qF ".github/skills/post-release-activities/SKILL.md" ".github/skills/post-release-activities/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/post-release-activities/SKILL.md b/.github/skills/post-release-activities/SKILL.md

PATCH

echo "Gold patch applied."
