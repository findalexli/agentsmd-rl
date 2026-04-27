"""Behavioral checks for understand-anything-fixskills-harden-plugin-root-resolution (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/understand-anything")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('understand-anything-plugin/skills/understand-dashboard/SKILL.md')
    assert 'COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand-dashboard 2>/dev/null || readlink -f ~/.copilot/skills/understand-dashboard 2>/dev/null || echo "")' in text, "expected to find: " + 'COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand-dashboard 2>/dev/null || readlink -f ~/.copilot/skills/understand-dashboard 2>/dev/null || echo "")'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('understand-anything-plugin/skills/understand-dashboard/SKILL.md')
    assert 'COPILOT_SELF_RELATIVE=$([ -n "$COPILOT_SKILL_REAL" ] && cd "$COPILOT_SKILL_REAL/../.." 2>/dev/null && pwd || echo "")' in text, "expected to find: " + 'COPILOT_SELF_RELATIVE=$([ -n "$COPILOT_SKILL_REAL" ] && cd "$COPILOT_SKILL_REAL/../.." 2>/dev/null && pwd || echo "")'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('understand-anything-plugin/skills/understand-dashboard/SKILL.md')
    assert '- Two levels up from `~/.copilot/skills/understand-dashboard` real path (Copilot personal skills fallback)' in text, "expected to find: " + '- Two levels up from `~/.copilot/skills/understand-dashboard` real path (Copilot personal skills fallback)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('understand-anything-plugin/skills/understand/SKILL.md')
    assert '**Important:** do **not** assume the plugin root is simply two directories above the skill path string. In many installations `~/.agents/skills/understand` is a symlink into the real plugin checkout. ' in text, "expected to find: " + '**Important:** do **not** assume the plugin root is simply two directories above the skill path string. In many installations `~/.agents/skills/understand` is a symlink into the real plugin checkout. '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('understand-anything-plugin/skills/understand/SKILL.md')
    assert '1.5. **Ensure the plugin is built.** Later phases invoke Node scripts that import `@understand-anything/core`. On a fresh install `packages/core/dist/` does not exist yet — build once.' in text, "expected to find: " + '1.5. **Ensure the plugin is built.** Later phases invoke Node scripts that import `@understand-anything/core`. On a fresh install `packages/core/dist/` does not exist yet — build once.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('understand-anything-plugin/skills/understand/SKILL.md')
    assert 'COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand 2>/dev/null || readlink -f ~/.copilot/skills/understand 2>/dev/null || echo "")' in text, "expected to find: " + 'COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand 2>/dev/null || readlink -f ~/.copilot/skills/understand 2>/dev/null || echo "")'[:80]

