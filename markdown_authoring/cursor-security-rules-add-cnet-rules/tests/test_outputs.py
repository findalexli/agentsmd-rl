"""Behavioral checks for cursor-security-rules-add-cnet-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cursor-security-rules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('secure-dev-c-sharp.mdc')
    assert '- **Rule:** Handling of mutable data in Singleton services should be avoided to prevent data inconsistencies. Ensure thread safety in Singletons to avoid race conditions that can cause logic bypass, f' in text, "expected to find: " + '- **Rule:** Handling of mutable data in Singleton services should be avoided to prevent data inconsistencies. Ensure thread safety in Singletons to avoid race conditions that can cause logic bypass, f'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('secure-dev-c-sharp.mdc')
    assert 'These rules apply to all C#/.NET code in the repository and aim to prevent common security risks through disciplined use of input validation and deserialization, output encoding, and safe APIs.' in text, "expected to find: " + 'These rules apply to all C#/.NET code in the repository and aim to prevent common security risks through disciplined use of input validation and deserialization, output encoding, and safe APIs.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('secure-dev-c-sharp.mdc')
    assert "For file validation, utilize MIME Type Validation libraries, like `MimeDetective` or `HeyRed.Mime` to check whether a file's type and content actually matches the expected type." in text, "expected to find: " + "For file validation, utilize MIME Type Validation libraries, like `MimeDetective` or `HeyRed.Mime` to check whether a file's type and content actually matches the expected type."[:80]

