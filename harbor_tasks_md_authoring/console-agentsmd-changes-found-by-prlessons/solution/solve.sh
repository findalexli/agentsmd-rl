#!/usr/bin/env bash
set -euo pipefail

cd /workspace/console

# Idempotency guard
if grep -qF "- Hoist static column definitions to module scope; `useMemo` with an empty depen" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -30,6 +30,7 @@
 - When UI needs new mock behavior, extend the MSW handlers/db minimally so E2E tests stay deterministic; prefer storing full API responses so subsequent calls see the updated state (`mock-api/msw/db.ts`, `mock-api/msw/handlers.ts`).
 - Co-locate Vitest specs next to the code they cover; use Testing Library utilities (`render`, `renderHook`, `fireEvent`, fake timers) to assert observable output rather than implementation details (`app/ui/lib/FileInput.spec.tsx`, `app/hooks/use-pagination.spec.ts`).
 - For sweeping styling changes, coordinate with the visual regression harness and follow `test/visual/README.md` for the workflow.
+- Fix root causes of flaky timing rather than adding `sleep()` workarounds in tests.
 
 # Data fetching pattern
 
@@ -38,14 +39,17 @@
 - Use `ALL_ISH` from `app/util/consts.ts` when UI needs "all" items. Use `queryClient.invalidateEndpoint` to invalidate queries.
 - For paginated tables, compose `getListQFn` with `useQueryTable`; the helper wraps `limit`/`pageToken` handling and keeps placeholder data stable (`app/api/hooks.ts:123-188`, `app/pages/ProjectsPage.tsx:40-132`).
 - When a loader needs dependent data, fetch the primary list with `queryClient.fetchQuery`, prefetch its per-item queries, and only await a bounded batch so render isn't blocked (see `app/pages/project/affinity/AffinityPage.tsx`).
+- When modals need async data, fetch with `queryClient.ensureQueryData` before opening the modal so cached data is reused and there's no content pop-in.
+- Use `qErrorsAllowed` in loaders for endpoints where some users may lack permission, so the page degrades gracefully instead of the loader throwing (see `SiloScimTab.tsx`).
 
 # Mutations & UI flow
 
 - Wrap writes in `useApiMutation`, use `confirmAction` to guard destructive intent, and surface results with `addToast`.
 - Keep page scaffolding consistent: `PageHeader`, `PageTitle`, `DocsPopover`, `RefreshButton`, `PropertiesTable`, and `CardBlock` provide the expected layout for new system pages.
 - When a page should be discoverable from the command palette, extend `useQuickActions` with the new entry so it appears in the quick actions menu (see `app/pages/ProjectsPage.tsx:100-115`).
 - Gate per-resource actions with capability helpers: `instanceCan.start(instance)`, `diskCan.delete(disk)`, etc. (`app/api/util.ts:91-207`)—these return booleans and have `.states` properties listing valid states. Always use these instead of inline state checks; they centralize business logic and link to Omicron source explaining restrictions.
-- Pass `disabledReason` prop (accepts ReactNode) when disabling buttons so the UI explains why the action is unavailable.
+- Prefer disabling buttons with `disabledReason` over hiding them so users can discover the action exists. Compute `disabledReason` as a `string | undefined` ternary chain and derive `disabled` from `!!disabledReason`.
+- When closing a modal that uses `useApiMutation`, call `mutation.reset()` in the dismiss handler to clear stale error state so it doesn't persist on next open.
 
 # Upgrading pinned omicron version
 
@@ -75,7 +79,10 @@
 - Wire submissions through `useApiMutation`, invalidate or seed queries with `useApiQueryClient`, and surface success with toasts/navigation (`app/forms/project-create.tsx:34-55`).
 - Prefer the existing field components (`app/components/form/fields`) and only introduce new ones when the design system requires it.
 - Let form state mirror the form's UI structure, not the API request shape. Transform to the API shape in the `onSubmit` handler. This keeps fields, validation, and conditional logic straightforward.
-- Use react-hook-form's `watch` and conditional rendering to keep fields in sync. Avoid `useEffect` to propagate form values between fields—it causes extra renders and subtle ordering bugs. Reset related fields in change handlers instead.
+- Use react-hook-form's `watch` and conditional rendering to keep fields in sync. Avoid `useEffect` to propagate form values between fields—it causes extra renders and subtle ordering bugs. Reset related fields in change handlers instead. Compute default values up front in `useForm({ defaultValues })` rather than using `useEffect` + `setValue`.
+- Never access react-hook-form internals like `control._formValues`; use `useWatch` or restructure so you don't need the value.
+- In nested form contexts (sub-forms inside a page form), `preventDefault()` on Enter in text inputs to avoid accidental outer-form submission.
+- In submit handlers, prefer early return over `invariant` for states that form validation should have prevented—crashing the app is worse than a silent noop for an edge case no user can reach.
 - In general, use `useEffect` as a last resort! Try to figure out a non-useEffect version first. See https://react.dev/learn/you-might-not-need-an-effect.md when thinking about difficult cases.
 
 # Tables & detail views
@@ -85,6 +92,7 @@
 - `getActionsCol` automatically includes "Copy ID" if row has `id` field, and actions labeled "delete" get destructive styling. Pass `disabled` prop with ReactNode for tooltip explaining why action is unavailable (`app/table/columns/action-col.tsx`).
 - Let `useQueryTable` drive pagination, scroll reset, and placeholder loading states instead of reimplementing TanStack Table plumbing (`app/table/QueryTable.tsx`).
 - Use `PropertiesTable` compound component for detail views: `PropertiesTable.Row`, `PropertiesTable.IdRow` (truncated ID with copy), `PropertiesTable.DescriptionRow`, `PropertiesTable.DateRow` (`app/ui/lib/PropertiesTable.tsx`).
+- Hoist static column definitions to module scope; `useMemo` with an empty dependency array is a code smell indicating the value doesn't belong inside the component. More generally, don't reach for `useMemo` for simple ternary/conditional logic; reserve it for genuinely expensive computation or when referential identity matters for downstream deps.
 
 # Layout & accessibility
 
@@ -110,6 +118,10 @@
 - Reuse utility components for consistent formatting—`TimeAgo`, `EmptyMessage`, `CardBlock`, `DocsPopover`, `PropertiesTable`, etc.
 - Import icons from `@oxide/design-system/icons/react` with size suffixes: `16` for inline/table, `24` for headers/buttons, `12` for tiny indicators.
 - Keep help URLs in `links`/`docLinks` (`app/util/links.ts`).
+- Prefer flexbox `gap` for spacing between inline elements over margin utilities like `ml-*`.
+- Use proper casing in badge and label source text even when CSS `text-transform` changes display, since screen readers and clipboard copy use the source.
+- Keep UI microcopy concise and imperative ("Manage resources" not "Can manage resources"); avoid semicolons.
+- Don't use default prop values that force callers to pass empty strings to opt out; make props truly optional.
 
 # Error handling
 
@@ -126,3 +138,8 @@
 - Avoid type casts (`as`) where possible; prefer type-safe alternatives like `satisfies`, `.returnType<T>()` for ts-pattern, or `as const`
 - Use `remeda` (imported as `R`) for sorting and data transformations—e.g., `R.sortBy(items, (x) => x.key1, (x) => x.key2)` instead of manual `.sort()` comparators.
 - Prefer small composable predicates (e.g., `poolHasIpVersion(versions)`) that chain with `.filter()` over monolithic filter functions with multiple optional parameters.
+- When using `!` (non-null assertion), add a comment justifying why the value is guaranteed to exist.
+- When multiple boolean states control mutually exclusive UI, consolidate into a single discriminated union type (pairs with ts-pattern exhaustive matching).
+- Use generated API types from `@oxide/api` rather than redeclaring their shape as inline object types.
+- Add explicit type annotations on `.then`/`.catch` callbacks in generic API wrappers to prevent `any` from leaking.
+- Use `satisfies` to catch type errors masked by `any`-typed callbacks (e.g., react-hook-form's `onChange`). The assertion costs nothing at runtime but catches mismatches at build time.
PATCH

echo "Gold patch applied."
