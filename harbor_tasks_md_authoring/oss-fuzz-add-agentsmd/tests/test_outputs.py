"""Behavioral checks for oss-fuzz-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oss-fuzz")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "* If doing development on infra/ you should use a venv and if it doesn't already exist, install deps from infra/ci/requirements.txt build/functions/requirements.txt with pip." in text, "expected to find: " + "* If doing development on infra/ you should use a venv and if it doesn't already exist, install deps from infra/ci/requirements.txt build/functions/requirements.txt with pip."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* If doing development on infra/ run python infra/presubmit.py to format, lint and run tests.' in text, "expected to find: " + '* If doing development on infra/ run python infra/presubmit.py to format, lint and run tests.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Use python3 infra/helper.py to build projects and run fuzzers.' in text, "expected to find: " + '* Use python3 infra/helper.py to build projects and run fuzzers.'[:80]

