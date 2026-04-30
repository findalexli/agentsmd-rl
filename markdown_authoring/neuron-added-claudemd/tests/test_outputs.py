"""Behavioral checks for neuron-added-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neuron")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Neuron is a Swift-based machine learning framework built from scratch for iOS, macOS, tvOS, and watchOS. It implements neural networks with custom backpropagation, supporting various architectures inc' in text, "expected to find: " + 'Neuron is a Swift-based machine learning framework built from scratch for iOS, macOS, tvOS, and watchOS. It implements neural networks with custom backpropagation, supporting various architectures inc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Only the first layer in a network requires explicit `inputSize` specification. All subsequent layers automatically calculate their input sizes when compiled by an `Optimizer`.' in text, "expected to find: " + 'Only the first layer in a network requires explicit `inputSize` specification. All subsequent layers automatically calculate their input sizes when compiled by an `Optimizer`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '4. **Multi-branch Graphs**: When tensors have multiple inputs, set graph for each: `output.setGraph(input1); output.setGraph(input2)`' in text, "expected to find: " + '4. **Multi-branch Graphs**: When tensors have multiple inputs, set graph for each: `output.setGraph(input1); output.setGraph(input2)`'[:80]

