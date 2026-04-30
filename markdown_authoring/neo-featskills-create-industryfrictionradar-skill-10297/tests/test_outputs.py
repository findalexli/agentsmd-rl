"""Behavioral checks for neo-featskills-create-industryfrictionradar-skill-10297 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/industry-friction-radar/SKILL.md')
    assert 'If you are tasked with executing an industry friction radar scan, you MUST immediately use the `view_file` tool to read and strictly adhere to `.agent/skills/industry-friction-radar/references/industr' in text, "expected to find: " + 'If you are tasked with executing an industry friction radar scan, you MUST immediately use the `view_file` tool to read and strictly adhere to `.agent/skills/industry-friction-radar/references/industr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/industry-friction-radar/SKILL.md')
    assert 'triggers: Use this skill when executing periodic "horizon scans" for the Dream Pipeline, researching external solutions to deeply complex engine-level friction points, or evaluating JS ecosystem trend' in text, "expected to find: " + 'triggers: Use this skill when executing periodic "horizon scans" for the Dream Pipeline, researching external solutions to deeply complex engine-level friction points, or evaluating JS ecosystem trend'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/industry-friction-radar/SKILL.md')
    assert 'description: Proactive SOTA research loop using a strict 3-step abstraction protocol to extract engine-category friction points without importing framework-category bias or stealing code.' in text, "expected to find: " + 'description: Proactive SOTA research loop using a strict 3-step abstraction protocol to extract engine-category friction points without importing framework-category bias or stealing code.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/industry-friction-radar/references/industry-friction-radar-workflow.md')
    assert "**Anchor Summary:** This protocol governs the Neo organism's external sensory organ. It defines a strict 3-step abstraction pipeline required to systematically ingest State of the Art (SOTA) industry " in text, "expected to find: " + "**Anchor Summary:** This protocol governs the Neo organism's external sensory organ. It defines a strict 3-step abstraction pipeline required to systematically ingest State of the Art (SOTA) industry "[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/industry-friction-radar/references/industry-friction-radar-workflow.md')
    assert '- **Attribution:** The resulting GitHub Discussion MUST include an Author\'s Note citing the provenance of the friction point, using the `citations` array from Step 2. (e.g., *"External friction observ' in text, "expected to find: " + '- **Attribution:** The resulting GitHub Discussion MUST include an Author\'s Note citing the provenance of the friction point, using the `citations` array from Step 2. (e.g., *"External friction observ'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/industry-friction-radar/references/industry-friction-radar-workflow.md')
    assert '- ✅ **Prioritize Engine-Category Signal:** New ECMAScript native features (e.g., native typing), SharedArrayBuffer memory management, zero-allocation math, WebGPU compute, continuous-simulation in Wor' in text, "expected to find: " + '- ✅ **Prioritize Engine-Category Signal:** New ECMAScript native features (e.g., native typing), SharedArrayBuffer memory management, zero-allocation math, WebGPU compute, continuous-simulation in Wor'[:80]

