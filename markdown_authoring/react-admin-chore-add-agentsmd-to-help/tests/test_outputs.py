"""Behavioral checks for react-admin-chore-add-agentsmd-to-help (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/react-admin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert 'Communication between components can be challenging, especially in large React applications, where passing props down several levels can become cumbersome. React-admin addresses this issue using a pul' in text, "expected to find: " + 'Communication between components can be challenging, especially in large React applications, where passing props down several levels can become cumbersome. React-admin addresses this issue using a pul'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert "React-admin is a comprehensive frontend framework for building B2B and admin applications on top of REST/GraphQL APIs, using TypeScript, React, and Material UI. It's an open-source project maintained " in text, "expected to find: " + "React-admin is a comprehensive frontend framework for building B2B and admin applications on top of REST/GraphQL APIs, using TypeScript, React, and Material UI. It's an open-source project maintained "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('Agents.md')
    assert "- **Assertions**: Use testing-library to render and assert on elements. Don't test implementation details or HTML attributes, use assertions based on user interactions and visible output." in text, "expected to find: " + "- **Assertions**: Use testing-library to render and assert on elements. Don't test implementation details or HTML attributes, use assertions based on user interactions and visible output."[:80]

