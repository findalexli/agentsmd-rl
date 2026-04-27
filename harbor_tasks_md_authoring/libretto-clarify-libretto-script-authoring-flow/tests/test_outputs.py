"""Behavioral checks for libretto-clarify-libretto-script-authoring-flow (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libretto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert '- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.' in text, "expected to find: " + '- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert '- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.' in text, "expected to find: " + '- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert '- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.' in text, "expected to find: " + '- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/libretto/SKILL.md')
    assert '- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.' in text, "expected to find: " + '- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/libretto/SKILL.md')
    assert '- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.' in text, "expected to find: " + '- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/libretto/SKILL.md')
    assert '- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.' in text, "expected to find: " + '- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/libretto/SKILL.md')
    assert '- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.' in text, "expected to find: " + '- Treat Libretto as a script-authoring workflow: choose or create a workflow file, inspect the page, try focused actions, then update code outside the CLI and verify it with `run`.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/libretto/SKILL.md')
    assert '- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.' in text, "expected to find: " + '- For a new automation, you may use `open`, `snapshot`, or `exec` first to learn the page, but do not finish or reply as if the task is complete until the workflow file exists.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/libretto/SKILL.md')
    assert '- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.' in text, "expected to find: " + '- When the task is to build or change an automation, create or update the workflow file and use Libretto commands to gather the information needed for that code change.'[:80]

