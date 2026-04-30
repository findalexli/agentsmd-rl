"""Behavioral checks for tfplan2md-clarify-copilot-branch-handling-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tfplan2md")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When you are creating or choosing a work branch yourself, use the documented `feature/`, `fix/`, `workflow/`, or `website/` naming convention. If GitHub has already placed you on a coding-agent PR b' in text, "expected to find: " + '- When you are creating or choosing a work branch yourself, use the documented `feature/`, `fix/`, `workflow/`, or `website/` naming convention. If GitHub has already placed you on a coding-agent PR b'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Treat `copilot/*` as a GitHub-managed branch name for the current PR, not as a repository workflow-naming violation. The underlying work still follows the documented feature/fix/workflow/website conve' in text, "expected to find: " + 'Treat `copilot/*` as a GitHub-managed branch name for the current PR, not as a repository workflow-naming violation. The underlying work still follows the documented feature/fix/workflow/website conve'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/agents.md')
    assert '**GitHub Copilot PR branch exception:** When GitHub creates a coding-agent pull request, it may place the work on an auto-generated `copilot/*` branch. That branch name is an execution-context detail ' in text, "expected to find: " + '**GitHub Copilot PR branch exception:** When GitHub creates a coding-agent pull request, it may place the work on an auto-generated `copilot/*` branch. That branch name is an execution-context detail '[:80]

