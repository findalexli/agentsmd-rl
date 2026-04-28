"""Behavioral checks for shinkaevolve-update-skillmd-to-wrap-subsection (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shinkaevolve")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shinka-setup/SKILL.md')
    assert '## Template: `evaluate.py` (non-Python `initial.<ext>` path)' in text, "expected to find: " + '## Template: `evaluate.py` (non-Python `initial.<ext>` path)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shinka-setup/SKILL.md')
    assert '## Template: `evaluate.py` (Python `run_shinka_eval` path)' in text, "expected to find: " + '## Template: `evaluate.py` (Python `run_shinka_eval` path)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/shinka-setup/SKILL.md')
    assert '## Template: `initial.<ext>` (Python example)' in text, "expected to find: " + '## Template: `initial.<ext>` (Python example)'[:80]

