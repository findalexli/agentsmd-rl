"""Behavioral checks for wp-calypso-agentsmd-restructure-root-and-client (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wp-calypso")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Image Studio** (`packages/image-studio`) — AI-powered image editing and generation' in text, "expected to find: " + '- **Image Studio** (`packages/image-studio`) — AI-powered image editing and generation'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('client/AGENTS.md')
    assert '- Dialog buttons on mobile: `.dialog__action-buttons` flips to `flex-direction: column-reverse` below `$break-mobile`. Flex labels inside buttons need `width: 100%` for `justify-content: center` to wo' in text, "expected to find: " + '- Dialog buttons on mobile: `.dialog__action-buttons` flips to `flex-direction: column-reverse` below `$break-mobile`. Flex labels inside buttons need `width: 100%` for `justify-content: center` to wo'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('client/AGENTS.md')
    assert '- Classic Calypso (`client/me/`, `client/my-sites/`) uses Redux + page.js routing.' in text, "expected to find: " + '- Classic Calypso (`client/me/`, `client/my-sites/`) uses Redux + page.js routing.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('client/AGENTS.md')
    assert '- Avoid `__experimental*` components unless already used in the codebase.' in text, "expected to find: " + '- Avoid `__experimental*` components unless already used in the codebase.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/image-studio/AGENTS.md')
    assert '# Image Studio' in text, "expected to find: " + '# Image Studio'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/image-studio/CLAUDE.md')
    assert 'packages/image-studio/CLAUDE.md' in text, "expected to find: " + 'packages/image-studio/CLAUDE.md'[:80]

