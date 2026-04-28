"""Behavioral checks for templates-docs-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/templates")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For reference, example templates using the provider `exampleservice.domainconnect.org` are available in this repository. These templates demonstrate proper structure and can be used as a starting poin' in text, "expected to find: " + 'For reference, example templates using the provider `exampleservice.domainconnect.org` are available in this repository. These templates demonstrate proper structure and can be used as a starting poin'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The template file schema is defined in [`template.schema`](template.schema). This schema **MUST be followed** for all template files.' in text, "expected to find: " + 'The template file schema is defined in [`template.schema`](template.schema). This schema **MUST be followed** for all template files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **Note:** If `dc-template-linter` returns a non-zero exit value, the template is invalid and must be corrected before submission.' in text, "expected to find: " + '> **Note:** If `dc-template-linter` returns a non-zero exit value, the template is invalid and must be corrected before submission.'[:80]

