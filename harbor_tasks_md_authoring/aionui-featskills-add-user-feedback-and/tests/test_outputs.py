"""Behavioral checks for aionui-featskills-add-user-feedback-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aionui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/SKILL.md')
    assert '| Attachment type | Name / MIME pattern             | Analysis method                                                           |' in text, "expected to find: " + '| Attachment type | Name / MIME pattern             | Analysis method                                                           |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/SKILL.md')
    assert '| Logs            | `logs.gz`, `*.log`, `*.txt`     | Download → decompress → search for error patterns, stack traces, warnings |' in text, "expected to find: " + '| Logs            | `logs.gz`, `*.log`, `*.txt`     | Download → decompress → search for error patterns, stack traces, warnings |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/SKILL.md')
    assert '| Screenshots     | `*.png`, `*.jpg`, `screenshot*` | Download → use vision to identify UI state, error dialogs, frozen screens |' in text, "expected to find: " + '| Screenshots     | `*.png`, `*.jpg`, `screenshot*` | Download → use vision to identify UI state, error dialogs, frozen screens |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/references/report-template.md')
    assert 'Total: N fixed (PR created), F from feedback, P pending review, M already fixed, K skipped' in text, "expected to find: " + 'Total: N fixed (PR created), F from feedback, P pending review, M already fixed, K skipped'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/references/report-template.md')
    assert '→ Attachment: logs.gz — stack trace found pointing to src/renderer/hooks/useChat.ts' in text, "expected to find: " + '→ Attachment: logs.gz — stack trace found pointing to src/renderer/hooks/useChat.ts'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/references/report-template.md')
    assert '1. [ELECTRON-FF] User-reported UI freeze during stream response' in text, "expected to find: " + '1. [ELECTRON-FF] User-reported UI freeze during stream response'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/references/triage-rules.md')
    assert '| Category          | Criteria                                                     | Action                        |' in text, "expected to find: " + '| Category          | Criteria                                                     | Action                        |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/references/triage-rules.md')
    assert '| **Direct fix**    | Stack trace → our code, clear cause                          | Fix with targeted code change |' in text, "expected to find: " + '| **Direct fix**    | Stack trace → our code, clear cause                          | Fix with targeted code change |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/fix-sentry/references/triage-rules.md')
    assert '| **Defensive fix** | No stack trace, but error path matches our code              | Fix with defensive guards     |' in text, "expected to find: " + '| **Defensive fix** | No stack trace, but error path matches our code              | Fix with defensive guards     |'[:80]

