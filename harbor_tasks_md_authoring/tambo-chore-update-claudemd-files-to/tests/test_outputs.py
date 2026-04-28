"""Behavioral checks for tambo-chore-update-claudemd-files-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tambo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and development workflows.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and development workflows.**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For detailed information on architecture, development patterns, and cross-package workflows, see @AGENTS.md.' in text, "expected to find: " + 'For detailed information on architecture, development patterns, and cross-package workflows, see @AGENTS.md.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and command workflows.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and command workflows.**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('create-tambo-app/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and proxy patterns.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and proxy patterns.**'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and content workflows.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and content workflows.**'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('react-sdk/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and development patterns.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and development patterns.**'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('showcase/CLAUDE.md')
    assert '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and component patterns.**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read @AGENTS.md before making any changes or using any tools. It contains detailed architectural guidance and component patterns.**'[:80]

