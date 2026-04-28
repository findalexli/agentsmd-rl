"""Behavioral checks for vltpkg-chore-add-more-cursor-rules (markdown_authoring task).

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
    text = _read('.cursor/rules/catalogs.mdc')
    assert 'This project itself uses catalogs — see root `vlt.json` for a real-world example with `tap`, `typescript`, `eslint`, `prettier`, etc.' in text, "expected to find: " + 'This project itself uses catalogs — see root `vlt.json` for a real-world example with `tap`, `typescript`, `eslint`, `prettier`, etc.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/catalogs.mdc')
    assert 'Centralized dependency specs in `vlt.json`, referenced via `catalog:` protocol in `package.json`.' in text, "expected to find: " + 'Centralized dependency specs in `vlt.json`, referenced via `catalog:` protocol in `package.json`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/catalogs.mdc')
    assert '2. Looks up the package name in `specOptions.catalog` (default) or `specOptions.catalogs[name]`' in text, "expected to find: " + '2. Looks up the package name in `specOptions.catalog` (default) or `specOptions.catalogs[name]`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dep-id.mdc')
    assert '`/` → `+`, special chars use `_X` escapes: `_c` = `:`, `_t` = `~`, `__` = `_`, `_d` = trailing `.`, control chars = `_XX` hex.' in text, "expected to find: " + '`/` → `+`, special chars use `_X` escapes: `_c` = `:`, `_t` = `~`, `__` = `_`, `_d` = trailing `.`, control chars = `_XX` hex.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dep-id.mdc')
    assert '**Extra** (4th segment): stores modifier query + `peerSetHash` (e.g., `peer.1`). See `joinExtra()`/`splitExtra()`.' in text, "expected to find: " + '**Extra** (4th segment): stores modifier query + `peerSetHash` (e.g., `peer.1`). See `joinExtra()`/`splitExtra()`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dep-id.mdc')
    assert '- **registry**: `~~name@version` (default reg), `~npm~name@version`, `~http%3A...~name@ver`' in text, "expected to find: " + '- **registry**: `~~name@version` (default reg), `~npm~name@version`, `~http%3A...~name@ver`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/docs-website.mdc')
    assert 'Use `<Code code="..." title="Terminal" lang="bash" />` for command examples.' in text, "expected to find: " + 'Use `<Code code="..." title="Terminal" lang="bash" />` for command examples.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/docs-website.mdc')
    assert '- Changing install/build behavior → update relevant command + concept docs' in text, "expected to find: " + '- Changing install/build behavior → update relevant command + concept docs'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/docs-website.mdc')
    assert '- Adding/changing commands → update/create `cli/commands/<cmd>.mdx`' in text, "expected to find: " + '- Adding/changing commands → update/create `cli/commands/<cmd>.mdx`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dss-breadcrumb.mdc')
    assert 'Limited subset for modifiers: `:root`, `:project`, `:workspace`, `#name` (id), `> #name` (child combinator). Pseudo selectors with semver params (`:semver(^1.0.0)`) supported via comparator functions.' in text, "expected to find: " + 'Limited subset for modifiers: `:root`, `:project`, `:workspace`, `#name` (id), `> #name` (child combinator). Pseudo selectors with semver params (`:semver(^1.0.0)`) supported via comparator functions.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dss-breadcrumb.mdc')
    assert "**Core concept**: A breadcrumb tracks position in a DSS query as the graph is traversed node-by-node. Used by `GraphModifier` to determine when a modifier's selector fully matches." in text, "expected to find: " + "**Core concept**: A breadcrumb tracks position in a DSS query as the graph is traversed node-by-node. Used by `GraphModifier` to determine when a modifier's selector fully matches."[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/dss-breadcrumb.mdc')
    assert 'Dependency Selector Syntax — CSS-like query language used by `vlt query`, `vlt build --target`, modifiers, `--scope`, `--allow-scripts`.' in text, "expected to find: " + 'Dependency Selector Syntax — CSS-like query language used by `vlt query`, `vlt build --target`, modifiers, `--scope`, `--allow-scripts`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/install-build-phases.mdc')
    assert 'globs: src/graph/src/install.ts,src/graph/src/reify/*,src/cli-sdk/src/commands/install.ts,src/cli-sdk/src/commands/build.ts' in text, "expected to find: " + 'globs: src/graph/src/install.ts,src/graph/src/reify/*,src/cli-sdk/src/commands/install.ts,src/cli-sdk/src/commands/build.ts'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/install-build-phases.mdc')
    assert "Tracked per node: `'none' | 'needed' | 'built' | 'failed'`. Query with `:built`, `:scripts`, `:scripts:not(:built)`." in text, "expected to find: " + "Tracked per node: `'none' | 'needed' | 'built' | 'failed'`. Query with `:built`, `:scripts`, `:scripts:not(:built)`."[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/install-build-phases.mdc')
    assert '**Default target**: `:scripts:not(:built):not(:malware)` — excludes already-built and malware-flagged packages.' in text, "expected to find: " + '**Default target**: `:scripts:not(:built):not(:malware)` — excludes already-built and malware-flagged packages.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/registries-and-auth.mdc')
    assert "Child deps inherit parent's registry by default. If `foo` comes from registry X, its dep `bar@1.x` also resolves from X — prevents accidental cross-registry resolution." in text, "expected to find: " + "Child deps inherit parent's registry by default. If `foo` comes from registry X, its dep `bar@1.x` also resolves from X — prevents accidental cross-registry resolution."[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/registries-and-auth.mdc')
    assert 'globs: src/registry-client/src/*,src/keychain/src/*,src/cli-sdk/src/commands/login.ts,src/cli-sdk/src/commands/logout.ts,src/cli-sdk/src/commands/token.ts' in text, "expected to find: " + 'globs: src/registry-client/src/*,src/keychain/src/*,src/cli-sdk/src/commands/login.ts,src/cli-sdk/src/commands/logout.ts,src/cli-sdk/src/commands/token.ts'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/registries-and-auth.mdc')
    assert '2. **Named aliases**: `--registries=<name>=<url>` → use as `name:pkg@ver` in dependencies' in text, "expected to find: " + '2. **Named aliases**: `--registries=<name>=<url>` → use as `name:pkg@ver` in dependencies'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security-archive.mdc')
    assert '**Trust**: `:abandoned`, `:confused`, `:unmaintained`, `:unstable`, `:unknown`, `:unpopular`, `:trivial`, `:squat(type)`' in text, "expected to find: " + '**Trust**: `:abandoned`, `:confused`, `:unmaintained`, `:unstable`, `:unknown`, `:unpopular`, `:trivial`, `:squat(type)`'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security-archive.mdc')
    assert '**Malware/threats**: `:malware`, `:malware(critical|high|medium|low)`, `:obfuscated`, `:eval`, `:shell`, `:scripts`' in text, "expected to find: " + '**Malware/threats**: `:malware`, `:malware(critical|high|medium|low)`, `:obfuscated`, `:eval`, `:shell`, `:scripts`'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security-archive.mdc')
    assert '- `src/security-archive/src/index.ts` — `SecurityArchive` class (extends `LRUCache<DepID, PackageReportData>`)' in text, "expected to find: " + '- `src/security-archive/src/index.ts` — `SecurityArchive` class (extends `LRUCache<DepID, PackageReportData>`)'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/smoke-tests.mdc')
    assert 'Each test gets isolated `testdir` with separate `root/project/config/cache/data/state/runtime` dirs. `HOME`/`XDG_*` env vars locked to testdir to prevent config leakage.' in text, "expected to find: " + 'Each test gets isolated `testdir` with separate `root/project/config/cache/data/state/runtime` dirs. `HOME`/`XDG_*` env vars locked to testdir to prevent config leakage.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/smoke-tests.mdc')
    assert 'Tests run against multiple CLI build variants: `Source` (dev), `Bundle` (bundled), `Compile` (compiled). Results are compared across variants for consistency.' in text, "expected to find: " + 'Tests run against multiple CLI build variants: `Source` (dev), `Bundle` (bundled), `Compile` (compiled). Results are compared across variants for consistency.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/smoke-tests.mdc')
    assert '`test/install.ts`, `test/pkg.ts`, `test/version.ts`, `test/cache-unzip.ts`, `test/postinstall.ts`, `test/rollback-remove.ts`' in text, "expected to find: " + '`test/install.ts`, `test/pkg.ts`, `test/version.ts`, `test/cache-unzip.ts`, `test/postinstall.ts`, `test/rollback-remove.ts`'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/spec-parsing.mdc')
    assert 'Parses dependency specifiers into typed `Spec` objects. Used throughout the graph system.' in text, "expected to find: " + 'Parses dependency specifiers into typed `Spec` objects. Used throughout the graph system.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/spec-parsing.mdc')
    assert '- `registry` — `express@^1.0.0`, `npm:react@18`, `jsr:@am/foo@1`, `registry:URL#name@ver`' in text, "expected to find: " + '- `registry` — `express@^1.0.0`, `npm:react@18`, `jsr:@am/foo@1`, `registry:URL#name@ver`'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/spec-parsing.mdc')
    assert '- `subspec` — inner Spec for aliases (`alias@npm:pkg@ver` → subspec is the npm spec)' in text, "expected to find: " + '- `subspec` — inner Spec for aliases (`alias@npm:pkg@ver` → subspec is the npm spec)'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/vlt-json-config.mdc')
    assert 'CLI args → project `vlt.json` → user `vlt.json` (XDG config dir) → defaults. Object values merge; set `null` to remove. Command-specific overrides via `command.{name}` nesting.' in text, "expected to find: " + 'CLI args → project `vlt.json` → user `vlt.json` (XDG config dir) → defaults. Object values merge; set `null` to remove. Command-specific overrides via `command.{name}` nesting.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/vlt-json-config.mdc')
    assert '**Caching**: module-level caches for parsed data, mtimes, paths, lstat results. Must `unload()` to get fresh reads. See `@config-reload-jackspeak-issues.mdc`.' in text, "expected to find: " + '**Caching**: module-level caches for parsed data, mtimes, paths, lstat results. Must `unload()` to get fresh reads. See `@config-reload-jackspeak-issues.mdc`.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/vlt-json-config.mdc')
    assert '**JSON formatting**: preserves indentation/newlines from original file via `polite-json` symbols (`kIndent`, `kNewline`).' in text, "expected to find: " + '**JSON formatting**: preserves indentation/newlines from original file via `polite-json` symbols (`kIndent`, `kNewline`).'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/vlx.mdc')
    assert '- `vlx.resolve(positionals, options, promptFn?)` → `string | undefined` — core resolution logic: find local bin → find local package → install to cache → infer default executable. Returns `undefined` ' in text, "expected to find: " + '- `vlx.resolve(positionals, options, promptFn?)` → `string | undefined` — core resolution logic: find local bin → find local package → install to cache → infer default executable. Returns `undefined` '[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/vlx.mdc')
    assert 'globs: src/cli-sdk/src/commands/exec.ts,src/cli-sdk/src/commands/exec-local.ts,src/cli-sdk/src/commands/exec-cache.ts,src/vlx/src/*.ts,www/docs/src/content/docs/cli/commands/exec*.mdx' in text, "expected to find: " + 'globs: src/cli-sdk/src/commands/exec.ts,src/cli-sdk/src/commands/exec-local.ts,src/cli-sdk/src/commands/exec-cache.ts,src/vlx/src/*.ts,www/docs/src/content/docs/cli/commands/exec*.mdx'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/vlx.mdc')
    assert 'Runs command with local `node_modules/.bin` prepended to PATH. No remote installs. No args → spawns interactive shell.' in text, "expected to find: " + 'Runs command with local `node_modules/.bin` prepended to PATH. No remote installs. No args → spawns interactive shell.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/workspaces.mdc')
    assert '`cd` into a workspace dir → vlt auto-targets that workspace for install/run/etc. For linked folders (`file:` protocol), the folder must already be in the dependency chain for `vlt install`/`vlt uninst' in text, "expected to find: " + '`cd` into a workspace dir → vlt auto-targets that workspace for install/run/etc. For linked folders (`file:` protocol), the folder must already be in the dependency chain for `vlt install`/`vlt uninst'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/workspaces.mdc')
    assert 'globs: src/workspaces/src/index.ts,src/cli-sdk/src/index.ts,src/cli-sdk/src/exec-command.ts,www/docs/src/content/docs/cli/workspaces.mdx' in text, "expected to find: " + 'globs: src/workspaces/src/index.ts,src/cli-sdk/src/index.ts,src/cli-sdk/src/exec-command.ts,www/docs/src/content/docs/cli/workspaces.mdx'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/workspaces.mdc')
    assert 'Checks in order: group name match → direct name/path match → glob pattern match against `ws.keys`. Yields in topological order.' in text, "expected to find: " + 'Checks in order: group name match → direct name/path match → glob pattern match against `ws.keys`. Yields in topological order.'[:80]

