#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "Source skill files live in `packages/libretto/skills/` and are mirrored to `.age" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,31 @@
+# Libretto Monorepo
+
+## Releasing a New Version
+
+**Never manually edit `packages/libretto/package.json` version.** Use the release script:
+
+```bash
+scripts/prepare-release.sh [patch|minor|major]
+```
+
+This script:
+1. Checks out and updates `main`
+2. Runs type-check and tests
+3. Bumps the version in `packages/libretto/package.json`
+4. Updates version in SKILL.md files via `set-libretto-skill-version.mjs`
+5. Syncs all mirrors (`pnpm sync:mirrors`) — READMEs, skill directories, `create-libretto` version
+6. Validates mirror parity (`pnpm check:mirrors`)
+7. Commits, pushes a `release-v*` branch, and opens a PR
+
+The release CI workflow triggers automatically when the PR merges to `main`.
+
+## Mirror System
+
+Skill files and READMEs are mirrored across multiple locations. After any change to source files:
+
+```bash
+pnpm sync:mirrors    # sync all mirrored files
+pnpm check:mirrors   # validate everything is in sync
+```
+
+Source skill files live in `packages/libretto/skills/` and are mirrored to `.agents/skills/` and `.claude/skills/`.
PATCH

echo "Gold patch applied."
