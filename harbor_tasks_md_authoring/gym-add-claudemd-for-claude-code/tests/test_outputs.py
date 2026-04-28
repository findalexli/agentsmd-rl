"""Behavioral checks for gym-add-claudemd-for-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gym")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For wrapping an existing 3rd-party benchmark library, integrate at the agent server level: wrap the library in `/run`, pre-process from Gym schema to library input, post-process back to `BaseVerifyRes' in text, "expected to find: " + 'For wrapping an existing 3rd-party benchmark library, integrate at the agent server level: wrap the library in `/run`, pre-process from Gym schema to library input, post-process back to `BaseVerifyRes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For multi-turn agents, propagate cookies from the incoming request through all downstream calls: `cookies=request.cookies`. Also propagate token IDs (`prompt_token_ids`, `generation_token_ids`, `gener' in text, "expected to find: " + 'For multi-turn agents, propagate cookies from the incoming request through all downstream calls: `cookies=request.cookies`. Also propagate token IDs (`prompt_token_ids`, `generation_token_ids`, `gener'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The `verify()` method receives the model output and `verifier_metadata`, returns a response with `reward` field. The `verifier_metadata` dict is opaque to the framework — define whatever fields your b' in text, "expected to find: " + 'The `verify()` method receives the model output and `verifier_metadata`, returns a response with `reward` field. The `verifier_metadata` dict is opaque to the framework — define whatever fields your b'[:80]

