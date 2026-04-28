"""Behavioral checks for sdk-generator-feat-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sdk-generator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The generator does not auto-discover templates. Every output file must have an explicit entry in the `getFiles(): array` method of the corresponding Language class. Forgetting this means the file sile' in text, "expected to find: " + 'The generator does not auto-discover templates. Every output file must have an explicit entry in the `getFiles(): array` method of the corresponding Language class. Forgetting this means the file sile'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Templates are not used directly — they're rendered at generation time. The `examples/` folder is the ground truth for what the generator actually produces. Always regenerate after making template chan" in text, "expected to find: " + "Templates are not used directly — they're rendered at generation time. The `examples/` folder is the ground truth for what the generator actually produces. Always regenerate after making template chan"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Files with `'scope' => 'copy'` are copied verbatim — no variable substitution happens. If your new file needs template variables, use `'scope' => 'default'` (or `service`, `method`, etc.)." in text, "expected to find: " + "Files with `'scope' => 'copy'` are copied verbatim — no variable substitution happens. If your new file needs template variables, use `'scope' => 'default'` (or `service`, `method`, etc.)."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

