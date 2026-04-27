"""Behavioral checks for bria-skill-fix-api-key-exposure-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bria-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert '### Step 1: Check if the key exists (without printing the key)' in text, "expected to find: " + '### Step 1: Check if the key exists (without printing the key)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert 'if [ -z "$BRIA_API_KEY" ]; then' in text, "expected to find: " + 'if [ -z "$BRIA_API_KEY" ]; then'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert 'echo "BRIA_API_KEY is not set"' in text, "expected to find: " + 'echo "BRIA_API_KEY is not set"'[:80]

