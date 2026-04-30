"""Behavioral checks for lobehub-docsversionrelease-add-hotfix-changelog-example (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lobehub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/reference/changelog-example/hotfix.md')
    assert "- **Stale topic on agent switch** — Switching from `/agent/agt_A/tpc_X` to `/agent/agt_B` no longer leaves the previous topic's messages on screen, and _Start new topic_ responds again. (#14231)" in text, "expected to find: " + "- **Stale topic on agent switch** — Switching from `/agent/agt_A/tpc_X` to `/agent/agt_B` no longer leaves the previous topic's messages on screen, and _Start new topic_ responds again. (#14231)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/reference/changelog-example/hotfix.md')
    assert "- **Header & sidebar consistency** — Conversation header now shows the active subtopic's title, and the sidebar keeps the parent topic's thread list expanded while a thread is open." in text, "expected to find: " + "- **Header & sidebar consistency** — Conversation header now shows the active subtopic's title, and the sidebar keeps the parent topic's thread list expanded while a thread is open."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/reference/changelog-example/hotfix.md')
    assert "> **Note for Claude**: Replace `{pr-author}` with the actual PR author. Retrieve via `gh pr view <number> --json author --jq '.author.login'`. Do not hardcode a username." in text, "expected to find: " + "> **Note for Claude**: Replace `{pr-author}` with the actual PR author. Retrieve via `gh pr view <number> --json author --jq '.author.login'`. Do not hardcode a username."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/reference/patch-release-scenarios.md')
    assert '3. **Write a short hotfix changelog** — See `changelog-example/hotfix.md`. Keep it minimal: scope line, 1-3 fix bullets (symptom + fix in one sentence), upgrade note, owner. No long root-cause section' in text, "expected to find: " + '3. **Write a short hotfix changelog** — See `changelog-example/hotfix.md`. Keep it minimal: scope line, 1-3 fix bullets (symptom + fix in one sentence), upgrade note, owner. No long root-cause section'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/reference/patch-release-scenarios.md')
    assert "- **Hotfix owner**: Use the actual PR author (retrieve via `gh pr view <number> --json author --jq '.author.login'`), never hardcode a username." in text, "expected to find: " + "- **Hotfix owner**: Use the actual PR author (retrieve via `gh pr view <number> --json author --jq '.author.login'`), never hardcode a username."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/version-release/reference/patch-release-scenarios.md')
    assert '4. **After merge**: auto-tag-release detects `hotfix/*` branch → auto patch +1.' in text, "expected to find: " + '4. **After merge**: auto-tag-release detects `hotfix/*` branch → auto patch +1.'[:80]

