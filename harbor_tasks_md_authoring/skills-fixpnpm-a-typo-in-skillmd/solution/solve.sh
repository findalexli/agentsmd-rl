#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "pnpm is a fast, disk space efficient package manager. It uses a content-addressa" "skills/pnpm/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/pnpm/SKILL.md b/skills/pnpm/SKILL.md
@@ -7,7 +7,7 @@ metadata:
   source: Generated from https://github.com/pnpm/pnpm, scripts located at https://github.com/antfu/skills
 ---
 
-pnpm is a fast, disk space efficient package manager. It uses a content-addressable store to deduplicate packages across all projects on a machine, saving significant disk space. pnpm enforces strict dependency resolution by default, preventing phantom dependencies. Configuration should preferrably be placed in `pnpm-workspace.yaml` for pnpm-specific settings.
+pnpm is a fast, disk space efficient package manager. It uses a content-addressable store to deduplicate packages across all projects on a machine, saving significant disk space. pnpm enforces strict dependency resolution by default, preventing phantom dependencies. Configuration should preferably be placed in `pnpm-workspace.yaml` for pnpm-specific settings.
 
 **Important:** When working with pnpm projects, agents should check for `pnpm-workspace.yaml` and `.npmrc` files to understand workspace structure and configuration. Always use `--frozen-lockfile` in CI environments.
 
PATCH

echo "Gold patch applied."
