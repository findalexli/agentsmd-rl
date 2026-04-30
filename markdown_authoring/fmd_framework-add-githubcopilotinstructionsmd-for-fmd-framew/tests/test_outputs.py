"""Behavioral checks for fmd_framework-add-githubcopilotinstructionsmd-for-fmd-framew (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fmd-framework")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The **Fabric Metadata-Driven Framework (FMD)** is an open-source Microsoft Fabric framework that automates, orchestrates, and standardises metadata-driven data pipelines. It targets a **Lakehouse-firs' in text, "expected to find: " + 'The **Fabric Metadata-Driven Framework (FMD)** is an open-source Microsoft Fabric framework that automates, orchestrates, and standardises metadata-driven data pipelines. It targets a **Lakehouse-firs'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| Workspace Identity vs. Service Principal | Workspace Identity is auto-assigned as Contributor; Service Principals must be manually added. Use Object ID from **Enterprise Applications** in Entra ID, ' in text, "expected to find: " + '| Workspace Identity vs. Service Principal | Workspace Identity is auto-assigned as Contributor; Service Principals must be manually added. Use Object ID from **Enterprise Applications** in Entra ID, '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| `NB_FMD_UTILITY_FUNCTIONS` | Shared helper functions — always referenced via `%run` or `notebookutils.notebook.run`. Contains `execute_with_outputs` (pyodbc + AAD token) and `build_exec_statement`. ' in text, "expected to find: " + '| `NB_FMD_UTILITY_FUNCTIONS` | Shared helper functions — always referenced via `%run` or `notebookutils.notebook.run`. Contains `execute_with_outputs` (pyodbc + AAD token) and `build_exec_statement`. '[:80]

