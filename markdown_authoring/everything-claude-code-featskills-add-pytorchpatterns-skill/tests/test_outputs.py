"""Behavioral checks for everything-claude-code-featskills-add-pytorchpatterns-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pytorch-patterns/SKILL.md')
    assert '__Remember__: PyTorch code should be device-agnostic, reproducible, and memory-conscious. When in doubt, profile with `torch.profiler` and check GPU memory with `torch.cuda.memory_summary()`.' in text, "expected to find: " + '__Remember__: PyTorch code should be device-agnostic, reproducible, and memory-conscious. When in doubt, profile with `torch.profiler` and check GPU memory with `torch.cuda.memory_summary()`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pytorch-patterns/SKILL.md')
    assert 'description: PyTorch deep learning patterns and best practices for building robust, efficient, and reproducible training pipelines, model architectures, and data loading.' in text, "expected to find: " + 'description: PyTorch deep learning patterns and best practices for building robust, efficient, and reproducible training pipelines, model architectures, and data loading.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pytorch-patterns/SKILL.md')
    assert 'Idiomatic PyTorch patterns and best practices for building robust, efficient, and reproducible deep learning applications.' in text, "expected to find: " + 'Idiomatic PyTorch patterns and best practices for building robust, efficient, and reproducible deep learning applications.'[:80]

