"""Behavioral checks for spring-ai-alibaba-feat-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spring-ai-alibaba")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Spring AI Alibaba is a production-ready framework for building Agentic, Workflow, and Multi-agent applications. It is an implementation of the Spring AI framework tailored for Alibaba Cloud services a' in text, "expected to find: " + 'Spring AI Alibaba is a production-ready framework for building Agentic, Workflow, and Multi-agent applications. It is an implementation of the Spring AI framework tailored for Alibaba Cloud services a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '5.  **Structure**: When adding new features, prefer creating or updating modules within `spring-ai-alibaba-agent-framework` or `spring-boot-starters` depending on the scope.' in text, "expected to find: " + '5.  **Structure**: When adding new features, prefer creating or updating modules within `spring-ai-alibaba-agent-framework` or `spring-boot-starters` depending on the scope.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Graph Core**: Underlying engine for stateful agents, supporting persistence (PostgreSQL, MySQL, Oracle, MongoDB, Redis, File).' in text, "expected to find: " + '- **Graph Core**: Underlying engine for stateful agents, supporting persistence (PostgreSQL, MySQL, Oracle, MongoDB, Redis, File).'[:80]

