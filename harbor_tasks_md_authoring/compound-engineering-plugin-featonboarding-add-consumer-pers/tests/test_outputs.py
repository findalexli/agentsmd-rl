"""Behavioral checks for compound-engineering-plugin-featonboarding-add-consumer-pers (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/onboarding/SKILL.md')
    assert 'Before a contributor can reason about architecture, they need to understand what the project *does* from the outside. This section bridges "what is this" (Section 1) and "how is it built" (Section 3).' in text, "expected to find: " + 'Before a contributor can reason about architecture, they need to understand what the project *does* from the outside. This section bridges "what is this" (Section 1) and "how is it built" (Section 3).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/onboarding/SKILL.md')
    assert '- **Developer tool** (SDK, library, dev CLI, framework) -- Title: **"Developer Experience"**. Describe how a developer consumes the tool: installation, a minimal usage example showing the primary API ' in text, "expected to find: " + '- **Developer tool** (SDK, library, dev CLI, framework) -- Title: **"Developer Experience"**. Describe how a developer consumes the tool: installation, a minimal usage example showing the primary API '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/onboarding/SKILL.md')
    assert '1. **Architecture diagram** -- Components, how they connect, and what protocols or transports they use. A developer looks at this to understand where code lives and how pieces talk to each other. Labe' in text, "expected to find: " + '1. **Architecture diagram** -- Components, how they connect, and what protocols or transports they use. A developer looks at this to understand where code lives and how pieces talk to each other. Labe'[:80]

