"""Behavioral checks for kubb-set-up-copilot-instructions (markdown_authoring task).

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
    text = _read('.github/copilot-instructions.md')
    assert 'Components are React components located in `packages/plugin-*/src/components/` that generate code templates using JSX syntax.' in text, "expected to find: " + 'Components are React components located in `packages/plugin-*/src/components/` that generate code templates using JSX syntax.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Generators are located in `packages/plugin-*/src/generators/`. Prefer React-based generators using `createReactGenerator`.' in text, "expected to find: " + 'Generators are located in `packages/plugin-*/src/generators/`. Prefer React-based generators using `createReactGenerator`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'For more detailed architecture information and examples, see the `AGENTS.md` file in the repository root.' in text, "expected to find: " + 'For more detailed architecture information and examples, see the `AGENTS.md` file in the repository root.'[:80]

