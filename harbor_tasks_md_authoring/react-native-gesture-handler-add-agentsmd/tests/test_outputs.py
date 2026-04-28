"""Behavioral checks for react-native-gesture-handler-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/react-native-gesture-handler")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Android codebase is located in `/packages/react-native-gesture-handler/android` directory. iOS and macos in `/packages/react-native-gesture-handler/apple`. Web can be found in `/packages/react-nativ' in text, "expected to find: " + '- Android codebase is located in `/packages/react-native-gesture-handler/android` directory. iOS and macos in `/packages/react-native-gesture-handler/apple`. Web can be found in `/packages/react-nativ'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- This project contains 3 versions of API. The newest is located in `packages/react-native-gesture-handler/src/v3` directory. Most of the logic is shared, but make sure that your changes do not break ' in text, "expected to find: " + '- This project contains 3 versions of API. The newest is located in `packages/react-native-gesture-handler/src/v3` directory. Most of the logic is shared, but make sure that your changes do not break '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- After any build on macOS/Linux stop the Metro server with `for pid in $(lsof -ti :8081); do kill "$pid"; done` (this no-ops cleanly when nothing is listening on port 8081; `pkill -f "metro"` is not ' in text, "expected to find: " + '- After any build on macOS/Linux stop the Metro server with `for pid in $(lsof -ti :8081); do kill "$pid"; done` (this no-ops cleanly when nothing is listening on port 8081; `pkill -f "metro"` is not '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

