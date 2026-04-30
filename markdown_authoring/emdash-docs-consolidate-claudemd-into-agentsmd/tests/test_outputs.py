"""Behavioral checks for emdash-docs-consolidate-claudemd-into-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/emdash")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `main.ts` — Loads `.env`, fixes PATH for CLI discovery on macOS/Linux/Windows (adds Homebrew, npm global, nvm paths so agents like `gh`, `codex`, `claude` are found when launched from Finder), detec' in text, "expected to find: " + '- `main.ts` — Loads `.env`, fixes PATH for CLI discovery on macOS/Linux/Windows (adds Homebrew, npm global, nvm paths so agents like `gh`, `codex`, `claude` are found when launched from Finder), detec'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- `entry.ts` — Sets app name (must happen before `app.getPath('userData')`, or Electron defaults to `~/Library/Application Support/Electron`). Monkey-patches `Module._resolveFilename` to resolve `@sha" in text, "expected to find: " + "- `entry.ts` — Sets app name (must happen before `app.getPath('userData')`, or Electron defaults to `~/Library/Application Support/Electron`). Monkey-patches `Module._resolveFilename` to resolve `@sha"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- 25+ handler files total (19 in `ipc/` + 6 colocated in `services/`) covering app, db, git, github, browser, connections, project, settings, telemetry, SSH, Linear, Jira, skills, and more' in text, "expected to find: " + '- 25+ handler files total (19 in `ipc/` + 6 colocated in `services/`) covering app, db, git, github, browser, connections, project, settings, telemetry, SSH, Linear, Jira, skills, and more'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

