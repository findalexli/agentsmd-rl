"""Behavioral checks for skillpack-feat-improve-skill-scores-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skillpack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skillpack-creator/SKILL.md')
    assert '- If the task is still too broad, narrow the scope instead of writing a vague mega-skill. If key success conditions depend on hidden human judgment, mark the pack as a best-effort assistant workflow.' in text, "expected to find: " + '- If the task is still too broad, narrow the scope instead of writing a vague mega-skill. If key success conditions depend on hidden human judgment, mark the pack as a best-effort assistant workflow.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skillpack-creator/SKILL.md')
    assert 'The script validates the manifest, writes `skillpack.json`, creates `skills/`, copies `start.sh`/`start.bat` from `templates/`, and optionally runs `npx -y @cremini/skillpack zip`.' in text, "expected to find: " + 'The script validates the manifest, writes `skillpack.json`, creates `skills/`, copies `start.sh`/`start.bat` from `templates/`, and optionally runs `npx -y @cremini/skillpack zip`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skillpack-creator/SKILL.md')
    assert '- **Prompts** (`skillpack.json`): 1–3 pack-level starter inputs for the UI — not a DAG or state machine. See `references/skillpack-format.md` for exact pack semantics.' in text, "expected to find: " + '- **Prompts** (`skillpack.json`): 1–3 pack-level starter inputs for the UI — not a DAG or state machine. See `references/skillpack-format.md` for exact pack semantics.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/builtin-skills/skill-creator/SKILL.md')
    assert 'The `description` is the primary triggering mechanism — make it concrete with both what the skill does and when to use it. Keep the body focused on workflow, decisions, and output expectations. Place ' in text, "expected to find: " + 'The `description` is the primary triggering mechanism — make it concrete with both what the skill does and when to use it. Keep the body focused on workflow, decisions, and output expectations. Place '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/builtin-skills/skill-creator/SKILL.md')
    assert 'Prefer imperative instructions. Structure skills as: purpose, trigger guidance, required inputs, step-by-step workflow, output format, edge cases. For multi-domain skills, organize references by varia' in text, "expected to find: " + 'Prefer imperative instructions. Structure skills as: purpose, trigger guidance, required inputs, step-by-step workflow, output format, edge cases. For multi-domain skills, organize references by varia'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/builtin-skills/skill-creator/SKILL.md')
    assert 'All skills live under `{{SKILLS_PATH}}/<skill-name>/SKILL.md` and config is at `{{PACK_CONFIG_PATH}}`. These paths override any generic advice. Never create skills in the current workspace directory —' in text, "expected to find: " + 'All skills live under `{{SKILLS_PATH}}/<skill-name>/SKILL.md` and config is at `{{PACK_CONFIG_PATH}}`. These paths override any generic advice. Never create skills in the current workspace directory —'[:80]

