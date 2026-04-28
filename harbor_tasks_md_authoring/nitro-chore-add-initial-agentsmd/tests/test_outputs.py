"""Behavioral checks for nitro-chore-add-initial-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nitro")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Main tests are defined in `test/tests.ts` and setup per each deployment provider in `test/presets` and run against `test/fixture` nitro app. Add new regression tests to `test/fixture`.' in text, "expected to find: " + 'Main tests are defined in `test/tests.ts` and setup per each deployment provider in `test/presets` and run against `test/fixture` nitro app. Add new regression tests to `test/fixture`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Nitro is a framework-agnostic and deployment-agnostic server framework powered by [H3](https://github.com/h3js/h3), [UnJS](https://github.com/unjs), and Vite | Rolldown | Rollup.' in text, "expected to find: " + 'Nitro is a framework-agnostic and deployment-agnostic server framework powered by [H3](https://github.com/h3js/h3), [UnJS](https://github.com/unjs), and Vite | Rolldown | Rollup.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Bug fixes MUST include a failing test first** — add regression tests to `test/fixture/` and make sure test script fails before attempting the fix and resolves after.' in text, "expected to find: " + '- **Bug fixes MUST include a failing test first** — add regression tests to `test/fixture/` and make sure test script fails before attempting the fix and resolves after.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

