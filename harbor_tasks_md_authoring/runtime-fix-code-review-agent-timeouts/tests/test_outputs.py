"""Behavioral checks for runtime-fix-code-review-agent-timeouts (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/runtime")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/code-review/SKILL.md')
    assert '4. Present a single unified review to the user, noting when an issue was flagged by multiple models. **After posting the review, immediately exit.** Do not wait for any remaining sub-agents. Do not at' in text, "expected to find: " + '4. Present a single unified review to the user, noting when an issue was flagged by multiple models. **After posting the review, immediately exit.** Do not wait for any remaining sub-agents. Do not at'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/code-review/SKILL.md')
    assert '- **Do not use `gpt-5.4`** — it has known reliability issues causing sub-agent timeouts in >90% of affected runs. For the OpenAI/GPT family, prefer `gpt-5.3-codex` if it is explicitly listed as availa' in text, "expected to find: " + '- **Do not use `gpt-5.4`** — it has known reliability issues causing sub-agent timeouts in >90% of affected runs. For the OpenAI/GPT family, prefer `gpt-5.3-codex` if it is explicitly listed as availa'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/code-review/SKILL.md')
    assert '1. Inspect the available model list and select models from 2-3 distinct model families, up to 3 sub-agent models total. If fewer than 2 eligible families are available, use what is available. **Model ' in text, "expected to find: " + '1. Inspect the available model list and select models from 2-3 distinct model families, up to 3 sub-agent models total. If fewer than 2 eligible families are available, use what is available. **Model '[:80]

