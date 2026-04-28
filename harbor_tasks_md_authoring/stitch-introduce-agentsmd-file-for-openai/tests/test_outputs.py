"""Behavioral checks for stitch-introduce-agentsmd-file-for-openai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stitch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Swift style enforced by SwiftLint. Key rules: `line_length: 120`, `vertical_whitespace: 2`; several complexity rules are disabled to favor iteration.' in text, "expected to find: " + '- Swift style enforced by SwiftLint. Key rules: `line_length: 120`, `vertical_whitespace: 2`; several complexity rules are disabled to favor iteration.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Update bundle IDs and Development Team for both `Stitch` and `StitchQuickLookExtension` targets; enable CloudKit per README.' in text, "expected to find: " + '- Update bundle IDs and Development Team for both `Stitch` and `StitchQuickLookExtension` targets; enable CloudKit per README.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do not commit secrets. In CI, `ci_scripts/ci_pre_xcodebuild.sh` writes `secrets.json` from environment variables.' in text, "expected to find: " + '- Do not commit secrets. In CI, `ci_scripts/ci_pre_xcodebuild.sh` writes `secrets.json` from environment variables.'[:80]

