#!/usr/bin/env bash
set -euo pipefail

cd /workspace/angular

# Idempotency guard
if grep -qF "- **Zoneless & Async-First:** Assume a zoneless environment where state changes " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -15,6 +15,20 @@ This is the source code for the Angular framework. This guide outlines standard
 - [Coding Standards](contributing-docs/coding-standards.md): style guide for TypeScript and other files.
 - [Commit Guidelines](contributing-docs/commit-message-guidelines.md): format for commit messages and PR titles.
 
+## Testing
+
+- **Zoneless & Async-First:** Assume a zoneless environment where state changes schedule updates asynchronously.
+  - **Do NOT** use `fixture.detectChanges()` to manually trigger updates.
+  - **ALWAYS** use the "Act, Wait, Assert" pattern:
+    1. **Act:** Update state or perform an action.
+    2. **Wait:** `await fixture.whenStable()` to allow the framework to process the scheduled update.
+    3. **Assert:** Verify the output.
+- To keep tests fast, minimize the need for waiting:
+  - Use `useAutoTick()` (from `packages/private/testing/src/utils.ts`) to fast-forward time via the mock clock.
+- When waiting is necessary, use real async tests (`it('...', async () => { ... })`) along with:
+  - `await timeout(ms)` (from `packages/private/testing/src/utils.ts`) to wait a specific number of milliseconds.
+  - `await fixture.whenStable()` to wait for framework stability.
+
 ## Pull Requests
 
 - Use the `gh` CLI (GitHub CLI) for creating and managing pull requests.
PATCH

echo "Gold patch applied."
