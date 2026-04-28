"""Behavioral checks for gradio-fe-unit-testing-skill-wording (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gradio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/frontend-unit-testing/SKILL.md')
    assert '- **Never use `container.querySelector`**. It is unconditionally banned. Use `getByRole`, `getByText`, `getByLabelText`, `getByDisplayValue`, `getByPlaceholderText`, or `getByTestId`. If none of those' in text, "expected to find: " + '- **Never use `container.querySelector`**. It is unconditionally banned. Use `getByRole`, `getByText`, `getByLabelText`, `getByDisplayValue`, `getByPlaceholderText`, or `getByTestId`. If none of those'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/frontend-unit-testing/SKILL.md')
    assert 'If the element lacks a `data-testid`, **add one to the component source**. This is always the right move. `container.querySelector` is never acceptable — adding a `data-testid` is cheap, explicit, and' in text, "expected to find: " + 'If the element lacks a `data-testid`, **add one to the component source**. This is always the right move. `container.querySelector` is never acceptable — adding a `data-testid` is cheap, explicit, and'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/frontend-unit-testing/SKILL.md')
    assert '3. **Test ID queries** (required fallback — when no semantic/text query works):' in text, "expected to find: " + '3. **Test ID queries** (required fallback — when no semantic/text query works):'[:80]

