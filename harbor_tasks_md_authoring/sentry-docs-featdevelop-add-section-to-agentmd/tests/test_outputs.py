"""Behavioral checks for sentry-docs-featdevelop-add-section-to-agentmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Use RFC 2119 Keywords**: Use "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" as defined in [RFC 2119](https://www.ietf.org/rfc/r' in text, "expected to find: " + '1. **Use RFC 2119 Keywords**: Use "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" as defined in [RFC 2119](https://www.ietf.org/rfc/r'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **Add RFC 2119 Alert**: When creating a new file with requirements, or adding requirements to an existing file, ensure the file has an Alert at the top (after frontmatter) to clarify RFC 2119 usage' in text, "expected to find: " + '2. **Add RFC 2119 Alert**: When creating a new file with requirements, or adding requirements to an existing file, ensure the file has an Alert at the top (after frontmatter) to clarify RFC 2119 usage'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document uses key words such as "MUST", "SHOULD", and "MAY" as defined in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) to indicate requirement levels.' in text, "expected to find: " + 'This document uses key words such as "MUST", "SHOULD", and "MAY" as defined in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) to indicate requirement levels.'[:80]

