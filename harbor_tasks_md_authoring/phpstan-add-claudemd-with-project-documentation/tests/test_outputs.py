"""Behavioral checks for phpstan-add-claudemd-with-project-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phpstan")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'PHPStan finds errors in PHP code without running it. It catches bugs before tests are written, moving PHP closer to compiled languages. This is the **distribution repository** — the compiled PHAR and ' in text, "expected to find: " + 'PHPStan finds errors in PHP code without running it. It catches bugs before tests are written, moving PHP closer to compiled languages. This is the **distribution repository** — the compiled PHAR and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This repository distributes a pre-built PHAR archive. The source code is in [phpstan/phpstan-src](https://github.com/phpstan/phpstan-src), which is on PHP 8.1+ internally but the PHAR build is downgra' in text, "expected to find: " + 'This repository distributes a pre-built PHAR archive. The source code is in [phpstan/phpstan-src](https://github.com/phpstan/phpstan-src), which is on PHP 8.1+ internally but the PHAR build is downgra'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Every PHPStan error has a unique identifier (e.g., `argument.type`, `deadCode.unreachable`). The `identifier-extractor/` tool scans all PHPStan repositories to extract these identifiers, producing JSO' in text, "expected to find: " + 'Every PHPStan error has a unique identifier (e.g., `argument.type`, `deadCode.unreachable`). The `identifier-extractor/` tool scans all PHPStan repositories to extract these identifiers, producing JSO'[:80]

