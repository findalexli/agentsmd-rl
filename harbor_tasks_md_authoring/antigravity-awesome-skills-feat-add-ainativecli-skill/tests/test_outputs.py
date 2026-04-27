"""Behavioral checks for antigravity-awesome-skills-feat-add-ainativecli-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-native-cli/SKILL.md')
    assert 'description: "Design spec with 98 rules for building CLI tools that AI agents can safely use. Covers structured JSON output, error handling, input contracts, safety guardrails, exit codes, and agent s' in text, "expected to find: " + 'description: "Design spec with 98 rules for building CLI tools that AI agents can safely use. Covers structured JSON output, error handling, input contracts, safety guardrails, exit codes, and agent s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-native-cli/SKILL.md')
    assert 'Goal: CLI has identity, behavior contract, skill system, and feedback loop. Agent can learn the tool, extend its use, and report problems -- full closed-loop collaboration.' in text, "expected to find: " + 'Goal: CLI has identity, behavior contract, skill system, and feedback loop. Agent can learn the tool, extend its use, and report problems -- full closed-loop collaboration.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-native-cli/SKILL.md')
    assert 'Goal: CLI is self-describing, well-named, and pipe-friendly. Agent discovers capabilities and chains commands without trial and error.' in text, "expected to find: " + 'Goal: CLI is self-describing, well-named, and pipe-friendly. Agent discovers capabilities and chains commands without trial and error.'[:80]

