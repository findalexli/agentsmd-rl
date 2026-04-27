"""Behavioral checks for ai-dev-kit-modernize-pythondev-skill-to-use (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-dev-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/python-dev/SKILL.md')
    assert '6. **Environment**: Use `uv` exclusively for dependencies and execution, Ruff for linting/formatting, Pyright for type checking' in text, "expected to find: " + '6. **Environment**: Use `uv` exclusively for dependencies and execution, Ruff for linting/formatting, Pyright for type checking'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/python-dev/SKILL.md')
    assert '- **Use uv exclusively**: All packaging, environment, and script execution via [uv](https://github.com/astral-sh/uv)' in text, "expected to find: " + '- **Use uv exclusively**: All packaging, environment, and script execution via [uv](https://github.com/astral-sh/uv)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/python-dev/SKILL.md')
    assert '- **pyproject.toml is the source of truth**: Define all dependencies in `pyproject.toml` (not `requirements.txt`)' in text, "expected to find: " + '- **pyproject.toml is the source of truth**: Define all dependencies in `pyproject.toml` (not `requirements.txt`)'[:80]

