"""Behavioral checks for generative-ai-for-beginners-dotnet-add-agentsmd-file-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/generative-ai-for-beginners-dotnet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains **Generative AI for Beginners .NET** - a hands-on course teaching .NET developers how to build Generative AI applications. The course focuses on practical, runnable code sampl' in text, "expected to find: " + 'This repository contains **Generative AI for Beginners .NET** - a hands-on course teaching .NET developers how to build Generative AI applications. The course focuses on practical, runnable code sampl'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository is primarily educational with sample applications. There are currently no automated unit or integration tests. Validation is done through:' in text, "expected to find: " + 'This repository is primarily educational with sample applications. There are currently no automated unit or integration tests. Validation is done through:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Lesson-based structure**: Organized in numbered folders (01-10) containing lessons, documentation, and code samples' in text, "expected to find: " + '- **Lesson-based structure**: Organized in numbered folders (01-10) containing lessons, documentation, and code samples'[:80]

