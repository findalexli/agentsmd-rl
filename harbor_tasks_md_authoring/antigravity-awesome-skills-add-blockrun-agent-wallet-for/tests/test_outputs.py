"""Behavioral checks for antigravity-awesome-skills-add-blockrun-agent-wallet-for (markdown_authoring task).

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
    text = _read('skills/blockrun/SKILL.md')
    assert 'description: Use when user needs capabilities Claude lacks (image generation, real-time X/Twitter data) or explicitly requests external models ("blockrun", "use grok", "use gpt", "dall-e", "deepseek")' in text, "expected to find: " + 'description: Use when user needs capabilities Claude lacks (image generation, real-time X/Twitter data) or explicitly requests external models ("blockrun", "use grok", "use gpt", "dall-e", "deepseek")'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blockrun/SKILL.md')
    assert '**How it works:** BlockRun uses x402 micropayments to route your requests to OpenAI, xAI, Google, and other providers. No API keys needed - your wallet pays per token.' in text, "expected to find: " + '**How it works:** BlockRun uses x402 micropayments to route your requests to OpenAI, xAI, Google, and other providers. No API keys needed - your wallet pays per token.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blockrun/SKILL.md')
    assert '| User explicitly requests ("blockrun second opinion with GPT on...", "use grok to check...", "generate image with dall-e") | Execute via BlockRun |' in text, "expected to find: " + '| User explicitly requests ("blockrun second opinion with GPT on...", "use grok to check...", "generate image with dall-e") | Execute via BlockRun |'[:80]

