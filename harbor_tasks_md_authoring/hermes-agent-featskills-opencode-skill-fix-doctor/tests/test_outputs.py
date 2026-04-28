"""Behavioral checks for hermes-agent-featskills-opencode-skill-fix-doctor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hermes-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/autonomous-ai-agents/opencode/SKILL.md')
    assert 'terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run \'Review this PR vs main. Report bugs, security risks, test gaps, and style iss' in text, "expected to find: " + 'terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run \'Review this PR vs main. Report bugs, security risks, test gaps, and style iss'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/autonomous-ai-agents/opencode/SKILL.md')
    assert 'description: Delegate coding tasks to OpenCode CLI agent for feature implementation, refactoring, PR review, and long-running autonomous sessions. Requires the opencode CLI installed and authenticated' in text, "expected to find: " + 'description: Delegate coding tasks to OpenCode CLI agent for feature implementation, refactoring, PR review, and long-running autonomous sessions. Requires the opencode CLI installed and authenticated'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/autonomous-ai-agents/opencode/SKILL.md')
    assert 'Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.' in text, "expected to find: " + 'Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.'[:80]

