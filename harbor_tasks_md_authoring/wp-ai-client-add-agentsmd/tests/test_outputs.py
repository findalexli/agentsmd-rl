"""Behavioral checks for wp-ai-client-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wp-ai-client")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'An AI client and API for WordPress to communicate with any generative AI models of various capabilities using a uniform API. Built on top of the [PHP AI Client](https://github.com/WordPress/php-ai-cli' in text, "expected to find: " + 'An AI client and API for WordPress to communicate with any generative AI models of various capabilities using a uniform API. Built on top of the [PHP AI Client](https://github.com/WordPress/php-ai-cli'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This project adheres to the WordPress Coding Standards with specific exceptions for PSR-4 autoloading (file names match class names). More details about coding and documentation standards are outlined' in text, "expected to find: " + 'This project adheres to the WordPress Coding Standards with specific exceptions for PSR-4 autoloading (file names match class names). More details about coding and documentation standards are outlined'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '*   **Ignoring the Fluent API:** While the traditional API is available, the fluent API is the preferred way for implementers to use the client. Avoid writing complex, nested method calls when the flu' in text, "expected to find: " + '*   **Ignoring the Fluent API:** While the traditional API is available, the fluent API is the preferred way for implementers to use the client. Avoid writing complex, nested method calls when the flu'[:80]

