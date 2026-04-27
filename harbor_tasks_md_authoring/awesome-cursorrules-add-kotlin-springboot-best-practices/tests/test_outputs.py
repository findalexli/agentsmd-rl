"""Behavioral checks for awesome-cursorrules-add-kotlin-springboot-best-practices (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/kotlin-springboot-best-practices-cursorrules-prompt-file/.cursorrules')
    assert '1.\tUse PascalCase for class and object names, camelCase for functions and variables, and UPPER_SNAKE_CASE for constants to follow Kotlin naming conventions and improve readability.' in text, "expected to find: " + '1.\tUse PascalCase for class and object names, camelCase for functions and variables, and UPPER_SNAKE_CASE for constants to follow Kotlin naming conventions and improve readability.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/kotlin-springboot-best-practices-cursorrules-prompt-file/.cursorrules')
    assert '5.\tPlace your Spring Boot application entry point in the root package and structure sub-packages by layer or feature to help Spring scan and organize components efficiently.' in text, "expected to find: " + '5.\tPlace your Spring Boot application entry point in the root package and structure sub-packages by layer or feature to help Spring scan and organize components efficiently.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/kotlin-springboot-best-practices-cursorrules-prompt-file/.cursorrules')
    assert '4.\tFormat your code consistently using 4-space indentation, proper spacing around operators and commas, and short, focused functions to improve clarity and maintainability.' in text, "expected to find: " + '4.\tFormat your code consistently using 4-space indentation, proper spacing around operators and commas, and short, focused functions to improve clarity and maintainability.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/kotlin-springboot-best-practices-cursorrules-prompt-file/kotlin-springboot-rules.mdc')
    assert '1.\tUse PascalCase for class and object names, camelCase for functions and variables, and UPPER_SNAKE_CASE for constants to follow Kotlin naming conventions and improve readability.' in text, "expected to find: " + '1.\tUse PascalCase for class and object names, camelCase for functions and variables, and UPPER_SNAKE_CASE for constants to follow Kotlin naming conventions and improve readability.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/kotlin-springboot-best-practices-cursorrules-prompt-file/kotlin-springboot-rules.mdc')
    assert '5.\tPlace your Spring Boot application entry point in the root package and structure sub-packages by layer or feature to help Spring scan and organize components efficiently.' in text, "expected to find: " + '5.\tPlace your Spring Boot application entry point in the root package and structure sub-packages by layer or feature to help Spring scan and organize components efficiently.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/kotlin-springboot-best-practices-cursorrules-prompt-file/kotlin-springboot-rules.mdc')
    assert '4.\tFormat your code consistently using 4-space indentation, proper spacing around operators and commas, and short, focused functions to improve clarity and maintainability.' in text, "expected to find: " + '4.\tFormat your code consistently using 4-space indentation, proper spacing around operators and commas, and short, focused functions to improve clarity and maintainability.'[:80]

