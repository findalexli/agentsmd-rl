"""Behavioral checks for higress-docs-mark-openclaw-commands-as (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/higress")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/higress-openclaw-integration/SKILL.md')
    assert '3. **OpenClaw Integration**: The `openclaw models auth login` and `openclaw gateway restart` commands are **interactive** and must be run by the user manually in their terminal' in text, "expected to find: " + '3. **OpenClaw Integration**: The `openclaw models auth login` and `openclaw gateway restart` commands are **interactive** and must be run by the user manually in their terminal'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/higress-openclaw-integration/SKILL.md')
    assert 'After configuration and restart, Higress models are available in OpenClaw with `higress/` prefix (e.g., `higress/glm-4`, `higress/auto`).' in text, "expected to find: " + 'After configuration and restart, Higress models are available in OpenClaw with `higress/` prefix (e.g., `higress/glm-4`, `higress/auto`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/higress-openclaw-integration/SKILL.md')
    assert '**⚠️ Tell user to run the following commands manually in their terminal (interactive commands, cannot be executed by AI agent):**' in text, "expected to find: " + '**⚠️ Tell user to run the following commands manually in their terminal (interactive commands, cannot be executed by AI agent):**'[:80]

