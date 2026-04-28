"""Behavioral checks for comfyui_skills_openclaw-docs-restructure-skillmd-for-better (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/comfyui-skills-openclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '4. **Cloud Node Unauthorized**: Workflow uses cloud API nodes (Kling, Sora, etc.). Guide user to: (1) Generate an API Key at https://platform.comfy.org, (2) Open Web UI → Server Settings → fill in "Co' in text, "expected to find: " + '4. **Cloud Node Unauthorized**: Workflow uses cloud API nodes (Kling, Sora, etc.). Guide user to: (1) Generate an API Key at https://platform.comfy.org, (2) Open Web UI → Server Settings → fill in "Co'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- **Schema**: Each workflow has a `schema.json` that maps business parameter names (e.g., `prompt`, `seed`) to internal ComfyUI node fields. Never expose node IDs to the user.' in text, "expected to find: " + '- **Schema**: Each workflow has a `schema.json` that maps business parameter names (e.g., `prompt`, `seed`) to internal ComfyUI node fields. Never expose node IDs to the user.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "> **Prerequisites**: Install the CLI: `pip install -U comfyui-skill-cli`. All commands must run from this project's root directory (where this `SKILL.md` is located)." in text, "expected to find: " + "> **Prerequisites**: Install the CLI: `pip install -U comfyui-skill-cli`. All commands must run from this project's root directory (where this `SKILL.md` is located)."[:80]

