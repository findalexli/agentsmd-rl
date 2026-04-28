#!/usr/bin/env bash
set -euo pipefail

cd /workspace/backend.ai-webui

# Idempotency guard
if grep -qF "- **`upsertNotification` with the same `key` replaces** the previous entry (inte" ".claude/skills/react-async-actions/SKILL.md" && grep -qF "Manual `useMemo` / `useCallback` should be reserved for profiled bottlenecks. Un" ".claude/skills/react-component-basics/SKILL.md" && grep -qF "- **`validateFields()` on every `onChange`** causes render storms. Trigger valid" ".claude/skills/react-form/SKILL.md" && grep -qF "`useFetchKey` (from `backend.ai-ui`) returns `[fetchKey, updateFetchKey, INITIAL" ".claude/skills/react-hooks-extraction/SKILL.md" && grep -qF "- **`BAIFlex` does not always stretch children by default.** Effective `alignIte" ".claude/skills/react-layout/SKILL.md" && grep -qF "- **id-state + `useTransition`**: use `open={!!idState || isPending}` so the mod" ".claude/skills/react-modal-drawer/SKILL.md" && grep -qF "- **`exportKey` is required when `dataIndex` doesn't match the GraphQL field nam" ".claude/skills/react-relay-table/SKILL.md" && grep -qF "- **Imperative `fetchQuery` updates the store by node id** \u2014 components only re-" ".claude/skills/react-suspense-fetching/SKILL.md" && grep -qF "- **Default `history: 'push'` adds a back-button entry per filter change** \u2014 use" ".claude/skills/react-url-state/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/react-async-actions/SKILL.md b/.claude/skills/react-async-actions/SKILL.md
@@ -0,0 +1,303 @@
+---
+name: react-async-actions
+description: >
+  Use when wiring an async button (submit, delete, save, toggle), batch
+  mutation, or showing success/error feedback. Covers `BAIButton.action`,
+  `Promise.allSettled` + `_.groupBy`, `App.useApp()` (message/modal),
+  `upsertNotification` for long-running work, and `updateFetchKey()` for refresh.
+---
+
+# Async Action Handling
+
+Patterns from `UserManagement.tsx` (toggle status / purge / bulk update),
+`FolderCreateModal.tsx` (submit + notification), FR-1384 (#4165) graceful
+fallback, FR-1494 (#4359, #4353) session notifications, FR-603 (#3270) folder
+creation notification, FR-1630 (#4484) invitation error handling.
+
+## Activation Triggers
+
+- Wiring an async button (submit, delete, save, toggle)
+- Batch operations across selected items
+- Showing success/error feedback after a mutation
+- Deciding between `message`, `notification`, and `modal.error`
+- Recovering / displaying structured errors from backend calls
+
+## Gotchas
+
+- **`BAIButton action={async () => { doWork(); }}`** drops loading state — the inner promise isn't returned. Either `await doWork()` or `return doWork()`.
+- **`action` + `onClick` on the same `BAIButton`**: `onClick` fires first and synchronously; `action`'s loading state only covers the async half. Don't combine.
+- **Menu item `onClick` returning a Promise**: you MUST `resolve()` in every branch including errors — the menu spinner only clears on settle.
+- **`App.useApp()` returns `{}` when called outside `<App>` context.** The root `ConfigProvider` + `<App>` must be in place; otherwise `message.success` is a no-op.
+- **`Promise.allSettled` returns `{ status, value|reason }`.** Use `_.groupBy(results, 'status')` for typed access — don't hand-roll `.filter(r => r.status === 'fulfilled')`.
+- **`upsertNotification` with the same `key` replaces** the previous entry (intended for progress updates). Different keys create separate entries; forgetting this creates ghost notifications.
+- **`useErrorMessageResolver.getErrorMessage`** only resolves structured `ESMClientErrorResponse`. Raw `Error` / network failures fall through to `.message`.
+- **`updateFetchKey()` only refreshes the orchestrator that owns the hook.** Child components with their own `useLazyLoadQuery` don't refresh. Place the fetch key at the right ownership level.
+
+## 1. `BAIButton` with `action` — the only supported async-button pattern
+
+`BAIButton.action` wraps your async callback in a React transition and tracks
+the returned promise. It disables the button and shows loading automatically.
+
+```tsx
+<BAIButton
+  type="primary"
+  action={async () => {
+    await commitMutation({ variables: { id } });
+    updateFetchKey();
+  }}
+>
+  {t('button.Save')}
+</BAIButton>
+```
+
+### 1.1 Rules
+
+- **Never** pair `action` with `onClick`. Pick one.
+- **Never** manage loading manually with `useState` + `onClick`.
+- The `action` function must `await` or `return` a promise — don't fire-and-forget.
+- `message.success` / error notifications happen **inside** the action, not in
+  a separate `.then()` after it returns.
+
+```tsx
+// ❌ Manual loading — brittle, races on unmount
+const [loading, setLoading] = useState(false);
+<Button loading={loading} onClick={async () => {
+  setLoading(true);
+  await save();
+  setLoading(false);
+}}>Save</Button>
+
+// ❌ Mixes action + onClick — confusing, loading state covers only `action`
+<BAIButton action={save} onClick={() => setExtraState(true)}>Save</BAIButton>
+
+// ✅ Canonical
+<BAIButton type="primary" action={async () => { await save(); setExtraState(true); }}>
+  Save
+</BAIButton>
+```
+
+### 1.2 Promise-returning row action (inside a menu item)
+
+Menu items that should block-and-spin until completion can return the promise:
+
+```tsx
+actions={[{
+  key: 'toggle-status',
+  onClick: () => new Promise<void>((resolve) => {
+    commitModifyUser({
+      variables: { email, props: { status: nextStatus } },
+      onCompleted: (res, errors) => {
+        if (res.modify_user?.ok === false || errors?.[0]) {
+          message.error(res.modify_user?.msg || errors?.[0]?.message || t('error.UnknownError'));
+          logger.error(res.modify_user?.msg, errors?.[0]?.message);
+          resolve();
+          return;
+        }
+        message.success(t('credential.StatusUpdatedSuccessfully'));
+        updateFetchKey();
+        resolve();
+      },
+      onError: (error) => {
+        message.error(error?.message);
+        logger.error(error);
+        resolve();
+      },
+    });
+  }),
+}]}
+```
+
+Note the **always resolve** pattern — the menu's loading state only clears when
+the promise settles, so never throw out of the handler without resolving.
+
+## 2. `App.useApp()` — never import modal/message/notification directly
+
+```tsx
+const { message, modal, notification } = App.useApp();
+```
+
+Why: direct imports don't pick up the app's theme/context. This was swept
+repo-wide in multiple 2025 PRs.
+
+| Use | Helper | Example |
+|---|---|---|
+| Confirmation prompt | `modal.confirm` | before delete |
+| Destructive error with details | `modal.error` | backend returned structured failure |
+| Inline success | `message.success` | save/update succeeded |
+| Inline error | `message.error` | mutation failed |
+| Background task update | `notification` / `upsertNotification` | folder creation, session start (multi-stage) |
+
+### 2.1 `message.success` over `message.info` on success
+
+If it's an "it worked" confirmation, use `message.success`. `message.info` is
+reserved for neutral advisory.
+
+## 3. Batch operations: `Promise.allSettled` + `_.groupBy`
+
+FR-1384 (#4165) introduced this pattern to handle backends that partially
+succeed — always use `Promise.allSettled` for any multi-item mutation.
+
+```tsx
+const results = await Promise.allSettled(
+  selectedItems.map((item) => mutate(item)),
+);
+
+const grouped = _.groupBy(results, 'status') as {
+  fulfilled?: PromiseFulfilledResult<T>[];
+  rejected?: PromiseRejectedResult[];
+};
+
+if (grouped.rejected?.length) {
+  const firstReason = grouped.rejected[0].reason;
+  message.error(
+    t('common.PartialFailure', {
+      ok: grouped.fulfilled?.length ?? 0,
+      failed: grouped.rejected.length,
+      reason: getErrorMessage(firstReason),
+    }),
+  );
+  logger.error('batch partial failure', grouped.rejected);
+}
+if (grouped.fulfilled?.length) {
+  message.success(
+    t('common.BatchSucceeded', { count: grouped.fulfilled.length }),
+  );
+}
+updateFetchKey();
+```
+
+### Typed helper in repo
+
+```ts
+export type StartSessionResults = {
+  fulfilled?: PromiseFulfilledResult<SessionCreationSuccess>[];
+  rejected?: PromiseRejectedResult[];
+};
+```
+
+`useStartSession` returns this shape. Reuse that pattern for new hooks that
+run multi-item operations.
+
+## 4. Error resolution: `useErrorMessageResolver`
+
+For errors from BAI client calls that come back with a structured
+`ESMClientErrorResponse`, resolve the message through the helper:
+
+```tsx
+import { useErrorMessageResolver } from 'backend.ai-ui';
+
+const { getErrorMessage } = useErrorMessageResolver();
+
+onError: (error) => {
+  message.error(getErrorMessage(error));
+  logger.error(error);
+}
+```
+
+This also handles i18n-aware backend error code mapping. Don't try to
+`.message` the raw error — it often loses the structured info.
+
+## 5. Long-running work: `upsertNotification`
+
+For work that outlives the modal (folder provisioning, session start, mount
+operations), push an entry into the global notification store instead of
+spinning a `message`:
+
+```tsx
+const { upsertNotification } = useSetBAINotification();
+
+upsertNotification({
+  key: `folder-create-success-${result.id}`,  // unique key so progress updates replace
+  icon: 'folder',
+  message: `${result.name}: ${t('data.folders.FolderCreated')}`,
+  toText: t('data.folders.OpenAFolder'),
+  to: { search: new URLSearchParams({ folder: result.id }).toString() },
+  open: true,
+});
+```
+
+- `key` is stable across updates — subsequent calls with the same key
+  replace the entry (progress bars, stage transitions).
+- `to` / `toText` embed a deep-link CTA.
+- `open: true` shows the popover; omit for silent insert.
+
+FR-1760 (#4753) removed duplicated onclick handler bindings — when writing
+notification `to` links, never attach ad-hoc `onClick` handlers; the stored
+route handles navigation.
+
+## 6. Triggering a refetch after mutation
+
+Three levels, from cheapest to heaviest:
+
+### 6.1 Relay store auto-update (preferred)
+
+When a mutation's `updater`/return fields cover the shape the UI reads, Relay
+automatically re-renders the affected components. Add the needed fields to the
+mutation's selection and trust the store.
+
+### 6.2 `updateFetchKey()` — re-issue the list query
+
+When the mutation changes list-level data (add/remove/rename row):
+
+```tsx
+const [fetchKey, updateFetchKey] = useFetchKey();
+
+onCompleted: () => {
+  message.success(t('...'));
+  updateFetchKey();  // bumps fetchKey → useLazyLoadQuery re-runs
+}
+```
+
+The orchestrator already wires `fetchKey` into `useLazyLoadQuery`. Don't also
+invalidate by router navigation.
+
+### 6.3 Imperative `fetchQuery` for side-effects outside the current query
+
+When you need latest data but the current component doesn't own the query
+(e.g. BAINotification callback):
+
+```tsx
+fetchQuery<MyQuery>(relayEnv, graphql`...`, { id: globalId })
+  .toPromise()
+  .then((result) => {
+    // Relay store updates automatically for matched node IDs
+  });
+```
+
+## 7. Don't swallow errors
+
+`.catch(() => {})` and empty catch blocks are banned (security scanner flags
+them, FR-1748). Either:
+
+```tsx
+// ✅ explicit ignore with a return
+try { await thing(); } catch { return undefined; }
+
+// ✅ log + surface
+try { await thing(); } catch (e) {
+  logger.error('thing failed', e);
+  message.error(getErrorMessage(e));
+}
+```
+
+FR-1748 (#4740) scanned the repo for empty catches and removed them. Don't
+bring them back.
+
+## Related Skills
+
+- **`react-form`** — submit handler and form validation
+- **`react-modal-drawer`** — submit button inside modal footer
+- **`react-suspense-fetching`** — `updateFetchKey()` to trigger orchestrator refetch
+- **`relay-patterns`** — mutation updater and optimistic responses
+- **`react-relay-table`** — row-level and bulk-action buttons bound to a table
+
+## 8. Verification Checklist
+
+- [ ] Every async button uses `BAIButton.action`, not `onClick + loading`.
+- [ ] `action` is never combined with `onClick` on the same `BAIButton`.
+- [ ] Batch mutations use `Promise.allSettled` + `_.groupBy(results, 'status')`.
+- [ ] Errors flow through `useErrorMessageResolver.getErrorMessage` before hitting `message.error`.
+- [ ] Long-running work uses `upsertNotification` with a stable `key`; not a dangling `message`.
+- [ ] Mutations end in `updateFetchKey()` when they change list-level data.
+- [ ] Success feedback uses `message.success`, not `message.info`.
+- [ ] No empty `catch` blocks; no direct `console.*` calls — `useBAILogger`.
diff --git a/.claude/skills/react-component-basics/SKILL.md b/.claude/skills/react-component-basics/SKILL.md
@@ -0,0 +1,334 @@
+---
+name: react-component-basics
+description: >
+  Use when creating a new React component under `react/src/` or
+  `packages/backend.ai-ui/src/`, or refactoring one's file layout, import
+  order, `'use memo'` placement, hook call order, or prop interface. Covers
+  naming conventions (`BAI*`, `*Nodes`, `*Page`) and React 19 rules.
+---
+
+# React Component Basics
+
+Baseline shape of a component file in this repo, extracted from patterns repeated
+across recent 2025 PRs (e.g. `UserManagement.tsx`, `BAIUserNodes.tsx`,
+`AdminComputeSessionListPage.tsx`, `FolderCreateModal.tsx`).
+
+This skill is deliberately scoped to **structure and conventions**. For topic-specific
+guidance see the sibling skills: `react-form`, `react-modal-drawer`, `react-layout`,
+`react-relay-table`, `react-url-state`, `react-async-actions`,
+`react-suspense-fetching`, `react-hooks-extraction`.
+
+## Activation Triggers
+
+- Creating a new `.tsx` component file
+- Refactoring a component's file structure, imports, or props interface
+- Questions like "where do I put 'use memo'?", "how are props named?",
+  "what order do the hooks go in?"
+
+## Gotchas
+
+- **`'use memo'` shows "Unknown directive"** in TypeScript/ESLint. Intentional — React Compiler consumes it. Never remove, rename, or switch to backticks.
+- **Hooks after an early return** silently break hook order. Put every hook at the top of the body before any `if (...) return`.
+- **Variable names starting with uppercase** compile fine but violate project convention. Exceptions: component names, types/interfaces, enum members only.
+- **`console.*` passes TypeScript** but is flagged by ESLint and swept by cleanups (FR-1749 #4802). Always `useBAILogger`.
+- **Empty `catch {}` blocks** trip the security scanner (FR-1748 #4740). For intentional ignore write `catch { return undefined; }` explicitly.
+- **`useMemoizedFn` from ahooks** is deprecated in favor of `useEffectEvent` (React 19.2+). See `.claude/rules/use-effect-event.md`. Don't introduce new usages.
+- **`extends Omit<ParentProps, 'key'>` with the wrong Omit list** silently drops props. Mirror antd v6 names — `<Alert title>` not `<Alert message>`. See `.claude/rules/antd-v6-props.md`.
+- **`React.FC<Props>` and `(props: Props) =>` both work**; the project mixes them. Don't introduce a `React.FC` → arrow migration in a scoped PR.
+
+## 1. File Skeleton
+
+Every component file follows this shape. Deviating is a red flag in review.
+
+```tsx
+/**
+ @license
+ Copyright (c) 2015-2026 Lablup Inc. All rights reserved.
+ */
+// 1. Generated types (Relay artifacts)
+import {
+  MyComponentFragment$data,
+  MyComponentFragment$key,
+} from '../__generated__/MyComponentFragment.graphql';
+
+// 2. Local (same-package) imports — components, hooks, helpers
+import { useCurrentProjectValue } from '../hooks/useCurrentProject';
+import BAIRadioGroup from './BAIRadioGroup';
+
+// 3. External imports — antd / BUI / lodash / relay / react
+import { App, theme } from 'antd';
+import {
+  BAIButton,
+  BAIFlex,
+  BAIModal,
+  useFetchKey,
+} from 'backend.ai-ui';
+import * as _ from 'lodash-es';
+import { useTranslation } from 'react-i18next';
+import { graphql, useFragment } from 'react-relay';
+
+interface MyComponentProps extends Omit<ParentProps, 'overriddenKey'> {
+  myFrgmt: MyComponentFragment$key;
+  customizeColumns?: (base: BAIColumnType[]) => BAIColumnType[];
+}
+
+const MyComponent: React.FC<MyComponentProps> = ({
+  myFrgmt,
+  customizeColumns,
+  ...tableProps
+}) => {
+  'use memo'; // always first line of the component body
+
+  // i18n / theme / app context
+  const { t } = useTranslation();
+  const { token } = theme.useToken();
+  const { message, modal } = App.useApp();
+
+  // Relay
+  const data = useFragment(graphql`...`, myFrgmt);
+
+  // derived values (NEVER useState + useEffect)
+  const derived = useMemo(() => computeFrom(data), [data]);
+
+  // handlers
+  const handleSave = async () => { /* ... */ };
+
+  // JSX
+  return (
+    <BAIFlex direction="column" gap="sm">
+      {/* ... */}
+    </BAIFlex>
+  );
+};
+
+export default MyComponent;
+```
+
+### Import Order (enforced by review)
+
+1. Generated GraphQL types from `../__generated__/`
+2. Local project imports (components, hooks, helpers — same package)
+3. External packages: `antd` → `backend.ai-ui` → `lodash-es`/utility → `react`/`react-*`/`relay`
+
+Within each group, sort alphabetically. Don't use `lodash`; use `lodash-es`.
+
+## 2. `'use memo'` Directive
+
+The React Compiler memoizes function bodies that begin with `'use memo'`. The directive has strict placement requirements:
+
+- **Must be at the very beginning of the function body**, before any other code.
+- Comments before the directive are allowed.
+- Use double or single quotes (`"use memo"` or `'use memo'`) — **never backticks**.
+- Cannot be placed conditionally or later in the function. Only the first directive is processed; additional directives are ignored.
+- Do NOT remove existing `'use memo'`, even if tooling warns "Unknown directive".
+
+```tsx
+// ✅ Good
+const MyComponent: React.FC<Props> = (props) => {
+  'use memo'; // first line
+
+  const { t } = useTranslation();
+  // ...
+};
+
+// ✅ Good — comment before the directive is allowed
+function AnotherComponent({ data }: Props) {
+  // Optimized by React Compiler
+  'use memo';
+
+  return <div>{data}</div>;
+}
+
+// ❌ Bad — directive after a statement
+function BadComponent({ data }: Props) {
+  const value = 'test';
+  'use memo';
+  return <div>{data}</div>;
+}
+
+// ❌ Bad — conditional directive
+function ConditionalBad({ data }: Props) {
+  if (condition) {
+    'use memo';
+  }
+  return <div>{data}</div>;
+}
+
+// ❌ Bad — backticks
+function BacktickBad({ data }: Props) {
+  `use memo`;
+  return <div>{data}</div>;
+}
+```
+
+Manual `useMemo` / `useCallback` should be reserved for profiled bottlenecks. Under `'use memo'` the compiler handles it automatically — reviewers will push back on speculative manual memoization.
+
+## 3. Hook Call Order
+
+Keep hooks in this order so readers can scan a component's dependencies at a glance:
+
+1. `useTranslation()` / `theme.useToken()` / `App.useApp()`
+2. Context hooks (`useCurrentProjectValue`, `useCurrentUserRole`, …)
+3. Router / URL state (`useQueryStates`, `useLocation`, `useWebUINavigate`)
+4. Relay hooks (`useLazyLoadQuery`, `useFragment`, `useMutation`)
+5. `useState` / `useTransition` / `useToggle`
+6. Derived `useMemo` / `useDeferredValue`
+7. `useEffect` / `useEffectEvent`
+8. Handler definitions (`handleFoo = async () => {}`)
+
+The **top-level hooks rule** still applies: no hooks inside conditions, loops,
+or after an early return.
+
+## 4. Props Interface
+
+### 4.1 Always extend the underlying component
+
+When wrapping antd or a BUI component, extend its props via `Omit<>` so
+consumers keep access to `className`, `style`, event handlers, etc. See
+`.claude/rules/component-props-extension.md`.
+
+```tsx
+// ✅
+interface FolderCreateModalProps extends BAIModalProps {
+  onRequestClose: (response?: FolderCreationResponse) => void;
+  initialValues?: Partial<FolderCreateFormItemsType>;
+}
+
+// ❌ Drops every antd Modal prop
+interface FolderCreateModalProps {
+  open: boolean;
+  onRequestClose: () => void;
+}
+```
+
+### 4.2 Prop Naming
+
+| Kind | Convention | Example |
+|---|---|---|
+| Query fragment ref | `queryRef` | `queryRef: PageQuery$data` |
+| Non-query fragment ref | `{typeName}Frgmt` | `userFrgmt`, `vfolderNodeFrgmt`, `usersFrgmt` (plural) |
+| Change callback | `onChange` (not `setValue`) | `onChange?: (v: string) => void` |
+| Table order callback | `onChangeOrder` | `onChangeOrder?: (order: ... \| null) => void` |
+| Close callback | `onRequestClose` | `onRequestClose?: (result?) => void` |
+| Column customizer | `customizeColumns` | `customizeColumns?: (base) => base` |
+| Boolean flag | descriptive, not `isXxx` in props | `disableSorter`, `showResetButton`, `showTitle` |
+
+Historical `setValue` props were migrated to `onChange` in FR-1720 (#4849).
+Don't introduce new `setValue` props.
+
+### 4.3 Discriminated Unions for Variants
+
+Instead of loose optional props, use discriminated unions so TypeScript enforces
+mutually exclusive fields.
+
+```tsx
+type CheckboxSettingItemProps = BaseProps & {
+  type: 'checkbox';
+  onChange?: (v?: boolean) => void;
+  checkboxProps?: Omit<CheckboxProps, 'value' | 'onChange'>;
+  selectProps?: never;
+};
+type SelectSettingItemProps = BaseProps & {
+  type: 'select';
+  onChange?: (v?: string) => void;
+  selectProps?: Omit<SelectProps, 'value' | 'onChange'>;
+  checkboxProps?: never;
+};
+type SettingItemProps = CheckboxSettingItemProps | SelectSettingItemProps;
+```
+
+## 5. Naming
+
+### Components
+
+- `BAI*` — Shared/generic component that lives (or will live) under `packages/backend.ai-ui/`
+  (`BAIButton`, `BAIFlex`, `BAIModal`, `BAIUserNodes`).
+- `*Nodes` — A Relay-backed table component bound to a GraphQL type
+  (`BAIUserNodes`, `SessionNodes`, `VFolderNodes`). Always colocates a `@relay(plural: true)` fragment.
+- `*Page` — Top-level route component under `react/src/pages/`
+  (`ComputeSessionListPage`, `AdminComputeSessionListPage`).
+- `*Modal` / `*Drawer` — UI shells. Partner component, not a page.
+- `*FormItems` — Group of related `Form.Item`s extracted for reuse
+  (`ResourceAllocationFormItems`, `SharedMemoryFormItems`).
+
+### Derived Types
+
+Export the "one row" type so consumers can type callbacks without re-deriving:
+
+```tsx
+export type UserNodeInList = NonNullable<BAIUserNodesFragment$data[number]>;
+
+const availableUserSorterKeys = ['email', 'username', ...] as const;
+export const availableUserSorterValues = [
+  ...availableUserSorterKeys,
+  ...availableUserSorterKeys.map((key) => `-${key}` as const),
+] as const;
+```
+
+### Variables
+
+- camelCase; never start a variable or prop with an uppercase letter.
+- Fragment results named after the GraphQL type: `const users = useFragment(...)`, `const vfolderNode = useFragment(...)` — not `data`, not `result`.
+- Don't abbreviate domain types ambiguously — `session`/`endpoint`/`vfolder` are distinct.
+
+## 6. React 19 Rules That Apply Here
+
+### 6.1 Derive, don't mirror
+
+```tsx
+// ❌
+const [derived, setDerived] = useState(null);
+useEffect(() => { setDerived(computeFrom(data)); }, [data]);
+
+// ✅
+const derived = useMemo(() => computeFrom(data), [data]);
+```
+
+### 6.2 `useEffectEvent` instead of disabling exhaustive-deps
+
+If an effect calls a helper that closes over props but isn't part of the
+synchronization key, wrap the helper in `useEffectEvent`. See
+`.claude/rules/use-effect-event.md`. Do **not** disable
+`react-hooks/exhaustive-deps` to omit a callback dep.
+
+### 6.3 Under `'use memo'`, don't manually `useMemo`/`useCallback`
+
+React Compiler handles it. Only add manual memoization when profiling proves
+it's needed — reviewers will push back otherwise.
+
+## 7. Ant Design v6 Props
+
+This project runs antd v6. Always use v6 prop names (`title` instead of
+`message` on `Alert`, `orientation` instead of `direction` on `Steps`, etc.).
+See `.claude/rules/antd-v6-props.md`.
+
+## 8. Logging
+
+Never `console.log` — use `useBAILogger` from `backend.ai-ui`:
+
+```tsx
+const { logger } = useBAILogger();
+logger.error('mutation failed', err);
+```
+
+## Related Skills
+
+- **`react-form`** — when the component owns a `<Form>`
+- **`react-modal-drawer`** — when it's a modal/drawer shell
+- **`react-relay-table`** — when it's a `*Nodes` table component
+- **`react-layout`** — `BAIFlex` and spacing details
+- **`relay-patterns`** — full fragment architecture for data-fetching components
+- **`fw:lead-frontend-coding-style`** — comprehensive umbrella style guide
+
+## 9. Verification Checklist
+
+Before committing a new component, confirm:
+
+- [ ] `'use memo'` is the first line of the component body.
+- [ ] Props interface `extends Omit<...>` the wrapped component's props.
+- [ ] No `console.*`; uses `useBAILogger`.
+- [ ] No hardcoded user-facing strings; everything goes through `t()`.
+- [ ] No `useState + useEffect` for values derivable via `useMemo`.
+- [ ] No `// eslint-disable-next-line react-hooks/exhaustive-deps` — use `useEffectEvent`.
+- [ ] Naming follows §5 (`BAI*`, `*Nodes`, `*Page`, fragment-typed variable names).
+- [ ] `bash scripts/verify.sh` passes.
diff --git a/.claude/skills/react-form/SKILL.md b/.claude/skills/react-form/SKILL.md
@@ -0,0 +1,350 @@
+---
+name: react-form
+description: >
+  Use when writing or editing components that use `antd` `Form`/`Form.Item`,
+  adding `rules` validators, extracting grouped `*FormItems`, or migrating
+  `setValue` callback props to `onChange`. Covers `initialValues` vs
+  `defaultValue`, required markers, and cross-field validation.
+---
+
+# React Form Patterns
+
+Patterns for `antd` forms in backend.ai-webui, distilled from
+`FolderCreateModal.tsx`, `UserSettingModal.tsx`,
+`ResourceAllocationFormItems.tsx`, and FR-1720 / FR-701 / FR-1260 / FR-1671.
+
+## Activation Triggers
+
+- Adding or modifying a `<Form>` / `<Form.Item>`
+- Writing async or cross-field validators
+- Extracting a reusable `*FormItems` component
+- Migrating `setValue` prop callbacks to `onChange`
+- Questions about `initialValues` vs `defaultValue`, `requiredMark`, or `Form.useForm`
+
+## Gotchas
+
+- **`defaultValue` on `Form.Item` silently overrides** antd's controlled value (FR-1260 #3976). Always use `<Form initialValues={...}>`.
+- **`required` prop is a visual marker**, not a validation rule by itself. Pair with explicit `rules={[{ required: true, message: t('...') }]}` or a validator that rejects empty values.
+- **`validateFields()` on every `onChange`** causes render storms. Trigger validation only on dependent-field changes and only when the target field has a value (see FolderCreateModal's `usage_mode` handler).
+- **`Form.useForm()` + `useRef<FormInstance>` in the same form** race — antd binds to only one. Pick one per form.
+- **`initialValues` is shallow-merged.** Nested objects replace entirely; `{ a: { b: 1 } }` does NOT merge with `{ a: { c: 2 } }`.
+- **`warningOnly: true` validators don't block submit** — `validateFields()` still resolves. Useful for soft nudges; don't rely on them as required rules.
+- **`dependencies={[...]}` re-runs the CURRENT item's validator**, not the dependent field's. If both need cross-validation, put validators on both sides.
+- **`<BAIButton action={async () => { handleOk(); }}>`** (without `await` or `return`) drops loading state — the promise isn't tracked.
+
+## 1. Form Instance: Ref vs `Form.useForm`
+
+Two supported patterns — pick based on who needs to control the form.
+
+### 1.1 Local form: `useRef<FormInstance>` (preferred for simple modals)
+
+```tsx
+const formRef = useRef<FormInstance>(null);
+
+<Form ref={formRef} initialValues={initialValues}>
+  <Form.Item name="name" rules={[...]}>
+    <Input />
+  </Form.Item>
+</Form>
+
+// Trigger validation / reset from handlers
+await formRef.current?.validateFields();
+formRef.current?.resetFields();
+```
+
+### 1.2 Shared form: `Form.useForm()` when child components need access
+
+```tsx
+const [form] = Form.useForm();
+// pass `form` to Form and children that need `form.getFieldValue(...)` / `form.setFieldsValue(...)`
+```
+
+Don't mix both in the same form. `formRef` wins for modal-scoped forms because
+state naturally unmounts with the modal.
+
+## 2. `initialValues` — never `defaultValue` on `Form.Item`
+
+FR-1260 (#3976) removed `defaultValue` from `Form.Item` because it conflicts
+with the controlled value antd injects. Always set initial values on `<Form>`.
+
+```tsx
+// ❌ Bad — stale value once the form is controlled
+<Form.Item name="host" defaultValue="default">
+  <StorageSelect />
+</Form.Item>
+
+// ✅ Good
+<Form initialValues={{ host: 'default' }}>
+  <Form.Item name="host">
+    <StorageSelect />
+  </Form.Item>
+</Form>
+```
+
+### Merging with prop-provided initial values
+
+```tsx
+const INITIAL_FORM_VALUES: FolderCreateFormItemsType = {
+  name: '',
+  host: undefined,
+  group: currentProject.id || undefined,
+  usage_mode: 'general',
+  type: 'user',
+  permission: 'rw',
+  cloneable: false,
+};
+
+const mergedInitialValues = {
+  ...INITIAL_FORM_VALUES,
+  ...initialValuesFromProps,
+};
+```
+
+## 3. Validators: Prefer `rules` over manual validation in handlers
+
+Use antd's `rules` array for every validation concern — pattern, length,
+required, cross-field, async. The handler just calls `validateFields()`.
+
+### 3.1 Cross-field validator via `({ getFieldValue })`
+
+```tsx
+<Form.Item
+  name="name"
+  rules={[
+    { pattern: /^[a-zA-Z0-9-_.]+$/, message: t('data.AllowsLettersNumbersAnd-_Dot') },
+    { max: 64, message: t('data.FolderNameTooLong') },
+    ({ getFieldValue }) => ({
+      validator(_rule, value) {
+        if (_.isEmpty(value)) {
+          return Promise.reject(new Error(t('data.FolderNameRequired')));
+        }
+        if (
+          getFieldValue('usage_mode') === 'automount' &&
+          !_.startsWith(value, '.')
+        ) {
+          return Promise.reject(
+            new Error(t('data.AutomountFolderNameMustStartWithDot')),
+          );
+        }
+        return Promise.resolve();
+      },
+    }),
+  ]}
+>
+  <Input placeholder={t('maxLength.64chars')} />
+</Form.Item>
+```
+
+### 3.2 Warning-only validator
+
+Use `warningOnly: true` for soft warnings that don't block submission:
+
+```tsx
+{
+  warningOnly: true,
+  validator: async (__, value) => {
+    if (!shouldDisableProject && value === 'project') {
+      return Promise.reject(
+        new Error(t('data.folders.ProjectFolderCreationHelp', {
+          projectName: currentProject?.name,
+        })),
+      );
+    }
+    return Promise.resolve();
+  },
+}
+```
+
+### 3.3 Validating on open
+
+If the modal opens with `initialValidate`, kick validation once the transition finishes:
+
+```tsx
+<BAIModal
+  afterOpenChange={(open) => {
+    if (open && initialValidate) {
+      formRef.current?.validateFields();
+    }
+  }}
+/>
+```
+
+Do **not** call `validateFields()` synchronously on every field change — it
+causes re-render storms. FolderCreateModal only validates `name` on
+`usage_mode` change if `name` already has a value:
+
+```tsx
+<Radio.Group
+  onChange={() => {
+    if (formRef.current?.getFieldValue('name')) {
+      formRef.current.validateFields(['name']);
+    }
+  }}
+/>
+```
+
+## 4. Required Indicators
+
+### 4.1 Mark every required field with `required` (FR-1671)
+
+FR-1671 (#4624) fixed missing `required` indicators. Every field that is
+validated as required must also carry the `required` prop on `Form.Item` so the
+label shows the indicator — otherwise the UI lies.
+
+```tsx
+// ✅
+<Form.Item
+  label={t('data.Foldername')}
+  name="name"
+  required
+  rules={[ /* … */ ]}
+>
+  <Input />
+</Form.Item>
+```
+
+### 4.2 Hide the default `*` marker when the label layout differs
+
+```tsx
+// Custom label styling — hide the default `::after` asterisk
+.ant-form-item-label > label::after { display: none !important; }
+```
+
+### 4.3 `requiredMark={false}` at the `<Form>` level
+
+When every visible field is optional or you show your own indicator pattern,
+set `requiredMark={false}` on the `<Form>`.
+
+## 5. `hidden` Field Control
+
+For conditional rendering of fields driven by props, prefer `hidden` over
+conditional rendering so form state remains consistent.
+
+```tsx
+type HiddenFormItemsType =
+  | keyof FolderCreateFormItemsType
+  | 'usage_mode_general'
+  | 'usage_mode_model'
+  | 'type_user'
+  | 'type_project';
+
+<Form.Item name="host" required hidden={_.includes(hiddenFormItems, 'host')}>
+  <StorageSelect />
+</Form.Item>
+```
+
+## 6. `onChange` Callback Convention (not `setValue`)
+
+FR-1720 (#4849) standardized this. Always expose `onChange` on component-level
+callback props — matches Ant Design and HTML form conventions.
+
+```tsx
+// ❌
+interface SettingItemProps {
+  setValue?: (v: string) => void;
+}
+
+// ✅
+interface SettingItemProps {
+  onChange?: (value: string) => void;
+}
+```
+
+For discriminated variants, each branch overrides the `onChange` signature:
+
+```tsx
+type CheckboxSettingItemProps = Base & {
+  type: 'checkbox';
+  onChange?: (value?: boolean) => void;
+};
+type SelectSettingItemProps = Base & {
+  type: 'select';
+  onChange?: (value?: string) => void;
+};
+```
+
+## 7. Submit Path
+
+### 7.1 Validate → mutate → notify
+
+```tsx
+const handleOk = async () => {
+  await formRef.current
+    ?.validateFields()
+    .then((values) => {
+      return mutationToCreateFolder.mutateAsync(values, {
+        onSuccess: (result) => {
+          upsertNotification({ /* … */ });
+          onRequestClose(result);
+        },
+        onError: (error) => {
+          message.error(getErrorMessage(error));
+        },
+      });
+    })
+    .catch((error) => logger.error(error));
+};
+```
+
+### 7.2 Button wiring — always `action`, never `onClick + isLoading`
+
+```tsx
+<BAIButton
+  type="primary"
+  action={async () => {
+    await handleOk();
+  }}
+>
+  {t('data.Create')}
+</BAIButton>
+```
+
+See `react-async-actions` for the full `BAIButton.action` contract.
+
+## 8. Extracting Grouped `*FormItems`
+
+When a cluster of fields is reused or dominated by cross-field logic, extract
+as `*FormItems` — a component that returns JSX, doesn't own the `<Form>`.
+
+Examples in repo: `ResourceAllocationFormItems`, `SharedMemoryFormItems`
+(FR-1492 #4303), `PortSelectFormItem`.
+
+```tsx
+// parent: owns Form
+<Form ref={formRef} initialValues={...}>
+  <ResourceAllocationFormItems />   {/* renders Form.Items inside */}
+  <SharedMemoryFormItems />
+</Form>
+```
+
+Guidelines:
+- `*FormItems` components use `Form.useFormInstance()` or field path
+  conventions — they do NOT own a `<Form>`.
+- Group by **concern**, not by size. A cluster that shares `dependencies` or
+  validators is a good candidate.
+- Export a constant of initial values (`RESOURCE_ALLOCATION_INITIAL_FORM_VALUES`)
+  so parents can spread it into `initialValues`.
+
+## 9. Inline Slider / Number Edge Cases (FR-701)
+
+For numeric sliders and inputs that accept `"0"` / negative values by
+mistake, handle the unexpected input at the form level rather than the
+component level. Don't scatter `if (value < 0) …` across useEffects — clamp in
+the slider's props and validate via `rules`.
+
+## Related Skills
+
+- **`react-modal-drawer`** — form-in-modal patterns (`BAIUnmountAfterClose`, `onRequestClose`)
+- **`react-async-actions`** — submit button `BAIButton.action`, error resolution, notifications
+- **`react-component-basics`** — file skeleton and prop-interface conventions
+- **`react-layout`** — form footer and field-row layout with `BAIFlex`
+
+## 10. Verification Checklist
+
+- [ ] No `defaultValue` on `Form.Item`; use `<Form initialValues={...}>`.
+- [ ] Every required field has `required` on `Form.Item` (FR-1671).
+- [ ] Validators live in `rules`, not in submit handlers.
+- [ ] No `setValue` prop names on new components — use `onChange`.
+- [ ] Submit button uses `BAIButton` with `action`, not manual `loading` state.
+- [ ] `validateFields()` is called in handlers, not synchronously in every `onChange`.
+- [ ] i18n strings for all `message` fields in `rules` and placeholders.
diff --git a/.claude/skills/react-hooks-extraction/SKILL.md b/.claude/skills/react-hooks-extraction/SKILL.md
@@ -0,0 +1,260 @@
+---
+name: react-hooks-extraction
+description: >
+  Use when refactoring logic out of a fat component into a custom hook,
+  deciding hook vs helper, applying `useEffectEvent` to avoid stale closures,
+  or designing a hook's return shape. Covers hook placement, naming, and
+  parameterization conventions.
+---
+
+# Custom Hook Extraction
+
+Patterns from FR-1653 (#4592) `useStartSession` extraction, FR-1656 (#4612)
+filebrowser image hook, FR-1492 (#4303) `SharedMemoryFormItems`, FR-1472
+(#4310) `useCurrentUserInfo`, FR-527 (#3169) `useFetchKey`, FR-1299-adjacent
+custom hooks, and `use-effect-event.md` rule.
+
+## Activation Triggers
+
+- A component has grown past ~500 lines and has clusters of related logic
+- Two or more components share the same state + effect + callback shape
+- An `useEffect` calls a helper that closes over props; deps array fights you
+- A mutation or API call needs the same "validate → run → notify → refetch"
+  sequence in multiple places
+- Question: "should this be a hook or a helper?"
+
+## Gotchas
+
+- **`'use memo'` works inside custom hooks too.** React Compiler memoizes hook bodies. Place it as the first line of the hook body, same as components (`useStartSession` does this).
+- **Tuple return `[value, setter]`** signals "useState-like"; object return signals "useQuery-like". Consumers read them differently — choose based on semantics, not convenience.
+- **Hooks returning JSX are still named `use*`**, not `render*`. If a hook would return a full `<Component/>`, reconsider — it probably wants to be a component.
+- **`useEffectEvent` is effect-internal** — calling it outside `useEffect` / `useLayoutEffect` / `useInsertionEffect` has undefined behavior (React docs). Don't pass to JSX `onClick`.
+- **`useSuspendedBackendaiClient()` suspends the caller.** Wrap the caller in `<Suspense>` or accept that the first render shows fallback.
+- **i18n inside the hook** — call `useTranslation()` internally. Don't make callers pass `t` (project convention from lead coding style).
+- **Parametrize per-call inputs on the returned function**, not on the hook argument. `const { startSession } = useStartSession(); startSession(values)` — not `useStartSession(values)`.
+- **New `useMemoizedFn` usage from ahooks is forbidden** (`.claude/rules/use-effect-event.md`). Remove existing occurrences when you touch nearby code.
+
+## 1. When to extract — decision rules
+
+### 1.1 Extract as a hook when ALL hold
+
+- The logic uses at least one React hook (`useState`, `useEffect`, `useLazyLoadQuery`, `useMutation`, …)
+- The logic is reused OR will be soon OR is non-trivial (≥ ~30 lines dominating a component)
+- You can name it `useSomething` such that the name describes what it returns or what it does
+
+### 1.2 Extract as a plain function when
+
+- No React hooks involved (pure transformation)
+- I18n: prefer the function NOT taking `t` as an argument — instead make it a
+  hook so it can call `useTranslation()` internally (a consistent repo
+  convention, stated in the lead coding style)
+
+### 1.3 Don't extract (yet) when
+
+- Only used once and it's ≤ ~20 lines
+- Extraction would cross a concern boundary unnaturally (e.g. splitting a
+  validator that depends on three local states)
+- You'd have to pass 5+ arguments to reconstruct the closure
+
+Scope discipline: if extraction isn't obviously a net win, leave it inline and
+note a TODO. The reviewer will push back on speculative hooks.
+
+## 2. Where hooks live
+
+| Path | Use |
+|---|---|
+| `react/src/hooks/useThing.ts` | Generic / cross-feature hook |
+| `react/src/hooks/useThing.tsx` | Hook that returns JSX (notifications, overlays) |
+| `react/src/components/FooBar/useFooBar.ts` | Hook specific to a component/feature |
+| `packages/backend.ai-ui/src/hooks/useBaiLogger.ts` etc | Hooks generalizable to BUI |
+
+`.tsx` extension only when the hook returns or constructs JSX.
+
+## 3. Anatomy of a well-extracted hook
+
+### 3.1 `useStartSession` — complex async action
+
+```tsx
+export const useStartSession = () => {
+  'use memo';
+
+  const { t } = useTranslation();                   // i18n inside
+  const currentProject = useCurrentProjectValue();
+  const { upsertNotification } = useSetBAINotification();
+  const relayEnv = useRelayEnvironment();
+  const baiClient = useSuspendedBackendaiClient();
+
+  const [currentGlobalResourceGroup] = useCurrentResourceGroupState();
+
+  const defaultFormValues: DeepPartial<SessionLauncherFormValue> = {
+    sessionType: 'interactive',
+    // …
+  };
+
+  const startSession = async (values: StartSessionValue): Promise<StartSessionResults> => {
+    // …compose sessionInfo, POST, fetchQuery, upsertNotification…
+  };
+
+  return {
+    startSession,
+    defaultFormValues,
+    supportsMountById: baiClient.supports('mount-by-id'),
+  };
+};
+```
+
+Patterns worth copying:
+
+- `'use memo'` at the top of the hook body too.
+- Collects all the required context inside — caller passes only data, not
+  dependencies.
+- Returns a **named object**, not a bare function, so future additions
+  (`supportsMountById`) don't break call sites.
+- Exports result-shape types (`StartSessionResults`, `StartSessionValue`) for
+  callers.
+- Accepts parameterized "values" as argument, not as hook argument. Hook
+  argument is reserved for initial/configuration data.
+
+### 3.2 `useFetchKey` — tiny state helper
+
+```tsx
+const [fetchKey, updateFetchKey] = useFetchKey();
+```
+
+`useFetchKey` (from `backend.ai-ui`) returns `[fetchKey, updateFetchKey, INITIAL_FETCH_KEY]`. Most call sites destructure the first two; pages that need to detect the initial render also pull in the third element to compare against `fetchKey` (e.g. switching `fetchPolicy` between `'store-and-network'` and `'network-only'`). The tuple shape mimics `useState` so call sites read naturally.
+
+### 3.3 `useCurrentProject` — context selector
+
+```tsx
+const currentProject = useCurrentProjectValue();
+const [resourceGroup, setResourceGroup] = useCurrentResourceGroupState();
+```
+
+Split read vs read-write variants: `useXValue` for read-only, `useXState` for
+pair. Matches the Jotai convention.
+
+### 3.4 `useControllableState` — controllable prop pattern
+
+When a BUI component should support both controlled and uncontrolled modes,
+use `useControllableState` (already in `react/src/hooks/`):
+
+```tsx
+const [value, setValue] = useControllableState({
+  value: props.value,
+  defaultValue: props.defaultValue,
+  onChange: props.onChange,
+});
+```
+
+## 4. Parameterization: what goes in arguments
+
+| Kind | Where | Example |
+|---|---|---|
+| Configuration (rarely changes) | hook argument | `useFoo({ scope: 'global' })` |
+| Per-call inputs | returned function's argument | `startSession(values)` |
+| Context (server, project) | resolved inside the hook | `useSuspendedBackendaiClient()` inside |
+| Callbacks (success / error) | on the returned function | or resolved via hook-owned notification |
+
+Avoid making the hook signature reflect every callable option — prefer a
+returned object of methods with their own signatures. Callers can destructure.
+
+## 5. `useEffectEvent` — effect-internal helpers
+
+React 19.2+ `useEffectEvent` separates "what triggers the effect" from "what
+the effect does". Use it when you've been tempted to disable
+`react-hooks/exhaustive-deps` to omit a callback.
+
+```tsx
+import { useEffect, useEffectEvent } from 'react';
+
+const Child = ({ data, onLoaded }: Props) => {
+  // Reads latest onLoaded without forcing it into deps
+  const onResolved = useEffectEvent(() => {
+    if (data) onLoaded(data);
+  });
+
+  useEffect(() => {
+    onResolved();
+  }, [data]);   // truly the only reactive dep
+};
+```
+
+Rules (from `.claude/rules/use-effect-event.md`):
+
+- Only call inside `useEffect` / `useLayoutEffect` / `useInsertionEffect`.
+- Don't pass to JSX as `onClick` etc.
+- Don't use to bypass legitimate dependencies — only for
+  closures-the-effect-calls-but-doesn't-sync-on.
+- Don't introduce new `ahooks` `useMemoizedFn`. Remove it when you see it
+  nearby — `useEffectEvent` is the modern replacement.
+
+## 6. Move-don't-abstract
+
+Before spawning a hook, consider if the logic wants to live closer to where
+it's used, not further. `SharedMemoryFormItems` (FR-1492 #4303) was extracted
+from `ResourceAllocationFormItems` not to hide logic but because it had grown
+into an independent concern.
+
+Good signs for moving code into a hook:
+
+- The caller only needs the return value, not the intermediate states
+- Pulling it out reduces `useState` count in the caller
+- Tests become easier (hook-level Jest vs component-level RTL)
+
+Bad signs (don't extract yet):
+
+- You'd have to pass 4+ args to reconstruct the closure
+- Caller still needs to mirror the state for rendering
+- The "hook" is really one `useMemo` wrapping a pure function
+
+## 7. Testing hooks
+
+Place Jest tests at `react/src/hooks/__tests__/useFoo.test.tsx` or colocated
+as `useFoo.test.tsx`. Use `@testing-library/react`'s `renderHook`:
+
+```tsx
+import { renderHook, act } from '@testing-library/react';
+
+const { result } = renderHook(() => useFetchKey());
+act(() => { result.current[1](); });
+expect(result.current[0]).not.toBe(INITIAL_FETCH_KEY);
+```
+
+For hooks that call Relay, use `RelayEnvironmentProvider` with a test env —
+see `useControllableState.test.ts` for a mock environment example.
+
+## 8. Returning JSX from a hook
+
+Fine when the hook owns an overlay/notification pattern. Naming stays
+`useX` (not `renderX`):
+
+```tsx
+export const useDeleteConfirm = () => {
+  const { modal } = App.useApp();
+  const confirm = (opts: Opts) => modal.confirm({ ... });
+  return { confirm };
+};
+```
+
+If a hook would return a full `<Component/>`, reconsider — that usually wants
+to be a component, not a hook.
+
+## Related Skills
+
+- **`react-component-basics`** — base file layout and when logic stays inline
+- **`react-async-actions`** — batch-operation hooks (`useStartSession` pattern)
+- **`react-form`** — extracting `*FormItems` component groups
+- **`relay-patterns`** — hooks that wrap Relay queries / mutations
+
+## 9. Verification Checklist
+
+- [ ] Hook uses at least one React hook internally (else it's a helper function).
+- [ ] Named `use*` matching what it returns/does.
+- [ ] `'use memo'` at the start of the hook body when it contains non-trivial work.
+- [ ] Collects its own context (`useTranslation`, clients, atoms) — caller doesn't have to pass `t`.
+- [ ] Returns a named object (not a tuple, unless mimicking `useState`).
+- [ ] Effect dependencies are only values the effect truly syncs on; callbacks closed over via `useEffectEvent`.
+- [ ] No `// eslint-disable-next-line react-hooks/exhaustive-deps`.
+- [ ] No new `ahooks` `useMemoizedFn` introduced.
+- [ ] Colocated with feature if feature-specific; under `react/src/hooks/` if cross-cutting.
+- [ ] Has a Jest test when it owns non-trivial state or side-effects.
diff --git a/.claude/skills/react-layout/SKILL.md b/.claude/skills/react-layout/SKILL.md
@@ -0,0 +1,241 @@
+---
+name: react-layout
+description: >
+  Use when laying out a page, card header, or action row with `BAIFlex`,
+  choosing spacing values, or migrating `<Space>` / raw `<Flex>` to `BAIFlex`.
+  Covers gap token scale, `token.*` spacing, `BAICard` extra alignment, and
+  responsive grid patterns.
+---
+
+# Layout & Spacing
+
+This repo uses **`BAIFlex`** for every flex-based layout and **theme tokens**
+for every spacing value. Hard-coded pixels and `<Space direction="…">` have
+been actively removed across 2025.
+
+## Activation Triggers
+
+- Writing any JSX that arranges children horizontally/vertically
+- Padding / margin decisions in a component
+- Card header with `extra` that looks misaligned
+- Responsive grid for dashboard-like pages
+- Migrating existing `<Space>` or `<Flex>` (antd) usage
+
+## Gotchas
+
+- **`BAIFlex` `gap` string tokens** resolve via `(token as any)['size' + 'XS'.toUpperCase()]`. If a custom theme doesn't define `sizeXS`/`sizeMD`/etc., gap silently collapses to `'0px'`. Verify the theme when customizing.
+- **`BAIFlex` does not always stretch children by default.** Effective `alignItems` comes from `align` (default: `center`) and can also be overridden by `style.alignItems`. Use `align="stretch"` when column-direction layouts should stretch their children.
+- **`justify="between"` / `"around"`** are BAIFlex shorthands for `space-between` / `space-around`. Passing raw CSS values doesn't work.
+- **`Space.direction` is deprecated for layout** (antd v6). `Space.Compact` is still canonical for button + dropdown grouping — don't migrate it to BAIFlex.
+- **Hardcoded px breaks theming.** Admin primary colors (FR-1785 #4816) and dark mode rely on tokens. `padding: 8` compiles but diverges visually across themes.
+- **`createStyles` from antd-style re-renders on theme change.** Prefer inline `style={{ padding: token.paddingSM }}` when tokens suffice; reserve `createStyles` for pseudo-class / nested antd-class selectors.
+- **Tables without `scroll={{ x: 'max-content' }}`** overflow their parent on narrow viewports. Always set it on `BAITable`/`*Nodes`.
+- **Responsive `grid={{ xs, sm, md, lg, xl, xxl }}`** uses antd breakpoints (`xxl` = 1600px). Don't invent a custom breakpoint — the design system caps at xxl on purpose.
+
+## 1. `BAIFlex` is the layout primitive
+
+### 1.1 API cheat sheet
+
+```tsx
+import { BAIFlex } from 'backend.ai-ui';
+
+<BAIFlex
+  direction="column"       // 'row' (default) | 'row-reverse' | 'column' | 'column-reverse'
+  gap="sm"                 // token-size string or a number (px) or a [rowGap, colGap] tuple
+  align="stretch"          // 'start' | 'end' | 'center' | 'baseline' | 'stretch'
+  justify="between"        // 'start' | 'end' | 'center' | 'between' | 'around'
+  wrap="wrap"              // 'nowrap' (default) | 'wrap' | 'wrap-reverse'
+>
+  {children}
+</BAIFlex>
+```
+
+### 1.2 Gap token scale
+
+`gap` accepts the theme's `size*` tokens as strings:
+
+| `gap` value | Token | Typical |
+|---|---|---|
+| `'xxs'` | `token.sizeXXS` | 4px |
+| `'xs'`  | `token.sizeXS`  | 8px |
+| `'sm'`  | `token.sizeSM`  | 12px |
+| `'ms'`  | `token.sizeMS`  | 16px |
+| `'md'`  | `token.sizeMD`  | 20px |
+| `'lg'`  | `token.sizeLG`  | 24px |
+| `'xl'`  | `token.sizeXL`  | 32px |
+| `'xxl'` | `token.sizeXXL` | 48px |
+
+Numeric `gap` (e.g. `gap={10}`) is legal but should be rare — prefer tokens.
+
+```tsx
+// ✅ token-sized gaps
+<BAIFlex direction="column" gap="sm">…</BAIFlex>
+<BAIFlex justify="between" align="start" gap="xs" wrap="wrap">…</BAIFlex>
+
+// ✅ asymmetric row/column gap (tuple)
+<BAIFlex wrap="wrap" gap={['sm', 'md']}>…</BAIFlex>
+
+// ⚠️ Avoid unless you have a specific px target
+<BAIFlex gap={10}>…</BAIFlex>
+```
+
+### 1.3 `BAIFlex` vs `Flex` vs `Space`
+
+| Use | When |
+|---|---|
+| `BAIFlex` | Always, by default |
+| `Flex` (antd) | Only in BUI code that must not depend on the repo root (rare) |
+| `Space` | Never for layout. Only the `Space.Compact` wrapper is still fine (e.g. grouped button + dropdown) |
+
+FR-1326 (#4065) deduplicated the old internal `Flex` component into
+`BAIFlex` from `backend.ai-ui`. FR-1331 (#4070) added Jest tests for
+`BAIFlex` — the public API is stable and safe to extend.
+
+## 2. Spacing values come from `theme.useToken()`
+
+```tsx
+const { token } = theme.useToken();
+
+<div style={{
+  padding: token.paddingSM,
+  marginTop: token.marginXS,
+  background: token.colorBgContainer,
+}} />
+```
+
+Common tokens used in this repo:
+
+- `token.paddingXXS | paddingXS | paddingSM | padding | paddingMD | paddingLG`
+- `token.marginXXS | marginXS | marginSM | margin | marginMD | marginLG`
+- `token.size*` (for gap / flex)
+
+Never hard-code values like `padding: 8`, `margin: '0 16px'`. They break theme
+customization (dark mode, admin accent colors from FR-1785 #4816) and create
+visual inconsistency.
+
+## 3. `BAICard` with `extra` — use `BAIFlex` wrapper (FR-1292 #4007)
+
+`BAICard`'s `extra` slot misaligns with the title when the extra contains
+multiple elements. Wrap it in `BAIFlex`:
+
+```tsx
+<BAICard
+  title={t('general.Users')}
+  extra={
+    <BAIFlex align="center" gap="xs">
+      <BAIFetchKeyButton loading={...} value={fetchKey} onChange={updateFetchKey} />
+      <Button type="primary" icon={<PlusIcon />}>{t('button.Add')}</Button>
+    </BAIFlex>
+  }
+>
+  …
+</BAICard>
+```
+
+The wrapper's default `align="center"` guarantees vertical centering against
+the title line-height.
+
+## 4. Responsive Grid
+
+### 4.1 Dashboard-style grid
+
+For card grids that reflow by viewport:
+
+```tsx
+<List
+  grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 }}
+  dataSource={panels}
+  renderItem={(panel) => <List.Item><PanelCard {...panel} /></List.Item>}
+/>
+```
+
+### 4.2 Splitter for resizable side-by-side
+
+`<Splitter>` with `defaultSize` is the preferred pattern for filebrowser-like
+split views. Don't hand-roll CSS resize handles.
+
+## 5. `BAIRowWrapWithDividers` for divider-separated inline lists
+
+FR-1363 (#4132) introduced `BAIRowWrapWithDividers` for horizontally wrapping
+status rows with vertical dividers between items. Use it for metric rows where
+pipe characters would otherwise be hand-inserted:
+
+```tsx
+<BAIRowWrapWithDividers>
+  <StatItem label="CPU" value={cpu} />
+  <StatItem label="Memory" value={mem} />
+  <StatItem label="GPU" value={gpu} />
+</BAIRowWrapWithDividers>
+```
+
+## 6. Page-level layout
+
+Pages under `react/src/pages/` start with a vertical stretch `BAIFlex`:
+
+```tsx
+return (
+  <BAIFlex direction="column" align="stretch" gap="sm">
+    {/* header row */}
+    <BAIFlex justify="between" align="start" gap="xs" wrap="wrap">
+      <BAIFlex direction="row" gap="sm" align="start" wrap="wrap">
+        {/* filters */}
+      </BAIFlex>
+      <BAIFlex gap="xs">
+        {/* actions */}
+      </BAIFlex>
+    </BAIFlex>
+    {/* main content */}
+    <BAIUserNodes … />
+  </BAIFlex>
+);
+```
+
+Two invariants:
+- `align="stretch"` so children (especially tables) fill width
+- Outer `BAIFlex direction="column"` gap is `"sm"` by convention
+
+## 7. Table containers
+
+Tables need `scroll={{ x: 'max-content' }}` to avoid layout breakage on wide
+columns. Give them the `BAITable` wrapper, which already handles this plus
+column resize / reordering.
+
+```tsx
+<BAIUserNodes usersFrgmt={…} scroll={{ x: 'max-content' }} />
+```
+
+## 8. Don't `antd-style` what tokens can do
+
+`antd-style` / `createStyles` is fine for selectors you can't express with
+inline `style` (pseudo-classes, nested antd class overrides). But if you're
+setting `padding`, `margin`, `background`, `color`, or any value that maps to a
+token — use tokens inline instead. It's cheaper and co-located with the JSX.
+
+```tsx
+// ✅ Inline tokens
+<div style={{ padding: token.paddingSM, color: token.colorTextSecondary }} />
+
+// ✅ antd-style for pseudo-selectors
+const useStyles = createStyles(({ css }) => ({
+  modal: css`
+    .ant-modal-body { padding-top: 24px !important; }
+  `,
+}));
+```
+
+## Related Skills
+
+- **`react-component-basics`** — page root shape (`<BAIFlex direction="column" align="stretch" gap="sm">`)
+- **`react-relay-table`** — header row layout above tables
+- **`react-modal-drawer`** — modal footer layout
+- **`react-form`** — form field row spacing
+
+## 9. Verification Checklist
+
+- [ ] No hardcoded spacing values; all through `token.*` or `BAIFlex` gap strings.
+- [ ] `BAIFlex` everywhere, not `Flex` (antd) or `Space` (except `Space.Compact`).
+- [ ] Card with multi-element `extra` wraps content in `BAIFlex`.
+- [ ] Tables have `scroll={{ x: 'max-content' }}`.
+- [ ] Page root is `BAIFlex direction="column" align="stretch" gap="sm"`.
+- [ ] Responsive grids use antd `grid` prop with the standard xs/sm/md/lg/xl/xxl scale.
+- [ ] `createStyles` is used only for selectors inline `style` can't express.
diff --git a/.claude/skills/react-modal-drawer/SKILL.md b/.claude/skills/react-modal-drawer/SKILL.md
@@ -0,0 +1,284 @@
+---
+name: react-modal-drawer
+description: >
+  Use when creating or editing a modal/drawer, adding a form inside one,
+  debugging stale state or close-animation issues, or deciding between
+  `BAIModal` and `modal.confirm`. Covers `BAIUnmountAfterClose` wrapping,
+  `onRequestClose` convention, and id-based open state.
+---
+
+# React Modal & Drawer Patterns
+
+Extracted from FR-1343 (#4093), FR-1404 (#4183), FR-502 (#3136),
+FR-1673 (#4628), FR-1511 (#4331), FR-1685/1695 (#4656/#4664), and FR-617 (#3294).
+
+## Activation Triggers
+
+- Creating a new modal or drawer component
+- Adding a form inside a modal/drawer
+- Stale state on reopen, or animation jank on close
+- Questions about `BAIUnmountAfterClose`, `destroyOnHidden`, or
+  `afterOpenChange` vs `afterClose`
+- Routing a modal's open state via URL / id state
+
+## Gotchas
+
+- **`BAIUnmountAfterClose` requires a SINGLE child** (`React.Children.only`). Wrap one modal/drawer per wrapper — not a fragment, not two siblings.
+- **The wrapper chains `afterClose` / `afterOpenChange`**, so your child's callback still runs. Don't duplicate unmount logic on both sides.
+- **`destroyOnHidden` (antd) unmounts synchronously** and skips the exit animation. It is NOT a substitute for `BAIUnmountAfterClose`.
+- **Drawer uses `afterOpenChange(open: boolean)`**, Modal uses `afterClose()` (no arg). Don't assume the same signature.
+- **`modal.confirm({ onOk: async () => { ... } })`**: the loader is shown while pending and rethrows on rejection — always wrap in try/catch inside `onOk`.
+- **id-state + `useTransition`**: use `open={!!idState || isPending}` so the modal paints during the transition instead of waiting for the heavy query to resolve.
+- **URL-driven modal open (FR-1846 #4921)** still needs `BAIUnmountAfterClose` — reloading while open otherwise reopens with stale query/form state.
+- **`BAIModal.loading` shows the built-in skeleton**, separate from any `<Suspense fallback>` inside the body. Don't stack both on the same region.
+
+## 1. Always Wrap with `BAIUnmountAfterClose`
+
+Modals and drawers that own any of the following MUST be wrapped:
+
+- A `<Form>` (state survives close → stale values next open)
+- A Relay `useLazyLoadQuery` or subscription
+- A mutation's intermediate `useState`
+- Any `useState` that isn't reset on close
+
+`BAIUnmountAfterClose` preserves the exit animation then unmounts the child —
+so the next open starts with fresh state.
+
+```tsx
+import { BAIUnmountAfterClose } from 'backend.ai-ui';
+
+<BAIUnmountAfterClose>
+  <PurgeUsersModal
+    open={openPurgeUsersModal}
+    onOk={...}
+    onCancel={...}
+    usersFrgmt={_.compact(selectedUserList.map((u) => u?.node))}
+  />
+</BAIUnmountAfterClose>
+```
+
+### How it works (so you don't fight it)
+
+Intercepts the child's `afterClose` (Modal) and `afterOpenChange` (Drawer)
+callbacks. If you also provide those callbacks, they still run — the wrapper
+chains them.
+
+```tsx
+// child can define its own afterClose; wrapper preserves it
+<BAIUnmountAfterClose>
+  <BAIModal open={open} afterClose={() => doSomething()} />
+</BAIUnmountAfterClose>
+```
+
+### Do NOT use `destroyOnHidden` as a substitute
+
+`destroyOnHidden` (antd) unmounts immediately, skipping the close animation.
+`BAIUnmountAfterClose` is the project-wide answer. `destroyOnHidden` is OK for
+a modal with **only** refs-based forms when the flash is acceptable — in practice
+we default to the wrapper.
+
+## 2. `onRequestClose` — the project's close-callback convention
+
+Instead of two separate props `onCancel` / `onOk`, most modal components in
+this repo expose a single `onRequestClose(result?)` that distinguishes success
+via its argument.
+
+```tsx
+interface FolderCreateModalProps extends BAIModalProps {
+  onRequestClose: (response?: FolderCreationResponse) => void;
+  initialValidate?: boolean;
+  initialValues?: Partial<FolderCreateFormItemsType>;
+}
+
+// caller
+<FolderCreateModal
+  open={open}
+  onRequestClose={(result) => {
+    if (result) updateFetchKey();  // success path
+    setOpen(false);
+  }}
+/>
+```
+
+When a modal MUST surface both buttons' intent (e.g. delete flow with different
+follow-up), keep the antd-native `onOk` / `onCancel` pair — PurgeUsersModal
+does this.
+
+## 3. Open State: by-id beats by-boolean
+
+If a modal depends on a specific record, drive its `open` prop from the id
+state instead of a separate boolean. Two fewer `useState`s, and the record
+context is always in sync.
+
+```tsx
+// ❌ Two useStates drift out of sync
+const [openInfo, setOpenInfo] = useState(false);
+const [selectedEmail, setSelectedEmail] = useState<string | null>(null);
+
+// ✅ Id IS the open state
+const [emailForInfoModal, setEmailForInfoModal] = useState<string | null>(null);
+
+<UserInfoModal
+  userEmail={emailForInfoModal || ''}
+  open={!!emailForInfoModal}
+  onRequestClose={() => setEmailForInfoModal(null)}
+/>
+```
+
+### 3.1 With `useTransition` for deferred open
+
+When opening a modal would synchronously trigger a heavy query:
+
+```tsx
+const [isPending, startTransition] = useTransition();
+const [emailForSettingModal, setEmailForSettingModal] = useState<string | null>(null);
+
+<BAIButton
+  onClick={() =>
+    startTransition(() => setEmailForSettingModal(record.email))
+  }
+>
+  Edit
+</BAIButton>
+
+<UserSettingModal
+  userEmail={emailForSettingModal}
+  open={!!emailForSettingModal || isPending}
+  loading={isPending}
+  onRequestClose={() => setEmailForSettingModal(null)}
+/>
+```
+
+`open` stays truthy during the transition so the modal can paint its skeleton
+instead of waiting on the heavy query to resolve.
+
+### 3.2 Opening from URL (FR-1846)
+
+If a modal can be opened via query param (e.g. deep-link), drive `open` from
+URL state. Use `useQueryStates` with `parseAsString` — see `react-url-state`.
+
+## 4. `afterOpenChange` vs `afterClose`
+
+| Hook | Fires when | Use for |
+|---|---|---|
+| `afterOpenChange(true)` | After open animation ends | One-shot setup (e.g. `validateFields()` if `initialValidate`) |
+| `afterOpenChange(false)` | After close animation ends | Reset local state not in the form |
+| `afterClose` | Modal only, after close anim | Cleanup callback for non-Drawer modals |
+
+```tsx
+<BAIModal
+  open={open}
+  afterOpenChange={(open) => {
+    if (open && initialValidate) {
+      formRef.current?.validateFields();
+    }
+  }}
+/>
+```
+
+When using `BAIUnmountAfterClose`, your `afterClose`/`afterOpenChange` still run.
+
+## 5. Confirmation Dialogs: `App.useModal()` for ad-hoc
+
+Don't build a `<Modal open>` component for a one-shot "Are you sure?" prompt.
+Use `modal.confirm()` from `App.useApp()`.
+
+```tsx
+const { modal } = App.useApp();
+
+const handleRemoveShare = () => {
+  modal.confirm({
+    title: t('data.folders.RemoveFolderSharing'),
+    content: t('data.folders.RemoveFolderSharingDescription'),
+    okButtonProps: { danger: true },
+    onOk: async () => {
+      await removeSharing();
+      message.success(t('data.folders.RemoveFolderSharingSuccess'));
+    },
+  });
+};
+```
+
+When the confirmation needs rich content / form / mutation with multi-stage
+feedback → then build a proper `*Modal` component.
+
+Reusable confirmation helpers that exist:
+- `BAIConfirmModalWithInput` — confirm by typing a token
+- `BAIDeleteConfirmModal` — dangerous delete flow with double-check
+
+## 6. Modal Footer Layout
+
+Use `BAIFlex` for footer layout, not `<Space>`:
+
+```tsx
+footer={
+  <BAIFlex justify="between">
+    <BAIButton danger onClick={() => formRef.current?.resetFields()}>
+      {t('button.Reset')}
+    </BAIButton>
+    <BAIFlex gap="sm">
+      <BAIButton onClick={() => onRequestClose()}>
+        {t('button.Cancel')}
+      </BAIButton>
+      <BAIButton
+        type="primary"
+        action={async () => { await handleOk(); }}
+      >
+        {t('data.Create')}
+      </BAIButton>
+    </BAIFlex>
+  </BAIFlex>
+}
+```
+
+The primary submit button always uses `BAIButton.action` so loading state is
+automatic. Never pair `action` with `onClick`.
+
+## 7. Loading Skeleton While Data Not Ready
+
+If the modal's header depends on a suspended query, use `loading` on the modal
+to show the built-in skeleton:
+
+```tsx
+<BAIModal
+  loading={isFetchingAllowedTypes}
+  title={t('data.CreateANewStorageFolder')}
+  // ...
+/>
+```
+
+Inside the body, wrap Relay content in `<Suspense fallback={<Skeleton active />}>`.
+
+## 8. Drawer Specifics
+
+Drawers follow the same rules with two additions:
+
+- Use `afterOpenChange(false)` to detect close (no `afterClose`).
+- Wrap in `BAIUnmountAfterClose` when the drawer owns form / Relay state, same
+  as modals — the wrapper handles `afterOpenChange` interception.
+
+## 9. Cross-Modal Communication
+
+Avoid `useEffect`-driven coordination between sibling modals. Instead:
+
+- Lift the shared state to the parent.
+- On child success, call `onRequestClose(result)` — parent decides what to do.
+- For data refresh, call `updateFetchKey()` on the parent's `useFetchKey` hook.
+
+## Related Skills
+
+- **`react-form`** — forms inside modals (validators, required markers)
+- **`react-url-state`** — opening a modal from URL query params
+- **`react-async-actions`** — submit button and feedback inside modal footer
+- **`react-component-basics`** — `BAIModalProps` / `BAIDrawerProps` extension pattern
+- **`react-suspense-fetching`** — when the modal body owns a Relay query
+
+## 10. Verification Checklist
+
+- [ ] Modals with forms or Relay queries are wrapped in `BAIUnmountAfterClose`.
+- [ ] Record-bound modals use id-state for `open` (not a separate boolean).
+- [ ] Primary submit button uses `BAIButton.action` (not `loading={…}`).
+- [ ] `onRequestClose` convention used instead of split `onOk`/`onCancel` when no distinct success-vs-cancel path is needed.
+- [ ] Simple confirmations use `modal.confirm()` from `App.useApp()`, not an inline `<Modal>`.
+- [ ] Footer uses `BAIFlex`, not `<Space>`.
+- [ ] No `useEffect` chains between parent and modal — prefer lifted state + `onRequestClose`.
diff --git a/.claude/skills/react-relay-table/SKILL.md b/.claude/skills/react-relay-table/SKILL.md
@@ -0,0 +1,388 @@
+---
+name: react-relay-table
+description: >
+  Use when creating a `*Nodes` component bound to a Relay fragment, wiring a
+  page to one with `customizeColumns` / URL state / pagination, adding row
+  selection and bulk actions, or setting up CSV export. Covers the query
+  orchestrator + fragment split and `BAITable` conventions.
+---
+
+# Relay Fragment Tables
+
+Patterns extracted from `BAIUserNodes`, `SessionNodes`, `VFolderNodes`,
+`UserManagement.tsx`, and `AdminComputeSessionListPage.tsx`. Relevant PRs:
+FR-319 (#2932) intro NEO list, FR-465 (#3104) NEO prop, FR-448 (#3170) tab
+counts, FR-466/883 (#3586) sort cycle, FR-966 (#3627) custom pagination slot,
+FR-1315 (#4063) column visibility, FR-1804 (#4863) `customizeColumns`,
+FR-1788 (#4820) `BooleanTagWithFallBack`.
+
+See the `create-relay-nodes-component` skill for a generator that creates a
+fresh `*Nodes` file skeleton; this skill documents the patterns that skeleton
+should conform to and how the orchestrator page binds to it.
+
+## Activation Triggers
+
+- Creating a new `*Nodes` component bound to a GraphQL type
+- Creating or modifying a page that embeds a `*Nodes` table
+- Adding/removing/reordering columns from a consumer via `customizeColumns`
+- Wiring table sort / filter / pagination to URL query params
+- Column visibility settings (`tableSettings.columnOverrides`)
+- CSV export of table data
+
+Also consult:
+- `relay-patterns` — general fragment architecture
+- `react-url-state` — the nuqs side of pagination / filter state
+- `react-suspense-fetching` — fetchKey / deferred variables
+
+## Gotchas
+
+- **`tablePaginationOption.current` is 1-indexed, `baiPaginationOption.offset` is 0-indexed.** `useBAIPaginationOptionStateOnSearchParam` converts via `(current - 1) * pageSize` — don't swap them.
+- **`@relay(plural: true)` fragment** needs an *array* of refs. Pass `edges.map((e) => e.node)` through `filterOutNullAndUndefined`, not the raw edge array.
+- **`@catch(to: RESULT)` changes the return shape** to `{ ok, value } | { ok: false, ... }`. Consumers must check `.ok` before accessing `.value`.
+- **`customizeColumns(base)` runs on every render.** The passed function should be stable (React Compiler handles this under `'use memo'`) — don't do heavy work inside.
+- **Duplicate column `key`** silently breaks the column-visibility settings modal AND CSV export. Keys must be unique across base + customized columns.
+- **`fixed: true` + `required: true` on the primary column** means users can't hide it or scroll it off-screen. Apply only to the identifying column (email / name / id).
+- **`exportKey` is required when `dataIndex` doesn't match the GraphQL field name.** Without it, CSV export writes `undefined` for computed columns (e.g. `project` column exporting `project_name`).
+- **`availableXxxSorterKeys` is the single source of truth.** Adding a sortable column means updating the const array AND the column's `sorter: isEnableSorter('key')`.
+
+## 1. Two-file architecture: orchestrator vs `*Nodes`
+
+```
+Page/*Management component (orchestrator)       `*Nodes` component (fragment)
+├── useLazyLoadQuery + fetchKey + useDeferred   ├── useFragment with @relay(plural: true)
+├── nuqs URL state (order, filter, status)      ├── Exports `UserNodeInList` type
+├── useBAIPaginationOptionStateOnSearchParam    ├── Owns `baseColumns`
+├── Passes `usersFrgmt={edges.map(node)}`       ├── Applies `customizeColumns?(base)`
+├── Passes `customizeColumns={…}`               ├── Renders <BAITable>
+└── Passes pagination / selection props         └── Emits `onChangeOrder`
+```
+
+The `*Nodes` component is **dumb about fetching** — it does not trigger refetches,
+does not own the URL state, does not know about `fetchKey`. All of that lives on
+the orchestrator. This is what makes `customizeColumns` composable.
+
+## 2. Fragment Component Skeleton
+
+```tsx
+import { BAITable, BAIColumnType, BAITableProps, filterOutNullAndUndefined }
+  from '..';
+
+export type UserNodeInList = NonNullable<BAIUserNodesFragment$data[number]>;
+
+const availableUserSorterKeys = [
+  'email', 'username', 'full_name', 'role', 'created_at',
+] as const;
+export const availableUserSorterValues = [
+  ...availableUserSorterKeys,
+  ...availableUserSorterKeys.map((k) => `-${k}` as const),
+] as const;
+
+const isEnableSorter = (key: string) =>
+  _.includes(availableUserSorterKeys, key);
+
+interface BAIUserNodesProps extends Omit<
+  BAITableProps<UserNodeInList>,
+  'dataSource' | 'columns' | 'onChangeOrder'
+> {
+  usersFrgmt: BAIUserNodesFragment$key;
+  customizeColumns?: (base: BAIColumnType<UserNodeInList>[]) =>
+    BAIColumnType<UserNodeInList>[];
+  disableSorter?: boolean;
+  onChangeOrder?: (order: (typeof availableUserSorterValues)[number] | null) =>
+    void;
+}
+
+const BAIUserNodes: React.FC<BAIUserNodesProps> = ({
+  usersFrgmt, customizeColumns, disableSorter, onChangeOrder, ...tableProps
+}) => {
+  'use memo';
+  const { t } = useTranslation();
+
+  const users = useFragment(graphql`
+    fragment BAIUserNodesFragment on UserNode @relay(plural: true) {
+      id @required(action: NONE)
+      email @required(action: NONE)
+      username
+      // … fields the table might ever render
+    }
+  `, usersFrgmt);
+
+  const baseColumns = _.map(
+    filterOutEmpty<BAIColumnType<UserNodeInList>>([
+      {
+        key: 'email',
+        title: t('comp:UserNodes.Email'),
+        sorter: isEnableSorter('email'),
+        dataIndex: 'email',
+        fixed: true,
+        required: true,
+        render: (__, record) => <BAIText copyable>{record.email}</BAIText>,
+      },
+      // … more columns
+    ]),
+    (column) => disableSorter ? _.omit(column, 'sorter') : column,
+  );
+
+  const allColumns = customizeColumns ? customizeColumns(baseColumns) : baseColumns;
+
+  return (
+    <BAITable
+      resizable
+      rowKey="id"
+      size="small"
+      dataSource={filterOutNullAndUndefined(users)}
+      columns={allColumns}
+      scroll={{ x: 'max-content' }}
+      onChangeOrder={(order) =>
+        onChangeOrder?.((order as (typeof availableUserSorterValues)[number]) || null)
+      }
+      {...tableProps}
+    />
+  );
+};
+export default BAIUserNodes;
+```
+
+### Key invariants
+
+- Fragment is `@relay(plural: true)` — `usersFrgmt` is an array of refs,
+  orchestrator passes `edges.map((e) => e.node)`.
+- All i18n keys under the `comp:` namespace (`comp:UserNodes.Email`).
+- `@required(action: NONE)` on id and the human-key field (`email`/`name`).
+- `fixed: true` + `required: true` on the primary identifying column so
+  column settings UI can't hide it and it doesn't scroll horizontally.
+- Sorter keys live in a `const as const` array once, reused for prop typing.
+- Order descending by default on `created_at` if present: `defaultSortOrder: 'descend'`.
+
+## 3. `customizeColumns` composition
+
+Consumers override, not append. Array-based `extraColumns` is the old pattern
+and should be migrated.
+
+```tsx
+// ❌ Old array-based API (can only append at the end)
+<BAIUserNodes extraColumns={[actionColumn]} />
+
+// ✅ Function-based: full control
+<BAIUserNodes
+  usersFrgmt={…}
+  customizeColumns={(baseColumns) => [
+    { ...baseColumns[0], render: renderEmailWithActions }, // wrap primary column
+    ...baseColumns.slice(1),                                // keep the rest
+  ]}
+/>
+
+// ✅ Filter + reorder example
+customizeColumns={(base) =>
+  base
+    .filter((c) => c.key !== 'container_gids')
+    .map((c) => c.key === 'role' ? { ...c, width: 200 } : c)
+}
+```
+
+When a consumer needs to inject an action column mid-table, use
+`baseColumns.slice(0, n)` + new column + `baseColumns.slice(n)`.
+
+## 4. Orchestrator Wiring (full example)
+
+```tsx
+const UserManagement: React.FC = () => {
+  'use memo';
+  const { t } = useTranslation();
+  const { token } = theme.useToken();
+
+  // URL state (see react-url-state)
+  const [queryParams, setQueryParams] = useQueryStates({
+    filter: parseAsString.withDefault(''),
+    order: parseAsString,   // null means default; enables ascend/descend/null cycle
+    status: parseAsStringLiteral(['active', 'inactive']).withDefault('active'),
+  });
+
+  const { baiPaginationOption, tablePaginationOption, setTablePaginationOption } =
+    useBAIPaginationOptionStateOnSearchParam({ current: 1, pageSize: 10 });
+
+  const [fetchKey, updateFetchKey] = useFetchKey();
+
+  const queryVariables = {
+    first: baiPaginationOption.limit,
+    offset: baiPaginationOption.offset,
+    filter: mergeFilterValues([queryParams.filter, statusFilter]),
+    order: queryParams.order || '-created_at',   // fall back in variables, not URL
+  };
+  const deferredQueryVariables = useDeferredValue(queryVariables);
+  const deferredFetchKey = useDeferredValue(fetchKey);
+
+  const { user_nodes } = useLazyLoadQuery<UserManagementQuery>(
+    graphql`
+      query UserManagementQuery(
+        $first: Int, $offset: Int, $filter: String, $order: String
+      ) {
+        user_nodes(first: $first, offset: $offset, filter: $filter, order: $order) {
+          count
+          edges {
+            node {
+              id @required(action: THROW)
+              email @required(action: THROW)
+              ...BAIUserNodesFragment
+            }
+          }
+        }
+      }
+    `,
+    deferredQueryVariables,
+    {
+      fetchKey: deferredFetchKey,
+      fetchPolicy:
+        deferredFetchKey === INITIAL_FETCH_KEY ? 'store-and-network' : 'network-only',
+    },
+  );
+
+  const [columnOverrides, setColumnOverrides] = useBAISettingUserState(
+    'table_column_overrides.UserManagement',
+  );
+  const { supportedFields, exportCSV } = useCSVExport('users');
+
+  return (
+    <BAIUserNodes
+      usersFrgmt={filterOutNullAndUndefined(_.map(user_nodes?.edges, 'node'))}
+      customizeColumns={(base) => [
+        { ...base[0], render: renderEmailWithActions },
+        ...base.slice(1),
+      ]}
+      scroll={{ x: 'max-content' }}
+      pagination={{
+        pageSize: tablePaginationOption.pageSize,
+        total: user_nodes?.count || 0,
+        current: tablePaginationOption.current,
+        onChange: (current, pageSize) => setTablePaginationOption({ current, pageSize }),
+      }}
+      onChangeOrder={(next) => setQueryParams({ order: next })}
+      order={queryParams.order}
+      loading={
+        deferredQueryVariables !== queryVariables ||
+        deferredFetchKey !== fetchKey
+      }
+      tableSettings={{
+        columnOverrides,
+        onColumnOverridesChange: setColumnOverrides,
+      }}
+      exportSettings={!_.isEmpty(supportedFields) ? {
+        supportedFields,
+        onExport: async (keys) => { await exportCSV(keys, { status: [queryParams.status] }); },
+      } : undefined}
+    />
+  );
+};
+```
+
+Key points:
+
+- **`loading` derives from deferred equality**, not a manual `useState(false)`.
+- **Default order lives in `queryVariables`, not URL state** — so `?order=` stays
+  clean but the API still gets `-created_at`. Supports null → ascend → descend → null cycle.
+- **`fetchKey` deferred separately** so hitting refresh doesn't tear state twice.
+- **Column overrides persist in user settings** via
+  `useBAISettingUserState('table_column_overrides.<StableKey>')`.
+
+## 5. Selection, Bulk Actions
+
+```tsx
+const [selected, setSelected] = useState<UserNode[]>([]);
+
+<BAIUserNodes
+  usersFrgmt={…}
+  rowSelection={{
+    type: 'checkbox',
+    selectedRowKeys: _.compact(selected.map((u) => u.node?.id)),
+    onChange: (keys) => {
+      const edges = _.compact(user_nodes?.edges);
+      setSelected(edges.filter((e) => e.node && keys.includes(e.node.id)));
+    },
+  }}
+/>
+
+// visible counter + bulk action buttons
+{selected.length > 0 && (
+  <BAIFlex gap="xs">
+    <BAISelectionLabel count={selected.length} onClearSelection={() => setSelected([])} />
+    <BAIButton icon={<EditIcon />} onClick={…} />
+  </BAIFlex>
+)}
+```
+
+## 6. Filter UX: `BAIPropertyFilter`
+
+Use `BAIPropertyFilter` with `filterOutEmpty` to compose feature-flagged rules:
+
+```tsx
+<BAIPropertyFilter
+  filterProperties={filterOutEmpty([
+    { key: 'email', propertyLabel: t('general.E-Mail'), type: 'string' },
+    bailClient.supports('user-node-query-project-filter') && {
+      key: 'project_name', propertyLabel: t('general.Project'), type: 'string',
+    },
+    { key: 'role', propertyLabel: t('credential.Role'), type: 'string',
+      strictSelection: true, defaultOperator: '==',
+      options: [{ label: 'superadmin', value: 'superadmin' }] },
+  ])}
+  value={queryParams.filter || undefined}
+  onChange={(v) => setQueryParams({ filter: v || '' })}
+/>
+```
+
+- Pass `undefined` (not `''`) into `value` so the filter pill doesn't render for an empty filter.
+- Use `mergeFilterValues([queryParams.filter, statusFilter, typeFilter])` to
+  compose URL filter with page-derived fragments (e.g. status tab).
+
+## 7. Refresh Button
+
+```tsx
+<BAIFetchKeyButton
+  loading={deferredFetchKey !== fetchKey}
+  value={fetchKey}
+  onChange={updateFetchKey}
+/>
+```
+
+Its `loading` binds to the deferred/non-deferred comparison, so spinning state
+matches the actual query.
+
+## 8. Column Visibility / Export
+
+`tableSettings.columnOverrides` + `exportSettings` plug into the column-settings
+modal baked into `BAITable` (FR-1315, FR-1443). Persist overrides per-page
+under a stable key:
+
+```tsx
+useBAISettingUserState('table_column_overrides.AdminComputeSessionListPage')
+useBAISettingUserState('table_column_overrides.UserManagement')
+```
+
+For CSV, declare `exportKey` on a column when its GraphQL field name differs
+from `dataIndex`:
+
+```tsx
+{ key: 'id', title: 'ID', exportKey: 'uuid', render: … }
+{ key: 'project', title: t('comp:UserNodes.Project'), exportKey: 'project_name', render: … }
+```
+
+## Related Skills
+
+- **`create-relay-nodes-component`** — generator that scaffolds a fresh `*Nodes` file
+- **`relay-patterns`** — general Relay fragment architecture
+- **`react-url-state`** — URL side of filter / order / pagination state
+- **`react-suspense-fetching`** — `fetchKey` + `useDeferredValue` on the orchestrator
+- **`react-async-actions`** — bulk-action buttons and row-level mutations
+- **`relay-infinite-scroll-select`** — select-based variant (not table-based)
+
+## 9. Verification Checklist
+
+- [ ] `*Nodes` file does not call `useLazyLoadQuery`.
+- [ ] Orchestrator page passes a plain array of nodes, not the edge array.
+- [ ] `availableXxxSorterValues` is a single source of truth, reused on both sides.
+- [ ] Primary column is `fixed: true` and `required: true`.
+- [ ] Consumers override columns via `customizeColumns`, never by extending an `extraColumns` array.
+- [ ] `loading` on the table binds to deferred-variable equality, not manual state.
+- [ ] Column overrides persist with a unique page key.
+- [ ] CSV `exportKey` set when differs from `dataIndex`.
+- [ ] `scroll={{ x: 'max-content' }}` set on the table.
diff --git a/.claude/skills/react-suspense-fetching/SKILL.md b/.claude/skills/react-suspense-fetching/SKILL.md
@@ -0,0 +1,276 @@
+---
+name: react-suspense-fetching
+description: >
+  Use when fetching Relay data with `useLazyLoadQuery`, choosing a
+  `fetchPolicy`, placing Suspense boundaries, triggering a refetch after
+  mutation, or deciding when `useTanQuery` (REST) is acceptable. Covers
+  `fetchKey` + `useDeferredValue` and auto-refresh patterns.
+---
+
+# Data Fetching & Suspense
+
+Patterns from `AdminComputeSessionListPage`, `UserManagement`, `useStartSession`,
+FR-602 (#3249) Suspense, FR-1232 (#3989) Dashboard suspense, FR-941 (#3602)
+no-fallback-on-auto-refresh, FR-527 (#3169) `BAIFetchKeyButton`, FR-1351 (#4104)
+`useFetchKey` over `useUpdatableState`.
+
+## Activation Triggers
+
+- Writing a component that fetches via Relay `useLazyLoadQuery`
+- Choosing between Suspense fallback and inline skeleton
+- Variables change but don't want to retrigger a full Suspense fallback
+- Mutations need to refresh list data
+- Legacy REST endpoint: when is `useTanQuery` acceptable?
+
+## Gotchas
+
+- **`useLazyLoadQuery` suspends on every variable identity change.** Wrap `queryVariables` AND `fetchKey` in `useDeferredValue` or the UI tears on every keystroke/sort/page change.
+- **`INITIAL_FETCH_KEY` equality** uses the imported constant, not a string literal. `import { INITIAL_FETCH_KEY } from 'backend.ai-ui'` — comparing against `'INITIAL_FETCH_KEY'` always returns false.
+- **`fetchPolicy: 'network-only'` skips cache reads.** If the optimistic update hasn't landed yet, first render shows Suspense fallback. Choose `store-and-network` on initial load.
+- **Auto-refreshing cards must NOT sit inside a narrow Suspense** — each tick flashes the fallback (the FR-941 regression). Use `useRefetchableFragment` + `useTransition` and put the Suspense higher.
+- **`@catch(to: RESULT)` + `@required(action: THROW)` inside edges**: a thrown required inside the catch boundary makes the whole field `{ ok: false }`. Consumers must branch on `!ok`.
+- **`useTanQuery` `queryKey` must include every reactive variable** or stale-closure bugs appear. `enabled: false` does NOT suppress queryKey tracking.
+- **Imperative `fetchQuery` updates the store by node id** — components only re-render when their fragment shape matches. If nothing re-renders after `fetchQuery`, your fragment doesn't match the returned data.
+- **Nested Suspense boundaries cascade inside-out** — innermost paints its fallback first. Place boundaries where *independent* subtrees can fail, not at every route.
+
+## 1. The canonical orchestrator pattern
+
+```tsx
+const [queryParams, setQueryParams] = useQueryStates({ /* … */ });
+const { baiPaginationOption } = useBAIPaginationOptionStateOnSearchParam({
+  current: 1, pageSize: 10,
+});
+
+const [fetchKey, updateFetchKey] = useFetchKey();
+
+const queryVariables = {
+  first: baiPaginationOption.first,
+  offset: baiPaginationOption.offset,
+  filter: queryParams.filter,
+  order: queryParams.order || '-created_at',
+};
+
+const deferredQueryVariables = useDeferredValue(queryVariables);
+const deferredFetchKey = useDeferredValue(fetchKey);
+
+const data = useLazyLoadQuery<QueryType>(
+  graphql`…`,
+  deferredQueryVariables,
+  {
+    fetchKey: deferredFetchKey,
+    fetchPolicy: deferredFetchKey === INITIAL_FETCH_KEY
+      ? 'store-and-network'   // first load — can use cached data while revalidating
+      : 'network-only',        // subsequent refresh — always hit network
+  },
+);
+```
+
+### Why these four moving parts
+
+| Piece | What it does |
+|---|---|
+| `useFetchKey()` | Gives a bumpable key so refresh buttons can force a re-query |
+| `useDeferredValue(queryVariables)` | Variables change → next render starts fetching, but current UI keeps painting |
+| `useDeferredValue(fetchKey)` | Same, for the refresh trigger |
+| `fetchPolicy` dispatch on `INITIAL_FETCH_KEY` | First render: show cache if any; subsequent refresh: always re-fetch |
+
+Loading indicator derives from the deferred-inequality, NOT a separate `useState`:
+
+```tsx
+const loading =
+  deferredQueryVariables !== queryVariables ||
+  deferredFetchKey !== fetchKey;
+```
+
+`BAIFetchKeyButton` uses that same derivation.
+
+## 2. `useFetchKey`, not `useUpdatableState`
+
+FR-1351 (#4104) migrated `ComputeSessionListPage` off `useUpdatableState('first')`.
+Always use `useFetchKey`:
+
+```tsx
+import { useFetchKey, INITIAL_FETCH_KEY } from 'backend.ai-ui';
+
+const [fetchKey, updateFetchKey] = useFetchKey();
+
+// in a mutation:
+onCompleted: () => { updateFetchKey(); message.success(...); }
+```
+
+## 3. Suspense fallback placement
+
+### 3.1 Page boundary
+
+Pages use a Suspense at the route level (it's already there via the router setup
+after FR-2521 #6596). Individual page components **can** define a narrower
+Suspense when they show rich skeletons for long queries.
+
+```tsx
+<Suspense fallback={<Skeleton active />}>
+  <PageContents />
+</Suspense>
+```
+
+Never put `<Suspense>` on a boundary that unmounts on every variable change —
+that causes UI flashing. Rely on `useDeferredValue` instead to keep the old
+UI painting while loading.
+
+### 3.2 Card-shaped skeletons
+
+Use `BAIFallbackCard` for card containers:
+
+```tsx
+<Suspense fallback={<BAIFallbackCard />}>
+  <ResourcePanel />
+</Suspense>
+```
+
+### 3.3 Button-shaped skeletons
+
+Never render `<Button loading />` as a Suspense fallback. Use
+`<Skeleton.Button size="small" active />`:
+
+```tsx
+<Suspense fallback={<Skeleton.Button size="small" active />}>
+  <LazyFetchedButton />
+</Suspense>
+```
+
+### 3.4 Do NOT show fallback on auto-refresh (FR-941)
+
+When a card's data auto-refreshes (interval, subscription), a Suspense fallback
+flashes each tick. Patterns to avoid this:
+
+- Use `useRefetchableFragment` with `useTransition` so the transition keeps the
+  old data while loading.
+- Or gate the refresh behind `useDeferredValue` and don't wrap in a narrow
+  Suspense — let the parent route handle it.
+
+```tsx
+const [isPending, startTransition] = useTransition();
+
+startTransition(() => refetch({ /* new vars */ }));
+// UI shows `isPending` as a subtle indicator, but prior data stays visible.
+```
+
+## 4. `fetchPolicy` selection
+
+| Policy | Use |
+|---|---|
+| `store-and-network` | First load / navigating to a page — show cache if any, re-validate in background |
+| `network-only` | User hit refresh, or mutation-triggered refresh — don't trust cache |
+| `store-only` | Re-render from cache after an imperative `fetchQuery` populated the store |
+| `store-or-network` | Rare — only cache if present; otherwise fetch. Don't re-validate |
+
+The `deferredFetchKey === INITIAL_FETCH_KEY` dispatch is idiomatic: it's only
+`store-and-network` on the very first render (and a `router.Nav` that resets the
+fetchKey). Any refresh thereafter is `network-only`.
+
+## 5. Imperative: `fetchQuery`
+
+For side-effect callbacks that aren't part of a component's rendered query
+(e.g. notification `onClick` resolvers, `useStartSession`):
+
+```tsx
+fetchQuery<MyQuery>(relayEnv, graphql`…`, { id: globalId }).toPromise()
+  .then((result) => {
+    // Relay store updates automatically for matched node IDs.
+    // Other components reading those nodes re-render.
+  });
+```
+
+Prefer this over `refetch` when you don't need to re-render your own component.
+
+## 6. React-Query (`useTanQuery`) — only for REST
+
+Relay is the default. `useTanQuery` / `useTanMutation` (TanStack Query, aliased
+in `hooks/reactQueryAlias`) is used ONLY for legacy REST endpoints like
+`baiClient.vfolder.list_allowed_types()` — calls that aren't exposed through
+the GraphQL manager.
+
+```tsx
+const { data: allowedTypes, isFetching } = useTanQuery({
+  queryKey: ['allowedTypes', modalProps.open],
+  enabled: modalProps.open,
+  queryFn: () =>
+    modalProps.open ? baiClient.vfolder.list_allowed_types() : undefined,
+});
+```
+
+Rules:
+
+- `queryKey` must include any state the query depends on (don't rely on stale
+  closures — FR-1260-ish lesson).
+- `enabled` so the query doesn't run when the owning modal/drawer is closed.
+- Mutations go through `useTanMutation` with strongly-typed `TData`, `TError`,
+  `TVariables`.
+
+## 7. Handling nullable / error result unions
+
+Use Relay client `@catch(to: RESULT)` for GraphQL nodes that can fail at the
+node level:
+
+```graphql
+computeSessionNodeResult: compute_session_nodes(...) @catch(to: RESULT) {
+  edges @required(action: THROW) {
+    node @required(action: THROW) { … }
+  }
+  count
+}
+```
+
+Then:
+
+```tsx
+const { computeSessionNodeResult } = queryRef;
+const sessions = computeSessionNodeResult.ok
+  ? computeSessionNodeResult.value
+  : null;
+```
+
+For lists, use `filterOutNullAndUndefined` / `filterOutEmpty` instead of
+inline `.filter(Boolean)` to keep types narrow.
+
+## 8. Error Boundaries
+
+- `BAIErrorBoundary` — user-facing error UI (the default).
+- `ErrorBoundaryWithNullFallback` — silent failure for non-critical widgets.
+
+Place boundaries at component boundaries that should fail independently. Do
+NOT wrap every single route in a new boundary — lift the common one up.
+FR-1578 (#4430) cleaned up duplicate per-route boundaries.
+
+```tsx
+<BAIErrorBoundary>
+  <FeatureSection />
+</BAIErrorBoundary>
+
+<ErrorBoundaryWithNullFallback>
+  <OptionalBadge />
+</ErrorBoundaryWithNullFallback>
+```
+
+## 9. Promise.allSettled for fan-out REST
+
+When firing multiple REST calls, `Promise.allSettled` makes partial failures
+explicit (FR-1384 #4165). See `react-async-actions` for the full pattern.
+
+## Related Skills
+
+- **`relay-patterns`** — fragment architecture (`useFragment`, `useRefetchableFragment`)
+- **`react-url-state`** — deferred URL-backed query variables
+- **`react-relay-table`** — orchestrator wiring for list queries
+- **`react-async-actions`** — `updateFetchKey()` to trigger refresh after mutation
+- **`relay-infinite-scroll-select`** — `usePaginationFragment` variant
+
+## 10. Verification Checklist
+
+- [ ] Query variables + fetchKey both go through `useDeferredValue`.
+- [ ] `fetchPolicy` dispatches on `INITIAL_FETCH_KEY` vs later refresh.
+- [ ] `useFetchKey`, not `useUpdatableState`.
+- [ ] Auto-refreshing cards use transitions/refetch, not a Suspense boundary that flashes.
+- [ ] Suspense fallback sized to the content (Skeleton.Button, BAIFallbackCard, etc.).
+- [ ] REST-only dependency uses `useTanQuery` with a complete `queryKey` and `enabled` gating.
+- [ ] Nodes that can fail at node-level use `@catch(to: RESULT)`.
+- [ ] Error boundaries placed at independent-failure boundaries, not per-route.
diff --git a/.claude/skills/react-url-state/SKILL.md b/.claude/skills/react-url-state/SKILL.md
@@ -0,0 +1,270 @@
+---
+name: react-url-state
+description: >
+  Use when page state (filter, order, tab, pagination, modal-open) must
+  survive reload or be URL-shareable, or when migrating `use-query-params`
+  to `nuqs`. Covers `useQueryStates`, `parseAs*` parsers, `history: 'replace'`,
+  and pairing with `useDeferredValue` for React Transitions.
+---
+
+# URL State with nuqs
+
+Patterns from FR-1683 (#4646) migration to nuqs, FR-1431 (#4252), FR-1412
+(#4193), FR-706 (#3405), FR-567 (#3245), FR-1401 (#4179), FR-1058 (#3743).
+
+## Activation Triggers
+
+- Persisting filter / order / tab / pagination / modal open state across reloads
+- A URL should be shareable and reproduce the same view
+- Migrating existing `useQueryParams` / `useDeferredQueryParams` to `nuqs`
+- Pairing URL-backed query variables with `useLazyLoadQuery` + Suspense
+
+## Gotchas
+
+- **`parseAsString.withDefault('')` OMITS the key from the URL** when value equals `''`; `parseAsString` (no default) keeps `null` and the key. Pick based on whether "empty" means "default".
+- **Default `history: 'push'` adds a back-button entry per filter change** — user presses Back and lands on the previous filter instead of leaving the page. Always pass `{ history: 'replace' }` unless that's the desired UX.
+- **`setQueryParams(null)` resets ALL keys in the group to defaults.** `setQueryParams({ key: null })` clears only that key. The AdminComputeSessionListPage tab switcher relies on this reset.
+- **`parseAsStringLiteral(values)` silently coerces unknown URL values** to the default (or `undefined`) — no visible error. Type-safe on read but a typo in the URL doesn't fail loudly.
+- **Without `useDeferredValue` on `queryVariables`**, `useLazyLoadQuery` suspends on every keystroke/sort/page change — Suspense fallback flashes. This is the whole FR-1683 motivation.
+- **`useBAIPaginationOptionStateOnSearchParam` uses its own `useQueryStates`** — it doesn't share context with your page-level `useQueryStates`. Both write cleanly to URL but are independent.
+- **Batched setters in the same tick merge**, not overwrite. `setQueryParams({ a: 1 }); setQueryParams({ b: 2 })` → `{ a: 1, b: 2 }`, not `{ b: 2 }`.
+- **`useBAIPaginationOptionStateOnSearchParamLegacy` still exists** — don't introduce new usages; legacy only.
+
+## 1. Import and hook shape
+
+```tsx
+import {
+  parseAsString,
+  parseAsInteger,
+  parseAsBoolean,
+  parseAsStringLiteral,
+  useQueryStates,
+} from 'nuqs';
+
+const [queryParams, setQueryParams] = useQueryStates(
+  {
+    filter: parseAsString.withDefault(''),
+    order: parseAsString,  // null means "no explicit order" — default in variables
+    type: parseAsStringLiteral(['all', 'interactive', 'batch'] as const)
+            .withDefault('all'),
+    open: parseAsBoolean.withDefault(false),
+    first: parseAsInteger.withDefault(20),
+  },
+  { history: 'replace' },   // always replace unless "Back" semantics are important
+);
+```
+
+`queryParams.filter` is always a string (default `''`). `queryParams.order`
+can be `null` — keep the actual default in the query variables so URLs stay
+clean.
+
+### 1.1 `withDefault` vs not
+
+| Form | URL when value equals default | Param type |
+|---|---|---|
+| `parseAsString.withDefault('')` | omitted | `string` |
+| `parseAsString` | omitted when null | `string \| null` |
+| `parseAsStringLiteral([...]).withDefault('all')` | omitted | the literal union |
+
+Only use `.withDefault()` when there's a semantically meaningful default. Keep
+`order`/`search` nullable when a missing value means "use backend default".
+
+### 1.2 `history: 'replace'`
+
+Always pass `{ history: 'replace' }` unless the page treats filter/tab changes
+as navigable history entries. Tabs usually do NOT — user expects Back to leave
+the page, not cycle through filter states.
+
+## 2. Sorter cycle: null → ascend → descend → null
+
+When binding a sort column to URL state, keep `order` nullable and fall back
+inside `queryVariables`:
+
+```tsx
+const [queryParams, setQueryParams] = useQueryStates({
+  order: parseAsString,  // null, 'email', '-email', …
+});
+
+const queryVariables = {
+  order: queryParams.order || '-created_at', // default lives here
+};
+```
+
+In the `*Nodes`'s `onChangeOrder`:
+
+```tsx
+<BAIUserNodes
+  order={queryParams.order}
+  onChangeOrder={(next) => setQueryParams({ order: next })}
+/>
+```
+
+`null` back into the setter clears the URL key — no `?order=` on the URL when
+the user is on default. FR-460 / FR-883 established this cycle.
+
+## 3. Pagination: `useBAIPaginationOptionStateOnSearchParam`
+
+Don't hand-roll pagination URL state. Use the shared hook:
+
+```tsx
+import { useBAIPaginationOptionStateOnSearchParam }
+  from 'src/hooks/reactPaginationQueryOptions';
+
+const {
+  baiPaginationOption,       // { limit, first, offset }  — for GraphQL variables
+  tablePaginationOption,     // { pageSize, current }      — for antd table
+  setTablePaginationOption,  // partial updater
+} = useBAIPaginationOptionStateOnSearchParam({ current: 1, pageSize: 10 });
+```
+
+Internally it uses `parseAsInteger.withDefault(initial)` on `current`/`pageSize`
+with `history: 'replace'`. Don't duplicate this anywhere.
+
+## 4. Pair URL state with `useDeferredValue`
+
+`useLazyLoadQuery` suspends on variable changes. To keep the UI responsive
+while the next page loads, defer the variables:
+
+```tsx
+const queryVariables = {
+  first: baiPaginationOption.first,
+  offset: baiPaginationOption.offset,
+  filter: mergeFilterValues([queryParams.filter, statusFilter]),
+  order: queryParams.order || '-created_at',
+};
+
+const deferredQueryVariables = useDeferredValue(queryVariables);
+const deferredFetchKey = useDeferredValue(fetchKey);
+
+const { user_nodes } = useLazyLoadQuery(query, deferredQueryVariables, {
+  fetchKey: deferredFetchKey,
+  fetchPolicy: deferredFetchKey === INITIAL_FETCH_KEY
+    ? 'store-and-network' : 'network-only',
+});
+
+// derive table "loading" from deferred inequality
+const loading =
+  deferredQueryVariables !== queryVariables ||
+  deferredFetchKey !== fetchKey;
+```
+
+This is the whole transition contract. FR-1683's motivation was that `nuqs`
+`useQueryStates` plays well with React Transitions, whereas the old
+`useQueryParams` didn't. Don't bring back `useDeferredQueryParams`.
+
+## 5. Tab-scoped state cache via `useRef`
+
+When tabs represent independent views (session type all/interactive/batch…)
+and each tab should remember its own filter/order/page, cache the per-tab
+queryParams in a ref:
+
+```tsx
+const queryMapRef = useRef({
+  [queryParams.type]: { queryParams, tablePaginationOption },
+});
+
+useEffect(() => {
+  queryMapRef.current[queryParams.type] = { queryParams, tablePaginationOption };
+}, [queryParams, tablePaginationOption]);
+
+<BAITabs
+  activeKey={queryParams.type}
+  onChange={(key) => {
+    const stored = queryMapRef.current[key] || { queryParams: {} };
+    setQueryParams(null);                  // reset to defaults first
+    setQueryParams({ ...stored.queryParams, type: key as TypeFilterType });
+    setTablePaginationOption(stored.tablePaginationOption || { current: 1 });
+  }}
+/>
+```
+
+The `setQueryParams(null)` reset-to-defaults line is important — without it,
+values from the previous tab leak into the next (e.g. filtering by "email"
+stays applied when switching to a tab without that column).
+
+## 6. Controlled modals via URL (deep-link support)
+
+For modals users should be able to deep-link to (e.g. the Folder Explorer in
+FR-1846 #4921):
+
+```tsx
+const [{ folder: folderId }, setFolderId] = useQueryStates({
+  folder: parseAsString,
+});
+
+<BAIUnmountAfterClose>
+  <FolderExplorerModal
+    open={!!folderId}
+    folderId={folderId || undefined}
+    onRequestClose={() => setFolderId({ folder: null })}
+  />
+</BAIUnmountAfterClose>
+```
+
+Reload in the middle of an explorer session → the modal reopens on the same
+folder. Use `history: 'push'` (default) for these so Back closes the modal.
+
+## 7. Do NOT mix `useQueryParams` (legacy) and `nuqs`
+
+The repo still contains `useQueryParams` from `use-query-params` for a few
+legacy flows (`useRelayPaginationQueryOptions` etc). Do not introduce new
+usages. Migrate when touching nearby code:
+
+```tsx
+// ❌ legacy
+const [params, setParams] = useQueryParams({
+  filter: StringParam,
+  page: withDefault(NumberParam, 1),
+});
+
+// ✅ nuqs
+const [params, setParams] = useQueryStates({
+  filter: parseAsString.withDefault(''),
+  page: parseAsInteger.withDefault(1),
+}, { history: 'replace' });
+```
+
+`useBAIPaginationOptionStateOnSearchParamLegacy` still exists for backward
+compat — prefer the non-legacy variant (nuqs-based) for anything new.
+
+## 8. Typing URL-sized enums with `parseAsStringLiteral`
+
+```tsx
+const typeFilterValues = ['all', 'interactive', 'batch', 'inference', 'system'] as const;
+type TypeFilterType = (typeof typeFilterValues)[number];
+
+const [queryParams] = useQueryStates({
+  type: parseAsStringLiteral(typeFilterValues).withDefault('all'),
+});
+
+// queryParams.type: TypeFilterType
+```
+
+Invalid `?type=foo` in the URL is coerced to `undefined` (or the default),
+so consumers never have to defend against out-of-range strings.
+
+## 9. When NOT to use URL state
+
+- Ephemeral local state (modal open driven by button click, hover, selection in a form) → `useState`
+- Global UI state that applies across routes (sidebar collapsed) → `jotai`
+- Server/GraphQL state → Relay
+- Form draft values → antd Form
+
+URL state is for: what someone else pasting the URL should see.
+
+## Related Skills
+
+- **`react-suspense-fetching`** — pairing deferred URL variables with `useLazyLoadQuery`
+- **`react-relay-table`** — table pagination / filter / order as URL state
+- **`react-modal-drawer`** — deep-linking a modal via query param
+- **`relay-patterns`** — fragment architecture on the data side
+
+## 10. Verification Checklist
+
+- [ ] Uses `nuqs` (`useQueryStates`, `parseAs*`), not `use-query-params`.
+- [ ] `history: 'replace'` unless Back-button navigation through tab/filter changes is a desired feature.
+- [ ] Defaults either live in `.withDefault()` (when omission means the default) or in the derived `queryVariables` (for sort keys that should fall back without appearing in URL).
+- [ ] Query variables and fetchKey wrapped in `useDeferredValue` when feeding `useLazyLoadQuery`.
+- [ ] Pagination binds through `useBAIPaginationOptionStateOnSearchParam`, not hand-rolled.
+- [ ] Tab-scoped per-tab state cached via `useRef`, with a `setQueryParams(null)` reset before applying stored values.
+- [ ] `useBAIPaginationOptionStateOnSearchParamLegacy` not introduced in new code.
PATCH

echo "Gold patch applied."
