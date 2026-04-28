"""Behavioral checks for airframe-doc-add-claudemd-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/airframe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is a multi-module sbt project using Scala 3 as the default version, with cross-building support for Scala 2.12, 2.13, and Scala Native/JS platforms.' in text, "expected to find: " + 'This is a multi-module sbt project using Scala 3 as the default version, with cross-building support for Scala 2.12, 2.13, and Scala Native/JS platforms.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Airframe is a collection of essential building blocks for developing applications in Scala, including:' in text, "expected to find: " + 'Airframe is a collection of essential building blocks for developing applications in Scala, including:'[:80]

