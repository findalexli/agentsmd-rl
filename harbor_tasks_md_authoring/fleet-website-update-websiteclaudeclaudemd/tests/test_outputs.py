"""Behavioral checks for fleet-website-update-websiteclaudeclaudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fleet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('website/.claude/CLAUDE.md')
    assert 'New pages should mirror the structure and styling of existing landing pages rather than inventing new patterns. Before writing markup or LESS, open 1–2 existing landing pages in `views/pages/landing-p' in text, "expected to find: " + 'New pages should mirror the structure and styling of existing landing pages rather than inventing new patterns. Before writing markup or LESS, open 1–2 existing landing pages in `views/pages/landing-p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('website/.claude/CLAUDE.md')
    assert "**Always use `sails generate page <name>` or `sails generate page <folder>/<name>` — don't hand-create the controller/view/script/LESS files.** The generator produces the correct Actions2 shape, view " in text, "expected to find: " + "**Always use `sails generate page <name>` or `sails generate page <folder>/<name>` — don't hand-create the controller/view/script/LESS files.** The generator produces the correct Actions2 shape, view "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('website/.claude/CLAUDE.md')
    assert "Do **not** use `sails generate landing-page` (the custom generator under `website/generators/landing-page/`). It's deprecated; use `sails generate page` for landing pages too." in text, "expected to find: " + "Do **not** use `sails generate landing-page` (the custom generator under `website/generators/landing-page/`). It's deprecated; use `sails generate page` for landing pages too."[:80]

