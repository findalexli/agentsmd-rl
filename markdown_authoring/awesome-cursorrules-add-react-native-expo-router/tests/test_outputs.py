"""Behavioral checks for awesome-cursorrules-add-react-native-expo-router (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/react-native-expo-router-typescript-windows-cursorrules-prompt-file/.cursorrules')
    assert '"Follow the recommended folder structure and maintain organized code for scalability and readability.",' in text, "expected to find: " + '"Follow the recommended folder structure and maintain organized code for scalability and readability.",'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/react-native-expo-router-typescript-windows-cursorrules-prompt-file/.cursorrules')
    assert '"If unsure about the current structure or details, use PowerShell to list out necessary information:",' in text, "expected to find: " + '"If unsure about the current structure or details, use PowerShell to list out necessary information:",'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/react-native-expo-router-typescript-windows-cursorrules-prompt-file/.cursorrules')
    assert '"Use PowerShell commands to manage the project, e.g., moving and renaming files:",' in text, "expected to find: " + '"Use PowerShell commands to manage the project, e.g., moving and renaming files:",'[:80]

