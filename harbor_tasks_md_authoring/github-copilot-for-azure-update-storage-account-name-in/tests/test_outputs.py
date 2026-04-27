"""Behavioral checks for github-copilot-for-azure-update-storage-account-name-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/github-copilot-for-azure")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/analyze-skill-issues/SKILL.md')
    assert 'MCP tools are used exclusively for **blob discovery** — finding which blob paths exist. All calls require `account: "strdashboarddevveobvk"` and `container: "integration-reports"`. Use `az storage blo' in text, "expected to find: " + 'MCP tools are used exclusively for **blob discovery** — finding which blob paths exist. All calls require `account: "strdashboarddevveobvk"` and `container: "integration-reports"`. Use `az storage blo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/analyze-skill-issues/SKILL.md')
    assert '| Blob list is empty | Container access issue or wrong account | Confirm `account: "strdashboarddevveobvk"` and that the user has Azure CLI credentials |' in text, "expected to find: " + '| Blob list is empty | Container access issue or wrong account | Confirm `account: "strdashboarddevveobvk"` and that the user has Azure CLI credentials |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/analyze-skill-issues/SKILL.md')
    assert 'Queries the `strdashboarddevveobvk` Azure Storage account that stores all integration test results and retrieves error details for a given skill.' in text, "expected to find: " + 'Queries the `strdashboarddevveobvk` Azure Storage account that stores all integration test results and retrieves error details for a given skill.'[:80]

