"""Behavioral checks for endurain-add-comprehensive-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/endurain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Endurain is a self-hosted fitness tracking application built with Vue.js frontend, Python FastAPI backend, and supports PostgreSQL/MariaDB databases. The primary development approach uses Docker, but ' in text, "expected to find: " + 'Endurain is a self-hosted fitness tracking application built with Vue.js frontend, Python FastAPI backend, and supports PostgreSQL/MariaDB databases. The primary development approach uses Docker, but '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Screenshot validation**: The application should look like a clean, modern fitness tracking login page with blue "Sign in" button and Strava/Garmin Connect compatibility badges' in text, "expected to find: " + '- **Screenshot validation**: The application should look like a clean, modern fitness tracking login page with blue "Sign in" button and Strava/Garmin Connect compatibility badges'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.' in text, "expected to find: " + 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.'[:80]

