"""Behavioral checks for codeflash-docs-improve-claude-rules-based (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/codeflash")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- **Docstrings**: Do not add docstrings to new or changed code unless the user explicitly asks for them — not even one-liners. The codebase intentionally keeps functions self-documenting through clear' in text, "expected to find: " + '- **Docstrings**: Do not add docstrings to new or changed code unless the user explicitly asks for them — not even one-liners. The codebase intentionally keeps functions self-documenting through clear'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- **Verification**: Use `uv run prek` to verify code — it handles ruff, ty, mypy in one pass. Don\'t run `ruff`, `mypy`, or `python -c "import ..."` separately; `prek` is the single verification comman' in text, "expected to find: " + '- **Verification**: Use `uv run prek` to verify code — it handles ruff, ty, mypy in one pass. Don\'t run `ruff`, `mypy`, or `python -c "import ..."` separately; `prek` is the single verification comman'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- **Types**: Match the type annotation style of surrounding code — the codebase uses annotations, so add them in new code' in text, "expected to find: " + '- **Types**: Match the type annotation style of surrounding code — the codebase uses annotations, so add them in new code'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/git.md')
    assert "- Don't commit intermediate states — wait until the full implementation is complete, reviewed, and explicitly approved before committing. If the user corrects direction mid-implementation, incorporate" in text, "expected to find: " + "- Don't commit intermediate states — wait until the full implementation is complete, reviewed, and explicitly approved before committing. If the user corrects direction mid-implementation, incorporate"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/git.md')
    assert '- Always create a new branch from `main` before starting any new work — never commit directly to `main` or reuse an existing feature branch for unrelated changes' in text, "expected to find: " + '- Always create a new branch from `main` before starting any new work — never commit directly to `main` or reuse an existing feature branch for unrelated changes'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/git.md')
    assert "- When committing to an external/third-party repo, follow that repo's own conventions for versioning, changelog, and CI" in text, "expected to find: " + "- When committing to an external/third-party repo, follow that repo's own conventions for versioning, changelog, and CI"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert "- Use pytest's `tmp_path` fixture for temp directories — do not use `tempfile.mkdtemp()`, `tempfile.TemporaryDirectory()`, or `NamedTemporaryFile`. Some existing tests still use `tempfile` but new tes" in text, "expected to find: " + "- Use pytest's `tmp_path` fixture for temp directories — do not use `tempfile.mkdtemp()`, `tempfile.TemporaryDirectory()`, or `NamedTemporaryFile`. Some existing tests still use `tempfile` but new tes"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert '- Always call `.resolve()` on Path objects before passing them to functions under test — this ensures absolute paths and resolves symlinks. Example: `source_file = (tmp_path / "example.py").resolve()`' in text, "expected to find: " + '- Always call `.resolve()` on Path objects before passing them to functions under test — this ensures absolute paths and resolves symlinks. Example: `source_file = (tmp_path / "example.py").resolve()`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. Spawn subagents (using the Agent tool) to attempt the fix — each subagent should apply a fix and run the test to prove it passes' in text, "expected to find: " + '3. Spawn subagents (using the Agent tool) to attempt the fix — each subagent should apply a fix and run the test to prove it passes'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '5. Never jump straight to writing a fix yourself — always go through steps 1-4' in text, "expected to find: " + '5. Never jump straight to writing a fix yourself — always go through steps 1-4'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Bug fix workflow** — follow these steps in order, do not skip ahead:' in text, "expected to find: " + '- **Bug fix workflow** — follow these steps in order, do not skip ahead:'[:80]

