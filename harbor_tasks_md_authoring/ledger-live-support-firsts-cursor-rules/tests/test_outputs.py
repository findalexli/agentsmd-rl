"""Behavioral checks for ledger-live-support-firsts-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ledger-live")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/git-workflow.mdc')
    assert '- Scope is optional but recommended (`desktop`, `mobile`, `coin`, `common`, etc.)' in text, "expected to find: " + '- Scope is optional but recommended (`desktop`, `mobile`, `coin`, `common`, etc.)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/git-workflow.mdc')
    assert 'description: Git workflow and commit conventions for Ledger Wallet' in text, "expected to find: " + 'description: Git workflow and commit conventions for Ledger Wallet'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/git-workflow.mdc')
    assert '- Prefer **multiple focused commits** over large mixed ones' in text, "expected to find: " + '- Prefer **multiple focused commits** over large mixed ones'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ldls.mdc')
    assert '@node_modules/@ledgerhq/ldls-ui-react/ai-rules/RULES.md' in text, "expected to find: " + '@node_modules/@ledgerhq/ldls-ui-react/ai-rules/RULES.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ldls.mdc')
    assert 'description: LDLS UI React design system rules' in text, "expected to find: " + 'description: LDLS UI React design system rules'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ldls.mdc')
    assert 'globs: ["**/*.tsx", "**/*.jsx"]' in text, "expected to find: " + 'globs: ["**/*.tsx", "**/*.jsx"]'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-general.mdc')
    assert 'description: General React and React Native engineering rules for Ledger Live' in text, "expected to find: " + 'description: General React and React Native engineering rules for Ledger Live'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-general.mdc')
    assert '_These rules apply to all files, including those inside `src/newArch/`._' in text, "expected to find: " + '_These rules apply to all files, including those inside `src/newArch/`._'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-general.mdc')
    assert '- Use RTK Query (with slices) only when necessary for app-wide state.' in text, "expected to find: " + '- Use RTK Query (with slices) only when necessary for app-wide state.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-new-arch.mdc')
    assert '- Integration tests ensure that screens, components, hooks, and navigation work together as expected within the New Architecture.' in text, "expected to find: " + '- Integration tests ensure that screens, components, hooks, and navigation work together as expected within the New Architecture.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-new-arch.mdc')
    assert '- Keep test files close to their source whenever appropriate (e.g., `utils/` and `hooks/` can contain their own `__tests__/`).' in text, "expected to find: " + '- Keep test files close to their source whenever appropriate (e.g., `utils/` and `hooks/` can contain their own `__tests__/`).'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-new-arch.mdc')
    assert '- Every new feature under `src/newArch/` **must include an integration test** located inside its `__integrations__/` folder.' in text, "expected to find: " + '- Every new feature under `src/newArch/` **must include an integration test** located inside its `__integrations__/` folder.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert '- use MSW for Network API calls (use same pattern as `apps/ledger-live-mobile/__tests__/server.ts` with `handlers`)' in text, "expected to find: " + '- use MSW for Network API calls (use same pattern as `apps/ledger-live-mobile/__tests__/server.ts` with `handlers`)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert '- **Test Data:** Fixtures under `__fixtures__`, use factories/builders, avoid hardcoded/unrealistic values' in text, "expected to find: " + '- **Test Data:** Fixtures under `__fixtures__`, use factories/builders, avoid hardcoded/unrealistic values'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing.mdc')
    assert '- **Command** inside ledger-live-desktop `pnpm test:jest "filename"` or `pnpm test:jest` to run them all' in text, "expected to find: " + '- **Command** inside ledger-live-desktop `pnpm test:jest "filename"` or `pnpm test:jest` to run them all'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typescript.mdc')
    assert '- Prefer **React.FC** only when children typing is needed; otherwise avoid.' in text, "expected to find: " + '- Prefer **React.FC** only when children typing is needed; otherwise avoid.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typescript.mdc')
    assert 'description: React and React Native development patterns for Ledger Wallet' in text, "expected to find: " + 'description: React and React Native development patterns for Ledger Wallet'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typescript.mdc')
    assert '- Memoize when beneficial (`React.memo`, `useMemo`, `useCallback`).' in text, "expected to find: " + '- Memoize when beneficial (`React.memo`, `useMemo`, `useCallback`).'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '.cursorrules' in text, "expected to find: " + '.cursorrules'[:80]

