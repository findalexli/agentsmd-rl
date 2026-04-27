"""Behavioral checks for open-skills-add-filetracker-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/chat-logger/SKILL.md')
    assert 'Automatically logs all incoming and outgoing chat messages to a SQLite database. Essential for building a searchable chat history and auditing conversations.' in text, "expected to find: " + 'Automatically logs all incoming and outgoing chat messages to a SQLite database. Essential for building a searchable chat history and auditing conversations.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/chat-logger/SKILL.md')
    assert 'description: Log all chat messages (user and assistant) from all channels to a SQLite database for verbatim recall.' in text, "expected to find: " + 'description: Log all chat messages (user and assistant) from all channels to a SQLite database for verbatim recall.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/chat-logger/SKILL.md')
    assert 'def _log_message(self, msg: InboundMessage | OutboundMessage, msg_type: str, tools_used: list | None = None):' in text, "expected to find: " + 'def _log_message(self, msg: InboundMessage | OutboundMessage, msg_type: str, tools_used: list | None = None):'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/file-tracker/SKILL.md')
    assert 'description: Log all file changes (write, edit, delete) to a SQLite database for debugging and audit. Use when: (1) Tracking code changes, (2) Debugging issues, (3) Auditing file modifications, or (4)' in text, "expected to find: " + 'description: Log all file changes (write, edit, delete) to a SQLite database for debugging and audit. Use when: (1) Tracking code changes, (2) Debugging issues, (3) Auditing file modifications, or (4)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/file-tracker/SKILL.md')
    assert '"INSERT INTO file_changes (timestamp, channel, chat_id, action, file_path, old_content, new_content) VALUES (?, ?, ?, ?, ?, ?, ?)",' in text, "expected to find: " + '"INSERT INTO file_changes (timestamp, channel, chat_id, action, file_path, old_content, new_content) VALUES (?, ?, ?, ?, ?, ?, ?)",'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/file-tracker/SKILL.md')
    assert 'def log_file_change(channel: str, chat_id: str, action: str, file_path: str, old_content: str = None, new_content: str = None):' in text, "expected to find: " + 'def log_file_change(channel: str, chat_id: str, action: str, file_path: str, old_content: str = None, new_content: str = None):'[:80]

