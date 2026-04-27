"""Behavioral checks for linkedin-mcp-server-fixskills-add-paginate-and-failure (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/linkedin-mcp-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage-reviews/SKILL.md')
    assert '- If a failure cannot be fixed automatically, skip that fix and report it as **Valid (unfixed)** in the Phase 4 table' in text, "expected to find: " + '- If a failure cannot be fixed automatically, skip that fix and report it as **Valid (unfixed)** in the Phase 4 table'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage-reviews/SKILL.md')
    assert '- `btca ask -r <resource> -q "..."` for library/framework questions (`btca resources` to list available)' in text, "expected to find: " + '- `btca ask -r <resource> -q "..."` for library/framework questions (`btca resources` to list available)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage-reviews/SKILL.md')
    assert 'gh api --paginate repos/{owner}/{repo}/issues/{pr}/comments' in text, "expected to find: " + 'gh api --paginate repos/{owner}/{repo}/issues/{pr}/comments'[:80]

