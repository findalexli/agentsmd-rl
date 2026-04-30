"""Behavioral checks for agents-fix-skill-hook-paths-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Important:** Hooks in `SKILL.md` frontmatter can use **relative paths** from the skill's directory (e.g., `./scripts/bar.py`). Use `${CLAUDE_PLUGIN_ROOT}` in `marketplace.json` to reference the plug" in text, "expected to find: " + "**Important:** Hooks in `SKILL.md` frontmatter can use **relative paths** from the skill's directory (e.g., `./scripts/bar.py`). Use `${CLAUDE_PLUGIN_ROOT}` in `marketplace.json` to reference the plug"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `skills/*/hooks/*.sh` - Hook scripts (co-located with skills, referenced via relative paths from SKILL.md or `${CLAUDE_PLUGIN_ROOT}/skills/<name>/hooks/...` from marketplace.json)' in text, "expected to find: " + '- `skills/*/hooks/*.sh` - Hook scripts (co-located with skills, referenced via relative paths from SKILL.md or `${CLAUDE_PLUGIN_ROOT}/skills/<name>/hooks/...` from marketplace.json)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-data/SKILL.md')
    assert 'command: "uv run ./scripts/cli.py ensure"' in text, "expected to find: " + 'command: "uv run ./scripts/cli.py ensure"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/analyzing-data/SKILL.md')
    assert 'command: "uv run ./scripts/cli.py stop"' in text, "expected to find: " + 'command: "uv run ./scripts/cli.py stop"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/init/SKILL.md')
    assert 'command: "uv run ../analyzing-data/scripts/cli.py ensure"' in text, "expected to find: " + 'command: "uv run ../analyzing-data/scripts/cli.py ensure"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/init/SKILL.md')
    assert 'command: "uv run ../analyzing-data/scripts/cli.py stop"' in text, "expected to find: " + 'command: "uv run ../analyzing-data/scripts/cli.py stop"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/init/SKILL.md')
    assert '**Scripts:** `../analyzing-data/scripts/`' in text, "expected to find: " + '**Scripts:** `../analyzing-data/scripts/`'[:80]

