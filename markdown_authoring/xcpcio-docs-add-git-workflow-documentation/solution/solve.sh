#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xcpcio

# Idempotency guard
if grep -qF "gh pr create --title \"<type>: <description>\" --body \"Brief summary of changes\"" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -163,3 +163,46 @@ Libraries export both ESM and CommonJS formats with proper TypeScript declaratio
 4. Run tests: `pnpm test`
 5. Lint before committing: `pnpm lint`
 6. Build for production: `pnpm build`
+
+## Git Workflow
+
+### Standard Development Workflow
+
+```bash
+# Create appropriate branch based on task type
+git checkout -b <type>/<description>
+# Examples:
+# feat/add-dark-mode-support
+# fix/search-filter-bug
+# chore/update-dependencies
+# docs/api-documentation
+
+# Make changes, format, and commit with proper format and signoff
+pnpm run format
+git add .
+git commit -m "<type>: <description>" --signoff
+# Examples:
+# feat: add dark mode support for search components
+# fix: resolve search filter not working with special characters
+# chore: bump @types/node to latest version
+# docs: add API documentation for ranking system
+
+# Push branch and create PR
+git push -u origin <branch-name>
+gh pr create --title "<type>: <description>" --body "Brief summary of changes"
+
+# Merge and cleanup
+gh pr merge <pr-number> --squash
+git checkout main && git pull origin main
+git branch -d <branch-name>
+```
+
+### Commit Types
+
+- `feat`: New features or enhancements
+- `fix`: Bug fixes
+- `chore`: Maintenance tasks, dependency updates
+- `docs`: Documentation changes
+- `refactor`: Code refactoring without functional changes
+- `test`: Adding or updating tests
+- `style`: Code formatting, white-space fixes
PATCH

echo "Gold patch applied."
