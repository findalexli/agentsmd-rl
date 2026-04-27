"""Behavioral checks for ouroboros-feat-add-ooo-publish-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ouroboros")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `ooo publish` or `ooo publish ...` | Read `skills/publish/SKILL.md` and follow it |' in text, "expected to find: " + '| `ooo publish` or `ooo publish ...` | Read `skills/publish/SKILL.md` and follow it |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `ooo publish` | `gh` CLI — Seed to GitHub Issues |' in text, "expected to find: " + '| `ooo publish` | `gh` CLI — Seed to GitHub Issues |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/help/SKILL.md')
    assert '| "publish to github", "create issues from seed", "seed to issues" | `ooo publish` |' in text, "expected to find: " + '| "publish to github", "create issues from seed", "seed to issues" | `ooo publish` |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/help/SKILL.md')
    assert '| `/ouroboros:publish` | Publish Seed as GitHub Issues for teams | Plugin |' in text, "expected to find: " + '| `/ouroboros:publish` | Publish Seed as GitHub Issues for teams | Plugin |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/help/SKILL.md')
    assert '| `ooo publish` | Publish Seed as GitHub Issues for teams | Plugin |' in text, "expected to find: " + '| `ooo publish` | Publish Seed as GitHub Issues for teams | Plugin |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/publish/SKILL.md')
    assert 'Analyze the acceptance criteria and group them into logical implementation units. Each unit becomes a Task issue. Use your understanding of the domain to create meaningful groupings (e.g., group by fe' in text, "expected to find: " + 'Analyze the acceptance criteria and group them into logical implementation units. Each unit becomes a Task issue. Use your understanding of the domain to create meaningful groupings (e.g., group by fe'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/publish/SKILL.md')
    assert '"question": "Here\'s the planned issue structure:\\n\\n**Epic**: <goal summary>\\n\\n**Tasks**:\\n1. <task_1_title> — <brief scope>\\n2. <task_2_title> — <brief scope>\\n3. <task_3_title> — <brief scope>\\n\\nP' in text, "expected to find: " + '"question": "Here\'s the planned issue structure:\\n\\n**Epic**: <goal summary>\\n\\n**Tasks**:\\n1. <task_1_title> — <brief scope>\\n2. <task_2_title> — <brief scope>\\n3. <task_3_title> — <brief scope>\\n\\nP'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/publish/SKILL.md')
    assert "The search uses the seed's unique identifier (`metadata.seed_id` for YAML seeds, `pm_id` for JSON seeds). This works because Step 7 persists the identifier in the Epic body (see the `Seed ID` field in" in text, "expected to find: " + "The search uses the seed's unique identifier (`metadata.seed_id` for YAML seeds, `pm_id` for JSON seeds). This works because Step 7 persists the identifier in the Epic body (see the `Seed ID` field in"[:80]

