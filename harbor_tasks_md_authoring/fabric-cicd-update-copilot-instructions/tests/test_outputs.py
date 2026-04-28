"""Behavioral checks for fabric-cicd-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fabric-cicd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Valid values for `item_type_in_scope` are defined in the `ItemType` enum in `src/fabric_cicd/constants.py`. Always reference that file for the current list — do not hard-code item type strings without' in text, "expected to find: " + 'Valid values for `item_type_in_scope` are defined in the `ItemType` enum in `src/fabric_cicd/constants.py`. Always reference that file for the current list — do not hard-code item type strings without'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'fabric-cicd is a Python library for Microsoft Fabric CI/CD automation. It supports code-first Continuous Integration/Continuous Deployment automations to integrate Source Controlled workspaces into a ' in text, "expected to find: " + 'fabric-cicd is a Python library for Microsoft Fabric CI/CD automation. It supports code-first Continuous Integration/Continuous Deployment automations to integrate Source Controlled workspaces into a '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Testing approach**: Mock all external dependencies, use `requests_mock` for Azure APIs, `tmpdir` for file operations. Focus on testing business logic, error handling, and integration points.' in text, "expected to find: " + '**Testing approach**: Mock all external dependencies, use `requests_mock` for Azure APIs, `tmpdir` for file operations. Focus on testing business logic, error handling, and integration points.'[:80]

