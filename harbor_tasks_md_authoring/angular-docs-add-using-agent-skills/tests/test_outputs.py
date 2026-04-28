"""Behavioral checks for angular-docs-add-using-agent-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/angular")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dev-skills/README.md')
    assert 'Agent Skills are designed to be used with agentic coding tools like [Gemini CLI](https://geminicli.com/docs/cli/skills/), [Antigravity](https://antigravity.google/docs/skills) and more. Activating a s' in text, "expected to find: " + 'Agent Skills are designed to be used with agentic coding tools like [Gemini CLI](https://geminicli.com/docs/cli/skills/), [Antigravity](https://antigravity.google/docs/skills) and more. Activating a s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dev-skills/README.md')
    assert 'To use these skills in your own environment you may follow the instructions for your specific tool or use a community tool like [skills.sh](https://skills.sh/).' in text, "expected to find: " + 'To use these skills in your own environment you may follow the instructions for your specific tool or use a community tool like [skills.sh](https://skills.sh/).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dev-skills/README.md')
    assert 'npx skills add https://github.com/angular/skills' in text, "expected to find: " + 'npx skills add https://github.com/angular/skills'[:80]

