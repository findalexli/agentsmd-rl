"""Behavioral checks for pulumi-add-claudemd-symlink-use-mise (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pulumi")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repo uses [mise](https://mise.jdx.dev/) to manage tool versions (Go, Node, Python, protoc, etc.). See `.mise.toml` for the full list. If mise is installed and activated (via `mise activate` in yo' in text, "expected to find: " + 'This repo uses [mise](https://mise.jdx.dev/) to manage tool versions (Go, Node, Python, protoc, etc.). See `.mise.toml` for the full list. If mise is installed and activated (via `mise activate` in yo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Multiple Go modules (`pkg/go.mod`, `sdk/go.mod`, `tests/go.mod`, etc.). Changes to `go.mod` in one module may require updates in others. Run `mise exec -- make tidy` to verify.' in text, "expected to find: " + '- Multiple Go modules (`pkg/go.mod`, `sdk/go.mod`, `tests/go.mod`, etc.). Changes to `go.mod` in one module may require updates in others. Run `mise exec -- make tidy` to verify.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'See subdirectory `AGENTS.md` files (`pkg/`, `sdk/nodejs/`, `sdk/python/`, `sdk/go/`) for package-specific instructions.' in text, "expected to find: " + 'See subdirectory `AGENTS.md` files (`pkg/`, `sdk/nodejs/`, `sdk/python/`, `sdk/go/`) for package-specific instructions.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/AGENTS.md')
    assert '- Anything that adds or changes the engine, resource options, or the provider interface → add a test to `pkg/engine/lifecycletest/`' in text, "expected to find: " + '- Anything that adds or changes the engine, resource options, or the provider interface → add a test to `pkg/engine/lifecycletest/`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/AGENTS.md')
    assert '- Anything in `pkg/backend/display/` → add a test using pre-constructed, JSON-serialized engine events (ref. `testProgressEvents`)' in text, "expected to find: " + '- Anything in `pkg/backend/display/` → add a test using pre-constructed, JSON-serialized engine events (ref. `testProgressEvents`)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('pkg/AGENTS.md')
    assert '- Anything in `pkg/codegen/` → run codegen tests: `cd pkg && go test -count=1 -tags all ./codegen/...`' in text, "expected to find: " + '- Anything in `pkg/codegen/` → run codegen tests: `cd pkg && go test -count=1 -tags all ./codegen/...`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/go/AGENTS.md')
    assert 'All commands run from `sdk/go/`. Prefix with `mise exec --` if mise is not activated.' in text, "expected to find: " + 'All commands run from `sdk/go/`. Prefix with `mise exec --` if mise is not activated.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/go/AGENTS.md')
    assert '- Go files → `mise exec -- make lint && mise exec -- make test_fast`' in text, "expected to find: " + '- Go files → `mise exec -- make lint && mise exec -- make test_fast`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/go/AGENTS.md')
    assert '- **Fast tests:** `mise exec -- make test_fast`' in text, "expected to find: " + '- **Fast tests:** `mise exec -- make test_fast`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/nodejs/AGENTS.md')
    assert '- You must run `mise exec -- make install` to make the SDK available via `yarn link` before running integration tests.' in text, "expected to find: " + '- You must run `mise exec -- make install` to make the SDK available via `yarn link` before running integration tests.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/nodejs/AGENTS.md')
    assert 'All commands run from `sdk/nodejs/`. Prefix with `mise exec --` if mise is not activated.' in text, "expected to find: " + 'All commands run from `sdk/nodejs/`. Prefix with `mise exec --` if mise is not activated.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/nodejs/AGENTS.md')
    assert '- **Install (required before integration tests):** `mise exec -- make install`' in text, "expected to find: " + '- **Install (required before integration tests):** `mise exec -- make install`'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/python/AGENTS.md')
    assert 'All commands run from `sdk/python/`. Prefix with `mise exec --` if mise is not activated.' in text, "expected to find: " + 'All commands run from `sdk/python/`. Prefix with `mise exec --` if mise is not activated.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/python/AGENTS.md')
    assert '- Python files → `mise exec -- make lint && mise exec -- make test_fast`' in text, "expected to find: " + '- Python files → `mise exec -- make lint && mise exec -- make test_fast`'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('sdk/python/AGENTS.md')
    assert '- **Fast tests:** `mise exec -- make test_fast`' in text, "expected to find: " + '- **Fast tests:** `mise exec -- make test_fast`'[:80]

