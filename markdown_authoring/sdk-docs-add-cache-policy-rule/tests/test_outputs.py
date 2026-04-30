"""Behavioral checks for sdk-docs-add-cache-policy-rule (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Video/image generation costs real money ($0.05–$0.50+ per generation) and takes 60–180 seconds' in text, "expected to find: " + '- Video/image generation costs real money ($0.05–$0.50+ per generation) and takes 60–180 seconds'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- The cache is the user's asset — treat it as production data, not disposable debug state" in text, "expected to find: " + "- The cache is the user's asset — treat it as production data, not disposable debug state"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- If you need to regenerate, modify the prompt slightly or use a different cache key' in text, "expected to find: " + '- If you need to regenerate, modify the prompt slightly or use a different cache key'[:80]

