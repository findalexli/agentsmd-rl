"""Behavioral checks for claude-code-plugins-plus-skills-featnotionpack-build-skill-5 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-common-errors/SKILL.md')
    assert '**Fix:** Retry with exponential backoff. If persistent (>5 minutes), check [status.notion.so](https://status.notion.so) for ongoing incidents. Consider filing a bug report at [developers.notion.com](h' in text, "expected to find: " + '**Fix:** Retry with exponential backoff. If persistent (>5 minutes), check [status.notion.so](https://status.notion.so) for ongoing incidents. Consider filing a bug report at [developers.notion.com](h'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-common-errors/SKILL.md')
    assert "**Page ID gotcha:** Notion URLs use 32-character hex IDs without dashes (`https://notion.so/Page-abc123def456...`). The API accepts both dashed (`abc123de-f456-...`) and undashed formats. If you're ex" in text, "expected to find: " + "**Page ID gotcha:** Notion URLs use 32-character hex IDs without dashes (`https://notion.so/Page-abc123def456...`). The API accepts both dashed (`abc123de-f456-...`) and undashed formats. If you're ex"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-common-errors/SKILL.md')
    assert '**Fix:** Go to [notion.so/my-integrations](https://www.notion.so/my-integrations), select your integration, and enable the needed capabilities under "Capabilities." Common missing capability: "Read co' in text, "expected to find: " + '**Fix:** Go to [notion.so/my-integrations](https://www.notion.so/my-integrations), select your integration, and enable the needed capabilities under "Capabilities." Common missing capability: "Read co'[:80]

