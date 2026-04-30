"""Behavioral checks for pulumi-terraform-bridge-add-claudemd-for-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pulumi-terraform-bridge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The codebase follows Go conventions with gRPC for provider communication and supports creating new bridged providers from existing Terraform providers.' in text, "expected to find: " + 'The codebase follows Go conventions with gRPC for provider communication and supports creating new bridged providers from existing Terraform providers.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is the Pulumi Terraform Bridge, which adapts Terraform Providers for use with Pulumi. The codebase consists of:' in text, "expected to find: " + 'This is the Pulumi Terraform Bridge, which adapts Terraform Providers for use with Pulumi. The codebase consists of:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]

