"""Behavioral checks for agent-message-queue-fix-correct-amroot-guidance-in (markdown_authoring task).

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
    assert '- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agen' in text, "expected to find: " + '- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agen'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert '- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.' in text, "expected to find: " + '- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert '| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |' in text, "expected to find: " + '| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert '- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agen' in text, "expected to find: " + '- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agen'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert '- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.' in text, "expected to find: " + '- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert '| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |' in text, "expected to find: " + '| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agen' in text, "expected to find: " + '- **Pitfall**: `coop exec` defaults to `--session collab` (i.e. `.agent-mail/collab`). If you manually use `.agent-mail/collab` outside `coop exec`, messages go to a different mailbox tree than `.agen'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.' in text, "expected to find: " + '- **Do NOT append a session name** (e.g. `/collab`) unless you intentionally want an isolated session. Outside `coop exec`, the base root from `.amqrc` is where agents live.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |' in text, "expected to find: " + '| Outside `coop exec`, isolated session | `amq env --session auth --me claude` | `.agent-mail/auth` |'[:80]

