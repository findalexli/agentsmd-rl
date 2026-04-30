"""Behavioral checks for cursor-security-rules-added-private-keys-to-the (markdown_authoring task).

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
    text = _read('secure-dev-node.mdc')
    assert '- **Rule:** Never hardcode secrets such as API Keys, private keys or credentials. Use environment variables and secure configuration loading.' in text, "expected to find: " + '- **Rule:** Never hardcode secrets such as API Keys, private keys or credentials. Use environment variables and secure configuration loading.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('secure-dev-python.mdc')
    assert '- **Rule:** Logs must not contain passwords, tokens, API keys, private keys, or personally identifiable information (PII).' in text, "expected to find: " + '- **Rule:** Logs must not contain passwords, tokens, API keys, private keys, or personally identifiable information (PII).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('secure-development-principles.mdc')
    assert '- **Rule:** Secrets such as API keys, credentials, private keys, or tokens must not appear in frontend code, public repositories, or client-distributed files.' in text, "expected to find: " + '- **Rule:** Secrets such as API keys, credentials, private keys, or tokens must not appear in frontend code, public repositories, or client-distributed files.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('secure-mcp-usage.mdc')
    assert '- **Examples of Sensitive Data:** Passwords, API keys, authentication tokens, email addresses, phone numbers, government-issued IDs, private keys, or any data that could be used to identify or authent' in text, "expected to find: " + '- **Examples of Sensitive Data:** Passwords, API keys, authentication tokens, email addresses, phone numbers, government-issued IDs, private keys, or any data that could be used to identify or authent'[:80]

