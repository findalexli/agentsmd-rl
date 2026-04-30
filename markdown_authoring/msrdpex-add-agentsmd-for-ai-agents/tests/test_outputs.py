"""Behavioral checks for msrdpex-add-agentsmd-for-ai-agents (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/msrdpex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If you can’t run a full build (missing toolchain), keep the changes minimal and explain what should be validated by a human (arch matrix, MSI packaging, etc.).' in text, "expected to find: " + 'If you can’t run a full build (missing toolchain), keep the changes minimal and explain what should be validated by a human (arch matrix, MSI packaging, etc.).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The workflow also rewrites `installer/Variables.wxi` to set `ProductVersion` (MSI short version) during packaging. Avoid manual edits unless asked.' in text, "expected to find: " + 'The workflow also rewrites `installer/Variables.wxi` to set `ProductVersion` (MSI short version) during packaging. Avoid manual edits unless asked.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If you’re producing a NuGet package locally, ensure those native binaries are present (CI populates them by building native per-arch first).' in text, "expected to find: " + '- If you’re producing a NuGet package locally, ensure those native binaries are present (CI populates them by building native per-arch first).'[:80]

