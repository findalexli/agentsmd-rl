#!/usr/bin/env bash
set -euo pipefail

cd /workspace/safe-wallet-monorepo

# Idempotency guard
if grep -qF "**NEVER push directly to `dev` (default branch) or `main` (production branch).**" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,6 +2,34 @@
 
 **📖 Read @AGENTS.md for comprehensive guidelines on contributing to this repository.**
 
+## 🚨 Critical Git Workflow Rules
+
+**NEVER push directly to `dev` (default branch) or `main` (production branch).**
+
+Always create a feature branch and submit a pull request:
+
+```bash
+# Create a feature branch
+git checkout -b feature/your-feature-name
+
+# Make your changes and ALWAYS run tests before committing
+yarn workspace @safe-global/web type-check
+yarn workspace @safe-global/web lint
+yarn workspace @safe-global/web test
+
+# Commit only after tests pass
+git add .
+git commit -m "feat: your change description"
+
+# Push to your branch
+git push -u origin feature/your-feature-name
+
+# Create a PR via GitHub UI or gh CLI
+gh pr create
+```
+
+**All tests must pass before committing. Never commit failing code.**
+
 Use `@AGENTS.md` in your prompts to include the full guidelines, which cover:
 
 - Quick start commands
PATCH

echo "Gold patch applied."
