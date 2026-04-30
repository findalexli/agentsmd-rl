"""Behavioral checks for vercel-fix-vercelcli-skill-discovery-by (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vercel")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vercel-cli/SKILL.md')
    assert 'description: Deploy, manage, and develop projects on Vercel from the command line' in text, "expected to find: " + 'description: Deploy, manage, and develop projects on Vercel from the command line'[:80]

