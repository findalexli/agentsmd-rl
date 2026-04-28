"""Behavioral checks for explorer-docsagents-refresh-agentsmd-and-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/explorer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architect.mdc')
    assert '- `CONTEXT_OPTIMIZATION.md`, `CACHING.md`, `RATE_LIMITING.md` - Performance and rate-limit considerations' in text, "expected to find: " + '- `CONTEXT_OPTIMIZATION.md`, `CACHING.md`, `RATE_LIMITING.md` - Performance and rate-limit considerations'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architect.mdc')
    assert '- `app/settings/` - Settings page screen + per-network API key / decompilation opt-in storage' in text, "expected to find: " + '- `app/settings/` - Settings page screen + per-network API key / decompilation opt-in storage'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/architect.mdc')
    assert '- `docs/FEATURES_SPECIFICATION.md` - Canonical feature catalog (`FEAT-*` IDs) — keep in sync' in text, "expected to find: " + '- `docs/FEATURES_SPECIFICATION.md` - Canonical feature catalog (`FEAT-*` IDs) — keep in sync'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coder.mdc')
    assert '5. If you touch routes/tabs or page metadata, follow `.cursor/skills/aptos-explorer-llm-seo/SKILL.md` (and update `public/llms.txt`, `public/llms-full.txt`, `public/sitemap.xml`, and `app/components/h' in text, "expected to find: " + '5. If you touch routes/tabs or page metadata, follow `.cursor/skills/aptos-explorer-llm-seo/SKILL.md` (and update `public/llms.txt`, `public/llms-full.txt`, `public/sitemap.xml`, and `app/components/h'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coder.mdc')
    assert '4. Check `docs/FEATURES_SPECIFICATION.md` for any `FEAT-*` entry your change touches and keep it in sync' in text, "expected to find: " + '4. Check `docs/FEATURES_SPECIFICATION.md` for any `FEAT-*` entry your change touches and keep it in sync'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coder.mdc')
    assert 'pnpm ci:verify        # Local CI: routes:generate + lint + test + build' in text, "expected to find: " + 'pnpm ci:verify        # Local CI: routes:generate + lint + test + build'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cost-cutter.mdc')
    assert '# Match `.node-version` (currently Node 24)' in text, "expected to find: " + '# Match `.node-version` (currently Node 24)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cost-cutter.mdc')
    assert 'NODE_VERSION = "24"' in text, "expected to find: " + 'NODE_VERSION = "24"'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/modernizer.mdc')
    assert 'The `src/` folder is nearly drained — only `src/components/IndividualPageContent` remains. Finishing this migration retires `src/`:' in text, "expected to find: " + 'The `src/` folder is nearly drained — only `src/components/IndividualPageContent` remains. Finishing this migration retires `src/`:'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/modernizer.mdc')
    assert '- `src/components/IndividualPageContent` — last legacy component blocking removal of `src/`' in text, "expected to find: " + '- `src/components/IndividualPageContent` — last legacy component blocking removal of `src/`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/modernizer.mdc')
    assert '- `src/components/IndividualPageContent` → `app/components/`' in text, "expected to find: " + '- `src/components/IndividualPageContent` → `app/components/`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tester.mdc')
    assert '- **E2E**: Playwright (`e2e/smoke.spec.ts`, `playwright.config.ts`). Run with `pnpm test:e2e` against a `vite preview` build (port 4173). One-time setup: `pnpm test:e2e:install` to install Chromium + ' in text, "expected to find: " + '- **E2E**: Playwright (`e2e/smoke.spec.ts`, `playwright.config.ts`). Run with `pnpm test:e2e` against a `vite preview` build (port 4173). One-time setup: `pnpm test:e2e:install` to install Chromium + '[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tester.mdc')
    assert '- **Unit/Component**: Vitest + React Testing Library (`*.test.ts(x)` next to the implementation, run via `pnpm test`).' in text, "expected to find: " + '- **Unit/Component**: Vitest + React Testing Library (`*.test.ts(x)` next to the implementation, run via `pnpm test`).'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tester.mdc')
    assert 'pnpm test:e2e            # Playwright smoke tests (vite preview on :4173)' in text, "expected to find: " + 'pnpm test:e2e            # Playwright smoke tests (vite preview on :4173)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- End-to-end smoke tests live in `e2e/` and run with **Playwright** against a `vite preview` build (`pnpm test:e2e`). The `e2e/**` glob is excluded from Vitest. CI runs Playwright after `pnpm ci:verif' in text, "expected to find: " + '- End-to-end smoke tests live in `e2e/` and run with **Playwright** against a `vite preview` build (`pnpm test:e2e`). The `e2e/**` glob is excluded from Vitest. CI runs Playwright after `pnpm ci:verif'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Vite exposes variables prefixed with `VITE_` (and `REACT_APP_` for compatibility) to the client bundle; everything else is server-only. Users can also set per-network API keys at runtime via **Setting' in text, "expected to find: " + 'Vite exposes variables prefixed with `VITE_` (and `REACT_APP_` for compatibility) to the client bundle; everything else is server-only. Users can also set per-network API keys at runtime via **Setting'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Unit tests live next to the implementation as `*.test.ts(x)` and run with **Vitest**. The `pretest` script regenerates the route tree first.' in text, "expected to find: " + '- Unit tests live next to the implementation as `*.test.ts(x)` and run with **Vitest**. The `pretest` script regenerates the route tree first.'[:80]

