#!/usr/bin/env bash
set -euo pipefail

cd /workspace/archon

# Idempotency guard
if grep -qF "# path depends on BUNDLED_IS_BINARY=true, which is set by scripts/build-binaries" ".claude/skills/release/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/release/SKILL.md b/.claude/skills/release/SKILL.md
@@ -64,9 +64,15 @@ if [ -f scripts/build-binaries.sh ] && [ -f packages/cli/src/cli.ts ]; then
     packages/cli/src/cli.ts
 
   # Smoke test: the binary must start and exit 0 on a safe, non-interactive command.
-  # `version` or `--help` are both acceptable — pick one that does NOT touch the
-  # network, database, or require env vars.
-  if ! "$TMP_BINARY" version > /tmp/archon-preflight.log 2>&1; then
+  # Use `--help` (NOT `version`). The `version` command's compiled-binary code
+  # path depends on BUNDLED_IS_BINARY=true, which is set by scripts/build-binaries.sh
+  # — but we're doing a bare `bun build --compile` here to keep the smoke fast,
+  # so BUNDLED_IS_BINARY is still `false`. That sends `version` down the dev
+  # branch of version.ts which tries to read package.json from a path that only
+  # exists in node_modules, producing a false-positive ENOENT. `--help` has no
+  # such dev/binary branch and exercises the same module-init graph we're
+  # actually testing. Must NOT touch network, database, or require env vars.
+  if ! "$TMP_BINARY" --help > /tmp/archon-preflight.log 2>&1; then
     echo "ERROR: compiled binary crashed at startup"
     cat /tmp/archon-preflight.log
     echo ""
PATCH

echo "Gold patch applied."
