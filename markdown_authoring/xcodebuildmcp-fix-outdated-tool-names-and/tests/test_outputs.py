"""Behavioral checks for xcodebuildmcp-fix-outdated-tool-names-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xcodebuildmcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/xcodebuildmcp-cli/SKILL.md')
    assert 'xcodebuildmcp simulator build-and-run --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"' in text, "expected to find: " + 'xcodebuildmcp simulator build-and-run --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/xcodebuildmcp-cli/SKILL.md')
    assert 'xcodebuildmcp simulator test --scheme MyAppTests --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"' in text, "expected to find: " + 'xcodebuildmcp simulator test --scheme MyAppTests --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/xcodebuildmcp-cli/SKILL.md')
    assert 'xcodebuildmcp simulator build --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"' in text, "expected to find: " + 'xcodebuildmcp simulator build --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"'[:80]

