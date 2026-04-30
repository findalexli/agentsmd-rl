#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ragflow

# Idempotency guard
if grep -qF "The folder `src/components/ui/` is the project's **shared UI library** \u2014 it cont" "web/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/web/CLAUDE.md b/web/CLAUDE.md
@@ -41,6 +41,14 @@ When refactoring or extracting components, **verify layout behavior after each s
 For React Query / cache invalidation bugs, **carefully compare query keys across all consuming components and mutation hooks**. Mismatched keys (e.g., with/without `refreshCount`) are a common root cause of stale data or duplicate requests.
 - Systematically: (1) list every component/hook that calls `useQuery` for this data, (2) compare their query keys character-for-character, (3) check every mutation's `onSuccess` for cache invalidation, and (4) verify no parent re-renders are remounting the observer.
 
+### Shared UI Component Lock
+The folder `src/components/ui/` is the project's **shared UI library** — it contains both official shadcn/ui primitives and project-authored common components built on top of shadcn. Both kinds are intended to be reused across the app and **must not be modified casually**.
+
+- **Do not modify, refactor, restyle, or "improve"** any file under `src/components/ui/` (including subfolders), even if it seems like the most direct fix.
+- If a component does not meet requirements, **wrap or compose it** in a new component **outside** `src/components/ui/` (e.g., under `src/components/` or a feature folder), and customize via `className`, `props`, or composition.
+- Exceptions require **explicit user approval** in the same conversation. When in doubt, ask first and propose a wrapper-based alternative.
+- Adding a new shared component to `src/components/ui/`, or upgrading a shadcn primitive via the official `shadcn` CLI, is allowed only when the user explicitly requests it.
+
 ### React Patterns and Conventions
 - **Prefer `requestAnimationFrame` or `useLayoutEffect`** over `setTimeout(..., 0)` for focus or DOM measurement operations.
 - **Prefer `useTranslation` from `react-i18next`** over project-wrapped utilities like `useTranslate`.
PATCH

echo "Gold patch applied."
