"""Behavioral checks for dash.js-add-agentsmd-with-information-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dash.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Loggers:** `logger = debug.getLogger(instance)` — use `logger.debug()`, `logger.info()`, `logger.warn()`, `logger.error()`' in text, "expected to find: " + '- **Loggers:** `logger = debug.getLogger(instance)` — use `logger.debug()`, `logger.info()`, `logger.warn()`, `logger.error()`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Error codes are defined as constants in `src/core/errors/Errors.js` and `src/streaming/vo/metrics/PlayList.js`' in text, "expected to find: " + '- Error codes are defined as constants in `src/core/errors/Errors.js` and `src/streaming/vo/metrics/PlayList.js`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'npm run build              # Full build: clean, typecheck, test, lint, then webpack (modern + legacy)' in text, "expected to find: " + 'npm run build              # Full build: clean, typecheck, test, lint, then webpack (modern + legacy)'[:80]

