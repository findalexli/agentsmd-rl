"""Behavioral checks for tidb-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tidb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The PR description **must** strictly follow the template located at @.github/pull_request_template.md and **must** keep the HTML comment elements like `Tests <!-- At least one of them must be included' in text, "expected to find: " + 'The PR description **must** strictly follow the template located at @.github/pull_request_template.md and **must** keep the HTML comment elements like `Tests <!-- At least one of them must be included'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- You added new unit tests (UT) or RealTiKV tests and updated Bazel test targets accordingly (for example: adding new `_test.go` files to a `go_test` rule `srcs`, adjusting `shard_count`, or creating/' in text, "expected to find: " + '- You added new unit tests (UT) or RealTiKV tests and updated Bazel test targets accordingly (for example: adding new `_test.go` files to a `go_test` rule `srcs`, adjusting `shard_count`, or creating/'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Bazel note:** If you run tests via Bazel, use `make bazel-failpoint-enable` before `bazel test` / `make bazel_test`. You can still run `make failpoint-disable` afterward to restore the workspace (Ba' in text, "expected to find: " + '**Bazel note:** If you run tests via Bazel, use `make bazel-failpoint-enable` before `bazel test` / `make bazel_test`. You can still run `make failpoint-disable` afterward to restore the workspace (Ba'[:80]

