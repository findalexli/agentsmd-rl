"""Behavioral checks for godogen-add-task-resumption-and-status (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/godogen")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/game-decomposer.md')
    assert "- **Requirements** — high-level behaviors the task must achieve. Focus on *what* the player experiences, not *how* to implement it. The task executor is a strong LLM — it doesn't need pixel-exact dime" in text, "expected to find: " + "- **Requirements** — high-level behaviors the task must achieve. Focus on *what* the player experiences, not *how* to implement it. The task executor is a strong LLM — it doesn't need pixel-exact dime"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/game-decomposer.md')
    assert 'Each task builds directly into the shared project — features are integrated by default. Only add a merge task when integration is genuinely non-trivial (e.g., two large independent systems with comple' in text, "expected to find: " + 'Each task builds directly into the shared project — features are integrated by default. Only add a merge task when integration is genuinely non-trivial (e.g., two large independent systems with comple'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/game-decomposer.md')
    assert '- Detailed technical specs — the task executor is a strong LLM, it makes good implementation decisions on its own. Focus on *what* each task should achieve, not *how*.' in text, "expected to find: " + '- Detailed technical specs — the task executor is a strong LLM, it makes good implementation decisions on its own. Focus on *what* each task should achieve, not *how*.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/gamedev.md')
    assert 'Keep a `**Status:**` field on each task in PLAN.md: `pending` | `in_progress` | `done` | `done (partial)` | `skipped`. Update it immediately when state changes — before launching the sub-agent and aft' in text, "expected to find: " + 'Keep a `**Status:**` field on each task in PLAN.md: `pending` | `in_progress` | `done` | `done (partial)` | `skipped`. Update it immediately when state changes — before launching the sub-agent and aft'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/gamedev.md')
    assert '**PLAN.md** — decomposer agent is the primary author. You own the `**Status:**` fields. Between decomposer runs, you may also tweak tasks when discoveries change future work (adjust approach, mark tas' in text, "expected to find: " + '**PLAN.md** — decomposer agent is the primary author. You own the `**Status:**` fields. Between decomposer runs, you may also tweak tasks when discoveries change future work (adjust approach, mark tas'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/gamedev.md')
    assert 'At the start of every run, check if `build/PLAN.md` exists. If so, read it along with STRUCTURE.md and MEMORY.md, then resume from the first non-`done` task. Treat `in_progress` as needing a retry.' in text, "expected to find: " + 'At the start of every run, check if `build/PLAN.md` exists. If so, read it along with STRUCTURE.md and MEMORY.md, then resume from the first non-`done` task. Treat `in_progress` as needing a retry.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/godot-task.md')
    assert "- **Visual quality & logic:** look for obvious bugs — geometry clipping through other geometry, objects floating in mid-air when they shouldn't be, wrong assets used (e.g., dog image where cat is expe" in text, "expected to find: " + "- **Visual quality & logic:** look for obvious bugs — geometry clipping through other geometry, objects floating in mid-air when they shouldn't be, wrong assets used (e.g., dog image where cat is expe"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/godot-task.md')
    assert 'If either check fails, identify the issue, fix scene/script/test, and repeat from step 3.' in text, "expected to find: " + 'If either check fails, identify the issue, fix scene/script/test, and repeat from step 3.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/godot-task.md')
    assert '- **Task goal:** does the screenshot match the **Verify** description?' in text, "expected to find: " + '- **Task goal:** does the screenshot match the **Verify** description?'[:80]

