"""Behavioral checks for prompt-master-update-skillmd-to-version-140 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prompt-master")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Description: Generates surgical, credit-efficient prompts for any AI tool or IDE. ALWAYS invoke this skill when the user wants to write, build, fix, improve, rewrite, edit, adapt, or decompose a promp' in text, "expected to find: " + 'Description: Generates surgical, credit-efficient prompts for any AI tool or IDE. ALWAYS invoke this skill when the user wants to write, build, fix, improve, rewrite, edit, adapt, or decompose a promp'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Always instruct the user to attach the reference image to the tool first. Then build the prompt around the delta only — what changes, what stays the same.' in text, "expected to find: " + 'Always instruct the user to attach the reference image to the tool first. Then build the prompt around the delta only — what changes, what stays the same.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Node-based workflow, not a single prompt box. Ask which checkpoint model is loaded (SD 1.5, SDXL, Flux) before writing — prompt syntax changes per model.' in text, "expected to find: " + 'Node-based workflow, not a single prompt box. Ask which checkpoint model is loaded (SD 1.5, SDXL, Flux) before writing — prompt syntax changes per model.'[:80]

