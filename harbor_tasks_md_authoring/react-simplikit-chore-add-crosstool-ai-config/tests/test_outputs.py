"""Behavioral checks for react-simplikit-chore-add-crosstool-ai-config (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/react-simplikit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- Function declarations use `function` keyword, not arrow: `function toggle(state: boolean) { return !state; }`' in text, "expected to find: " + '- Function declarations use `function` keyword, not arrow: `function toggle(state: boolean) { return !state; }`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- No implicit boolean coercion: `if (value)` → `if (value != null)` (enforced by `strict-boolean-expressions`)' in text, "expected to find: " + '- No implicit boolean coercion: `if (value)` → `if (value != null)` (enforced by `strict-boolean-expressions`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- Nullish checks: `== null` for both null and undefined, `!== undefined` only when distinction matters' in text, "expected to find: " + '- Nullish checks: `== null` for both null and undefined, `!== undefined` only when distinction matters'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- No implicit boolean coercion: `if (value)` → `if (value != null)` (enforced by `strict-boolean-expressions`)' in text, "expected to find: " + '- No implicit boolean coercion: `if (value)` → `if (value != null)` (enforced by `strict-boolean-expressions`)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Nullish checks: `== null` for both null and undefined, `!== undefined` only when distinction matters' in text, "expected to find: " + '- Nullish checks: `== null` for both null and undefined, `!== undefined` only when distinction matters'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Architecture: `components → hooks → utils → _internal` (unidirectional, no circular imports)' in text, "expected to find: " + '- Architecture: `components → hooks → utils → _internal` (unidirectional, no circular imports)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **No implicit boolean coercion** — `if (value)` → `if (value != null)` (enforced by `strict-boolean-expressions`)' in text, "expected to find: " + '- **No implicit boolean coercion** — `if (value)` → `if (value != null)` (enforced by `strict-boolean-expressions`)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Import extensions** — Use `.ts`/`.tsx` extensions in source imports (tsup converts to `.js` for ESM output)' in text, "expected to find: " + '- **Import extensions** — Use `.ts`/`.tsx` extensions in source imports (tsup converts to `.js` for ESM output)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Named functions in useEffect** — `useEffect(function handleResize() { ... }, [])` not arrow functions' in text, "expected to find: " + '- **Named functions in useEffect** — `useEffect(function handleResize() { ... }, [])` not arrow functions'[:80]

