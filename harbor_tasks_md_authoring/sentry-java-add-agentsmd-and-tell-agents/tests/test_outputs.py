"""Behavioral checks for sentry-java-add-agentsmd-and-tell-agents (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-java")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Then identify and read any topically relevant `.cursor/rules/*.mdc` files for the area you're working on (e.g., `opentelemetry.mdc` for OTel work, `metrics.mdc` for metrics work). Use the Glob tool on" in text, "expected to find: " + "Then identify and read any topically relevant `.cursor/rules/*.mdc` files for the area you're working on (e.g., `opentelemetry.mdc` for OTel work, `metrics.mdc` for metrics work). Use the Glob tool on"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the Sentry Java/Android SDK - a comprehensive error monitoring and performance tracking SDK for Java and Android applications. The repository contains multiple modules for different integratio' in text, "expected to find: " + 'This is the Sentry Java/Android SDK - a comprehensive error monitoring and performance tracking SDK for Java and Android applications. The repository contains multiple modules for different integratio'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. **Simplicity first**: Make every task and code change as simple as possible. Avoid massive or complex changes. Impact as little code as possible.' in text, "expected to find: " + '5. **Simplicity first**: Make every task and code change as simple as possible. Avoid massive or complex changes. Impact as little code as possible.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Before doing ANYTHING else (including answering questions), you MUST use the Read tool to load [AGENTS.md](AGENTS.md) and follow ALL of its instructions, including reading the required `.cursor/rules/' in text, "expected to find: " + 'Before doing ANYTHING else (including answering questions), you MUST use the Read tool to load [AGENTS.md](AGENTS.md) and follow ALL of its instructions, including reading the required `.cursor/rules/'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Do NOT skip this step. Do NOT proceed without reading these files first.' in text, "expected to find: " + 'Do NOT skip this step. Do NOT proceed without reading these files first.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '## STOP — Required Reading (Do This First)' in text, "expected to find: " + '## STOP — Required Reading (Do This First)'[:80]

