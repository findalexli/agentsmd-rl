"""Behavioral checks for slack-gamebot-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/slack-gamebot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* YYYY/MM/DD: Description of change - [@dblock](https://github.com/dblock), [@Copilot](https://github.com/apps/copilot-swe-agent).' in text, "expected to find: " + '* YYYY/MM/DD: Description of change - [@dblock](https://github.com/dblock), [@Copilot](https://github.com/apps/copilot-swe-agent).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Update [CHANGELOG.md](CHANGELOG.md) for any user-facing change. Add a line at the top under `### Changelog` in the format:' in text, "expected to find: " + 'Update [CHANGELOG.md](CHANGELOG.md) for any user-facing change. Add a line at the top under `### Changelog` in the format:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Ruby style is enforced via RuboCop (`.rubocop.yml`). Persistent exceptions live in `.rubocop_todo.yml`.' in text, "expected to find: " + '- Ruby style is enforced via RuboCop (`.rubocop.yml`). Persistent exceptions live in `.rubocop_todo.yml`.'[:80]

