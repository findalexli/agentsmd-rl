"""Behavioral checks for browser-use-update-skillmd-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/browser-use")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/browser-use/SKILL.md')
    assert '- **real**: Uses a real Chrome binary. Without `--profile`, uses a persistent but empty CLI profile at `~/.config/browseruse/profiles/cli/`. With `--profile "ProfileName"`, copies your actual Chrome p' in text, "expected to find: " + '- **real**: Uses a real Chrome binary. Without `--profile`, uses a persistent but empty CLI profile at `~/.config/browseruse/profiles/cli/`. With `--profile "ProfileName"`, copies your actual Chrome p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/browser-use/SKILL.md')
    assert '**Session behavior**: All commands without `--session` use the same "default" session. The browser stays open and is reused across commands. Use `--session NAME` to run multiple browsers in parallel.' in text, "expected to find: " + '**Session behavior**: All commands without `--session` use the same "default" session. The browser stays open and is reused across commands. Use `--session NAME` to run multiple browsers in parallel.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/browser-use/SKILL.md')
    assert '**Note:** Tunnels are independent of browser sessions. They persist across `browser-use close` and can be managed separately. Cloudflared must be installed — run `browser-use doctor` to check.' in text, "expected to find: " + '**Note:** Tunnels are independent of browser sessions. They persist across `browser-use close` and can be managed separately. Cloudflared must be installed — run `browser-use doctor` to check.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/remote-browser/SKILL.md')
    assert '**Note:** Tunnels are independent of browser sessions. They persist across `browser-use close` and can be managed separately. Cloudflared must be installed — run `browser-use doctor` to check.' in text, "expected to find: " + '**Note:** Tunnels are independent of browser sessions. They persist across `browser-use close` and can be managed separately. Cloudflared must be installed — run `browser-use doctor` to check.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/remote-browser/SKILL.md')
    assert '**Task stuck at "started"**: Check cost with `task status` — if not increasing, the task is stuck. View live URL with `session get`, then stop and start a new agent.' in text, "expected to find: " + '**Task stuck at "started"**: Check cost with `task status` — if not increasing, the task is stuck. View live URL with `session get`, then stop and start a new agent.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/remote-browser/SKILL.md')
    assert '| `--profile ID` | Cloud profile ID for persistent cookies. Works with `open`, `session create`, etc. — does NOT work with `run` (use `--session-id` instead) |' in text, "expected to find: " + '| `--profile ID` | Cloud profile ID for persistent cookies. Works with `open`, `session create`, etc. — does NOT work with `run` (use `--session-id` instead) |'[:80]

