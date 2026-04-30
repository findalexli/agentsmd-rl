"""Behavioral checks for goose-docs-agentsmd-section-on-goose2 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/goose")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ui/goose2/AGENTS.md')
    assert '**Note on typed vs untyped calls.** Skills currently uses `client.extMethod("_goose/sources/...", ...)` (the untyped escape hatch) because it reshapes a generic `Source` API into skill-specific types.' in text, "expected to find: " + '**Note on typed vs untyped calls.** Skills currently uses `client.extMethod("_goose/sources/...", ...)` (the untyped escape hatch) because it reshapes a generic `Source` API into skill-specific types.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui/goose2/AGENTS.md')
    assert '1. **Define the request/response in `crates/goose-sdk/src/custom_requests.rs`.** Use the `JsonRpcRequest` / `JsonRpcResponse` derives and the `#[request(method = "_goose/<area>/<action>", response = .' in text, "expected to find: " + '1. **Define the request/response in `crates/goose-sdk/src/custom_requests.rs`.** Use the `JsonRpcRequest` / `JsonRpcResponse` derives and the `#[request(method = "_goose/<area>/<action>", response = .'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui/goose2/AGENTS.md')
    assert 'The skills → sources migration in [#8675](https://github.com/block/goose/pull/8675) is the clearest illustration of the rule. **It deleted 319 lines of Tauri-command code in `src-tauri/src/commands/sk' in text, "expected to find: " + 'The skills → sources migration in [#8675](https://github.com/block/goose/pull/8675) is the clearest illustration of the rule. **It deleted 319 lines of Tauri-command code in `src-tauri/src/commands/sk'[:80]

