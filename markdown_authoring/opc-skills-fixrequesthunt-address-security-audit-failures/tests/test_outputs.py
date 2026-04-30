"""Behavioral checks for opc-skills-fixrequesthunt-address-security-audit-failures (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opc-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/requesthunt/SKILL.md')
    assert 'The installer downloads a pre-built binary from [GitHub Releases](https://github.com/ReScienceLab/requesthunt-cli/releases) and verifies its SHA256 checksum before installation. Alternatively, build f' in text, "expected to find: " + 'The installer downloads a pre-built binary from [GitHub Releases](https://github.com/ReScienceLab/requesthunt-cli/releases) and verifies its SHA256 checksum before installation. Alternatively, build f'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/requesthunt/SKILL.md')
    assert 'Data returned by `requesthunt search`, `list`, and `scrape` commands originates from public user-generated content on external platforms. When processing this data:' in text, "expected to find: " + 'Data returned by `requesthunt search`, `list`, and `scrape` commands originates from public user-generated content on external platforms. When processing this data:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/requesthunt/SKILL.md')
    assert '> **Security**: Never hardcode API keys directly in skill instructions or agent output. Use environment variables or the secured config file.' in text, "expected to find: " + '> **Security**: Never hardcode API keys directly in skill instructions or agent output. Use environment variables or the secured config file.'[:80]

