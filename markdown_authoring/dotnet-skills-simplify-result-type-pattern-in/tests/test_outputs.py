"""Behavioral checks for dotnet-skills-simplify-result-type-pattern-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-coding-standards/composition-and-error-handling.md')
    assert "For expected errors, use a **domain-specific result type** instead of exceptions. Don't build a generic `Result<T>` — each operation knows what success and failure look like, so let the result type re" in text, "expected to find: " + "For expected errors, use a **domain-specific result type** instead of exceptions. Don't build a generic `Result<T>` — each operation knows what success and failure look like, so let the result type re"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-coding-standards/composition-and-error-handling.md')
    assert 'public static CreateOrderResult Failed(OrderErrorCode code, string message) => new()' in text, "expected to find: " + 'public static CreateOrderResult Failed(OrderErrorCode code, string message) => new()'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp-coding-standards/composition-and-error-handling.md')
    assert '_ => new ObjectResult(new { error = result.ErrorMessage }) { StatusCode = 500 }' in text, "expected to find: " + '_ => new ObjectResult(new { error = result.ErrorMessage }) { StatusCode = 500 }'[:80]

