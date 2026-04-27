"""Behavioral checks for compound-engineering-plugin-featdocumentreview-add-headless- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/document-review/SKILL.md')
    assert 'Check the skill arguments for `mode:headless`. Arguments may contain a document path, `mode:headless`, or both. Tokens starting with `mode:` are flags, not file paths -- strip them from the arguments ' in text, "expected to find: " + 'Check the skill arguments for `mode:headless`. Arguments may contain a document path, `mode:headless`, or both. Tokens starting with `mode:` are flags, not file paths -- strip them from the arguments '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/document-review/SKILL.md')
    assert '**Headless mode** changes the interaction model, not the classification boundaries. Document-review still applies the same judgment about what is deterministic vs. what needs verification. The only di' in text, "expected to find: " + '**Headless mode** changes the interaction model, not the classification boundaries. Document-review still applies the same judgment about what is deterministic vs. what needs verification. The only di'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/document-review/SKILL.md')
    assert '**Headless mode:** Do not prompt. Include `batch_confirm` findings in the structured text output alongside `present` findings, clearly marked with their classification so the caller can distinguish th' in text, "expected to find: " + '**Headless mode:** Do not prompt. Include `batch_confirm` findings in the structured text output alongside `present` findings, clearly marked with their classification so the caller can distinguish th'[:80]

