"""Behavioral checks for phoenix-feat-add-phoenixciskillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phoenix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-cli/SKILL.md')
    assert 'description: Debug LLM applications using the Phoenix CLI. Fetch traces, analyze errors, review experiments, and inspect datasets. Use when debugging AI/LLM applications, analyzing trace data, working' in text, "expected to find: " + 'description: Debug LLM applications using the Phoenix CLI. Fetch traces, analyze errors, review experiments, and inspect datasets. Use when debugging AI/LLM applications, analyzing trace data, working'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-cli/SKILL.md')
    assert 'jq -r \'.[].spans[] | select(.span_kind == "LLM") | {model: .attributes["llm.model_name"], prompt_tokens: .attributes["llm.token_count.prompt"], completion_tokens: .attributes["llm.token_count.completi' in text, "expected to find: " + 'jq -r \'.[].spans[] | select(.span_kind == "LLM") | {model: .attributes["llm.model_name"], prompt_tokens: .attributes["llm.token_count.prompt"], completion_tokens: .attributes["llm.token_count.completi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-cli/SKILL.md')
    assert "px trace <trace-id> --format raw | jq '.spans | sort_by(-.duration_ms) | .[0:5] | .[] | {name, duration_ms, span_kind}'" in text, "expected to find: " + "px trace <trace-id> --format raw | jq '.spans | sort_by(-.duration_ms) | .[0:5] | .[] | {name, duration_ms, span_kind}'"[:80]

