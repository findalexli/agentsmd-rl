"""Behavioral checks for genlayer-studio-chore-add-claude-code-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/genlayer-studio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/argocd-debug/SKILL.md')
    assert '.claude/skills/argocd-debug/SKILL.md' in text, "expected to find: " + '.claude/skills/argocd-debug/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/discord-community-feedback/SKILL.md')
    assert 'argocd app logs studio-prd-workload --name studio-consensus-worker --tail 500 2>&1 | grep -iE "(error|exception|timeout)"' in text, "expected to find: " + 'argocd app logs studio-prd-workload --name studio-consensus-worker --tail 500 2>&1 | grep -iE "(error|exception|timeout)"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/discord-community-feedback/SKILL.md')
    assert 'Monitor the GenLayer Discord community feedback channel for user-reported bugs, issues, and problems.' in text, "expected to find: " + 'Monitor the GenLayer Discord community feedback channel for user-reported bugs, issues, and problems.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/discord-community-feedback/SKILL.md')
    assert '- Discord MCP server configured and running ([discordmcp](https://github.com/v-3/discordmcp))' in text, "expected to find: " + '- Discord MCP server configured and running ([discordmcp](https://github.com/v-3/discordmcp))'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hosted-studio-debug/SKILL.md')
    assert '**Important:** The `argocd app logs --name <container>` command automatically aggregates logs from ALL pod replicas. This ensures full visibility across the entire deployment.' in text, "expected to find: " + '**Important:** The `argocd app logs --name <container>` command automatically aggregates logs from ALL pod replicas. This ensures full visibility across the entire deployment.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hosted-studio-debug/SKILL.md')
    assert '**Note:** When debugging, always check logs from ALL replicas to get complete visibility. The `argocd app logs --name <container>` command handles this automatically.' in text, "expected to find: " + '**Note:** When debugging, always check logs from ALL replicas to get complete visibility. The `argocd app logs --name <container>` command handles this automatically.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hosted-studio-debug/SKILL.md')
    assert 'argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(timeout|SocketTimeoutError|127.0.0.1:3999)"' in text, "expected to find: " + 'argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(timeout|SocketTimeoutError|127.0.0.1:3999)"'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/integration-tests/SKILL.md')
    assert 'source .venv/bin/activate && export PYTHONPATH="$(pwd)" && gltest --contracts-dir . tests/integration --leader-only' in text, "expected to find: " + 'source .venv/bin/activate && export PYTHONPATH="$(pwd)" && gltest --contracts-dir . tests/integration --leader-only'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/integration-tests/SKILL.md')
    assert 'source .venv/bin/activate && export PYTHONPATH="$(pwd)" && gltest --contracts-dir . tests/integration' in text, "expected to find: " + 'source .venv/bin/activate && export PYTHONPATH="$(pwd)" && gltest --contracts-dir . tests/integration'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/integration-tests/SKILL.md')
    assert 'Setup the Python environment, start the studio, and run integration tests for GenLayer Studio.' in text, "expected to find: " + 'Setup the Python environment, start the studio, and run integration tests for GenLayer Studio.'[:80]

