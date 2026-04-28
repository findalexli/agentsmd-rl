"""Behavioral checks for backend.ai-webui-chorefr2700-add-react-topiclevel-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/backend.ai-webui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-async-actions/SKILL.md')
    assert '- **`upsertNotification` with the same `key` replaces** the previous entry (intended for progress updates). Different keys create separate entries; forgetting this creates ghost notifications.' in text, "expected to find: " + '- **`upsertNotification` with the same `key` replaces** the previous entry (intended for progress updates). Different keys create separate entries; forgetting this creates ghost notifications.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-async-actions/SKILL.md')
    assert "- **`updateFetchKey()` only refreshes the orchestrator that owns the hook.** Child components with their own `useLazyLoadQuery` don't refresh. Place the fetch key at the right ownership level." in text, "expected to find: " + "- **`updateFetchKey()` only refreshes the orchestrator that owns the hook.** Child components with their own `useLazyLoadQuery` don't refresh. Place the fetch key at the right ownership level."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-async-actions/SKILL.md')
    assert "- **`Promise.allSettled` returns `{ status, value|reason }`.** Use `_.groupBy(results, 'status')` for typed access — don't hand-roll `.filter(r => r.status === 'fulfilled')`." in text, "expected to find: " + "- **`Promise.allSettled` returns `{ status, value|reason }`.** Use `_.groupBy(results, 'status')` for typed access — don't hand-roll `.filter(r => r.status === 'fulfilled')`."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-component-basics/SKILL.md')
    assert "Manual `useMemo` / `useCallback` should be reserved for profiled bottlenecks. Under `'use memo'` the compiler handles it automatically — reviewers will push back on speculative manual memoization." in text, "expected to find: " + "Manual `useMemo` / `useCallback` should be reserved for profiled bottlenecks. Under `'use memo'` the compiler handles it automatically — reviewers will push back on speculative manual memoization."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-component-basics/SKILL.md')
    assert "- **`extends Omit<ParentProps, 'key'>` with the wrong Omit list** silently drops props. Mirror antd v6 names — `<Alert title>` not `<Alert message>`. See `.claude/rules/antd-v6-props.md`." in text, "expected to find: " + "- **`extends Omit<ParentProps, 'key'>` with the wrong Omit list** silently drops props. Mirror antd v6 names — `<Alert title>` not `<Alert message>`. See `.claude/rules/antd-v6-props.md`."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-component-basics/SKILL.md')
    assert "- **`useMemoizedFn` from ahooks** is deprecated in favor of `useEffectEvent` (React 19.2+). See `.claude/rules/use-effect-event.md`. Don't introduce new usages." in text, "expected to find: " + "- **`useMemoizedFn` from ahooks** is deprecated in favor of `useEffectEvent` (React 19.2+). See `.claude/rules/use-effect-event.md`. Don't introduce new usages."[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-form/SKILL.md')
    assert "- **`validateFields()` on every `onChange`** causes render storms. Trigger validation only on dependent-field changes and only when the target field has a value (see FolderCreateModal's `usage_mode` h" in text, "expected to find: " + "- **`validateFields()` on every `onChange`** causes render storms. Trigger validation only on dependent-field changes and only when the target field has a value (see FolderCreateModal's `usage_mode` h"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-form/SKILL.md')
    assert "- **`required` prop is a visual marker**, not a validation rule by itself. Pair with explicit `rules={[{ required: true, message: t('...') }]}` or a validator that rejects empty values." in text, "expected to find: " + "- **`required` prop is a visual marker**, not a validation rule by itself. Pair with explicit `rules={[{ required: true, message: t('...') }]}` or a validator that rejects empty values."[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-form/SKILL.md')
    assert "- **`warningOnly: true` validators don't block submit** — `validateFields()` still resolves. Useful for soft nudges; don't rely on them as required rules." in text, "expected to find: " + "- **`warningOnly: true` validators don't block submit** — `validateFields()` still resolves. Useful for soft nudges; don't rely on them as required rules."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-hooks-extraction/SKILL.md')
    assert '`useFetchKey` (from `backend.ai-ui`) returns `[fetchKey, updateFetchKey, INITIAL_FETCH_KEY]`. Most call sites destructure the first two; pages that need to detect the initial render also pull in the t' in text, "expected to find: " + '`useFetchKey` (from `backend.ai-ui`) returns `[fetchKey, updateFetchKey, INITIAL_FETCH_KEY]`. Most call sites destructure the first two; pages that need to detect the initial render also pull in the t'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-hooks-extraction/SKILL.md')
    assert '- **Parametrize per-call inputs on the returned function**, not on the hook argument. `const { startSession } = useStartSession(); startSession(values)` — not `useStartSession(values)`.' in text, "expected to find: " + '- **Parametrize per-call inputs on the returned function**, not on the hook argument. `const { startSession } = useStartSession(); startSession(values)` — not `useStartSession(values)`.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-hooks-extraction/SKILL.md')
    assert "- **`useEffectEvent` is effect-internal** — calling it outside `useEffect` / `useLayoutEffect` / `useInsertionEffect` has undefined behavior (React docs). Don't pass to JSX `onClick`." in text, "expected to find: " + "- **`useEffectEvent` is effect-internal** — calling it outside `useEffect` / `useLayoutEffect` / `useInsertionEffect` has undefined behavior (React docs). Don't pass to JSX `onClick`."[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-layout/SKILL.md')
    assert '- **`BAIFlex` does not always stretch children by default.** Effective `alignItems` comes from `align` (default: `center`) and can also be overridden by `style.alignItems`. Use `align="stretch"` when ' in text, "expected to find: " + '- **`BAIFlex` does not always stretch children by default.** Effective `alignItems` comes from `align` (default: `center`) and can also be overridden by `style.alignItems`. Use `align="stretch"` when '[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-layout/SKILL.md')
    assert "- **`BAIFlex` `gap` string tokens** resolve via `(token as any)['size' + 'XS'.toUpperCase()]`. If a custom theme doesn't define `sizeXS`/`sizeMD`/etc., gap silently collapses to `'0px'`. Verify the th" in text, "expected to find: " + "- **`BAIFlex` `gap` string tokens** resolve via `(token as any)['size' + 'XS'.toUpperCase()]`. If a custom theme doesn't define `sizeXS`/`sizeMD`/etc., gap silently collapses to `'0px'`. Verify the th"[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-layout/SKILL.md')
    assert '- **`createStyles` from antd-style re-renders on theme change.** Prefer inline `style={{ padding: token.paddingSM }}` when tokens suffice; reserve `createStyles` for pseudo-class / nested antd-class s' in text, "expected to find: " + '- **`createStyles` from antd-style re-renders on theme change.** Prefer inline `style={{ padding: token.paddingSM }}` when tokens suffice; reserve `createStyles` for pseudo-class / nested antd-class s'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-modal-drawer/SKILL.md')
    assert '- **id-state + `useTransition`**: use `open={!!idState || isPending}` so the modal paints during the transition instead of waiting for the heavy query to resolve.' in text, "expected to find: " + '- **id-state + `useTransition`**: use `open={!!idState || isPending}` so the modal paints during the transition instead of waiting for the heavy query to resolve.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-modal-drawer/SKILL.md')
    assert '- **`modal.confirm({ onOk: async () => { ... } })`**: the loader is shown while pending and rethrows on rejection — always wrap in try/catch inside `onOk`.' in text, "expected to find: " + '- **`modal.confirm({ onOk: async () => { ... } })`**: the loader is shown while pending and rethrows on rejection — always wrap in try/catch inside `onOk`.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-modal-drawer/SKILL.md')
    assert '- **URL-driven modal open (FR-1846 #4921)** still needs `BAIUnmountAfterClose` — reloading while open otherwise reopens with stale query/form state.' in text, "expected to find: " + '- **URL-driven modal open (FR-1846 #4921)** still needs `BAIUnmountAfterClose` — reloading while open otherwise reopens with stale query/form state.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-relay-table/SKILL.md')
    assert "- **`exportKey` is required when `dataIndex` doesn't match the GraphQL field name.** Without it, CSV export writes `undefined` for computed columns (e.g. `project` column exporting `project_name`)." in text, "expected to find: " + "- **`exportKey` is required when `dataIndex` doesn't match the GraphQL field name.** Without it, CSV export writes `undefined` for computed columns (e.g. `project` column exporting `project_name`)."[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-relay-table/SKILL.md')
    assert "- **`tablePaginationOption.current` is 1-indexed, `baiPaginationOption.offset` is 0-indexed.** `useBAIPaginationOptionStateOnSearchParam` converts via `(current - 1) * pageSize` — don't swap them." in text, "expected to find: " + "- **`tablePaginationOption.current` is 1-indexed, `baiPaginationOption.offset` is 0-indexed.** `useBAIPaginationOptionStateOnSearchParam` converts via `(current - 1) * pageSize` — don't swap them."[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-relay-table/SKILL.md')
    assert "- **`fixed: true` + `required: true` on the primary column** means users can't hide it or scroll it off-screen. Apply only to the identifying column (email / name / id)." in text, "expected to find: " + "- **`fixed: true` + `required: true` on the primary column** means users can't hide it or scroll it off-screen. Apply only to the identifying column (email / name / id)."[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-suspense-fetching/SKILL.md')
    assert "- **Imperative `fetchQuery` updates the store by node id** — components only re-render when their fragment shape matches. If nothing re-renders after `fetchQuery`, your fragment doesn't match the retu" in text, "expected to find: " + "- **Imperative `fetchQuery` updates the store by node id** — components only re-render when their fragment shape matches. If nothing re-renders after `fetchQuery`, your fragment doesn't match the retu"[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-suspense-fetching/SKILL.md')
    assert "- **`INITIAL_FETCH_KEY` equality** uses the imported constant, not a string literal. `import { INITIAL_FETCH_KEY } from 'backend.ai-ui'` — comparing against `'INITIAL_FETCH_KEY'` always returns false." in text, "expected to find: " + "- **`INITIAL_FETCH_KEY` equality** uses the imported constant, not a string literal. `import { INITIAL_FETCH_KEY } from 'backend.ai-ui'` — comparing against `'INITIAL_FETCH_KEY'` always returns false."[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-suspense-fetching/SKILL.md')
    assert '- **Auto-refreshing cards must NOT sit inside a narrow Suspense** — each tick flashes the fallback (the FR-941 regression). Use `useRefetchableFragment` + `useTransition` and put the Suspense higher.' in text, "expected to find: " + '- **Auto-refreshing cards must NOT sit inside a narrow Suspense** — each tick flashes the fallback (the FR-941 regression). Use `useRefetchableFragment` + `useTransition` and put the Suspense higher.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-url-state/SKILL.md')
    assert "- **Default `history: 'push'` adds a back-button entry per filter change** — user presses Back and lands on the previous filter instead of leaving the page. Always pass `{ history: 'replace' }` unless" in text, "expected to find: " + "- **Default `history: 'push'` adds a back-button entry per filter change** — user presses Back and lands on the previous filter instead of leaving the page. Always pass `{ history: 'replace' }` unless"[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-url-state/SKILL.md')
    assert '- **`setQueryParams(null)` resets ALL keys in the group to defaults.** `setQueryParams({ key: null })` clears only that key. The AdminComputeSessionListPage tab switcher relies on this reset.' in text, "expected to find: " + '- **`setQueryParams(null)` resets ALL keys in the group to defaults.** `setQueryParams({ key: null })` clears only that key. The AdminComputeSessionListPage tab switcher relies on this reset.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/react-url-state/SKILL.md')
    assert "- **`useBAIPaginationOptionStateOnSearchParam` uses its own `useQueryStates`** — it doesn't share context with your page-level `useQueryStates`. Both write cleanly to URL but are independent." in text, "expected to find: " + "- **`useBAIPaginationOptionStateOnSearchParam` uses its own `useQueryStates`** — it doesn't share context with your page-level `useQueryStates`. Both write cleanly to URL but are independent."[:80]

