"""Behavioral checks for comfyui_skills_openclaw-docs-update-skillmd-for-new (markdown_authoring task).

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
    assert '| `comfyui-skill --json workflow import <path>` | Import workflow (auto-detect, warns about deprecated nodes) |' in text, "expected to find: " + '| `comfyui-skill --json workflow import <path>` | Import workflow (auto-detect, warns about deprecated nodes) |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "| `comfyui-skill --json run <id> --args '{...}'` | Execute a workflow (blocking, real-time streaming) |" in text, "expected to find: " + "| `comfyui-skill --json run <id> --args '{...}'` | Execute a workflow (blocking, real-time streaming) |"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- User says "inpainting / mask this area" → `comfyui-skill --json upload <mask> --mask`, then execute' in text, "expected to find: " + '- User says "inpainting / mask this area" → `comfyui-skill --json upload <mask> --mask`, then execute'[:80]

