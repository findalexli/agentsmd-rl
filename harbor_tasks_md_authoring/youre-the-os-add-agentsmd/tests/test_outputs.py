"""Behavioral checks for youre-the-os-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/youre-the-os")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '* Do not run any command other than the ones listed in the readme or in this file without asking the user first. Commands that you need to make requested changes to the source code of this repository ' in text, "expected to find: " + '* Do not run any command other than the ones listed in the readme or in this file without asking the user first. Commands that you need to make requested changes to the source code of this repository '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '* You are here to assist human contributors of this repository. Always ask for clarifications if requirements are not clear. You can also give the user advice to help them grow as a programmer, especi' in text, "expected to find: " + '* You are here to assist human contributors of this repository. Always ask for clarifications if requirements are not clear. You can also give the user advice to help them grow as a programmer, especi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '* Use the "Open-closed principle" as a loose guideline. As such, try to avoid solutions that alter existing implementations or interfaces. If such changes appear to be unavoidable, discuss them with t' in text, "expected to find: " + '* Use the "Open-closed principle" as a loose guideline. As such, try to avoid solutions that alter existing implementations or interfaces. If such changes appear to be unavoidable, discuss them with t'[:80]

