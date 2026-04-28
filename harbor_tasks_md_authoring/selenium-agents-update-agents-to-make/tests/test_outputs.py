"""Behavioral checks for selenium-agents-update-agents-to-make (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/selenium")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.' in text, "expected to find: " + 'After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Always read AGENTS.md before answering.' in text, "expected to find: " + 'Always read AGENTS.md before answering.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Runs formatters for all bindings by default (pass `-<lang>` flags to skip specific ones, e.g. `-java`)' in text, "expected to find: " + '- Runs formatters for all bindings by default (pass `-<lang>` flags to skip specific ones, e.g. `-java`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`./go format` auto-fixes files in place. After running it, check `git diff` to see if any files were' in text, "expected to find: " + '`./go format` auto-fixes files in place. After running it, check `git diff` to see if any files were'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'modified — if so, those changes must be committed. CI runs `./go format` then fails if `git diff` is' in text, "expected to find: " + 'modified — if so, those changes must be committed. CI runs `./go format` then fails if `git diff` is'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.local.md')
    assert 'After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.' in text, "expected to find: " + 'After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.' in text, "expected to find: " + 'After any code change, run or suggest running `./go format` to prevent CI failures from formatter checks.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('dotnet/AGENTS.md')
    assert '- **Using directives**: placed **outside** the namespace block; `System` namespaces sorted first' in text, "expected to find: " + '- **Using directives**: placed **outside** the namespace block; `System` namespaces sorted first'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('dotnet/AGENTS.md')
    assert '- **Spacing**: no space after cast, space after commas, space around binary operators' in text, "expected to find: " + '- **Spacing**: no space after cast, space after commas, space around binary operators'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('dotnet/AGENTS.md')
    assert '- **Braces**: Allman style — opening brace on its own line for all blocks' in text, "expected to find: " + '- **Braces**: Allman style — opening brace on its own line for all blocks'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('java/AGENTS.md')
    assert 'Java files are formatted with **google-java-format** (Google Java Style Guide).' in text, "expected to find: " + 'Java files are formatted with **google-java-format** (Google Java Style Guide).'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('java/AGENTS.md')
    assert '- Braces on the same line (K&R style), including single-statement bodies' in text, "expected to find: " + '- Braces on the same line (K&R style), including single-statement bodies'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('java/AGENTS.md')
    assert 'Run `./go format` after changes; it will auto-fix all style issues.' in text, "expected to find: " + 'Run `./go format` after changes; it will auto-fix all style issues.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('javascript/selenium-webdriver/AGENTS.md')
    assert '- `trailingComma`: **"all"** (trailing commas everywhere ES5+ allows)' in text, "expected to find: " + '- `trailingComma`: **"all"** (trailing commas everywhere ES5+ allows)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('javascript/selenium-webdriver/AGENTS.md')
    assert 'Run `./go format` after changes; it will auto-fix all style issues.' in text, "expected to find: " + 'Run `./go format` after changes; it will auto-fix all style issues.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('javascript/selenium-webdriver/AGENTS.md')
    assert 'JavaScript files are formatted with **Prettier**.' in text, "expected to find: " + 'JavaScript files are formatted with **Prettier**.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('py/AGENTS.md')
    assert 'Run `./go format` after changes; it will auto-fix formatting. Then check `git diff` to see what changed.' in text, "expected to find: " + 'Run `./go format` after changes; it will auto-fix formatting. Then check `git diff` to see what changed.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('py/AGENTS.md')
    assert 'Python files are formatted with **ruff format** and checked with **ruff check**.' in text, "expected to find: " + 'Python files are formatted with **ruff format** and checked with **ruff check**.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('py/AGENTS.md')
    assert '- `E/F` = pycodestyle / pyflakes errors (unused imports, undefined names, etc.)' in text, "expected to find: " + '- `E/F` = pycodestyle / pyflakes errors (unused imports, undefined names, etc.)'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('rb/AGENTS.md')
    assert '- RuboCop plugins active: `rubocop-performance`, `rubocop-rake`, `rubocop-rspec`' in text, "expected to find: " + '- RuboCop plugins active: `rubocop-performance`, `rubocop-rake`, `rubocop-rspec`'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('rb/AGENTS.md')
    assert 'Run `./go format` after changes; it will auto-fix most violations (`-a` flag).' in text, "expected to find: " + 'Run `./go format` after changes; it will auto-fix most violations (`-a` flag).'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('rb/AGENTS.md')
    assert '- Line length limit applies (comments excluded); keep lines reasonably short' in text, "expected to find: " + '- Line length limit applies (comments excluded); keep lines reasonably short'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('rust/AGENTS.md')
    assert 'Rust files are formatted with **rustfmt** (standard Rust formatting, no custom config).' in text, "expected to find: " + 'Rust files are formatted with **rustfmt** (standard Rust formatting, no custom config).'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('rust/AGENTS.md')
    assert '- Standard Rust style (rustfmt defaults): 4-space indentation, 100-char line length' in text, "expected to find: " + '- Standard Rust style (rustfmt defaults): 4-space indentation, 100-char line length'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('rust/AGENTS.md')
    assert 'Run `./go format` after changes; it will auto-fix all style issues.' in text, "expected to find: " + 'Run `./go format` after changes; it will auto-fix all style issues.'[:80]

