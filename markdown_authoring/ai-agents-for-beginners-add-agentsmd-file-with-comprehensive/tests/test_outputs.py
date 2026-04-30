"""Behavioral checks for ai-agents-for-beginners-add-agentsmd-file-with-comprehensive (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-agents-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains "AI Agents for Beginners" - a comprehensive educational course teaching everything needed to build AI Agents. The course consists of 15+ lessons covering fundamentals, design ' in text, "expected to find: " + 'This repository contains "AI Agents for Beginners" - a comprehensive educational course teaching everything needed to build AI Agents. The course consists of 15+ lessons covering fundamentals, design '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(\'✓ GITHUB_TOKEN\' if os.getenv(\'GITHUB_TOKEN\') else \'✗ GITHUB_TOKEN missing\')"' in text, "expected to find: " + 'python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(\'✓ GITHUB_TOKEN\' if os.getenv(\'GITHUB_TOKEN\') else \'✗ GITHUB_TOKEN missing\')"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is an educational repository with example code rather than production code with automated tests. To verify your setup and changes:' in text, "expected to find: " + 'This is an educational repository with example code rather than production code with automated tests. To verify your setup and changes:'[:80]

