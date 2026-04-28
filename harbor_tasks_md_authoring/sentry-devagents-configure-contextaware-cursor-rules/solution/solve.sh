#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry

# Idempotency guard
if grep -qF "This directory contains `.mdc` (Markdown with Cursor directives) files that conf" ".cursor/rules/README.md" && grep -qF "- '!src/**/tests/**'" ".cursor/rules/backend.mdc" && grep -qF "- 'static/**/*.{ts,tsx,js,jsx}'" ".cursor/rules/frontend.mdc" && grep -qF "alwaysApply: true" ".cursor/rules/general.mdc" && grep -qF "- 'src/**/tests/**/*.py'" ".cursor/rules/tests.mdc" && grep -qF "Cursor is configured to automatically load relevant AGENTS.md files based on the" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/README.md b/.cursor/rules/README.md
@@ -0,0 +1,53 @@
+# Cursor Rules Configuration
+
+This directory contains `.mdc` (Markdown with Cursor directives) files that configure context-aware loading of AGENTS.md files in Cursor's AI assistant.
+
+## How It Works
+
+When you edit a file, Cursor automatically loads the relevant AGENTS.md based on glob patterns:
+
+| File Type      | Loaded Guide       | Glob Pattern                            |
+| -------------- | ------------------ | --------------------------------------- |
+| Backend Python | `src/AGENTS.md`    | `src/**/*.py` (excluding tests)         |
+| Test files     | `tests/AGENTS.md`  | `tests/**/*.py`, `src/**/tests/**/*.py` |
+| Frontend       | `static/AGENTS.md` | `static/**/*.{ts,tsx,js,jsx,css,scss}`  |
+| All files      | `AGENTS.md`        | Always loaded                           |
+
+## Files
+
+- **`general.mdc`** - Always loads root `AGENTS.md` for general Sentry context
+- **`backend.mdc`** - Loads backend patterns for Python files in `src/`
+- **`tests.mdc`** - Loads testing patterns for test files
+- **`frontend.mdc`** - Loads frontend patterns for TypeScript/JavaScript/CSS files
+
+## Benefits
+
+- **Token efficient**: Only relevant context is loaded
+- **Better AI responses**: Targeted guidance for the current task
+- **Maintainable**: Content lives in AGENTS.md files, rules just reference them
+
+## Adding New Rules
+
+To add a new context-specific rule:
+
+1. Create a new `.mdc` file in this directory
+2. Add YAML frontmatter with `globs:` or `alwaysApply:`
+3. Reference the appropriate AGENTS.md file with `@file:`
+
+Example:
+
+```markdown
+---
+globs:
+  - 'migrations/**/*.py'
+---
+
+@file:migrations/AGENTS.md
+```
+
+## Documentation
+
+For more information, see:
+
+- [Cursor Context Rules Documentation](https://docs.cursor.com/en/context/rules)
+- Root `AGENTS.md` - "Context-Aware Loading" section
diff --git a/.cursor/rules/backend.mdc b/.cursor/rules/backend.mdc
@@ -0,0 +1,7 @@
+---
+globs:
+  - 'src/**/*.py'
+  - '!src/**/tests/**'
+---
+
+@file:src/AGENTS.md
diff --git a/.cursor/rules/frontend.mdc b/.cursor/rules/frontend.mdc
@@ -0,0 +1,7 @@
+---
+globs:
+  - 'static/**/*.{ts,tsx,js,jsx}'
+  - 'static/**/*.{css,scss}'
+---
+
+@file:static/AGENTS.md
diff --git a/.cursor/rules/general.mdc b/.cursor/rules/general.mdc
@@ -0,0 +1,5 @@
+---
+alwaysApply: true
+---
+
+@file:AGENTS.md
diff --git a/.cursor/rules/tests.mdc b/.cursor/rules/tests.mdc
@@ -0,0 +1,7 @@
+---
+globs:
+  - 'tests/**/*.py'
+  - 'src/**/tests/**/*.py'
+---
+
+@file:tests/AGENTS.md
diff --git a/AGENTS.md b/AGENTS.md
@@ -34,6 +34,17 @@ sentry/
 > - **Backend testing patterns**: `tests/AGENTS.md`
 > - **Frontend patterns**: `static/AGENTS.md`
 
+### Context-Aware Loading
+
+Cursor is configured to automatically load relevant AGENTS.md files based on the file being edited (via `.cursor/rules/*.mdc`). This provides context-specific guidance without token bloat:
+
+- Editing `src/**/*.py` → Loads `src/AGENTS.md` (backend patterns)
+- Editing `tests/**/*.py` → Loads `tests/AGENTS.md` (testing patterns)
+- Editing `static/**/*.{ts,tsx,js,jsx}` → Loads `static/AGENTS.md` (frontend patterns)
+- Always loads this file (`AGENTS.md`) for general Sentry context
+
+**Note**: These `.mdc` files only _reference_ AGENTS.md files—they don't duplicate content. All actual guidance should be added to the appropriate AGENTS.md file, not to Cursor rules.
+
 ## Backend
 
 For backend development patterns, commands, security guidelines, and architecture, see `src/AGENTS.md`.
PATCH

echo "Gold patch applied."
