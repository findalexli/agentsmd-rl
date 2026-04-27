"""Behavioral checks for marketingskills-fix-clean-up-asoaudit-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marketingskills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aso-audit/SKILL.md')
    assert 'description: "When the user wants to audit or optimize an App Store or Google Play listing. Also use when the user mentions \'ASO audit,\' \'app store optimization,\' \'optimize my app listing,\' \'improve a' in text, "expected to find: " + 'description: "When the user wants to audit or optimize an App Store or Google Play listing. Also use when the user mentions \'ASO audit,\' \'app store optimization,\' \'optimize my app listing,\' \'improve a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aso-audit/SKILL.md')
    assert '- **page-cro**: For optimizing the conversion of web-based landing pages that drive app installs' in text, "expected to find: " + '- **page-cro**: For optimizing the conversion of web-based landing pages that drive app installs'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aso-audit/SKILL.md')
    assert '- **customer-research**: For understanding user needs and language to inform listing copy' in text, "expected to find: " + '- **customer-research**: For understanding user needs and language to inform listing copy'[:80]

