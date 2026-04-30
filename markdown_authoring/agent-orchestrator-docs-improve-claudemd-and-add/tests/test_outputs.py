"""Behavioral checks for agent-orchestrator-docs-improve-claudemd-and-add (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-orchestrator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Open-source system for orchestrating parallel AI coding agents. Agent-agnostic (Claude Code, Codex, Aider), runtime-agnostic (tmux, docker, k8s), tracker-agnostic (GitHub, Linear, Jira). Manages sessi' in text, "expected to find: " + 'Open-source system for orchestrating parallel AI coding agents. Agent-agnostic (Claude Code, Codex, Aider), runtime-agnostic (tmux, docker, k8s), tracker-agnostic (GitHub, Linear, Jira). Manages sessi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'TypeScript (ESM), Node 20+, pnpm workspaces. Next.js 15 (App Router) + Tailwind. Commander.js CLI. YAML + Zod config. Server-Sent Events for real-time. Flat metadata files + JSONL event log. ESLint + ' in text, "expected to find: " + 'TypeScript (ESM), Node 20+, pnpm workspaces. Next.js 15 (App Router) + Tailwind. Commander.js CLI. YAML + Zod config. Server-Sent Events for real-time. Flat metadata files + JSONL event log. ESLint + '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Config loaded from `agent-orchestrator.yaml` (see `agent-orchestrator.yaml.example`). Paths support `~` expansion. Validated with Zod at load time. Per-project overrides for plugins and reactions.' in text, "expected to find: " + 'Config loaded from `agent-orchestrator.yaml` (see `agent-orchestrator.yaml.example`). Paths support `~` expansion. Validated with Zod at load time. Per-project overrides for plugins and reactions.'[:80]

