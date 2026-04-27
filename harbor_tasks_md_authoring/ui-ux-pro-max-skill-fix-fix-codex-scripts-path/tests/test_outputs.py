"""Behavioral checks for ui-ux-pro-max-skill-fix-fix-codex-scripts-path (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ui-ux-pro-max-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/ui-ux-pro-max/SKILL.md')
    assert 'python3 .codex/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]' in text, "expected to find: " + 'python3 .codex/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/ui-ux-pro-max/SKILL.md')
    assert 'python3 .codex/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --domain product' in text, "expected to find: " + 'python3 .codex/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --domain product'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/ui-ux-pro-max/SKILL.md')
    assert 'python3 .codex/skills/ui-ux-pro-max/scripts/search.py "hero-centric social-proof" --domain landing' in text, "expected to find: " + 'python3 .codex/skills/ui-ux-pro-max/scripts/search.py "hero-centric social-proof" --domain landing'[:80]

