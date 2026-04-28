"""Behavioral checks for spawn-fix-document-sprite-vs-normal (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spawn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/SKILL.md')
    assert '**Note:** The wrapper script (`start-<service-name>.sh`) sets the actual env vars (`TRIGGER_SECRET`, `TARGET_SCRIPT`, etc.). The systemd service just executes the wrapper.' in text, "expected to find: " + '**Note:** The wrapper script (`start-<service-name>.sh`) sets the actual env vars (`TRIGGER_SECRET`, `TARGET_SCRIPT`, etc.). The systemd service just executes the wrapper.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/SKILL.md')
    assert '**NEVER guess the repository path. NEVER invent home directories (e.g., `/home/claude-runner`). ASK the user where the repo lives.**' in text, "expected to find: " + '**NEVER guess the repository path. NEVER invent home directories (e.g., `/home/claude-runner`). ASK the user where the repo lives.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/SKILL.md')
    assert '- The wrapper scripts (e.g., `start-security.sh`) MUST live inside the repo at `{REPO_ROOT}/.claude/skills/setup-agent-team/`' in text, "expected to find: " + '- The wrapper scripts (e.g., `start-security.sh`) MUST live inside the repo at `{REPO_ROOT}/.claude/skills/setup-agent-team/`'[:80]

