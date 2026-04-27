"""Behavioral checks for composio-document-file-support-for-cli (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/composio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ts/packages/cli/skills/composio-cli/SKILL.md')
    assert '`composio run` executes an inline ESM JavaScript/Typescript (bun compatible) snippet with authenticated `execute()`, `search()`, `proxy()`, and the experimental `experimental_subAgent()` helper pre-in' in text, "expected to find: " + '`composio run` executes an inline ESM JavaScript/Typescript (bun compatible) snippet with authenticated `execute()`, `search()`, `proxy()`, and the experimental `experimental_subAgent()` helper pre-in'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ts/packages/cli/skills/composio-cli/SKILL.md')
    assert "`--file` injects the local path into the tool's single uploadable file field. If a tool has no uploadable file input, or has more than one, use explicit `-d` JSON instead." in text, "expected to find: " + "`--file` injects the local path into the tool's single uploadable file field. If a tool has no uploadable file input, or has more than one, use explicit `-d` JSON instead."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ts/packages/cli/skills/composio-cli/SKILL.md')
    assert 'Upload a local file when the tool has a single `file_uploadable` input:' in text, "expected to find: " + 'Upload a local file when the tool has a single `file_uploadable` input:'[:80]

