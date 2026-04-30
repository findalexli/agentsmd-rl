"""Behavioral checks for mlflow-clarify-workflow-approval-requirement-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mlflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/copilot/SKILL.md')
    assert 'Copilot commits require approval to trigger workflows for security reasons, while maintainer commits do not. Once the PR is finalized, run the approve script:' in text, "expected to find: " + 'Copilot commits require approval to trigger workflows for security reasons, while maintainer commits do not. Once the PR is finalized, run the approve script:'[:80]

