#!/usr/bin/env bash
set -euo pipefail

cd /workspace/blockscout

# Idempotency guard
if grep -qF ".agents/skills/alias-nested-modules/SKILL.md" ".agents/skills/alias-nested-modules/SKILL.md" && grep -qF ".agents/skills/alphabetically-ordered-aliases/SKILL.md" ".agents/skills/alphabetically-ordered-aliases/SKILL.md" && grep -qF ".agents/skills/code-formatting/SKILL.md" ".agents/skills/code-formatting/SKILL.md" && grep -qF ".agents/skills/compare-against-empty-list/SKILL.md" ".agents/skills/compare-against-empty-list/SKILL.md" && grep -qF ".agents/skills/compile-project/SKILL.md" ".agents/skills/compile-project/SKILL.md" && grep -qF ".agents/skills/ecto-migration/SKILL.md" ".agents/skills/ecto-migration/SKILL.md" && grep -qF ".agents/skills/efficient-list-building/SKILL.md" ".agents/skills/efficient-list-building/SKILL.md" && grep -qF ".agents/skills/heavy-db-index-operation/SKILL.md" ".agents/skills/heavy-db-index-operation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/alias-nested-modules/SKILL.md b/.agents/skills/alias-nested-modules/SKILL.md

diff --git a/.agents/skills/alphabetically-ordered-aliases/SKILL.md b/.agents/skills/alphabetically-ordered-aliases/SKILL.md

diff --git a/.agents/skills/code-formatting/SKILL.md b/.agents/skills/code-formatting/SKILL.md

diff --git a/.agents/skills/compare-against-empty-list/SKILL.md b/.agents/skills/compare-against-empty-list/SKILL.md

diff --git a/.agents/skills/compile-project/SKILL.md b/.agents/skills/compile-project/SKILL.md

diff --git a/.agents/skills/ecto-migration/SKILL.md b/.agents/skills/ecto-migration/SKILL.md

diff --git a/.agents/skills/efficient-list-building/SKILL.md b/.agents/skills/efficient-list-building/SKILL.md

diff --git a/.agents/skills/heavy-db-index-operation/SKILL.md b/.agents/skills/heavy-db-index-operation/SKILL.md

PATCH

echo "Gold patch applied."
