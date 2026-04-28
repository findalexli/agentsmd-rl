"""Behavioral checks for podman-initial-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/podman")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document is specifically designed for AI coding assistants (like Claude, ChatGPT, Copilot) to provide context and guidance when helping developers with Podman-related tasks. It contains essential' in text, "expected to find: " + 'This document is specifically designed for AI coding assistants (like Claude, ChatGPT, Copilot) to provide context and guidance when helping developers with Podman-related tasks. It contains essential'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Integration Tests** (`test/e2e/`): Test Podman CLI commands end-to-end, using actual binaries and real containers. Use for testing user-facing functionality and CLI behavior.' in text, "expected to find: " + '**Integration Tests** (`test/e2e/`): Test Podman CLI commands end-to-end, using actual binaries and real containers. Use for testing user-facing functionality and CLI behavior.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**System Tests** (`test/system/`): Test Podman in realistic environments with shell scripts. Use for testing complex scenarios, multi-command workflows, and system integration.' in text, "expected to find: " + '**System Tests** (`test/system/`): Test Podman in realistic environments with shell scripts. Use for testing complex scenarios, multi-command workflows, and system integration.'[:80]

