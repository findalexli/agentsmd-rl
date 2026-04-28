"""Behavioral checks for terraform-provider-btp-chore-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/terraform-provider-btp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Always add or update a corresponding `_test.go` file; include at least a happy path and one error or edge case (invalid input / missing attribute / permission denial simulation if feasible) as well ' in text, "expected to find: " + '- Always add or update a corresponding `_test.go` file; include at least a happy path and one error or edge case (invalid input / missing attribute / permission denial simulation if feasible) as well '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- For CRUD functions (Create / Read / Update / Delete): centralize API logic through `internal/btpcli` to keep resource files declarative; avoid raw `http` usage directly in resource files.' in text, "expected to find: " + '- For CRUD functions (Create / Read / Update / Delete): centralize API logic through `internal/btpcli` to keep resource files declarative; avoid raw `http` usage directly in resource files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Types: `type_<scope>_<entity>.go` or camel-case variant where hierarchical (e.g., `type_directoryHierarchy.go`). Keep internal naming consistent; prefer lower-case file-local helpers.' in text, "expected to find: " + '- Types: `type_<scope>_<entity>.go` or camel-case variant where hierarchical (e.g., `type_directoryHierarchy.go`). Keep internal naming consistent; prefer lower-case file-local helpers.'[:80]

