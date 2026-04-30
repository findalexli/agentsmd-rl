"""Behavioral checks for hilla-docs-add-claudemd-for-aiassisted (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hilla")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Hilla is a web framework that integrates a Spring Boot Java backend with a reactive TypeScript frontend, providing type-safe server communication through automatic code generation from Java endpoints ' in text, "expected to find: " + 'Hilla is a web framework that integrates a Spring Boot Java backend with a reactive TypeScript frontend, providing type-safe server communication through automatic code generation from Java endpoints '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Hilla uses **Jackson 3** (`tools.jackson.*`) for internal serialization but maintains **Jackson 2** (`com.fasterxml.jackson.*`) for OpenAPI/Swagger compatibility. See `JACKSON.md` for detailed migrati' in text, "expected to find: " + 'Hilla uses **Jackson 3** (`tools.jackson.*`) for internal serialization but maintains **Jackson 2** (`com.fasterxml.jackson.*`) for OpenAPI/Swagger compatibility. See `JACKSON.md` for detailed migrati'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- **frontend** (`packages/ts/frontend`): Core utilities (Authentication, Connect client, Cookie management)' in text, "expected to find: " + '- **frontend** (`packages/ts/frontend`): Core utilities (Authentication, Connect client, Cookie management)'[:80]

