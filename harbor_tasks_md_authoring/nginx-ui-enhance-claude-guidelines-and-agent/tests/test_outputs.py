"""Behavioral checks for nginx-ui-enhance-claude-guidelines-and-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nginx-ui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'AGENTS.md' in text, "expected to find: " + 'AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Backend**: `go generate ./...`, `go build ./...`, run `go test ./... -race -cover`; for release artifacts reuse the README command with `-tags=jsoniter -ldflags "$LD_FLAGS ..."`.' in text, "expected to find: " + '- **Backend**: `go generate ./...`, `go build ./...`, run `go test ./... -race -cover`; for release artifacts reuse the README command with `-tags=jsoniter -ldflags "$LD_FLAGS ..."`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Demo stack**: `docker-compose -f docker-compose-demo.yml up` to bootstrap the sample environment' in text, "expected to find: " + '- **Demo stack**: `docker-compose -f docker-compose-demo.yml up` to bootstrap the sample environment'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Run `pnpm lint`, `pnpm lint:fix`, and `pnpm typecheck` to keep style and typings aligned' in text, "expected to find: " + '- Run `pnpm lint`, `pnpm lint:fix`, and `pnpm typecheck` to keep style and typings aligned'[:80]

