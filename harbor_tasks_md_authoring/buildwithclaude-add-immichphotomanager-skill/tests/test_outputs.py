"""Behavioral checks for buildwithclaude-add-immichphotomanager-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/immich-photo-manager/SKILL.md')
    assert 'When your Immich library has grown past the point of manual management, this plugin gives Claude direct access to your instance through 21 MCP tools and 11 specialized skills. Search with natural lang' in text, "expected to find: " + 'When your Immich library has grown past the point of manual management, this plugin gives Claude direct access to your instance through 21 MCP tools and 11 specialized skills. Search with natural lang'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/immich-photo-manager/SKILL.md')
    assert 'description: "Manage your self-hosted Immich photo library through conversation — natural language search, geographic album curation, duplicate detection, library health audits, and interactive HTML g' in text, "expected to find: " + 'description: "Manage your self-hosted Immich photo library through conversation — natural language search, geographic album curation, duplicate detection, library health audits, and interactive HTML g'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/immich-photo-manager/SKILL.md')
    assert '- **Duplicate detection** — Cross-source analysis with perceptual hashing (catches re-encoded copies from Apple Photos, Google Takeout)' in text, "expected to find: " + '- **Duplicate detection** — Cross-source analysis with perceptual hashing (catches re-encoded copies from Apple Photos, Google Takeout)'[:80]

