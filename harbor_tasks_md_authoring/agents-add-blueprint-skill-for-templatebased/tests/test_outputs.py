"""Behavioral checks for agents-add-blueprint-skill-for-templatebased (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blueprint/SKILL.md')
    assert 'description: Define reusable Airflow task group templates with Pydantic validation and compose DAGs from YAML. Use when creating blueprint templates, composing DAGs from YAML, validating configuration' in text, "expected to find: " + 'description: Define reusable Airflow task group templates with Pydantic validation and compose DAGs from YAML. Use when creating blueprint templates, composing DAGs from YAML, validating configuration'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blueprint/SKILL.md')
    assert 'You are helping a user work with Blueprint, a system for composing Airflow DAGs from YAML using reusable Python templates. Execute steps in order and prefer the simplest configuration that meets the u' in text, "expected to find: " + 'You are helping a user work with Blueprint, a system for composing Airflow DAGs from YAML using reusable Python templates. Execute steps in order and prefer the simplest configuration that meets the u'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blueprint/SKILL.md')
    assert 'The Astro IDE reads `blueprint/generated-schemas/` to render configuration forms. Keeping schemas in sync ensures the visual builder always reflects the latest blueprint configs.' in text, "expected to find: " + 'The Astro IDE reads `blueprint/generated-schemas/` to render configuration forms. Keeping schemas in sync ensures the visual builder always reflects the latest blueprint configs.'[:80]

