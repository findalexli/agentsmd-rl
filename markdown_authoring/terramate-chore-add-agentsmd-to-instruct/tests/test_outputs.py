"""Behavioral checks for terramate-chore-add-agentsmd-to-instruct (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/terramate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Terramate** is an orchestration, code generation, and change management tool for Infrastructure as Code (IaC), with first-class support for Terraform, OpenTofu, and Terragrunt.' in text, "expected to find: " + '**Terramate** is an orchestration, code generation, and change management tool for Infrastructure as Code (IaC), with first-class support for Terraform, OpenTofu, and Terragrunt.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **`global.*`** - Global variables (can be defined in parent directories, imported files, labeled blocks)' in text, "expected to find: " + '1. **`global.*`** - Global variables (can be defined in parent directories, imported files, labeled blocks)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Naming**: Use descriptive names, avoid abbreviations except common ones (e.g., `ctx`, `err`)' in text, "expected to find: " + '- **Naming**: Use descriptive names, avoid abbreviations except common ones (e.g., `ctx`, `err`)'[:80]

