"""Behavioral checks for docker-otel-lgtm-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docker-otel-lgtm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Go code uses `.golangci.yaml` config. Markdown uses `.markdownlint.yaml`. EditorConfig rules in `.editorconfig`.' in text, "expected to find: " + 'Go code uses `.golangci.yaml` config. Markdown uses `.markdownlint.yaml`. EditorConfig rules in `.editorconfig`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`docker/otelcol-config-export-http.yaml` (external export). To test the merged' in text, "expected to find: " + '`docker/otelcol-config-export-http.yaml` (external export). To test the merged'[:80]

