"""Behavioral checks for operaton-docs-add-agentsmd-to-ease (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/operaton")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Public service interfaces: `ProcessEngine`, `RuntimeService`, `TaskService`, `HistoryService`, `RepositoryService`, `IdentityService`, `ManagementService`, `AuthorizationService`, `ExternalTaskServi' in text, "expected to find: " + '- Public service interfaces: `ProcessEngine`, `RuntimeService`, `TaskService`, `HistoryService`, `RepositoryService`, `IdentityService`, `ManagementService`, `AuthorizationService`, `ExternalTaskServi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Operaton** is a native BPMN 2.0 process engine that runs inside the Java Virtual Machine. It's a fork of Camunda 7 BPM platform, providing a complete stack for process automation including:" in text, "expected to find: " + "**Operaton** is a native BPMN 2.0 process engine that runs inside the Java Virtual Machine. It's a fork of Camunda 7 BPM platform, providing a complete stack for process automation including:"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Documentation:** Currently referencing Camunda 7 Manual at https://docs.camunda.org/manual/7.22/ (Operaton docs under construction at https://docs.operaton.org/)' in text, "expected to find: " + '- **Documentation:** Currently referencing Camunda 7 Manual at https://docs.camunda.org/manual/7.22/ (Operaton docs under construction at https://docs.operaton.org/)'[:80]

