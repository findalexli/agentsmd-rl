"""Behavioral checks for jstime-update-copilot-instructions-to-reflect (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jstime")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'For conformance tests, see [core/tests/CONFORMANCE_TESTS.md](../core/tests/CONFORMANCE_TESTS.md) for detailed coverage information.' in text, "expected to find: " + 'For conformance tests, see [core/tests/CONFORMANCE_TESTS.md](../core/tests/CONFORMANCE_TESTS.md) for detailed coverage information.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **WHATWG**: console, timers, fetch, URL, events (Event/EventTarget), base64, structured clone, microtask queue' in text, "expected to find: " + '- **WHATWG**: console, timers, fetch, URL, events (Event/EventTarget), base64, structured clone, microtask queue'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- See [core/src/builtins/README.md](../core/src/builtins/README.md) for built-in API structure' in text, "expected to find: " + '- See [core/src/builtins/README.md](../core/src/builtins/README.md) for built-in API structure'[:80]

