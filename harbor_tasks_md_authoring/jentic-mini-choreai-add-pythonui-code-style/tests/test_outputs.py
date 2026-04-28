"""Behavioral checks for jentic-mini-choreai-add-pythonui-code-style (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jentic-mini")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- **UI**: ESLint 9 (flat config) with Prettier as plugin. Config: `ui/eslint.config.js`, `ui/prettier.config.js`, `ui/.editorconfig`' in text, "expected to find: " + '- **UI**: ESLint 9 (flat config) with Prettier as plugin. Config: `ui/eslint.config.js`, `ui/prettier.config.js`, `ui/.editorconfig`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Shadcn-style owned components in `ui/src/components/ui/`.' in text, "expected to find: " + 'Shadcn-style owned components in `ui/src/components/ui/`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- **Icons**: Lucide React' in text, "expected to find: " + '- **Icons**: Lucide React'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/python-code-style.md')
    assert 'Formatting is `ruff format` — [PEP 8](https://peps.python.org/pep-0008/)-aligned, line length 100 (project standard; PEP 8 recommends 79). `ruff check` enforces our selected rule subset (`E4`, `E7`, `' in text, "expected to find: " + 'Formatting is `ruff format` — [PEP 8](https://peps.python.org/pep-0008/)-aligned, line length 100 (project standard; PEP 8 recommends 79). `ruff check` enforces our selected rule subset (`E4`, `E7`, `'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/python-code-style.md')
    assert "- **Don't import other modules' private names.** Symbols prefixed with `_` are module-private. If another module needs one, promote it to public (rename without the leading underscore) rather than cro" in text, "expected to find: " + "- **Don't import other modules' private names.** Symbols prefixed with `_` are module-private. If another module needs one, promote it to public (rename without the leading underscore) rather than cro"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/python-code-style.md')
    assert '- **Modern type syntax for Python 3.11.** Prefer `list[str]`, `dict[str, int]` ([PEP 585](https://peps.python.org/pep-0585/)) and `X | None` ([PEP 604](https://peps.python.org/pep-0604/)) over `typing' in text, "expected to find: " + '- **Modern type syntax for Python 3.11.** Prefer `list[str]`, `dict[str, int]` ([PEP 585](https://peps.python.org/pep-0585/)) and `X | None` ([PEP 604](https://peps.python.org/pep-0604/)) over `typing'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ui-code-style.md')
    assert "- **Use UI library primitives, not raw HTML.** In `src/pages/` and `src/components/layout/`, replace raw `<button>`, `<input>`, `<select>`, `<textarea>`, `<a>`, and `react-router-dom`'s `<Link>` with " in text, "expected to find: " + "- **Use UI library primitives, not raw HTML.** In `src/pages/` and `src/components/layout/`, replace raw `<button>`, `<input>`, `<select>`, `<textarea>`, `<a>`, and `react-router-dom`'s `<Link>` with "[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ui-code-style.md')
    assert '- **Named components use `function` declarations.** `forwardRef` primitives (Button, Input, Select, Textarea) take an anonymous function, so they write as `export const Name = forwardRef<...>((...) =>' in text, "expected to find: " + '- **Named components use `function` declarations.** `forwardRef` primitives (Button, Input, Select, Textarea) take an anonymous function, so they write as `export const Name = forwardRef<...>((...) =>'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ui-code-style.md')
    assert '- **Semantic design tokens only.** Use `bg-primary`, `text-muted-foreground`, `border-border` — not raw Tailwind colors like `bg-blue-500`. Add new tokens in `ui/src/index.css`; see CLAUDE.md for the ' in text, "expected to find: " + '- **Semantic design tokens only.** Use `bg-primary`, `text-muted-foreground`, `border-border` — not raw Tailwind colors like `bg-blue-500`. Add new tokens in `ui/src/index.css`; see CLAUDE.md for the '[:80]

