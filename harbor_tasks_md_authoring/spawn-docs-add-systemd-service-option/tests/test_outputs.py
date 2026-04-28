"""Behavioral checks for spawn-docs-add-systemd-service-option (markdown_authoring task).

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
    text = _read('.claude/skills/setup-agent-team/SKILL.md')
    assert "| systemd service won't start | Check `journalctl -u spawn-<name> -n 50` — common issues: port in use (EADDRINUSE), wrong PATH (bun/claude not found), permission denied |" in text, "expected to find: " + "| systemd service won't start | Check `journalctl -u spawn-<name> -n 50` — common issues: port in use (EADDRINUSE), wrong PATH (bun/claude not found), permission denied |"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/SKILL.md')
    assert '| `discovery.yml` (Trigger Discovery) | `lab-spawn-discovery` (Sprite) | sprite-env | `discovery-trigger` | `DISCOVERY_SPRITE_URL`, `DISCOVERY_TRIGGER_SECRET` |' in text, "expected to find: " + '| `discovery.yml` (Trigger Discovery) | `lab-spawn-discovery` (Sprite) | sprite-env | `discovery-trigger` | `DISCOVERY_SPRITE_URL`, `DISCOVERY_TRIGGER_SECRET` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/SKILL.md')
    assert '| systemd service keeps restarting | Check exit code in `systemctl status` — if exit 1, check journal logs. If EADDRINUSE, run `fuser -k 8080/tcp` first |' in text, "expected to find: " + '| systemd service keeps restarting | Check exit code in `systemctl status` — if exit 1, check journal logs. If EADDRINUSE, run `fuser -k 8080/tcp` first |'[:80]

