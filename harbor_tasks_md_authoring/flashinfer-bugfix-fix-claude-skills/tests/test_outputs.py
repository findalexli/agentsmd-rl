"""Behavioral checks for flashinfer-bugfix-fix-claude-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flashinfer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-cuda-kernel/SKILL.md')
    assert '**All new kernels should have benchmarks.** This helps track performance regressions and allows users to compare against other implementations.' in text, "expected to find: " + '**All new kernels should have benchmarks.** This helps track performance regressions and allows users to compare against other implementations.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-cuda-kernel/SKILL.md')
    assert '→ **For complete benchmarking guide, see [`.claude/skills/benchmark-kernel/SKILL.md`](../benchmark-kernel/SKILL.md)**' in text, "expected to find: " + '→ **For complete benchmarking guide, see [`.claude/skills/benchmark-kernel/SKILL.md`](../benchmark-kernel/SKILL.md)**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-cuda-kernel/SKILL.md')
    assert '- Using the unified benchmarking framework in `benchmarks/flashinfer_benchmark.py` if applicable' in text, "expected to find: " + '- Using the unified benchmarking framework in `benchmarks/flashinfer_benchmark.py` if applicable'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/benchmark-kernel/SKILL.md')
    assert 'description: Guide for benchmarking FlashInfer kernels with CUPTI timing' in text, "expected to find: " + 'description: Guide for benchmarking FlashInfer kernels with CUPTI timing'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/benchmark-kernel/SKILL.md')
    assert 'name: benchmark-kernel' in text, "expected to find: " + 'name: benchmark-kernel'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-cuda-crash/SKILL.md')
    assert 'description: Tutorial for debugging CUDA crashes using API logging' in text, "expected to find: " + 'description: Tutorial for debugging CUDA crashes using API logging'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-cuda-crash/SKILL.md')
    assert 'name: debug-cuda-crash' in text, "expected to find: " + 'name: debug-cuda-crash'[:80]

