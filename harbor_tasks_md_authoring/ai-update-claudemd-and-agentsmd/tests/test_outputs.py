"""Behavioral checks for ai-update-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Each core component has bridges in `src/<component>/src/Bridge/` that provide integrations with specific third-party services. Bridges are separate Composer packages with their own dependencies and ca' in text, "expected to find: " + 'Each core component has bridges in `src/<component>/src/Bridge/` that provide integrations with specific third-party services. Bridges are separate Composer packages with their own dependencies and ca'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Format: Use version headers like `UPGRADE FROM 0.X to 0.Y` with sections per component' in text, "expected to find: " + '- Format: Use version headers like `UPGRADE FROM 0.X to 0.Y` with sections per component'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Add entries for new features, and deprecations under the appropriate version heading' in text, "expected to find: " + '- Add entries for new features, and deprecations under the appropriate version heading'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Each core component has bridges in `src/<component>/src/Bridge/` that provide integrations with specific third-party services. Bridges are separate Composer packages with their own dependencies and ca' in text, "expected to find: " + 'Each core component has bridges in `src/<component>/src/Bridge/` that provide integrations with specific third-party services. Bridges are separate Composer packages with their own dependencies and ca'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Format: Use version headers like `UPGRADE FROM 0.X to 0.Y` with sections per component' in text, "expected to find: " + '- Format: Use version headers like `UPGRADE FROM 0.X to 0.Y` with sections per component'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Add entries for new features, and deprecations under the appropriate version heading' in text, "expected to find: " + '- Add entries for new features, and deprecations under the appropriate version heading'[:80]

