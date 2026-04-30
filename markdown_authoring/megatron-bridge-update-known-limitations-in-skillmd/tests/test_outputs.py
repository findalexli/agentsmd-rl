"""Behavioral checks for megatron-bridge-update-known-limitations-in-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/megatron-bridge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/perf-techniques/memory-tuning/SKILL.md')
    assert 'skills/perf-techniques/memory-tuning/SKILL.md' in text, "expected to find: " + 'skills/perf-techniques/memory-tuning/SKILL.md'[:80]

