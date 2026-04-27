"""Behavioral checks for agent-message-queue-docsskill-clarify-wake-is-optional (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-message-queue")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert '> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `am' in text, "expected to find: " + '> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `am'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert 'For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:' in text, "expected to find: " + 'For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert "amq env --wake               # Include 'amq wake &' (interactive terminals only)" in text, "expected to find: " + "amq env --wake               # Include 'amq wake &' (interactive terminals only)"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert '> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `am' in text, "expected to find: " + '> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `am'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert 'For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:' in text, "expected to find: " + 'For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert "amq env --wake               # Include 'amq wake &' (interactive terminals only)" in text, "expected to find: " + "amq env --wake               # Include 'amq wake &' (interactive terminals only)"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `am' in text, "expected to find: " + '> **AI agents**: Skip this section. Wake requires an interactive terminal with TTY access (TIOCSTI/ioctl). Non-interactive sessions (scripts, CI, headless) cannot use wake. Just use `amq drain` or `am'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert 'For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:' in text, "expected to find: " + 'For **human operators** running Claude Code or Codex CLI in an interactive terminal, wake provides background notifications when messages arrive:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert "amq env --wake               # Include 'amq wake &' (interactive terminals only)" in text, "expected to find: " + "amq env --wake               # Include 'amq wake &' (interactive terminals only)"[:80]

