#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mux

# Idempotency guard
if grep -qF "- **perf:** (improvement to performance, no functionality changes)" "docs/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/AGENTS.md b/docs/AGENTS.md
@@ -98,6 +98,24 @@ were created fresh each time. Moved to module scope for stable references.
 Verify with React DevTools Profiler - MarkdownCore should only re-render when content changes.
 ```
 
+### PR Title Structure
+
+Use these prefixes based on what best describes the PR:
+
+- **perf:** (improvement to performance, no functionality changes)
+- **refactor:** (improvement to codebase, no behavior changes)
+- **fix:** (conforming behavior to user expectations)
+- **feat:** (net new functionality)
+- **ci:** (concerned with build process or CI)
+
+Examples:
+
+- `🤖 perf: cache markdown plugin arrays to avoid re-parsing`
+- `🤖 refactor: extract IPC handlers to separate module`
+- `🤖 fix: handle workspace rename edge cases`
+- `🤖 feat: add keyboard shortcuts for workspace navigation`
+- `🤖 ci: update wait_pr_checks script timeout`
+
 ## Project Structure
 
 - `src/main.ts` - Main Electron process
PATCH

echo "Gold patch applied."
