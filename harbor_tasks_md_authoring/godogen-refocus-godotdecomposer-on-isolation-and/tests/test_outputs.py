"""Behavioral checks for godogen-refocus-godotdecomposer-on-isolation-and (markdown_authoring task).

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
    text = _read('.claude/skills/game-decomposer/SKILL.md')
    assert '- **Verify** — a concrete visual scenario for the test harness. The task executor generates a SceneTree script from this: it loads the scene, positions a camera, captures screenshots via `xvfb-run --w' in text, "expected to find: " + '- **Verify** — a concrete visual scenario for the test harness. The task executor generates a SceneTree script from this: it loads the scene, positions a camera, captures screenshots via `xvfb-run --w'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/game-decomposer/SKILL.md')
    assert 'Merge tasks integrate previously-independent features. Integrate 2-3 things at a time (A+B → AB, then AB+C → ABC), not everything at once. Merge requirements focus on **integration behavior** ("bullet' in text, "expected to find: " + 'Merge tasks integrate previously-independent features. Integrate 2-3 things at a time (A+B → AB, then AB+C → ABC), not everything at once. Merge requirements focus on **integration behavior** ("bullet'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/game-decomposer/SKILL.md')
    assert 'Each task gets its own test harness — a SceneTree script that loads the scene, positions a camera, captures screenshots, and verifies visually. When a task fails verification, only that task is regene' in text, "expected to find: " + 'Each task gets its own test harness — a SceneTree script that loads the scene, positions a camera, captures screenshots, and verifies visually. When a task fails verification, only that task is regene'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gamedev/SKILL.md')
    assert 'Read `build/assets.json` at the start to get the list of available assets. Pass the assets list to **godot-scaffold** and **game-decomposer** so they can plan around available models and textures.' in text, "expected to find: " + 'Read `build/assets.json` at the start to get the list of available assets. Pass the assets list to **godot-scaffold** and **game-decomposer** so they can plan around available models and textures.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gamedev/SKILL.md')
    assert '| **game-decomposer** | game description, STRUCTURE.md, assets | `build/PLAN.md` — task DAG with verification criteria | Once at start | Inline |' in text, "expected to find: " + '| **game-decomposer** | game description, STRUCTURE.md, assets | `build/PLAN.md` — task DAG with verification criteria | Once at start | Inline |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/godot-decomposer/SKILL.md')
    assert '.claude/skills/godot-decomposer/SKILL.md' in text, "expected to find: " + '.claude/skills/godot-decomposer/SKILL.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- game-decomposer' in text, "expected to find: " + '- game-decomposer'[:80]

