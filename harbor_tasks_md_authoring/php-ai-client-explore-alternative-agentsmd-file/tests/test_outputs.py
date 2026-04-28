"""Behavioral checks for php-ai-client-explore-alternative-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/php-ai-client")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The project uses PHPUnit for unit testing. Test files are located in the `tests/` directory and mirror the structure of the `src/` directory. The test suite is executed by running `composer phpunit`. ' in text, "expected to find: " + 'The project uses PHPUnit for unit testing. Test files are located in the `tests/` directory and mirror the structure of the `src/` directory. The test suite is executed by running `composer phpunit`. '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '*   **HTTP Communication:** A custom `HttpTransporter` layer abstracts HTTP communication, decoupling models from specific PSR-18 HTTP client implementations. Models create custom `Request` objects an' in text, "expected to find: " + '*   **HTTP Communication:** A custom `HttpTransporter` layer abstracts HTTP communication, decoupling models from specific PSR-18 HTTP client implementations. Models create custom `Request` objects an'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The PHP AI Client is a provider-agnostic PHP SDK designed to communicate with any generative AI model across various capabilities through a uniform API. It is a WordPress-agnostic PHP package that can' in text, "expected to find: " + 'The PHP AI Client is a provider-agnostic PHP SDK designed to communicate with any generative AI model across various capabilities through a uniform API. It is a WordPress-agnostic PHP package that can'[:80]

