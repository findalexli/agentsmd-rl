"""Behavioral checks for nushell-add-agentsmd-to-help-llms (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nushell")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '- Commands in `crates/nu-command/src/` implement `Command` trait - add examples in `examples()` (they become tests)' in text, "expected to find: " + '- Commands in `crates/nu-command/src/` implement `Command` trait - add examples in `examples()` (they become tests)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '- Before every commit: `nu -c "use toolkit.nu; toolkit fmt"` and `nu -c "use toolkit.nu; toolkit clippy"`' in text, "expected to find: " + '- Before every commit: `nu -c "use toolkit.nu; toolkit fmt"` and `nu -c "use toolkit.nu; toolkit clippy"`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '- Check deps: `cargo tree --duplicates` - use workspace deps, exact semver `"1.2.3"`, no git deps in PRs' in text, "expected to find: " + '- Check deps: `cargo tree --duplicates` - use workspace deps, exact semver `"1.2.3"`, no git deps in PRs'[:80]

