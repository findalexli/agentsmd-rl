"""Behavioral checks for kubb-add-agentsmd-documenting-agents-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kubb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Kubb uses a plugin-based architecture where plugins generate code from OpenAPI specifications. The system is inspired by Rollup, Unplugin, and Snowpack.' in text, "expected to find: " + 'Kubb uses a plugin-based architecture where plugins generate code from OpenAPI specifications. The system is inspired by Rollup, Unplugin, and Snowpack.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When fixing bugs: update relevant docs if the fix changes behavior, add notes if it affects user workflow, update examples if they were incorrect' in text, "expected to find: " + '- When fixing bugs: update relevant docs if the fix changes behavior, add notes if it affects user workflow, update examples if they were incorrect'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Components are React components (using `@kubb/react-fabric`) that generate code templates. They use JSX syntax to declaratively create files.' in text, "expected to find: " + 'Components are React components (using `@kubb/react-fabric`) that generate code templates. They use JSX syntax to declaratively create files.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'This document provides essential guidelines for AI coding assistants (Cursor, GitHub Copilot) working on Kubb documentation. Repository docs are located in the `docs/` folder and use Markdown (MD or M' in text, "expected to find: " + 'This document provides essential guidelines for AI coding assistants (Cursor, GitHub Copilot) working on Kubb documentation. Repository docs are located in the `docs/` folder and use Markdown (MD or M'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'See root `AGENTS.md` for general guidance on when to update documentation. This section covers documentation-specific details.' in text, "expected to find: " + 'See root `AGENTS.md` for general guidance on when to update documentation. This section covers documentation-specific details.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'See root `AGENTS.md` for general guidance on documenting bug fixes. Focus on documentation-specific details here.' in text, "expected to find: " + 'See root `AGENTS.md` for general guidance on documenting bug fixes. Focus on documentation-specific details here.'[:80]

