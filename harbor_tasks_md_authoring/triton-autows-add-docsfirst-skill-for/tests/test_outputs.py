"""Behavioral checks for triton-autows-add-docsfirst-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/triton")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autows-docs/SKILL.md')
    assert '| SMEM/TMEM allocation, multi-buffering | `docs/BufferAllocation.md`, `docs/SmemAllocationDesign.md` |' in text, "expected to find: " + '| SMEM/TMEM allocation, multi-buffering | `docs/BufferAllocation.md`, `docs/SmemAllocationDesign.md` |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autows-docs/SKILL.md')
    assert '- Docs live in `third_party/nvidia/hopper/lib/Transforms/WarpSpecialization/docs/`' in text, "expected to find: " + '- Docs live in `third_party/nvidia/hopper/lib/Transforms/WarpSpecialization/docs/`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autows-docs/SKILL.md')
    assert 'WarpSpecialization/, partition scheduling, warp_specialize ops, WSCodePartition,' in text, "expected to find: " + 'WarpSpecialization/, partition scheduling, warp_specialize ops, WSCodePartition,'[:80]

