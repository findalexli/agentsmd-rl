"""Behavioral checks for cocoindex-chore-revise-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cocoindex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "We prefer end-to-end tests on user-facing APIs, over unit tests on smaller internal functions. With this said, there're cases where unit tests are necessary, e.g. for internal logic with various situa" in text, "expected to find: " + "We prefer end-to-end tests on user-facing APIs, over unit tests on smaller internal functions. With this said, there're cases where unit tests are necessary, e.g. for internal logic with various situa"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'We distinguish between **internal modules** (under packages with `_` prefix, e.g. `_internal.*`) and **external modules** (which users can directly import).' in text, "expected to find: " + 'We distinguish between **internal modules** (under packages with `_` prefix, e.g. `_internal.*`) and **external modules** (which users can directly import).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '* Only prefix symbols that are truly private to the module itself (e.g. `_context_var` for a module-private ContextVar)' in text, "expected to find: " + '* Only prefix symbols that are truly private to the module itself (e.g. `_context_var` for a module-private ContextVar)'[:80]

