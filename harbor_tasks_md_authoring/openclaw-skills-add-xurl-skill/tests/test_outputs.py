"""Behavioral checks for openclaw-skills-add-xurl-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/xurl/SKILL.md')
    assert 'description: A CLI tool for making authenticated requests to the X (Twitter) API. Use this skill when you need to post tweets, reply, quote, search, read posts, manage followers, send DMs, upload medi' in text, "expected to find: " + 'description: A CLI tool for making authenticated requests to the X (Twitter) API. Use this skill when you need to post tweets, reply, quote, search, read posts, manage followers, send DMs, upload medi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/xurl/SKILL.md')
    assert 'Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated tokens. Do not read this file through the agent/LLM. Once authenticated, every command below will auto‑attach the right ' in text, "expected to find: " + 'Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated tokens. Do not read this file through the agent/LLM. Once authenticated, every command below will auto‑attach the right '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/xurl/SKILL.md')
    assert '`xurl` is a CLI tool for the X API. It supports both **shortcut commands** (human/agent‑friendly one‑liners) and **raw curl‑style** access to any v2 endpoint. All commands return JSON to stdout.' in text, "expected to find: " + '`xurl` is a CLI tool for the X API. It supports both **shortcut commands** (human/agent‑friendly one‑liners) and **raw curl‑style** access to any v2 endpoint. All commands return JSON to stdout.'[:80]

