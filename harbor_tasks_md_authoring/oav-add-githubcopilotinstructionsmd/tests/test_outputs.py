"""Behavioral checks for oav-add-githubcopilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oav")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'oav (openapi-validation-tools) is an npm package for validating Azure REST API specifications (OpenAPI/Swagger). It provides semantic validation, model validation, live traffic validation, example qua' in text, "expected to find: " + 'oav (openapi-validation-tools) is an npm package for validating Azure REST API specifications (OpenAPI/Swagger). It provides semantic validation, model validation, live traffic validation, example qua'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Linting**: ESLint with `@typescript-eslint/parser`, Prettier integration, and enforced import ordering (`import/order`)' in text, "expected to find: " + '- **Linting**: ESLint with `@typescript-eslint/parser`, Prettier integration, and enforced import ordering (`import/order`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Dependency injection** via inversify with decorators (`experimentalDecorators` and `emitDecoratorMetadata` enabled)' in text, "expected to find: " + '- **Dependency injection** via inversify with decorators (`experimentalDecorators` and `emitDecoratorMetadata` enabled)'[:80]

