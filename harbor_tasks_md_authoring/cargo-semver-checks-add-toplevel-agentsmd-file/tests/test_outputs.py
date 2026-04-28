"""Behavioral checks for cargo-semver-checks-add-toplevel-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cargo-semver-checks")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `scripts/rename_lint.sh <old-name> <new-name>` can be used to rename a lint. The lint names are the same as the name of the lint file without the `.ron` extension, and also the same as the `id` valu' in text, "expected to find: " + '- `scripts/rename_lint.sh <old-name> <new-name>` can be used to rename a lint. The lint names are the same as the name of the lint file without the `.ron` extension, and also the same as the `id` valu'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run `./scripts/regenerate_test_rustdocs.sh` then use `insta` and `cargo-insta` appropriately to update any snapshots. Review the snapshots to ensure they are correct and expected for the code change' in text, "expected to find: " + '- Run `./scripts/regenerate_test_rustdocs.sh` then use `insta` and `cargo-insta` appropriately to update any snapshots. Review the snapshots to ensure they are correct and expected for the code change'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Run `cargo clippy --all-targets --no-deps --fix --allow-dirty --allow-staged -- -D warnings --allow deprecated` to fix any auto-fixable lints. Manually fix anything that couldn't be auto-fixed." in text, "expected to find: " + "- Run `cargo clippy --all-targets --no-deps --fix --allow-dirty --allow-staged -- -D warnings --allow deprecated` to fix any auto-fixable lints. Manually fix anything that couldn't be auto-fixed."[:80]

