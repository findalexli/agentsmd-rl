"""Behavioral checks for cloudbase-mcp-fix-skill-add (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cloudbase-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/cloud-functions/SKILL.md')
    assert '- If the product requirement says "create when missing", implement that as an explicit collection-management step before the first write instead of assuming the runtime write call will provision it.' in text, "expected to find: " + '- If the product requirement says "create when missing", implement that as an explicit collection-management step before the first write instead of assuming the runtime write call will provision it.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/cloud-functions/SKILL.md')
    assert '- Assuming `db.collection("name").add(...)` will create a missing document-database collection automatically. Collection creation is a separate management step.' in text, "expected to find: " + '- Assuming `db.collection("name").add(...)` will create a missing document-database collection automatically. Collection creation is a separate management step.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/cloud-functions/SKILL.md')
    assert '- If a function will write to CloudBase document database, create the target collection first through console or management tooling.' in text, "expected to find: " + '- If a function will write to CloudBase document database, create the target collection first through console or management tooling.'[:80]

