#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mediawiki-skins-citizen

# Idempotency guard
if grep -qF "- Use Arrange-Act-Assert with blank lines separating each phase" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -54,6 +54,7 @@ When your test plan includes steps that require a browser (e.g., verifying scrip
 ### JavaScript
 
 - CommonJS modules: `require()` for imports, `module.exports` for exports
+- JS tests use Vitest (`tests/vitest/`)
 
 ### Vue
 
@@ -83,6 +84,10 @@ When your test plan includes steps that require a browser (e.g., verifying scrip
 - Use [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `fix(tests):`, `feat:`, `refactor:`)
 - Do **not** include emojis — a pre-commit hook adds them automatically based on the commit type prefix
 
+### Tests
+
+- Use Arrange-Act-Assert with blank lines separating each phase
+
 ### i18n
 
 - Any user-facing string needs a message key in `i18n/en.json`
PATCH

echo "Gold patch applied."
