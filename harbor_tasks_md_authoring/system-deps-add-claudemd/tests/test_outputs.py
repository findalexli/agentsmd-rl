"""Behavioral checks for system-deps-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/system-deps")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **`src/metadata.rs`** — Parses `[package.metadata.system-deps]` TOML tables. Handles simple version strings, complex table specs (name overrides, feature-gating, fallback names, `cfg()` expressions)' in text, "expected to find: " + '- **`src/metadata.rs`** — Parses `[package.metadata.system-deps]` TOML tables. Handles simple version strings, complex table specs (name overrides, feature-gating, fallback names, `cfg()` expressions)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`system-deps` is a Rust crate for declaring system library dependencies declaratively in `Cargo.toml` metadata (under `[package.metadata.system-deps]`) instead of programmatically in `build.rs`. It wr' in text, "expected to find: " + '`system-deps` is a Rust crate for declaring system library dependencies declaratively in `Cargo.toml` metadata (under `[package.metadata.system-deps]`) instead of programmatically in `build.rs`. It wr'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **`src/test.rs`** — Integration tests using fixed TOML manifests in `src/tests/toml-*/` directories. Each test directory contains a `Cargo.toml` and mock `.pc` files. Tests use `lazy_static` mutex +' in text, "expected to find: " + '- **`src/test.rs`** — Integration tests using fixed TOML manifests in `src/tests/toml-*/` directories. Each test directory contains a `Cargo.toml` and mock `.pc` files. Tests use `lazy_static` mutex +'[:80]

