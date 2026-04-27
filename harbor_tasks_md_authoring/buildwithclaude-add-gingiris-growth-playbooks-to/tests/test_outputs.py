"""Behavioral checks for buildwithclaude-add-gingiris-growth-playbooks-to (markdown_authoring task).

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
    text = _read('plugins/all-skills/skills/gingiris-growth-playbooks/SKILL.md')
    assert 'description: "Open-source growth playbooks for AI products, B2B SaaS, and developer tools. Covers Product Hunt launch, GitHub star growth, KOL/UGC strategy, ASO, and community building. MIT licensed."' in text, "expected to find: " + 'description: "Open-source growth playbooks for AI products, B2B SaaS, and developer tools. Covers Product Hunt launch, GitHub star growth, KOL/UGC strategy, ASO, and community building. MIT licensed."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/gingiris-growth-playbooks/SKILL.md')
    assert 'Reference the relevant playbook for your project type. All playbooks are MIT licensed and free to use, adapt, and contribute to.' in text, "expected to find: " + 'Reference the relevant playbook for your project type. All playbooks are MIT licensed and free to use, adapt, and contribute to.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/gingiris-growth-playbooks/SKILL.md')
    assert 'Battle-tested, open-source growth playbooks for developers and founders building AI products, B2B SaaS, and developer tools.' in text, "expected to find: " + 'Battle-tested, open-source growth playbooks for developers and founders building AI products, B2B SaaS, and developer tools.'[:80]

