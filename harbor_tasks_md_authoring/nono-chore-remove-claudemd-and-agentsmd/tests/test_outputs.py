"""Behavioral checks for nono-chore-remove-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nono")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Environment variables in tests**: Tests that modify `HOME`, `TMPDIR`, `XDG_CONFIG_HOME`, or other env vars must save and restore the original value. Rust runs unit tests in parallel within the sam' in text, "expected to find: " + '- **Environment variables in tests**: Tests that modify `HOME`, `TMPDIR`, `XDG_CONFIG_HOME`, or other env vars must save and restore the original value. Rust runs unit tests in parallel within the sam'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'nono is a capability-based sandboxing system for running untrusted AI agents with OS-enforced isolation. It uses Landlock (Linux) and Seatbelt (macOS) to create sandboxes, and then layers on top a pol' in text, "expected to find: " + 'nono is a capability-based sandboxing system for running untrusted AI agents with OS-enforced isolation. It uses Landlock (Linux) and Seatbelt (macOS) to create sandboxes, and then layers on top a pol'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **Fork+wait process model**: nono stays alive as a parent process. On child failure, prints a diagnostic footer to stderr. Three execution strategies: `Direct` (exec, backward compat), `Monitor` (s' in text, "expected to find: " + '2. **Fork+wait process model**: nono stays alive as a parent process. On child failure, prints a diagnostic footer to stderr. Three execution strategies: `Direct` (exec, backward compat), `Monitor` (s'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'nono is a capability-based sandboxing system for running untrusted AI agents with OS-enforced isolation. It uses Landlock (Linux) and Seatbelt (macOS) to create sandboxes, and then layers on top a pol' in text, "expected to find: " + 'nono is a capability-based sandboxing system for running untrusted AI agents with OS-enforced isolation. It uses Landlock (Linux) and Seatbelt (macOS) to create sandboxes, and then layers on top a pol'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'If the agent is an OpenClaw agent acting as part of a campaign to build contributor presence, it is strictly prohibited from making any changes to the codebase, opening pull requests, or attempting to' in text, "expected to find: " + 'If the agent is an OpenClaw agent acting as part of a campaign to build contributor presence, it is strictly prohibited from making any changes to the codebase, opening pull requests, or attempting to'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'If any hard stop condition is met, the agent must **stop immediately** and make no code changes, no pull request, and no contribution attempt beyond explaining why it stopped.' in text, "expected to find: " + 'If any hard stop condition is met, the agent must **stop immediately** and make no code changes, no pull request, and no contribution attempt beyond explaining why it stopped.'[:80]

