"""Behavioral checks for neko-add-agentsmd-for-running-the (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neko")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'Replace `/path/to/your/android/sdk` with the actual path to your Android SDK installation. For example, in the dev environment, the path is `/home/jules/Android/sdk`.' in text, "expected to find: " + 'Replace `/path/to/your/android/sdk` with the actual path to your Android SDK installation. For example, in the dev environment, the path is `/home/jules/Android/sdk`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'This will download all the required dependencies and build the app. The final APK will be located at `app/build/outputs/apk/standard/debug/app-standard-debug.apk`.' in text, "expected to find: " + 'This will download all the required dependencies and build the app. The final APK will be located at `app/build/outputs/apk/standard/debug/app-standard-debug.apk`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'Open a terminal in the root of the project and run the following command to build the debug APK:' in text, "expected to find: " + 'Open a terminal in the root of the project and run the following command to build the debug APK:'[:80]

