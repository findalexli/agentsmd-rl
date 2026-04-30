#!/usr/bin/env bash
set -euo pipefail

cd /workspace/insforge

# Idempotency guard
if grep -qF "The lowest-friction approach is to **temporarily hardcode** the three gates belo" ".agents/skills/insforge-dev/dashboard/SKILL.md" && grep -qF "The lowest-friction approach is to **temporarily hardcode** the three gates belo" ".claude/skills/insforge-dev/dashboard/SKILL.md" && grep -qF "The lowest-friction approach is to **temporarily hardcode** the three gates belo" ".codex/skills/insforge-dev/dashboard/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/insforge-dev/dashboard/SKILL.md b/.agents/skills/insforge-dev/dashboard/SKILL.md
@@ -45,6 +45,37 @@ Use this skill for dashboard work in the InsForge repository.
    - Keep `packages/dashboard/src/index.ts` and `packages/dashboard/src/types` aligned with the public package API.
    - Never use the TypeScript `any` type. Prefer precise prop, state, API, and hook result types.
 
+## Local debug: viewing cloud-hosting-only UI in self-hosting
+
+**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI connect panel) while running the local `frontend/` self-hosting shell.
+
+The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be fully reverted before committing — landing them breaks both self-hosting and cloud-hosting users.
+
+### Hardcodes
+
+1. `packages/dashboard/src/lib/config/DashboardHostContext.tsx` — `useIsCloudHostingMode()` → `return true;` (was `useDashboardHost().mode === 'cloud-hosting'`).
+2. `packages/dashboard/src/lib/utils/utils.ts` — `isInsForgeCloudProject()` → `return true;` (was the `.insforge.app` hostname check).
+3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` for `<ConnectDialogV2>`.
+
+Mark every hardcode with a trailing `// LOCAL DEBUG: <original expression>` comment so revert is a mechanical search.
+
+### Revert checklist — run all before committing
+
+1. `git grep -n "LOCAL DEBUG" packages/dashboard/src/` returns zero matches.
+2. Each gate is restored to its **original expression**, not just an equivalent value (the `mode === 'cloud-hosting'` comparison, the hostname check, the `getFeatureFlag(...)` call must all be back).
+3. Any imports deleted during debug (commonly `DashboardPage`, `getFeatureFlag`, `ConnectDialog`) are restored.
+4. `cd packages/dashboard && npm run lint && npm run typecheck` both pass.
+5. `git diff` of the four files above shows only intended changes — no `return true;`, no missing imports.
+
+### Rationalizations to reject
+
+| Excuse | Reality |
+|--------|---------|
+| "I'll revert in a follow-up PR." | Follow-up = a window where prod is broken. Revert now. |
+| "The original check was effectively the same." | If it were, you wouldn't have needed the hardcode. Restore the expression, not a value-equivalent. |
+| "Lint passed, so the deleted import doesn't matter." | Lint passed because the import was deleted; on revert the original code needs it back. |
+| "I'll ship the env-var override instead." | No env-var override is wired in the code. Don't invent one on the commit path — restore the original. |
+
 ## Validation
 
 - `cd packages/dashboard && npm run typecheck`
diff --git a/.claude/skills/insforge-dev/dashboard/SKILL.md b/.claude/skills/insforge-dev/dashboard/SKILL.md
@@ -45,6 +45,37 @@ Use this skill for dashboard work in the InsForge repository.
    - Keep `packages/dashboard/src/index.ts` and `packages/dashboard/src/types` aligned with the public package API.
    - Never use the TypeScript `any` type. Prefer precise prop, state, API, and hook result types.
 
+## Local debug: viewing cloud-hosting-only UI in self-hosting
+
+**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI connect panel) while running the local `frontend/` self-hosting shell.
+
+The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be fully reverted before committing — landing them breaks both self-hosting and cloud-hosting users.
+
+### Hardcodes
+
+1. `packages/dashboard/src/lib/config/DashboardHostContext.tsx` — `useIsCloudHostingMode()` → `return true;` (was `useDashboardHost().mode === 'cloud-hosting'`).
+2. `packages/dashboard/src/lib/utils/utils.ts` — `isInsForgeCloudProject()` → `return true;` (was the `.insforge.app` hostname check).
+3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` for `<ConnectDialogV2>`.
+
+Mark every hardcode with a trailing `// LOCAL DEBUG: <original expression>` comment so revert is a mechanical search.
+
+### Revert checklist — run all before committing
+
+1. `git grep -n "LOCAL DEBUG" packages/dashboard/src/` returns zero matches.
+2. Each gate is restored to its **original expression**, not just an equivalent value (the `mode === 'cloud-hosting'` comparison, the hostname check, the `getFeatureFlag(...)` call must all be back).
+3. Any imports deleted during debug (commonly `DashboardPage`, `getFeatureFlag`, `ConnectDialog`) are restored.
+4. `cd packages/dashboard && npm run lint && npm run typecheck` both pass.
+5. `git diff` of the four files above shows only intended changes — no `return true;`, no missing imports.
+
+### Rationalizations to reject
+
+| Excuse | Reality |
+|--------|---------|
+| "I'll revert in a follow-up PR." | Follow-up = a window where prod is broken. Revert now. |
+| "The original check was effectively the same." | If it were, you wouldn't have needed the hardcode. Restore the expression, not a value-equivalent. |
+| "Lint passed, so the deleted import doesn't matter." | Lint passed because the import was deleted; on revert the original code needs it back. |
+| "I'll ship the env-var override instead." | No env-var override is wired in the code. Don't invent one on the commit path — restore the original. |
+
 ## Validation
 
 - `cd packages/dashboard && npm run typecheck`
diff --git a/.codex/skills/insforge-dev/dashboard/SKILL.md b/.codex/skills/insforge-dev/dashboard/SKILL.md
@@ -45,6 +45,37 @@ Use this skill for dashboard work in the InsForge repository.
    - Keep `packages/dashboard/src/index.ts` and `packages/dashboard/src/types` aligned with the public package API.
    - Never use the TypeScript `any` type. Prefer precise prop, state, API, and hook result types.
 
+## Local debug: viewing cloud-hosting-only UI in self-hosting
+
+**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI connect panel) while running the local `frontend/` self-hosting shell.
+
+The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be fully reverted before committing — landing them breaks both self-hosting and cloud-hosting users.
+
+### Hardcodes
+
+1. `packages/dashboard/src/lib/config/DashboardHostContext.tsx` — `useIsCloudHostingMode()` → `return true;` (was `useDashboardHost().mode === 'cloud-hosting'`).
+2. `packages/dashboard/src/lib/utils/utils.ts` — `isInsForgeCloudProject()` → `return true;` (was the `.insforge.app` hostname check).
+3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` for `<ConnectDialogV2>`.
+
+Mark every hardcode with a trailing `// LOCAL DEBUG: <original expression>` comment so revert is a mechanical search.
+
+### Revert checklist — run all before committing
+
+1. `git grep -n "LOCAL DEBUG" packages/dashboard/src/` returns zero matches.
+2. Each gate is restored to its **original expression**, not just an equivalent value (the `mode === 'cloud-hosting'` comparison, the hostname check, the `getFeatureFlag(...)` call must all be back).
+3. Any imports deleted during debug (commonly `DashboardPage`, `getFeatureFlag`, `ConnectDialog`) are restored.
+4. `cd packages/dashboard && npm run lint && npm run typecheck` both pass.
+5. `git diff` of the four files above shows only intended changes — no `return true;`, no missing imports.
+
+### Rationalizations to reject
+
+| Excuse | Reality |
+|--------|---------|
+| "I'll revert in a follow-up PR." | Follow-up = a window where prod is broken. Revert now. |
+| "The original check was effectively the same." | If it were, you wouldn't have needed the hardcode. Restore the expression, not a value-equivalent. |
+| "Lint passed, so the deleted import doesn't matter." | Lint passed because the import was deleted; on revert the original code needs it back. |
+| "I'll ship the env-var override instead." | No env-var override is wired in the code. Don't invent one on the commit path — restore the original. |
+
 ## Validation
 
 - `cd packages/dashboard && npm run typecheck`
PATCH

echo "Gold patch applied."
