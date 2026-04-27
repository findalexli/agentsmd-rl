"""Behavioral checks for ox-fixclaws-clarify-openclaw-ox-install (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('claws/openclaw/sageox-distill/SKILL.md')
    assert '**wait for their response**. Do not pick a default. Do not guess. Do not' in text, "expected to find: " + '**wait for their response**. Do not pick a default. Do not guess. Do not'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('claws/openclaw/sageox-distill/SKILL.md')
    assert "> How do you want to install the `ox` CLI? Pick one — I won't choose for" in text, "expected to find: " + "> How do you want to install the `ox` CLI? Pick one — I won't choose for"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('claws/openclaw/sageox-distill/SKILL.md')
    assert '>    `/usr/local/bin` (Linux) or `/opt/homebrew/bin` or `/usr/local/bin`' in text, "expected to find: " + '>    `/usr/local/bin` (Linux) or `/opt/homebrew/bin` or `/usr/local/bin`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('claws/openclaw/sageox-summary/SKILL.md')
    assert '**wait for their response**. Do not pick a default. Do not guess. Do not' in text, "expected to find: " + '**wait for their response**. Do not pick a default. Do not guess. Do not'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('claws/openclaw/sageox-summary/SKILL.md')
    assert "> How do you want to install the `ox` CLI? Pick one — I won't choose for" in text, "expected to find: " + "> How do you want to install the `ox` CLI? Pick one — I won't choose for"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('claws/openclaw/sageox-summary/SKILL.md')
    assert '>    `/usr/local/bin` (Linux) or `/opt/homebrew/bin` or `/usr/local/bin`' in text, "expected to find: " + '>    `/usr/local/bin` (Linux) or `/opt/homebrew/bin` or `/usr/local/bin`'[:80]

