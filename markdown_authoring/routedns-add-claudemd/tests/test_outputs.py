"""Behavioral checks for routedns-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/routedns")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'TOML-based configuration defined in `cmd/routedns/config.go`. Four top-level sections: `[listeners]`, `[resolvers]`, `[groups]`, `[routers]`. Component instantiation in `cmd/routedns/resolver.go` uses' in text, "expected to find: " + 'TOML-based configuration defined in `cmd/routedns/config.go`. Four top-level sections: `[listeners]`, `[resolvers]`, `[groups]`, `[routers]`. Component instantiation in `cmd/routedns/resolver.go` uses'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Groups/Modifiers** (~30 types): Wrap one or more resolvers to add behavior — caching (`cache.go`), blocklists (`blocklist-v2.go`), load-balancing (`round-robin.go`, `failrotate.go`, `fastest.go`),' in text, "expected to find: " + '- **Groups/Modifiers** (~30 types): Wrap one or more resolvers to add behavior — caching (`cache.go`), blocklists (`blocklist-v2.go`), load-balancing (`round-robin.go`, `failrotate.go`, `fastest.go`),'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'RouteDNS is a composable DNS stub resolver, proxy and router written in Go. It builds processing pipelines from four component types (listeners, resolvers, groups/modifiers, routers) configured via TO' in text, "expected to find: " + 'RouteDNS is a composable DNS stub resolver, proxy and router written in Go. It builds processing pipelines from four component types (listeners, resolvers, groups/modifiers, routers) configured via TO'[:80]

