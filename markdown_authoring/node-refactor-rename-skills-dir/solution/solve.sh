#!/usr/bin/env bash
set -euo pipefail

cd /workspace/node

# Idempotency guard
if grep -qF ".agents/skills/setup-env/SKILL.md" ".agents/skills/setup-env/SKILL.md" && grep -qF ".agents/skills/smartcontracts/SKILL.md" ".agents/skills/smartcontracts/SKILL.md" && grep -qF ".agents/skills/vanity/SKILL.md" ".agents/skills/vanity/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/setup-env/SKILL.md b/.agents/skills/setup-env/SKILL.md

diff --git a/.agents/skills/smartcontracts/SKILL.md b/.agents/skills/smartcontracts/SKILL.md

diff --git a/.agents/skills/vanity/SKILL.md b/.agents/skills/vanity/SKILL.md

PATCH

echo "Gold patch applied."
