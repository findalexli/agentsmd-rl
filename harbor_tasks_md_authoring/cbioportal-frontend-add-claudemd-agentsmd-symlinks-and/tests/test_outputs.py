"""Behavioral checks for cbioportal-frontend-add-claudemd-agentsmd-symlinks-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cbioportal-frontend")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'When an upstream data source (Genome Nexus, OncoKB, cBioPortal backend) changes and the e2e reference screenshots go stale, CircleCI will fail on screenshot comparison. The fastest way to refresh the ' in text, "expected to find: " + 'When an upstream data source (Genome Nexus, OncoKB, cBioPortal backend) changes and the e2e reference screenshots go stale, CircleCI will fail on screenshot comparison. The fastest way to refresh the '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Only update the screenshots affected by the upstream change. Don't bundle unrelated screenshot updates. One upstream fix, one PR. PR #5514 (CCDS ID fix) is a reference example." in text, "expected to find: " + "Only update the screenshots affected by the upstream change. Don't bundle unrelated screenshot updates. One upstream fix, one PR. PR #5514 (CCDS ID fix) is a reference example."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Don't regenerate screenshots locally unless CircleCI can't produce them — per the note above, host-rendered images won't match the dockerized reference." in text, "expected to find: " + "Don't regenerate screenshots locally unless CircleCI can't produce them — per the note above, host-rendered images won't match the dockerized reference."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '.github/copilot-instructions.md' in text, "expected to find: " + '.github/copilot-instructions.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '.github/copilot-instructions.md' in text, "expected to find: " + '.github/copilot-instructions.md'[:80]

