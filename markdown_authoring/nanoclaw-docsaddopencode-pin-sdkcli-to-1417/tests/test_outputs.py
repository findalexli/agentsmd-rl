"""Behavioral checks for nanoclaw-docsaddopencode-pin-sdkcli-to-1417 (markdown_authoring task).

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
    text = _read('.claude/skills/add-opencode/SKILL.md')
    assert "- `ANTHROPIC_BASE_URL` — **required for non-`anthropic` providers.** The opencode container provider passes this as the `baseURL` for the upstream provider config so requests route through OneCLI's cr" in text, "expected to find: " + "- `ANTHROPIC_BASE_URL` — **required for non-`anthropic` providers.** The opencode container provider passes this as the `baseURL` for the upstream provider config so requests route through OneCLI's cr"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-opencode/SKILL.md')
    assert 'Each agent group has a live source overlay at `data/v2-sessions/<group-id>/agent-runner-src/providers/` that **overrides the image at runtime**. This overlay is created when the group is first wired a' in text, "expected to find: " + 'Each agent group has a live source overlay at `data/v2-sessions/<group-id>/agent-runner-src/providers/` that **overrides the image at runtime**. This overlay is created when the group is first wired a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-opencode/SKILL.md')
    assert '- Session continuation uses UUID format (SDK 1.4.x / CLI 1.4.x). Stale sessions are cleared by `isSessionInvalid` on OpenCode-specific error patterns. If you see UUID-related errors after an accidenta' in text, "expected to find: " + '- Session continuation uses UUID format (SDK 1.4.x / CLI 1.4.x). Stale sessions are cleared by `isSessionInvalid` on OpenCode-specific error patterns. If you see UUID-related errors after an accidenta'[:80]

