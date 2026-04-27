"""Behavioral checks for buildwithclaude-add-tubeify-lobsterdomains-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/lobsterdomains/SKILL.md')
    assert 'Register .com, .xyz, .org and 1000+ ICANN domains with cryptocurrency payments via a simple REST API. Built for AI agents to acquire domains fully autonomously.' in text, "expected to find: " + 'Register .com, .xyz, .org and 1000+ ICANN domains with cryptocurrency payments via a simple REST API. Built for AI agents to acquire domains fully autonomously.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/lobsterdomains/SKILL.md')
    assert 'description: Register ICANN domains with crypto payments (USDC/USDT/ETH/BTC) via API — built for AI agents' in text, "expected to find: " + 'description: Register ICANN domains with crypto payments (USDC/USDT/ETH/BTC) via API — built for AI agents'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/lobsterdomains/SKILL.md')
    assert 'Generate an API key at https://lobsterdomains.xyz/api-keys (requires Ethereum wallet auth).' in text, "expected to find: " + 'Generate an API key at https://lobsterdomains.xyz/api-keys (requires Ethereum wallet auth).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tubeify/SKILL.md')
    assert 'AI-powered video editing for YouTube creators. Submit a raw recording URL, get back a polished, trimmed video automatically — no manual editing required.' in text, "expected to find: " + 'AI-powered video editing for YouTube creators. Submit a raw recording URL, get back a polished, trimmed video automatically — no manual editing required.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tubeify/SKILL.md')
    assert 'description: AI video editor for YouTube — removes pauses, filler words, and dead air from raw recordings via API' in text, "expected to find: " + 'description: AI video editor for YouTube — removes pauses, filler words, and dead air from raw recordings via API'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/tubeify/SKILL.md')
    assert '- User wants to clean up filler words (um, uh, etc.) from a video' in text, "expected to find: " + '- User wants to clean up filler words (um, uh, etc.) from a video'[:80]

