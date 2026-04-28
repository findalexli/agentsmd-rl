"""Behavioral checks for actionbook-skillsactionbook-improve-skillmd-with-stricter (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/actionbook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert 'description: Activate when the user needs to interact with any website — browser automation, web scraping, screenshots, form filling, UI testing, monitoring, or building AI agents. Provides verified a' in text, "expected to find: " + 'description: Activate when the user needs to interact with any website — browser automation, web scraping, screenshots, form filling, UI testing, monitoring, or building AI agents. Provides verified a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert '> Before executing ANY `actionbook browser` command on a page, complete Phase 1 (`actionbook search` → `actionbook get`). This includes ALL browser commands: `click`, `fill`, `text`, `eval`, `snapshot' in text, "expected to find: " + '> Before executing ANY `actionbook browser` command on a page, complete Phase 1 (`actionbook search` → `actionbook get`). This includes ALL browser commands: `click`, `fill`, `text`, `eval`, `snapshot'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/actionbook/SKILL.md')
    assert '> **`eval` is last-resort only.** Before using `browser eval` with `querySelector`, you must have already run `snapshot` on this page. Base selectors on snapshot/inspect output, never on memorized DOM' in text, "expected to find: " + '> **`eval` is last-resort only.** Before using `browser eval` with `querySelector`, you must have already run `snapshot` on this page. Base selectors on snapshot/inspect output, never on memorized DOM'[:80]

