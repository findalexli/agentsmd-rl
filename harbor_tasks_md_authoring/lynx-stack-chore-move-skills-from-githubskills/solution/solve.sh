#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lynx-stack

# Idempotency guard
if grep -qF ".agents/skills/pr-ci-watch-subagent/SKILL.md" ".agents/skills/pr-ci-watch-subagent/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/pr-ci-watch-subagent/SKILL.md b/.agents/skills/pr-ci-watch-subagent/SKILL.md

PATCH

echo "Gold patch applied."
