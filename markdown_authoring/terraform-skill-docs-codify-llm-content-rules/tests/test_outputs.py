"""Behavioral checks for terraform-skill-docs-codify-llm-content-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/terraform-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**1. Shape — decision table before playbook.** The LLM retrieval path is: classify intent → pick branch → execute. When a topic has multiple viable approaches, open the section with a decision table (' in text, "expected to find: " + '**1. Shape — decision table before playbook.** The LLM retrieval path is: classify intent → pick branch → execute. When a topic has multiple viable approaches, open the section with a decision table ('[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**3. Compress prose → ❌/✅ Rules.** Any sentence starting with "You should...", "Note that...", "Keep in mind...", "It\'s important to..." — rewrite as terse imperative ❌/✅ bullet. One fact per bullet. ' in text, "expected to find: " + '**3. Compress prose → ❌/✅ Rules.** Any sentence starting with "You should...", "Note that...", "Keep in mind...", "It\'s important to..." — rewrite as terse imperative ❌/✅ bullet. One fact per bullet. '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**2. Cut human scaffolding.** Before/after config diffs, "Why this matters" paragraphs, and pedagogical asides are human-only signal. If the phase steps already name the required action, a before/afte' in text, "expected to find: " + '**2. Cut human scaffolding.** Before/after config diffs, "Why this matters" paragraphs, and pedagogical asides are human-only signal. If the phase steps already name the required action, a before/afte'[:80]

