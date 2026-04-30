#!/usr/bin/env bash
set -euo pipefail

cd /workspace/day1global-skills

# Idempotency guard
if grep -qF "tech-earnings-deepdive/SKILL.md" "tech-earnings-deepdive/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tech-earnings-deepdive/SKILL.md b/tech-earnings-deepdive/SKILL.md

PATCH

echo "Gold patch applied."
