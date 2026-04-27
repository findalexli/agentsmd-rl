"""Behavioral checks for antigravity-awesome-skills-fixagentic-auditor-metadata (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/advanced-evaluation/SKILL.md')
    assert 'date_added: 2026-03-18' in text, "expected to find: " + 'date_added: 2026-03-18'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/advanced-evaluation/SKILL.md')
    assert 'source: community' in text, "expected to find: " + 'source: community'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentic-actions-auditor/SKILL.md')
    assert 'Detects attack vectors where attacker-controlled' in text, "expected to find: " + 'Detects attack vectors where attacker-controlled'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentic-actions-auditor/SKILL.md')
    assert 'Audits GitHub Actions workflows for security' in text, "expected to find: " + 'Audits GitHub Actions workflows for security'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentic-actions-auditor/SKILL.md')
    assert 'vulnerabilities in AI agent integrations' in text, "expected to find: " + 'vulnerabilities in AI agent integrations'[:80]

