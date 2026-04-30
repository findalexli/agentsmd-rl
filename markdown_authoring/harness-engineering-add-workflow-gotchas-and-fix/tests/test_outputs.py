"""Behavioral checks for harness-engineering-add-workflow-gotchas-and-fix (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/harness-engineering")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **Two sets of generate-docs**: `scripts/repo-generate-docs.js` is this repo's auto-doc (scans `skills/`, `scripts/`, `tests/`). `skills/setup/scripts/lib/generate-docs.js` is the template installed " in text, "expected to find: " + "- **Two sets of generate-docs**: `scripts/repo-generate-docs.js` is this repo's auto-doc (scans `skills/`, `scripts/`, `tests/`). `skills/setup/scripts/lib/generate-docs.js` is the template installed "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Setup has two code paths**: Node/TS uses the "fast path" (scripts do the work). All other stacks use the "adaptive path" (Claude creates files). The eval uses `conversation_must_not_mention` to ca' in text, "expected to find: " + '- **Setup has two code paths**: Node/TS uses the "fast path" (scripts do the work). All other stacks use the "adaptive path" (Claude creates files). The eval uses `conversation_must_not_mention` to ca'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- **CLAUDE.md auto-updates on commit**: The pre-commit hook runs `repo-generate-docs.js` to regenerate AUTO markers. Don't manually edit content between `<!-- AUTO:tree -->` and `<!-- AUTO:modules -->" in text, "expected to find: " + "- **CLAUDE.md auto-updates on commit**: The pre-commit hook runs `repo-generate-docs.js` to regenerate AUTO markers. Don't manually edit content between `<!-- AUTO:tree -->` and `<!-- AUTO:modules -->"[:80]

