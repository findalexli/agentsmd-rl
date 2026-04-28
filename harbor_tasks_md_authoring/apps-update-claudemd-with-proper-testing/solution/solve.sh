#!/usr/bin/env bash
set -euo pipefail

cd /workspace/apps

# Idempotency guard
if grep -qF "- `pnpm test:ci` - Run unit tests for all projects" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -34,8 +34,7 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 **Testing**:
 
-- `pnpm test` - Run unit tests for all projects
-- `pnpm test:ci` - Run tests with coverage for CI
+- `pnpm test:ci` - Run unit tests for all projects
 - `vitest --project units` - Run unit tests for specific app
 - `vitest --project e2e` - Run E2E tests for specific app
 - `pnpm e2e` - Run E2E tests (app-level)
PATCH

echo "Gold patch applied."
