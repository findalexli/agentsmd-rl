"""Behavioral checks for handsontable-dev1480-reorganize-agentsmd-shrink-root (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/handsontable")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Behavioral guidelines to reduce common LLM coding mistakes. These complement - not replace - the [Mandatory checklist for every change](#mandatory-checklist-for-every-change) and [Architecture constra' in text, "expected to find: " + 'Behavioral guidelines to reduce common LLM coding mistakes. These complement - not replace - the [Mandatory checklist for every change](#mandatory-checklist-for-every-change) and [Architecture constra'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Use red-green TDD - tests come first, always.** Write the failing test(s) before touching any production code. Confirm they fail, implement the fix/feature, then confirm they pass. **Never write ' in text, "expected to find: " + '1. **Use red-green TDD - tests come first, always.** Write the failing test(s) before touching any production code. Confirm they fail, implement the fix/feature, then confirm they pass. **Never write '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `[skip changelog]` in the **PR body** for all other changes - docs (`docs/`), config, CI, scripts, AGENTS.md. "Source code" here means library packages, not the docs site or tooling. This line m' in text, "expected to find: " + '- Use `[skip changelog]` in the **PR body** for all other changes - docs (`docs/`), config, CI, scripts, AGENTS.md. "Source code" here means library packages, not the docs site or tooling. This line m'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'docs/AGENTS.md' in text, "expected to find: " + 'docs/AGENTS.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- **Control flow**: Use `@for`, `@if`, `@switch` (Angular 17+ built-in control flow). Do **not** use `*ngFor`, `*ngIf`, or `*ngSwitch` with structural directives — they require importing `NgFor`, `NgI' in text, "expected to find: " + '- **Control flow**: Use `@for`, `@if`, `@switch` (Angular 17+ built-in control flow). Do **not** use `*ngFor`, `*ngIf`, or `*ngSwitch` with structural directives — they require importing `NgFor`, `NgI'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- **CSS**: Put styles in the `--css` slot of the example directive (the example-runner injects them as a global `<style>` tag). Do **not** reference them in `styleUrls`. If the CSS must live in the co' in text, "expected to find: " + '- **CSS**: Put styles in the `--css` slot of the example directive (the example-runner injects them as a global `<style>` tag). Do **not** reference them in `styleUrls`. If the CSS must live in the co'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'All Angular docs examples use `standalone: true` bootstrapped via `bootstrapApplication`. The Angular JIT compiler runs in the browser and **cannot resolve file-based resources at runtime**. Violating' in text, "expected to find: " + 'All Angular docs examples use `standalone: true` bootstrapped via `bootstrapApplication`. The Angular JIT compiler runs in the browser and **cannot resolve file-based resources at runtime**. Violating'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/CLAUDE.md')
    assert 'docs/CLAUDE.md' in text, "expected to find: " + 'docs/CLAUDE.md'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/CLAUDE.md')
    assert 'docs/CLAUDE.md' in text, "expected to find: " + 'docs/CLAUDE.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/AGENTS.md')
    assert 'For server-backed grids (`dataProvider` with `fetchRows` and CRUD callbacks), enable **`notification`** if you want built-in error toasts on failed fetches or mutations. **`dialog: true` alone does no' in text, "expected to find: " + 'For server-backed grids (`dataProvider` with `fetchRows` and CRUD callbacks), enable **`notification`** if you want built-in error toasts on failed fetches or mutations. **`dialog: true` alone does no'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/AGENTS.md')
    assert '- No barrel imports from `plugins/index`, `editors/index`, `renderers/index`, `validators/index`, `cellTypes/index`, `i18n/index` - import from specific submodule paths. Only exception: `src/registry.' in text, "expected to find: " + '- No barrel imports from `plugins/index`, `editors/index`, `renderers/index`, `validators/index`, `cellTypes/index`, `i18n/index` - import from specific submodule paths. Only exception: `src/registry.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/AGENTS.md')
    assert 'Two build variants: `handsontable.js` (base, external deps) and `handsontable.full.js` (includes HyperFormula). The E2E runner loads `dist/handsontable.js` - rebuild after changing `src/`.' in text, "expected to find: " + 'Two build variants: `handsontable.js` (base, external deps) and `handsontable.full.js` (includes HyperFormula). The E2E runner loads `dist/handsontable.js` - rebuild after changing `src/`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/CLAUDE.md')
    assert 'handsontable/CLAUDE.md' in text, "expected to find: " + 'handsontable/CLAUDE.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/CLAUDE.md')
    assert 'handsontable/CLAUDE.md' in text, "expected to find: " + 'handsontable/CLAUDE.md'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/src/3rdparty/walkontable/AGENTS.md')
    assert 'Self-contained rendering engine for viewport calculation, DOM rendering, scroll synchronization, and the overlay system.' in text, "expected to find: " + 'Self-contained rendering engine for viewport calculation, DOM rendering, scroll synchronization, and the overlay system.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/src/3rdparty/walkontable/AGENTS.md')
    assert '- **Overlay system** (6 types): Frozen rows/columns and scroll sync. Fragile - proceed with caution.' in text, "expected to find: " + '- **Overlay system** (6 types): Frozen rows/columns and scroll sync. Fragile - proceed with caution.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/src/3rdparty/walkontable/AGENTS.md')
    assert '- Plugins must NEVER access Walkontable internals directly - always go through TableView' in text, "expected to find: " + '- Plugins must NEVER access Walkontable internals directly - always go through TableView'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/src/3rdparty/walkontable/CLAUDE.md')
    assert 'handsontable/src/3rdparty/walkontable/CLAUDE.md' in text, "expected to find: " + 'handsontable/src/3rdparty/walkontable/CLAUDE.md'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('handsontable/src/3rdparty/walkontable/CLAUDE.md')
    assert 'handsontable/src/3rdparty/walkontable/CLAUDE.md' in text, "expected to find: " + 'handsontable/src/3rdparty/walkontable/CLAUDE.md'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('visual-tests/AGENTS.md')
    assert '- Custom `tablePage` fixture from `src/test-runner.ts` (auto-navigates to demo, disables animations, waits for table)' in text, "expected to find: " + '- Custom `tablePage` fixture from `src/test-runner.ts` (auto-navigates to demo, disables animations, waits for table)'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('visual-tests/AGENTS.md')
    assert 'Playwright-based visual regression testing with Argos CI for screenshot comparison.' in text, "expected to find: " + 'Playwright-based visual regression testing with Argos CI for screenshot comparison.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('visual-tests/AGENTS.md')
    assert '- Organization: `tests/js-only/`, `tests/multi-frameworks/`, `tests/cross-browser/`' in text, "expected to find: " + '- Organization: `tests/js-only/`, `tests/multi-frameworks/`, `tests/cross-browser/`'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('visual-tests/CLAUDE.md')
    assert 'visual-tests/CLAUDE.md' in text, "expected to find: " + 'visual-tests/CLAUDE.md'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('visual-tests/CLAUDE.md')
    assert 'visual-tests/CLAUDE.md' in text, "expected to find: " + 'visual-tests/CLAUDE.md'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/angular-wrapper/AGENTS.md')
    assert '| Using `standalone: false` or `AppModule` | All Angular docs examples use `standalone: true` with `imports: [HotTableModule]` and `app.config.ts`. |' in text, "expected to find: " + '| Using `standalone: false` or `AppModule` | All Angular docs examples use `standalone: true` with `imports: [HotTableModule]` and `app.config.ts`. |'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/angular-wrapper/AGENTS.md')
    assert '| Adding `licenseKey` to individual `<hot-table>` | Set it globally via `HOT_GLOBAL_CONFIG` in `app.config.ts`. Never put it on each component. |' in text, "expected to find: " + '| Adding `licenseKey` to individual `<hot-table>` | Set it globally via `HOT_GLOBAL_CONFIG` in `app.config.ts`. Never put it on each component. |'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/angular-wrapper/AGENTS.md')
    assert '| Using `*ngIf` / `*ngFor` in templates | Use Angular 17+ built-in control flow: `@if (cond) { }` and `@for (x of list; track x.id) { }`. |' in text, "expected to find: " + '| Using `*ngIf` / `*ngFor` in templates | Use Angular 17+ built-in control flow: `@if (cond) { }` and `@for (x of list; track x.id) { }`. |'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/angular-wrapper/CLAUDE.md')
    assert 'wrappers/angular-wrapper/CLAUDE.md' in text, "expected to find: " + 'wrappers/angular-wrapper/CLAUDE.md'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/angular-wrapper/CLAUDE.md')
    assert 'wrappers/angular-wrapper/CLAUDE.md' in text, "expected to find: " + 'wrappers/angular-wrapper/CLAUDE.md'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/react-wrapper/AGENTS.md')
    assert '- **No business logic** in wrappers - data transformation, validation, cell manipulation belongs in `handsontable/src/`' in text, "expected to find: " + '- **No business logic** in wrappers - data transformation, validation, cell manipulation belongs in `handsontable/src/`'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/react-wrapper/AGENTS.md')
    assert '| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |' in text, "expected to find: " + '| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/react-wrapper/AGENTS.md')
    assert '- **Preserve selection** during updateSettings: use `selection.exportSelection()` / `selection.importSelection()`' in text, "expected to find: " + '- **Preserve selection** during updateSettings: use `selection.exportSelection()` / `selection.importSelection()`'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/react-wrapper/CLAUDE.md')
    assert 'wrappers/react-wrapper/CLAUDE.md' in text, "expected to find: " + 'wrappers/react-wrapper/CLAUDE.md'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/react-wrapper/CLAUDE.md')
    assert 'wrappers/react-wrapper/CLAUDE.md' in text, "expected to find: " + 'wrappers/react-wrapper/CLAUDE.md'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/vue3/AGENTS.md')
    assert '| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |' in text, "expected to find: " + '| `arr.push(...largeArray)` with large arrays | Causes stack overflow with 10k+ elements. Use `forEach` loop instead. |'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/vue3/AGENTS.md')
    assert '- **Build core first**: `npm run build --prefix handsontable` - wrappers consume `handsontable/tmp/` not `dist/`' in text, "expected to find: " + '- **Build core first**: `npm run build --prefix handsontable` - wrappers consume `handsontable/tmp/` not `dist/`'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/vue3/AGENTS.md')
    assert '- Deep watchers (`watch` with `deep: true`) detect prop changes -> `updateSettings()`' in text, "expected to find: " + '- Deep watchers (`watch` with `deep: true`) detect prop changes -> `updateSettings()`'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/vue3/CLAUDE.md')
    assert 'wrappers/vue3/CLAUDE.md' in text, "expected to find: " + 'wrappers/vue3/CLAUDE.md'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('wrappers/vue3/CLAUDE.md')
    assert 'wrappers/vue3/CLAUDE.md' in text, "expected to find: " + 'wrappers/vue3/CLAUDE.md'[:80]

