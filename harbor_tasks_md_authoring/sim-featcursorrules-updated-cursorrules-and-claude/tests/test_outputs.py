"""Behavioral checks for sim-featcursorrules-updated-cursorrules-and-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sim")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/emcn-components.mdc')
    assert "return <Primitive className={cn('style-classes', className)} {...props} />" in text, "expected to find: " + "return <Primitive className={cn('style-classes', className)} {...props} />"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/emcn-components.mdc')
    assert 'Import from `@/components/emcn`, never from subpaths (except CSS files).' in text, "expected to find: " + 'Import from `@/components/emcn`, never from subpaths (except CSS files).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/emcn-components.mdc')
    assert '**Use direct className when:** Single consistent style, no variations' in text, "expected to find: " + '**Use direct className when:** Single consistent style, no variations'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/global.mdc')
    assert 'Import `createLogger` from `sim/logger`. Use `logger.info`, `logger.warn`, `logger.error` instead of `console.log`.' in text, "expected to find: " + 'Import `createLogger` from `sim/logger`. Use `logger.info`, `logger.warn`, `logger.error` instead of `console.log`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-architecture.mdc')
    assert '- **Location**: `lib/` (app-wide) → `feature/utils/` (feature-scoped) → inline (single-use)' in text, "expected to find: " + '- **Location**: `lib/` (app-wide) → `feature/utils/` (feature-scoped) → inline (single-use)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-architecture.mdc')
    assert '- **Check existing sources** before duplicating (`lib/` has many utilities)' in text, "expected to find: " + '- **Check existing sources** before duplicating (`lib/` has many utilities)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-architecture.mdc')
    assert '├── utils/               # Feature-scoped utilities (2+ consumers)' in text, "expected to find: " + '├── utils/               # Feature-scoped utilities (2+ consumers)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-components.mdc')
    assert '**Extract when:** 50+ lines, used in 2+ files, or has own state/logic' in text, "expected to find: " + '**Extract when:** 50+ lines, used in 2+ files, or has own state/logic'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-components.mdc')
    assert '**Keep inline when:** < 10 lines, single use, purely presentational' in text, "expected to find: " + '**Keep inline when:** < 10 lines, single use, purely presentational'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-components.mdc')
    assert "1. `'use client'` only when using React hooks" in text, "expected to find: " + "1. `'use client'` only when using React hooks"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-hooks.mdc')
    assert '// 4. Operations (useCallback with empty deps when using refs)' in text, "expected to find: " + '// 4. Operations (useCallback with empty deps when using refs)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-hooks.mdc')
    assert '4. Wrap returned functions in useCallback' in text, "expected to find: " + '4. Wrap returned functions in useCallback'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-hooks.mdc')
    assert '3. Refs for stable callback dependencies' in text, "expected to find: " + '3. Refs for stable callback dependencies'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-imports.mdc')
    assert 'Use barrel exports (`index.ts`) when a folder has 3+ exports. Import from barrel, not individual files.' in text, "expected to find: " + 'Use barrel exports (`index.ts`) when a folder has 3+ exports. Import from barrel, not individual files.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-imports.mdc')
    assert "import { Dashboard } from '@/app/workspace/[workspaceId]/logs/components/dashboard/dashboard'" in text, "expected to find: " + "import { Dashboard } from '@/app/workspace/[workspaceId]/logs/components/dashboard/dashboard'"[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-imports.mdc')
    assert "import { Dashboard, Sidebar } from '@/app/workspace/[workspaceId]/logs/components'" in text, "expected to find: " + "import { Dashboard, Sidebar } from '@/app/workspace/[workspaceId]/logs/components'"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-integrations.mdc')
    assert '**SubBlock Types:** `short-input`, `long-input`, `dropdown`, `code`, `switch`, `slider`, `oauth-input`, `channel-selector`, `user-selector`, `file-upload`, etc.' in text, "expected to find: " + '**SubBlock Types:** `short-input`, `long-input`, `dropdown`, `code`, `switch`, `slider`, `oauth-input`, `channel-selector`, `user-selector`, `file-upload`, etc.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-integrations.mdc')
    assert 'export const {service}{Action}Tool: ToolConfig<{Service}Params, {Service}Response> = {' in text, "expected to find: " + 'export const {service}{Action}Tool: ToolConfig<{Service}Params, {Service}Response> = {'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-integrations.mdc')
    assert '<svg {...props} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' in text, "expected to find: " + '<svg {...props} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-queries.mdc')
    assert 'For optimistic mutations syncing with Zustand, use `createOptimisticMutationHandlers` from `@/hooks/queries/utils/optimistic-mutation`.' in text, "expected to find: " + 'For optimistic mutations syncing with Zustand, use `createOptimisticMutationHandlers` from `@/hooks/queries/utils/optimistic-mutation`.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-queries.mdc')
    assert "list: (workspaceId?: string) => [...entityKeys.all, 'list', workspaceId ?? ''] as const," in text, "expected to find: " + "list: (workspaceId?: string) => [...entityKeys.all, 'list', workspaceId ?? ''] as const,"[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-queries.mdc')
    assert 'export function useEntityList(workspaceId?: string, options?: { enabled?: boolean }) {' in text, "expected to find: " + 'export function useEntityList(workspaceId?: string, options?: { enabled?: boolean }) {'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-stores.mdc')
    assert 'const initialState = { items: [] as Item[], activeId: null as string | null }' in text, "expected to find: " + 'const initialState = { items: [] as Item[], activeId: null as string | null }'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-stores.mdc')
    assert 'Stores live in `stores/`. Complex stores split into `store.ts` + `types.ts`.' in text, "expected to find: " + 'Stores live in `stores/`. Complex stores split into `store.ts` + `types.ts`.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-stores.mdc')
    assert '4. `_hasHydrated` pattern for persisted stores needing hydration tracking' in text, "expected to find: " + '4. `_hasHydrated` pattern for persisted stores needing hydration tracking'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-styling.mdc')
    assert '2. **No duplicate dark classes** - Skip `dark:` when value matches light mode' in text, "expected to find: " + '2. **No duplicate dark classes** - Skip `dark:` when value matches light mode'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-styling.mdc')
    assert '4. **Transitions** - `transition-colors` for interactive states' in text, "expected to find: " + '4. **Transitions** - `transition-colors` for interactive states'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-styling.mdc')
    assert 'For dynamic values (widths, heights) synced with stores:' in text, "expected to find: " + 'For dynamic values (widths, heights) synced with stores:'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-testing.mdc')
    assert 'Use Vitest. Test files live next to source: `feature.ts` → `feature.test.ts`' in text, "expected to find: " + 'Use Vitest. Test files live next to source: `feature.ts` → `feature.test.ts`'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-testing.mdc')
    assert "import { createBlock, createWorkflow, createSession } from '@sim/testing'" in text, "expected to find: " + "import { createBlock, createWorkflow, createSession } from '@sim/testing'"[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-testing.mdc')
    assert "import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'" in text, "expected to find: " + "import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'"[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-typescript.mdc')
    assert '3. **Const assertions** - `as const` for constant objects/arrays' in text, "expected to find: " + '3. **Const assertions** - `as const` for constant objects/arrays'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-typescript.mdc')
    assert '5. **Type imports** - `import type { X }` for type-only imports' in text, "expected to find: " + '5. **Type imports** - `import type { X }` for type-only imports'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sim-typescript.mdc')
    assert '4. **Ref types** - Explicit: `useRef<HTMLDivElement>(null)`' in text, "expected to find: " + '4. **Ref types** - Explicit: `useRef<HTMLDivElement>(null)`'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Extract when: 50+ lines, used in 2+ files, or has own state/logic. Keep inline when: < 10 lines, single use, purely presentational.' in text, "expected to find: " + 'Extract when: 50+ lines, used in 2+ files, or has own state/logic. Keep inline when: < 10 lines, single use, purely presentational.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Logging**: Import `createLogger` from `@sim/logger`. Use `logger.info`, `logger.warn`, `logger.error` instead of `console.log`' in text, "expected to find: " + '- **Logging**: Import `createLogger` from `@sim/logger`. Use `logger.info`, `logger.warn`, `logger.error` instead of `console.log`'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Use `devtools` middleware. Use `persist` only when data should survive reload with `partialize` to persist only necessary state.' in text, "expected to find: " + 'Use `devtools` middleware. Use `persist` only when data should survive reload with `partialize` to persist only necessary state.'[:80]

