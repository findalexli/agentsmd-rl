"""Behavioral checks for hash-h5877-add-mir-builder-testing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hash")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-hashql/SKILL.md')
    assert 'For testing MIR transformation and analysis passes directly with programmatically constructed MIR bodies.' in text, "expected to find: " + 'For testing MIR transformation and analysis passes directly with programmatically constructed MIR bodies.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-hashql/SKILL.md')
    assert '- [MIR Builder Guide](resources/mir-builder-guide.md) - Programmatic MIR construction for tests' in text, "expected to find: " + '- [MIR Builder Guide](resources/mir-builder-guide.md) - Programmatic MIR construction for tests'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-hashql/SKILL.md')
    assert '- [compiletest Guide](resources/compiletest-guide.md) - Detailed UI test documentation' in text, "expected to find: " + '- [compiletest Guide](resources/compiletest-guide.md) - Detailed UI test documentation'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-hashql/references/mir-builder-guide.md')
    assert 'Ergonomic API for constructing MIR bodies in tests. Use for testing and benchmarking MIR passes without manual structure boilerplate.' in text, "expected to find: " + 'Ergonomic API for constructing MIR bodies in tests. Use for testing and benchmarking MIR passes without manual structure boilerplate.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-hashql/references/mir-builder-guide.md')
    assert 'r#type::{TypeBuilder, TypeFormatter, TypeFormatterOptions, environment::Environment},' in text, "expected to find: " + 'r#type::{TypeBuilder, TypeFormatter, TypeFormatterOptions, environment::Environment},'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-hashql/references/mir-builder-guide.md')
    assert '.assign_place(input_val, |rv| rv.input(InputOp::Load { required: true }, "param"))' in text, "expected to find: " + '.assign_place(input_val, |rv| rv.input(InputOp::Load { required: true }, "param"))'[:80]

