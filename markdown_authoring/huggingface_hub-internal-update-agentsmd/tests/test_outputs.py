"""Behavioral checks for huggingface_hub-internal-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/huggingface-hub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **PR description**: keep it casual. Include a `## Summary` with a few bullet points and real CLI/code **examples** from manual testing (copy-paste terminal output). No need for a formal "Test plan" ' in text, "expected to find: " + '- **PR description**: keep it casual. Include a `## Summary` with a few bullet points and real CLI/code **examples** from manual testing (copy-paste terminal output). No need for a formal "Test plan" '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `out.hint("...")` — actionable follow-up suggestion. Try to add hints when adding new commands or refactoring a command. Hints should preferably reuse the input args to be specific to the current us' in text, "expected to find: " + '- `out.hint("...")` — actionable follow-up suggestion. Try to add hints when adding new commands or refactoring a command. Hints should preferably reuse the input args to be specific to the current us'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Guides**: update the CLI guide `docs/sources/en/guides/cli.md` when adding / updating CLI commands. If the command is specific to a topic which has its own guide in `docs/sources/en/guides`, add a m' in text, "expected to find: " + '**Guides**: update the CLI guide `docs/sources/en/guides/cli.md` when adding / updating CLI commands. If the command is specific to a topic which has its own guide in `docs/sources/en/guides`, add a m'[:80]

