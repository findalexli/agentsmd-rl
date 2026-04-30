"""Behavioral checks for sync_gateway-agentsmd-describe-git-branches (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sync-gateway")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Git: `main` branch is the current in-development version. Released versions and backports end up in `release/x.y.z` branches. Feature branches are typically just named `CBG-xxxx` after the Jira tick' in text, "expected to find: " + '- Git: `main` branch is the current in-development version. Released versions and backports end up in `release/x.y.z` branches. Feature branches are typically just named `CBG-xxxx` after the Jira tick'[:80]

