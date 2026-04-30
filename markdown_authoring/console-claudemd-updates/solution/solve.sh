#!/usr/bin/env bash
set -euo pipefail

cd /workspace/console

# Idempotency guard
if grep -qF "- Use react-hook-form's `watch` and conditional rendering to keep fields in sync" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -12,7 +12,7 @@
 
 # Comment style
 
-- Prefer comments that spell out the motivation, constraints, or quirks behind a block—avoid narrating what the code already says. Good examples call out browser limits, backend caps, or sequencing expectations so future readers know the context, not just the mechanics.
+- Comment the _why_, not the _what_. If a line's purpose isn't obvious from context, give a short reason (e.g., `// clear API error state`)
 
 # API utilities & constants
 
@@ -21,8 +21,8 @@
 
 # Testing code
 
-- Run local checks before sending PRs: `npm run lint`, `npm run tsc`, `npm test run`, and `npm run e2ec`; pass `-- --ui` for Playwright UI mode or project/name filters like `npm run e2ec -- instance -g 'boot disk'`.
-- You don't usually need to run all the e2e tests, so try to filter by filename. CI will run the full set.
+- Run local checks before sending PRs: `npm run lint`, `npm run tsc`, `npm test run`, and `npm run e2ec`.
+- You don't usually need to run all the e2e tests, so try to filter by file and tes t name like `npm run e2ec -- instance -g 'boot disk'`. CI will run the full set.
 - Keep Playwright specs focused on user-visible behavior—use accessible locators (`getByRole`, `getByLabel`), the helpers in `test/e2e/utils.ts` (`expectToast`, `expectRowVisible`, `selectOption`, `clickRowAction`), and close toasts so follow-on assertions aren’t blocked.
 - Cover role-gated flows by logging in with `getPageAsUser`; exercise negative paths (e.g., forbidden actions) alongside happy paths as shown in `test/e2e/system-update.e2e.ts`.
 - Consider `expectVisible` and `expectNotVisible` deprecated: prefer `expect().toBeVisible()` and `toBeHidden()` in new code.
@@ -32,6 +32,7 @@
 
 # Data fetching pattern
 
+- Data from `usePrefetchedQuery` is guaranteed to be defined (the loader ensures it and the hook throws if it's not present). Do not add `if (!data) return` guards on these values.
 - Define queries with `q(api.endpoint, params)` for single items or `getListQFn(api.listEndpoint, params)` for lists. Prefetch in `clientLoader` and read with `usePrefetchedQuery`; for on-demand fetches (modals, secondary data), use `useQuery` directly.
 - Use `ALL_ISH` from `app/util/consts.ts` when UI needs "all" items. Use `queryClient.invalidateEndpoint` to invalidate queries.
 - For paginated tables, compose `getListQFn` with `useQueryTable`; the helper wraps `limit`/`pageToken` handling and keeps placeholder data stable (`app/api/hooks.ts:123-188`, `app/pages/ProjectsPage.tsx:40-132`).
@@ -72,6 +73,9 @@
 - Use `react-hook-form` with the shared shells (`SideModalForm`, `ModalForm`, `FullPageForm`) so UX and submit handling stay consistent (`app/components/form/SideModalForm.tsx:32-140`).
 - Wire submissions through `useApiMutation`, invalidate or seed queries with `useApiQueryClient`, and surface success with toasts/navigation (`app/forms/project-create.tsx:34-55`).
 - Prefer the existing field components (`app/components/form/fields`) and only introduce new ones when the design system requires it.
+- Let form state mirror the form's UI structure, not the API request shape. Transform to the API shape in the `onSubmit` handler. This keeps fields, validation, and conditional logic straightforward.
+- Use react-hook-form's `watch` and conditional rendering to keep fields in sync. Avoid `useEffect` to propagate form values between fields—it causes extra renders and subtle ordering bugs. Reset related fields in change handlers instead.
+- In general, use `useEffect` as a last resort! Try to figure out a non-useEffect version first. See https://react.dev/learn/you-might-not-need-an-effect.md when thinking about difficult cases.
 
 # Tables & detail views
 
@@ -119,3 +123,5 @@
 - Role helpers live in `app/api/roles.ts`.
 - Use ts-pattern exhaustive match when doing conditional logic on union types to make sure all arms are handled
 - Avoid type casts (`as`) where possible; prefer type-safe alternatives like `satisfies`, `.returnType<T>()` for ts-pattern, or `as const`
+- Use `remeda` (imported as `R`) for sorting and data transformations—e.g., `R.sortBy(items, (x) => x.key1, (x) => x.key2)` instead of manual `.sort()` comparators.
+- Prefer small composable predicates (e.g., `poolHasIpVersion(versions)`) that chain with `.filter()` over monolithic filter functions with multiple optional parameters.
PATCH

echo "Gold patch applied."
