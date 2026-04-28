"""Behavioral checks for comfyui_skills_openclaw-chore-optimize-skillmd-description-f (markdown_authoring task).

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
    assert 'Run ComfyUI workflows from any AI agent (Claude Code, OpenClaw, Codex) via a single CLI. Import workflows, manage dependencies, execute across multiple servers, and track history — all through shell c' in text, "expected to find: " + 'Run ComfyUI workflows from any AI agent (Claude Code, OpenClaw, Codex) via a single CLI. Import workflows, manage dependencies, execute across multiple servers, and track history — all through shell c'[:80]

