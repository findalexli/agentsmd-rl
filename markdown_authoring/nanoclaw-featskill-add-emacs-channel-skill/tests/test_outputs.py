"""Behavioral checks for nanoclaw-featskill-add-emacs-channel-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-emacs/SKILL.md')
    assert 'description: Add Emacs as a channel. Opens an interactive chat buffer and org-mode integration so you can talk to NanoClaw from within Emacs (Doom, Spacemacs, or vanilla). Uses a local HTTP bridge — n' in text, "expected to find: " + 'description: Add Emacs as a channel. Opens an interactive chat buffer and org-mode integration so you can talk to NanoClaw from within Emacs (Doom, Spacemacs, or vanilla). Uses a local HTTP bridge — n'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-emacs/SKILL.md')
    assert '6. Rebuild: `npm run build && launchctl kickstart -k gui/$(id -u)/com.nanoclaw` (macOS) or `npm run build && systemctl --user restart nanoclaw` (Linux)' in text, "expected to find: " + '6. Rebuild: `npm run build && launchctl kickstart -k gui/$(id -u)/com.nanoclaw` (macOS) or `npm run build && systemctl --user restart nanoclaw` (Linux)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-emacs/SKILL.md')
    assert '- **Code review** — select a region and send it with `nanoclaw-org-send`; the response appears as a child heading inline in your org file' in text, "expected to find: " + '- **Code review** — select a region and send it with `nanoclaw-org-send`; the response appears as a child heading inline in your org file'[:80]

