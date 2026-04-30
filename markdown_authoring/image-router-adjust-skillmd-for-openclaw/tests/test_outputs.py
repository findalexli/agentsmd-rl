"""Behavioral checks for image-router-adjust-skillmd-for-openclaw (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/image-router")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- **Do not paste API keys into chat**. Set the env var in the OpenClaw Gateway environment (in terminal) and restart the gateway. Example:' in text, "expected to find: " + '- **Do not paste API keys into chat**. Set the env var in the OpenClaw Gateway environment (in terminal) and restart the gateway. Example:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'metadata: {"openclaw":{"emoji":"🎨","requires":{"bins":["curl"]},"primaryEnv":"IMAGEROUTER_API_KEY"}}' in text, "expected to find: " + 'metadata: {"openclaw":{"emoji":"🎨","requires":{"bins":["curl"]},"primaryEnv":"IMAGEROUTER_API_KEY"}}'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- This skill expects your ImageRouter key in the environment variable `IMAGEROUTER_API_KEY`.' in text, "expected to find: " + '- This skill expects your ImageRouter key in the environment variable `IMAGEROUTER_API_KEY`.'[:80]

