"""Behavioral checks for spawn-fixgrowth-simpler-tweets-chill-replies (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spawn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/growth-prompt.md')
    assert '{a short casual reply, written like a real dev on reddit. Keep it TIGHT: 1-3 sentences max. Lowercase is fine. No corporate speak, no feature lists, no "one command to provision". Sound like you\'re ty' in text, "expected to find: " + '{a short casual reply, written like a real dev on reddit. Keep it TIGHT: 1-3 sentences max. Lowercase is fine. No corporate speak, no feature lists, no "one command to provision". Sound like you\'re ty'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/tweet-prompt.md')
    assert '- **BANNED terms in tweets**: `ps aux`, `OAuth`, `SigV4`, `TLS`, `CORS`, `RBAC`, `syscall`, `stdin`, `stdout`, `CLI args`, `process listing`, `temp file`, `env var`, `--flag names`, commit hashes, fil' in text, "expected to find: " + '- **BANNED terms in tweets**: `ps aux`, `OAuth`, `SigV4`, `TLS`, `CORS`, `RBAC`, `syscall`, `stdin`, `stdout`, `CLI args`, `process listing`, `temp file`, `env var`, `--flag names`, commit hashes, fil'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/tweet-prompt.md')
    assert 'You are writing a single tweet (max 280 characters) about the Spawn project (<https://github.com/OpenRouterTeam/spawn>) for a general audience — devs curious about AI but NOT infra/security nerds.' in text, "expected to find: " + 'You are writing a single tweet (max 280 characters) about the Spawn project (<https://github.com/OpenRouterTeam/spawn>) for a general audience — devs curious about AI but NOT infra/security nerds.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/tweet-prompt.md')
    assert 'Spawn lets anyone spin up an AI coding agent (Claude, Codex, etc.) on a cheap cloud server with one command. That\'s it. Think "AI coding assistant in the cloud, ready in 30 seconds."' in text, "expected to find: " + 'Spawn lets anyone spin up an AI coding agent (Claude, Codex, etc.) on a cheap cloud server with one command. That\'s it. Think "AI coding assistant in the cloud, ready in 30 seconds."'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/x-engage-prompt.md')
    assert '- Add "(disclosure: i help build this)" ONLY if it fits — if the reply is too short, skip disclosure entirely' in text, "expected to find: " + '- Add "(disclosure: i help build this)" ONLY if it fits — if the reply is too short, skip disclosure entirely'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/x-engage-prompt.md')
    assert '- NO corporate phrases: no "One command to provision", no "provides", no "enabling", no "seamlessly"' in text, "expected to find: " + '- NO corporate phrases: no "One command to provision", no "provides", no "enabling", no "seamlessly"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/x-engage-prompt.md')
    assert '- Sound like a friend dropping a quick reply, not a marketer pitching. Examples of the right vibe:' in text, "expected to find: " + '- Sound like a friend dropping a quick reply, not a marketer pitching. Examples of the right vibe:'[:80]

