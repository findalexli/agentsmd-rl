"""Behavioral checks for deepagents-chore-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/deepagents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Prefer inline `# noqa: RULE` over `[tool.ruff.lint.per-file-ignores]` for individual exceptions. `per-file-ignores` silences a rule for the *entire* file — If you add it for one violation, all future ' in text, "expected to find: " + 'Prefer inline `# noqa: RULE` over `[tool.ruff.lint.per-file-ignores]` for individual exceptions. `per-file-ignores` silences a rule for the *entire* file — If you add it for one violation, all future '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Reserve `per-file-ignores` for **categorical policy** that applies to a whole class of files (e.g., `"tests/**" = ["D1", "S101"]` — tests don\'t need docstrings, `assert` is expected). These are not ex' in text, "expected to find: " + 'Reserve `per-file-ignores` for **categorical policy** that applies to a whole class of files (e.g., `"tests/**" = ["D1", "S101"]` — tests don\'t need docstrings, `assert` is expected). These are not ex'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'timeout = 30  # noqa: PLR2004  # default HTTP timeout, not arbitrary' in text, "expected to find: " + 'timeout = 30  # noqa: PLR2004  # default HTTP timeout, not arbitrary'[:80]

