"""Behavioral checks for glimpse-docs-add-claudemd-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/glimpse")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Glimpse is a fast Rust CLI tool for extracting codebase content into LLM-friendly formats. It's designed to help users prepare source code for loading into Large Language Models with built-in token co" in text, "expected to find: " + "Glimpse is a fast Rust CLI tool for extracting codebase content into LLM-friendly formats. It's designed to help users prepare source code for loading into Large Language Models with built-in token co"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Edit `languages.yml` to add extensions, filenames, or interpreters. The build script will regenerate detection code automatically.' in text, "expected to find: " + 'Edit `languages.yml` to add extensions, filenames, or interpreters. The build script will regenerate detection code automatically.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. Global config: `~/.config/glimpse/config.toml` (Linux/macOS) or `%APPDATA%\\glimpse\\config.toml` (Windows)' in text, "expected to find: " + '1. Global config: `~/.config/glimpse/config.toml` (Linux/macOS) or `%APPDATA%\\glimpse\\config.toml` (Windows)'[:80]

