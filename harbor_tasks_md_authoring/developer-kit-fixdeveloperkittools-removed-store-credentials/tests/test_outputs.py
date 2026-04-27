"""Behavioral checks for developer-kit-fixdeveloperkittools-removed-store-credentials (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/developer-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/developer-kit-tools/skills/sonarqube-mcp/SKILL.md')
    assert '7. **Never change issue status autonomously** — Always present issues to the user and get explicit confirmation before calling `change_sonar_issue_status`' in text, "expected to find: " + '7. **Never change issue status autonomously** — Always present issues to the user and get explicit confirmation before calling `change_sonar_issue_status`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/developer-kit-tools/skills/sonarqube-mcp/SKILL.md')
    assert '2. **Always check quality gate before merge** — Run `get_project_quality_gate_status` as part of any PR review workflow' in text, "expected to find: " + '2. **Always check quality gate before merge** — Run `get_project_quality_gate_status` as part of any PR review workflow'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/developer-kit-tools/skills/sonarqube-mcp/SKILL.md')
    assert '6. **Paginate large result sets** — Use `p` and `ps` parameters; handle multi-page responses for complete coverage' in text, "expected to find: " + '6. **Paginate large result sets** — Use `p` and `ps` parameters; handle multi-page responses for complete coverage'[:80]

