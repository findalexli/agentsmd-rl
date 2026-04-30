"""Behavioral checks for nixopus-chore-add-support-for-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nixopus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert 'You are a senior backend engineer building the Nixopus API — a production-grade Go application using the Fuego framework, Bun ORM, and domain-driven architecture. Your focus is on writing clean, maint' in text, "expected to find: " + 'You are a senior backend engineer building the Nixopus API — a production-grade Go application using the Fuego framework, Bun ORM, and domain-driven architecture. Your focus is on writing clean, maint'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert 'func (c *DomainController) CreateItem(f fuego.ContextWithBody[types.CreateItemRequest]) (*shared_types.Response, error) {' in text, "expected to find: " + 'func (c *DomainController) CreateItem(f fuego.ContextWithBody[types.CreateItemRequest]) (*shared_types.Response, error) {'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert '- Check `internal/utils/` for common utilities (`GetUser`, `SendErrorResponse`, `SendJSONResponse`)' in text, "expected to find: " + '- Check `internal/utils/` for common utilities (`GetUser`, `SendErrorResponse`, `SendJSONResponse`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert 'You are a senior frontend engineer building the Nixopus dashboard — a modern, visually rich Next.js application with TypeScript. Your focus is on crafting maintainable, performant, and beautiful user ' in text, "expected to find: " + 'You are a senior frontend engineer building the Nixopus dashboard — a modern, visually rich Next.js application with TypeScript. Your focus is on crafting maintainable, performant, and beautiful user '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert '- Check `view/hooks/` for reusable hooks (e.g., `use-searchable`, `use-translation`, `use-mobile`)' in text, "expected to find: " + '- Check `view/hooks/` for reusable hooks (e.g., `use-searchable`, `use-translation`, `use-mobile`)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert '- Check `view/lib/utils.ts` for utility functions (e.g., `cn()`, `formatBytes()`, `formatDate()`)' in text, "expected to find: " + '- Check `view/lib/utils.ts` for utility functions (e.g., `cn()`, `formatBytes()`, `formatDate()`)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/installer_cli.mdc')
    assert 'You are a senior Python engineer building the Nixopus CLI — a production-grade command-line tool using Typer, Rich, and Pydantic. Your focus is on writing clean, maintainable, and user-friendly CLI co' in text, "expected to find: " + 'You are a senior Python engineer building the Nixopus CLI — a production-grade command-line tool using Typer, Rich, and Pydantic. Your focus is on writing clean, maintainable, and user-friendly CLI co'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/installer_cli.mdc')
    assert 'def build_steps(params: CommandParams) -> List[Tuple[str, Callable[[], tuple[bool, Optional[str]]]]]:' in text, "expected to find: " + 'def build_steps(params: CommandParams) -> List[Tuple[str, Callable[[], tuple[bool, Optional[str]]]]]:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/installer_cli.mdc')
    assert 'def clone_repository(repo: str, path: str, logger: LoggerProtocol) -> tuple[bool, Optional[str]]:' in text, "expected to find: " + 'def clone_repository(repo: str, path: str, logger: LoggerProtocol) -> tuple[bool, Optional[str]]:'[:80]

