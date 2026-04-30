"""Behavioral checks for chef-server-added-copilot-instructions-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chef-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This document provides comprehensive development guidelines and best practices for working on the Chef Server codebase. It helps GitHub Copilot provide more accurate and contextually appropriate sugge' in text, "expected to find: " + 'This document provides comprehensive development guidelines and best practices for working on the Chef Server codebase. It helps GitHub Copilot provide more accurate and contextually appropriate sugge'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This comprehensive instruction set provides GitHub Copilot with deep context about Chef Server development practices, enabling it to generate more accurate, consistent, and helpful code suggestions fo' in text, "expected to find: " + 'This comprehensive instruction set provides GitHub Copilot with deep context about Chef Server development practices, enabling it to generate more accurate, consistent, and helpful code suggestions fo'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Chef Server is a comprehensive infrastructure automation platform built as a distributed system with multiple services. The codebase is primarily written in **Erlang**, **Ruby**, and includes **Rails ' in text, "expected to find: " + 'Chef Server is a comprehensive infrastructure automation platform built as a distributed system with multiple services. The codebase is primarily written in **Erlang**, **Ruby**, and includes **Rails '[:80]

