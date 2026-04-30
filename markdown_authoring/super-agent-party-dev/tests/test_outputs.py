"""Behavioral checks for super-agent-party-dev (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/super-agent-party")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cli-anything/SKILL.md')
    assert 'Prefer the real software backend over reimplementation. Wrap the actual executable or scripting interface in `utils/<software>_backend.py` when possible. Use synthetic reimplementation only when the p' in text, "expected to find: " + 'Prefer the real software backend over reimplementation. Wrap the actual executable or scripting interface in `utils/<software>_backend.py` when possible. Use synthetic reimplementation only when the p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cli-anything/SKILL.md')
    assert 'description: Use when the user wants you to build, refine, test, or validate a CLI-Anything harness for a GUI application or source repository. Adapts the CLI-Anything methodology to you without chang' in text, "expected to find: " + 'description: Use when the user wants you to build, refine, test, or validate a CLI-Anything harness for a GUI application or source repository. Adapts the CLI-Anything methodology to you without chang'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cli-anything/SKILL.md')
    assert 'Read `https://github.com/HKUDS/CLI-Anything/blob/main/cli-anything-plugin/HARNESS.md` before implementation. That file is the full methodology source of truth. If it is not available, follow the conde' in text, "expected to find: " + 'Read `https://github.com/HKUDS/CLI-Anything/blob/main/cli-anything-plugin/HARNESS.md` before implementation. That file is the full methodology source of truth. If it is not available, follow the conde'[:80]

