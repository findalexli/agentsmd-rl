"""Behavioral checks for vltpkg-chore-optimize-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vltpkg")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cli-sdk-workspace.mdc')
    assert '- `src/cli-sdk/src/config/definition.ts` — **Central file**: all CLI options, flags, commands defined here (jackspeak)' in text, "expected to find: " + '- `src/cli-sdk/src/config/definition.ts` — **Central file**: all CLI options, flags, commands defined here (jackspeak)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cli-sdk-workspace.mdc')
    assert "const usageDef = { command: 'name', usage: '<args>', description: '...' } as const satisfies CommandUsageDefinition" in text, "expected to find: " + "const usageDef = { command: 'name', usage: '<args>', description: '...' } as const satisfies CommandUsageDefinition"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cli-sdk-workspace.mdc')
    assert 'CLI args → project vlt.json → user vlt.json → defaults. Command-specific: `command.{name}` in vlt.json.' in text, "expected to find: " + 'CLI args → project vlt.json → user vlt.json → defaults. Command-specific: `command.{name}` in vlt.json.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/code-validation-workflow.mdc')
    assert 'Run from the workspace dir (e.g., `cd src/semver`). If `package.json` deps changed, run `pnpm install` from repo root first.' in text, "expected to find: " + 'Run from the workspace dir (e.g., `cd src/semver`). If `package.json` deps changed, run `pnpm install` from repo root first.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/code-validation-workflow.mdc')
    assert '4. **Coverage:** `pnpm test -Rsilent --coverage-report=text-lcov` (single file: append `test/foo.ts`)' in text, "expected to find: " + '4. **Coverage:** `pnpm test -Rsilent --coverage-report=text-lcov` (single file: append `test/foo.ts`)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/code-validation-workflow.mdc')
    assert 'Update only when changes are intentional: `pnpm snap -Rtap --disable-coverage test/foo.ts`' in text, "expected to find: " + 'Update only when changes are intentional: `pnpm snap -Rtap --disable-coverage test/foo.ts`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/config-reload-jackspeak-issues.mdc')
    assert "1. JackSpeak parser retains internal state across instances — `setConfigValues()` can't override cached defaults" in text, "expected to find: " + "1. JackSpeak parser retains internal state across instances — `setConfigValues()` can't override cached defaults"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/config-reload-jackspeak-issues.mdc')
    assert '**For writes**: Create fresh Config instances per write. Use `addConfigToFile()`/`deleteConfigKeys()` directly.' in text, "expected to find: " + '**For writes**: Create fresh Config instances per write. Use `addConfigToFile()`/`deleteConfigKeys()` directly.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/config-reload-jackspeak-issues.mdc')
    assert '`src/server/src/config-data.ts`, `src/cli-sdk/src/config/index.ts`, `src/vlt-json/src/index.ts`' in text, "expected to find: " + '`src/server/src/config-data.ts`, `src/cli-sdk/src/config/index.ts`, `src/vlt-json/src/index.ts`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cursor-rules-location.mdc')
    assert 'Rule files (`.mdc`) go in `.cursor/rules/` only. Kebab-case filenames.' in text, "expected to find: " + 'Rule files (`.mdc`) go in `.cursor/rules/` only. Kebab-case filenames.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cursor-rules-location.mdc')
    assert '.cursor/rules/your-rule-name.mdc' in text, "expected to find: " + '.cursor/rules/your-rule-name.mdc'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cursor-rules-location.mdc')
    assert 'alwaysApply: false' in text, "expected to find: " + 'alwaysApply: false'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/data-structure.mdc')
    assert '**Location**: `location` (default: `./node_modules/.vlt/<DepID>/node_modules/<name>`), `inVltStore()` (memoized), `nodeModules(scurry)`, `setDefaultLocation()`' in text, "expected to find: " + '**Location**: `location` (default: `./node_modules/.vlt/<DepID>/node_modules/<name>`), `inVltStore()` (memoized), `nodeModules(scurry)`, `setDefaultLocation()`'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/data-structure.mdc')
    assert '- `placePackage(fromNode, depType, spec, manifest?, id?, extra?)` — high-level: creates node + edge, splits `extra` into `modifier`/`peerSetHash`' in text, "expected to find: " + '- `placePackage(fromNode, depType, spec, manifest?, id?, extra?)` — high-level: creates node + edge, splits `extra` into `modifier`/`peerSetHash`'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/data-structure.mdc')
    assert '- `LockfileNode` tuple: `[flags, name?, integrity?, resolved?, location?, manifest?, rawManifest?, platform?, bins?, buildState?]`' in text, "expected to find: " + '- `LockfileNode` tuple: `[flags, name?, integrity?, resolved?, location?, manifest?, rawManifest?, platform?, bins?, buildState?]`'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/ideal-append-nodes.mdc')
    assert "Check `activeModifier?.interactiveBreadcrumb.current === modifier.breadcrumb.last` for complete match. If complete and has `spec`, swap it. If `spec.bareSpec === '-'`, skip dep entirely. After placeme" in text, "expected to find: " + "Check `activeModifier?.interactiveBreadcrumb.current === modifier.breadcrumb.last` for complete match. If complete and has `spec`, swap it. If `spec.bareSpec === '-'`, skip dep entirely. After placeme"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/ideal-append-nodes.mdc')
    assert 'type AppendNodeEntry = { node: Node, deps: Dependency[], depth: number, peerContext: PeerContext, updateContext: { putEntries, resolvePeerDeps }, modifierRefs? }' in text, "expected to find: " + 'type AppendNodeEntry = { node: Node, deps: Dependency[], depth: number, peerContext: PeerContext, updateContext: { putEntries, resolvePeerDeps }, modifierRefs? }'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/ideal-append-nodes.mdc')
    assert 'If first satisfying node fails peer check, lazy-load `graph.nodesByName.get(name)` candidates and try each until compatible one found.' in text, "expected to find: " + 'If first satisfying node fails peer check, lazy-load `graph.nodesByName.get(name)` candidates and try each until compatible one found.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/ideal.mdc')
    assert '`projectRoot`, `packageJson`, `scurry`, `monorepo` (shared instances), `packageInfo` (required), `add?`, `remove?`, `actual?` (for early extraction), `modifiers?`' in text, "expected to find: " + '`projectRoot`, `packageJson`, `scurry`, `monorepo` (shared instances), `packageInfo` (required), `add?`, `remove?`, `actual?` (for early extraction), `modifiers?`'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/ideal.mdc')
    assert 'Non-main importers get fresh peer contexts in `appendNodes()` to prevent cross-workspace peer leakage. Fork cache prevents duplicate contexts.' in text, "expected to find: " + 'Non-main importers get fresh peer contexts in `appendNodes()` to prevent cross-workspace peer leakage. Fork cache prevents duplicate contexts.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/ideal.mdc')
    assert 'Loads Virtual from `vlt-lock.json` (`lockfile.load()`), falls back to Actual (`actual.load()`). Delegates to `buildIdealFromStartingGraph()`.' in text, "expected to find: " + 'Loads Virtual from `vlt-lock.json` (`lockfile.load()`), falls back to Actual (`actual.load()`). Delegates to `buildIdealFromStartingGraph()`.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/index.mdc')
    assert '- **Ideal** (desired state): `ideal.build()` from Virtual or Actual → fetches manifests → expands graph. Idempotent; re-running on same lockfile = identical result' in text, "expected to find: " + '- **Ideal** (desired state): `ideal.build()` from Virtual or Actual → fetches manifests → expands graph. Idempotent; re-running on same lockfile = identical result'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/index.mdc')
    assert '- **`Node`** (`node.ts`) — Unique package instance (identity via `@vltpkg/dep-id`). Tracks build state, platform, peerSetHash' in text, "expected to find: " + '- **`Node`** (`node.ts`) — Unique package instance (identity via `@vltpkg/dep-id`). Tracks build state, platform, peerSetHash'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/index.mdc')
    assert '- **Virtual** (lockfile): `lockfile.load()` from `vlt-lock.json`; `lockfile.loadHidden()` from `node_modules/.vlt-lock.json`' in text, "expected to find: " + '- **Virtual** (lockfile): `lockfile.load()` from `vlt-lock.json`; `lockfile.loadHidden()` from `node_modules/.vlt-lock.json`'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/load-actual.mdc')
    assert '`maybeApplyModifierToSpec()`: calls `modifiers.tryDependencies()` before placing, swaps spec if complete breadcrumb match (marks as `overridden`).' in text, "expected to find: " + '`maybeApplyModifierToSpec()`: calls `modifiers.tryDependencies()` before placing, swaps spec if complete breadcrumb match (marks as `overridden`).'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/load-actual.mdc')
    assert '4. Compare stored modifiers (`node_modules/.vlt/vlt.json`) to current; if changed and `skipLoadingNodesOnModifiersChange`, load importers only' in text, "expected to find: " + '4. Compare stored modifiers (`node_modules/.vlt/vlt.json`) to current; if changed and `skipLoadingNodesOnModifiersChange`, load importers only'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/load-actual.mdc')
    assert '- `loadManifests?: boolean` — true: accurate dep types, extraneous/missing detection; false: infer prod edges, no missing/extraneous' in text, "expected to find: " + '- `loadManifests?: boolean` — true: accurate dep types, extraneous/missing detection; false: infer prod edges, no missing/extraneous'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/lockfiles.mdc')
    assert '- `load.ts`: `load()` (from `vlt-lock.json`), `loadHidden()` (from hidden, sets `throwOnMissingManifest`), `loadObject()` (in-memory, merges lockfile options)' in text, "expected to find: " + '- `load.ts`: `load()` (from `vlt-lock.json`), `loadHidden()` (from hidden, sets `throwOnMissingManifest`), `loadObject()` (in-memory, merges lockfile options)'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/lockfiles.mdc')
    assert 'nodes: Record<DepID, LockfileNode>  // tuple: [flags, name?, integrity?, resolved?, location?, manifest?, rawManifest?, platform?, bins?, buildState?]' in text, "expected to find: " + 'nodes: Record<DepID, LockfileNode>  // tuple: [flags, name?, integrity?, resolved?, location?, manifest?, rawManifest?, platform?, bins?, buildState?]'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/lockfiles.mdc')
    assert 'Options stored: `modifiers`, `catalog`, `catalogs`, `scope-registries`, `jsr-registries`, `registry`, `registries`, `git-hosts`, `git-host-archives`' in text, "expected to find: " + 'Options stored: `modifiers`, `catalog`, `catalogs`, `scope-registries`, `jsr-registries`, `registry`, `registries`, `git-hosts`, `git-host-archives`'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/modifiers.mdc')
    assert "type NodeModifierEntry = { type: 'node', query: string, breadcrumb: ModifierBreadcrumb, manifest: NormalizedManifest, refs: Set<{name, from}> }" in text, "expected to find: " + "type NodeModifierEntry = { type: 'node', query: string, breadcrumb: ModifierBreadcrumb, manifest: NormalizedManifest, refs: Set<{name, from}> }"[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/modifiers.mdc')
    assert "type EdgeModifierEntry = { type: 'edge', query: string, breadcrumb: ModifierBreadcrumb, spec: Spec, value: string, refs: Set<{name, from}> }" in text, "expected to find: " + "type EdgeModifierEntry = { type: 'edge', query: string, breadcrumb: ModifierBreadcrumb, spec: Spec, value: string, refs: Set<{name, from}> }"[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/modifiers.mdc')
    assert 'type ModifierActiveEntry = { modifier: ModifierEntry, interactiveBreadcrumb, originalFrom: Node, originalEdge?, modifiedEdge? }' in text, "expected to find: " + 'type ModifierActiveEntry = { modifier: ModifierEntry, interactiveBreadcrumb, originalFrom: Node, originalEdge?, modifiedEdge? }'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/peers.mdc')
    assert '3. **Parent Declared Peer**: parent has alternative candidates → check via `graph.nodesByName.get(peerName)` → fork if alternative satisfies both' in text, "expected to find: " + '3. **Parent Declared Peer**: parent has alternative candidates → check via `graph.nodesByName.get(peerName)` → fork if alternative satisfies both'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/peers.mdc')
    assert 'Optional `peerSetHash?: string`. Set during ideal build on context forking. Preserved in serialization, parsed from DepID extra on lockfile load.' in text, "expected to find: " + 'Optional `peerSetHash?: string`. Set during ideal build on context forking. Preserved in serialization, parsed from DepID extra on lockfile load.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/peers.mdc')
    assert '1. **Context Mismatch**: context has different target → idempotency check first (existing target satisfies all specs?) → compatible or fork' in text, "expected to find: " + '1. **Context Mismatch**: context has different target → idempotency check first (existing target satisfies all specs?) → compatible or fork'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/reify.mdc')
    assert '8. **Hoist**: `internalHoist()` → `node_modules/.vlt/node_modules/<name>` symlinks. Preference: importer deps > registry > highest version > lexicographic DepID' in text, "expected to find: " + '8. **Hoist**: `internalHoist()` → `node_modules/.vlt/node_modules/<name>` symlinks. Preference: importer deps > registry > highest version > lexicographic DepID'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/reify.mdc')
    assert '4. **Extract nodes**: `addNodes()` → fetch/extract into `.vlt` store. Optional deps use `optionalFail()` to prune subgraphs instead of failing' in text, "expected to find: " + '4. **Extract nodes**: `addNodes()` → fetch/extract into `.vlt` store. Optional deps use `optionalFail()` to prune subgraphs instead of failing'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/graph/reify.mdc')
    assert '11. **Cleanup**: gc if optional failures, delete removed nodes, update importer `package.json` if `add/remove` changed deps, confirm rollback' in text, "expected to find: " + '11. **Cleanup**: gc if optional failures, delete removed nodes, update importer `package.json` if `add/remove` changed deps, confirm rollback'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/gui-validation-workflow.mdc')
    assert '3. `pnpm test --reporter=tap` (single file: `pnpm test --reporter=tap test/components/Foo.test.tsx`)' in text, "expected to find: " + '3. `pnpm test --reporter=tap` (single file: `pnpm test --reporter=tap test/components/Foo.test.tsx`)'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/gui-validation-workflow.mdc')
    assert "Uses Vitest: `import { describe, it, expect } from 'vitest'` with `describe()`/`it()`/`expect()`." in text, "expected to find: " + "Uses Vitest: `import { describe, it, expect } from 'vitest'` with `describe()`/`it()`/`expect()`."[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/gui-validation-workflow.mdc')
    assert 'Differs from `@code-validation-workflow.mdc`: uses **Vitest** (not tap), **no code coverage**.' in text, "expected to find: " + 'Differs from `@code-validation-workflow.mdc`: uses **Vitest** (not tap), **no code coverage**.'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/index.mdc')
    assert '**Utilities:** `src/keychain`, `src/security-archive`, `src/semver`, `src/git`, `src/error-cause`, `src/output`, `src/xdg`, `src/url-open`, `src/promise-spawn`, `src/cmd-shim`, `src/rollback-remove`, ' in text, "expected to find: " + '**Utilities:** `src/keychain`, `src/security-archive`, `src/semver`, `src/git`, `src/error-cause`, `src/output`, `src/xdg`, `src/url-open`, `src/promise-spawn`, `src/cmd-shim`, `src/rollback-remove`, '[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/index.mdc')
    assert '**Graph (core install engine):** `src/graph` — See `@graph/index.mdc` and sub-rules: `data-structure`, `ideal`, `ideal-append-nodes`, `load-actual`, `modifiers`, `lockfiles`, `reify`, `peers`' in text, "expected to find: " + '**Graph (core install engine):** `src/graph` — See `@graph/index.mdc` and sub-rules: `data-structure`, `ideal`, `ideal-append-nodes`, `load-actual`, `modifiers`, `lockfiles`, `reify`, `peers`'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/index.mdc')
    assert 'pnpm monorepo. Workspaces in `src/*`, `infra/*`, `www/*`. Workspaces published as `@vltpkg/*`, the built vlt CLI itself is published as `vlt`.' in text, "expected to find: " + 'pnpm monorepo. Workspaces in `src/*`, `infra/*`, `www/*`. Workspaces published as `@vltpkg/*`, the built vlt CLI itself is published as `vlt`.'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/linting-error-handler.mdc')
    assert '1. **Remove** the declaration (call expression without assignment if side-effects needed)' in text, "expected to find: " + '1. **Remove** the declaration (call expression without assignment if side-effects needed)'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/linting-error-handler.mdc')
    assert 'const paths = nodes.filter(n => n.location !== undefined).map(n => n.location!)' in text, "expected to find: " + 'const paths = nodes.filter(n => n.location !== undefined).map(n => n.location!)'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/linting-error-handler.mdc')
    assert 'description: Fixing common linting errors (unused vars, imports, type guards)' in text, "expected to find: " + 'description: Fixing common linting errors (unused vars, imports, type guards)'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/monorepo-structure.mdc')
    assert '.cursor/rules/monorepo-structure.mdc' in text, "expected to find: " + '.cursor/rules/monorepo-structure.mdc'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/query-pseudo-selector-creation.mdc')
    assert 'Use `getSimpleGraph()` from `test/fixtures/graph.ts`. Build `ParserState` with `postcssSelectorParser().astSync(query)`. Assert on `res.partial.nodes`/`res.partial.edges` using snapshots.' in text, "expected to find: " + 'Use `getSimpleGraph()` from `test/fixtures/graph.ts`. Build `ParserState` with `postcssSelectorParser().astSync(query)`. Assert on `res.partial.nodes`/`res.partial.edges` using snapshots.'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/query-pseudo-selector-creation.mdc')
    assert '1. **Study patterns**: `src/query/src/pseudo/` — see `missing.ts` (edge), `private.ts` (node), `overridden.ts` (edge property)' in text, "expected to find: " + '1. **Study patterns**: `src/query/src/pseudo/` — see `missing.ts` (edge), `private.ts` (node), `overridden.ts` (edge property)'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/query-pseudo-selector-creation.mdc')
    assert '3. **Register**: import in `src/query/src/pseudo.ts`, add to `pseudoSelectors` Map' in text, "expected to find: " + '3. **Register**: import in `src/query/src/pseudo.ts`, add to `pseudoSelectors` Map'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/registry-development.mdc')
    assert 'npm-compatible registry on Cloudflare Workers (Hono, D1, R2). Multi-upstream, stale-while-revalidate caching. Security audit endpoints are placeholders today (Socket.dev planned for v1.x).' in text, "expected to find: " + 'npm-compatible registry on Cloudflare Workers (Hono, D1, R2). Multi-upstream, stale-while-revalidate caching. Security audit endpoints are placeholders today (Socket.dev planned for v1.x).'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/registry-development.mdc')
    assert "- **Routing order matters**: upstream routes (`/:upstream/...`) validate + `c.set('upstream', upstream)` before local package routes (`/:pkg...`). Final `/*` is static assets fallback." in text, "expected to find: " + "- **Routing order matters**: upstream routes (`/:upstream/...`) validate + `c.set('upstream', upstream)` before local package routes (`/:pkg...`). Final `/*` is static assets fallback."[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/registry-development.mdc')
    assert '`src/index.ts` (router), `src/routes/packages.ts`, `src/routes/misc.ts`, `src/utils/cache.ts`, `src/utils/upstream.ts`, `src/utils/packages.ts`, `config.ts`' in text, "expected to find: " + '`src/index.ts` (router), `src/routes/packages.ts`, `src/routes/misc.ts`, `src/utils/cache.ts`, `src/utils/upstream.ts`, `src/utils/packages.ts`, `config.ts`'[:80]

