#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency guard
if grep -qF "description: Use when making code changes to ensure they pass VS Code's hygiene " ".github/skills/hygiene/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/hygiene/SKILL.md b/.github/skills/hygiene/SKILL.md
@@ -1,25 +1,38 @@
+---
+name: hygiene
+description: Use when making code changes to ensure they pass VS Code's hygiene checks. Covers the pre-commit hook, unicode restrictions, string quoting rules, copyright headers, indentation, formatting, ESLint, and stylelint. Run the hygiene check before declaring work complete.
+---
+
 # Hygiene Checks
 
 VS Code runs a hygiene check as a git pre-commit hook. Commits will be rejected if hygiene fails.
 
-## What it checks
-
-The hygiene linter scans all staged `.ts` files for issues including (but not limited to):
-
-- **Unicode characters**: Non-ASCII characters (em-dashes, curly quotes, emoji, etc.) are rejected. Use ASCII equivalents in comments and code.
-- **Double-quoted strings**: Only use `"double quotes"` for externalized (localized) strings. Use `'single quotes'` everywhere else.
-- **Copyright headers**: All files must include the Microsoft copyright header.
+## Running the hygiene check
 
-## How it runs
+**Always run the pre-commit hygiene check before declaring work complete.** This catches issues that would block a commit.
 
-The git pre-commit hook (via husky) runs `npm run precommit`, which executes:
+To run the hygiene check on your staged files:
 
 ```bash
-node --experimental-strip-types build/hygiene.ts
+npm run precommit
 ```
 
-This scans only **staged files** (from `git diff --cached`). To run it manually:
+This executes `node --experimental-strip-types build/hygiene.ts`, which scans only **staged files** (from `git diff --cached`).
+
+To check specific files directly (without staging them first):
 
 ```bash
-npm run precommit
+node --experimental-strip-types build/hygiene.ts path/to/file.ts
 ```
+
+## What it checks
+
+The hygiene linter scans staged files for issues including (but not limited to):
+
+- **Unicode characters**: Non-ASCII characters (em-dashes, curly quotes, emoji, etc.) are rejected. Use ASCII equivalents in comments and code. Suppress with `// allow-any-unicode-next-line` or `// allow-any-unicode-comment-file`.
+- **Double-quoted strings**: Only use `"double quotes"` for externalized (localized) strings. Use `'single quotes'` everywhere else.
+- **Copyright headers**: All files must include the Microsoft copyright header.
+- **Indentation**: Tabs only, no spaces for indentation.
+- **Formatting**: TypeScript files must match the formatter output (run `Format Document` to fix).
+- **ESLint**: TypeScript files are linted with ESLint.
+- **Stylelint**: CSS files are linted with stylelint.
PATCH

echo "Gold patch applied."
