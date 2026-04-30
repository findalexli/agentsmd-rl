#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pinme

# Idempotency guard
if grep -qF ".claude/skills/pinme/README.md" ".claude/skills/pinme/README.md" && grep -qF ".claude/skills/pinme/SKILL.md" ".claude/skills/pinme/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pinme/README.md b/.claude/skills/pinme/README.md

diff --git a/.claude/skills/pinme/SKILL.md b/.claude/skills/pinme/SKILL.md

PATCH

echo "Gold patch applied."
