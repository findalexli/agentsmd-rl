#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ledger-live

# Idempotency guard
if grep -qF "description: Privacy-protected ID management with @ledgerhq/client-ids \u2014 DeviceI" ".cursor/rules/client-ids.mdc" && grep -qF "- **Prefer smart activation (`description`) over `globs`** \u2014 the agent can judge" ".cursor/rules/cursor-rules.mdc" && grep -qF "alwaysApply: false" ".cursor/rules/git-workflow.mdc" && grep -qF "description: LDLS UI React design system rules (@ledgerhq/lumen-ui-react)" ".cursor/rules/ldls.mdc" && grep -qF "alwaysApply: false" ".cursor/rules/react-general.mdc" && grep -qF "alwaysApply: false" ".cursor/rules/react-mvvm.mdc" && grep -qF "alwaysApply: false" ".cursor/rules/redux-slice.mdc" && grep -qF "alwaysApply: false" ".cursor/rules/rtk-query-api.mdc" && grep -qF "globs: [\"*.test.*\", \"*.spec.*\", \"**/tests/**\", \"**/__tests__/**\"]" ".cursor/rules/testing.mdc" && grep -qF "globs: [\"**/*.ts\", \"**/*.tsx\"]" ".cursor/rules/typescript.mdc" && grep -qF "alwaysApply: false" ".cursor/rules/zod-schemas.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/client-ids.mdc b/.cursor/rules/client-ids.mdc
@@ -1,3 +1,8 @@
+---
+description: Privacy-protected ID management with @ledgerhq/client-ids — DeviceId, UserId, DatadogId, export-rules.json
+alwaysApply: false
+---
+
 # Client IDs Library (`@ledgerhq/client-ids`)
 
 ## Purpose
diff --git a/.cursor/rules/cursor-rules.mdc b/.cursor/rules/cursor-rules.mdc
@@ -0,0 +1,32 @@
+---
+globs: ["**/.cursor/rules/**"]
+description: Guidelines for authoring and configuring .cursor/rules — activation modes, frontmatter, best practices
+alwaysApply: false
+---
+
+# Cursor Rule Authoring
+
+Reference: https://cursor.com/docs/context/rules#rule-file-format
+
+## Rule Activation Modes
+
+Rules activate based on the combination of `description`, `globs`, and `alwaysApply` in their frontmatter:
+
+| Rule Type               | Frontmatter                                 | Behavior                           |
+| ----------------------- | ------------------------------------------- | ---------------------------------- |
+| Always Apply            | `alwaysApply: true`                         | Injected into every conversation   |
+| Apply Intelligently     | `description` + `alwaysApply: false`        | Agent decides based on description |
+| Apply to Specific Files | `globs` + `alwaysApply: false`              | Auto-activates on matching files   |
+| Apply Manually          | `alwaysApply: false` (no description/globs) | Only when @-mentioned in chat      |
+
+A `description` can be combined with `globs` — the description serves as documentation for human readers and also enables agent-decided activation when no matching file is open. The `description` field is always recommended.
+
+## Rules
+
+- **Avoid `alwaysApply: true`** — it clogs the context window by injecting the rule into every conversation unconditionally.
+- **Always add a `description`** — it documents the rule's purpose for human readers and enables intelligent agent-decided activation.
+- **Prefer smart activation (`description`) over `globs`** — the agent can judge relevance from conversation context better than broad file patterns. Add `globs` only when activation must be strictly tied to specific file types (e.g., test files, `.tsx` components).
+- **Never combine `alwaysApply: true` with `description` or `globs`** — it makes the other fields useless since the rule is always injected regardless.
+- If using `globs`, ensure patterns are precise (avoid overly broad patterns like `**/*`).
+- Keep rules under 500 lines. Split large rules into composable pieces.
+- Reference files with `@path` instead of copying their contents.
diff --git a/.cursor/rules/git-workflow.mdc b/.cursor/rules/git-workflow.mdc
@@ -1,7 +1,6 @@
 ---
 description: Git workflow and commit conventions for Ledger Wallet
-globs: ["**/*"]
-alwaysApply: true
+alwaysApply: false
 ---
 
 # Git Workflow & Commit Conventions
diff --git a/.cursor/rules/ldls.mdc b/.cursor/rules/ldls.mdc
@@ -1,7 +1,6 @@
 ---
-description: LDLS UI React design system rules
-globs: ["**/*.tsx", "**/*.jsx"]
-alwaysApply: true
+description: LDLS UI React design system rules (@ledgerhq/lumen-ui-react)
+alwaysApply: false
 ---
 
 @node_modules/@ledgerhq/lumen-ui-react/ai-rules/RULES.md
diff --git a/.cursor/rules/react-general.mdc b/.cursor/rules/react-general.mdc
@@ -1,7 +1,7 @@
 ---
-alwaysApply: true
 description: General React and React Native engineering rules for Ledger Live
 globs: ["**/*.{ts,tsx}"]
+alwaysApply: false
 ---
 
 # General React & React Native Patterns
diff --git a/.cursor/rules/react-mvvm.mdc b/.cursor/rules/react-mvvm.mdc
@@ -1,7 +1,7 @@
 ---
-alwaysApply: true
 description: React MVVM Architecture engineering rules (mvvm) for Ledger Wallet
 globs: ["**/*.ts", "**/*.tsx"]
+alwaysApply: false
 ---
 
 # React MVVM Architecture (`mvvm`)
diff --git a/.cursor/rules/redux-slice.mdc b/.cursor/rules/redux-slice.mdc
@@ -1,6 +1,6 @@
 ---
 description: Redux Toolkit createSlice best practices
-alwaysApply: true
+alwaysApply: false
 ---
 
 # Redux Toolkit - createSlice
diff --git a/.cursor/rules/rtk-query-api.mdc b/.cursor/rules/rtk-query-api.mdc
@@ -1,6 +1,6 @@
 ---
 description: RTK Query createApi best practices
-alwaysApply: true
+alwaysApply: false
 ---
 
 # RTK Query - createApi
diff --git a/.cursor/rules/testing.mdc b/.cursor/rules/testing.mdc
@@ -1,7 +1,7 @@
 ---
-globs: ["*.test.*", "*.spec.*", "**/tests/**", "**/__tests__/**"]
 description: General, Desktop, and Mobile testing patterns for Ledger Wallet
-alwaysApply: true
+globs: ["*.test.*", "*.spec.*", "**/tests/**", "**/__tests__/**"]
+alwaysApply: false
 ---
 
 # Testing Rules
diff --git a/.cursor/rules/typescript.mdc b/.cursor/rules/typescript.mdc
@@ -1,7 +1,7 @@
 ---
-alwaysApply: true
-globs: ["**/*.ts", "**/*.tsx"]
 description: React and React Native development patterns for Ledger Wallet
+globs: ["**/*.ts", "**/*.tsx"]
+alwaysApply: false
 ---
 
 ## **Components**
diff --git a/.cursor/rules/zod-schemas.mdc b/.cursor/rules/zod-schemas.mdc
@@ -1,6 +1,6 @@
 ---
 description: Zod schema validation patterns for API types
-alwaysApply: true
+alwaysApply: false
 ---
 
 # Zod Schema Validation
PATCH

echo "Gold patch applied."
