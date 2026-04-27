"""Behavioral checks for teamcity-cli-docs-add-agentsmd-with-issuefiling (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/teamcity-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Follow the template structure exactly.** Fill in each section as defined in the YAML' in text, "expected to find: " + '- **Follow the template structure exactly.** Fill in each section as defined in the YAML'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Verify labels exist before using them.** Templates declare labels (e.g. `eval`) that' in text, "expected to find: " + '- **Verify labels exist before using them.** Templates declare labels (e.g. `eval`) that'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'fields. Do not add extra sections, root-cause analysis, or fix suggestions unless the' in text, "expected to find: " + 'fields. Do not add extra sections, root-cause analysis, or fix suggestions unless the'[:80]

