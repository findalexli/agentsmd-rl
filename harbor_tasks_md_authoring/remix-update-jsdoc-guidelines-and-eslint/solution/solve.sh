#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency guard
if grep -qF "- Include an `@example` code block when it helps to show a use-case or pattern. " "skills/write-api-docs/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/write-api-docs/SKILL.md b/skills/write-api-docs/SKILL.md
@@ -64,12 +64,16 @@ Keep comments short, factual, and user-facing.
 - Keep parameter names in JSDoc exactly aligned with the function signature.
 - Use `@returns` for non-void functions and include a real description.
 - For `@param`, include descriptions and do not add a hyphen before the description.
+- Specify `@param` default values in parenthesis at the end of the comment, do not use `@default` tags
+- Include an `@example` code block when it helps to show a use-case or pattern. Skip `@example` for simple getters, trivial constructors, or APIs whose usage is self-evident.
+- Use `{@link API}` to link to related Remix APIs when it adds value. Don't link every related API — use discretion to avoid noise.
+- Use backticks for all other unlinked code references — identifiers, HTTP methods, special values.
 
 Good:
 
 ```ts
 /**
- * Creates a provider for direct credentials-based authentication.
+ * Creates an {@link AuthProvider} for direct credentials-based authentication.
  *
  * @param options Parsing and verification hooks for submitted credentials.
  * @returns A provider that can be passed to `login()`.
@@ -88,7 +92,7 @@ Avoid:
 
 ## ESLint Expectations
 
-The relevant rules live in [`eslint.config.js`](/Users/michael/.codex/worktrees/923e/remix/eslint.config.js).
+The relevant rules live in [`eslint.config.js`](../../eslint.config.js).
 
 For `packages/**/*.{ts,tsx}` (excluding tests), ESLint enforces JSDoc on callable declarations such as:
 
PATCH

echo "Gold patch applied."
