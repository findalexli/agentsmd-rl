"""Behavioral checks for toolhive-add-more-claude-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/toolhive")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/go-style.md')
    assert 'Never mutate a value passed in by a caller. Maps and slices have reference semantics — passing them copies the header but shares the underlying data, so mutations are visible to the caller. Pointer pa' in text, "expected to find: " + 'Never mutate a value passed in by a caller. Maps and slices have reference semantics — passing them copies the header but shares the underlying data, so mutations are visible to the caller. Pointer pa'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/go-style.md')
    assert 'If atomicity requirements grow beyond what `sync.Map` provides (e.g., you need read-modify-write), replace it with a plain `map` guarded by a `sync.Mutex` for all operations. The performance differenc' in text, "expected to find: " + 'If atomicity requirements grow beyond what `sync.Map` provides (e.g., you need read-modify-write), replace it with a plain `map` guarded by a `sync.Mutex` for all operations. The performance differenc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/go-style.md')
    assert 'Note that `maps.Clone` (and `slices.Clone`) perform a **shallow copy** — if map values or slice elements contain pointers, slices, or nested maps, mutating those nested values will still affect the ca' in text, "expected to find: " + 'Note that `maps.Clone` (and `slices.Clone`) perform a **shallow copy** — if map values or slice elements contain pointers, slices, or nested maps, mutating those nested values will still affect the ca'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert "In parallel tests, `defer` runs when the parent test function returns — which can happen before `t.Parallel()` subtests finish. `t.Cleanup` handlers are tied to the test's full lifecycle and run after" in text, "expected to find: " + "In parallel tests, `defer` runs when the parent test function returns — which can happen before `t.Parallel()` subtests finish. `t.Cleanup` handlers are tied to the test's full lifecycle and run after"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert 'Operator E2E tests live in `test/e2e/thv-operator/` and require a Kind cluster. All tasks are defined in `cmd/thv-operator/Taskfile.yml` and must be run from the repo root with `task -d cmd/thv-operat' in text, "expected to find: " + 'Operator E2E tests live in `test/e2e/thv-operator/` and require a Kind cluster. All tasks are defined in `cmd/thv-operator/Taskfile.yml` and must be run from the repo root with `task -d cmd/thv-operat'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert "Note: `require.*` uses `runtime.Goexit`, and panics unwind the stack — both run deferred functions. The difference is not about defers being skipped; it's about *when* they run relative to subtests." in text, "expected to find: " + "Note: `require.*` uses `runtime.Goexit`, and panics unwind the stack — both run deferred functions. The difference is not about defers being skipped; it's about *when* they run relative to subtests."[:80]

