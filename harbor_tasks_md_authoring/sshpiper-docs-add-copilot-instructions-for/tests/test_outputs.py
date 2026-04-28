"""Behavioral checks for sshpiper-docs-add-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sshpiper")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Confirm `git ls-tree HEAD crypto` shows the new submodule SHA. If you instead rebased a feature branch onto a moved `origin/master` and hit `go.mod`/`go.sum` conflicts, note that **`--ours`/`--theirs`' in text, "expected to find: " + 'Confirm `git ls-tree HEAD crypto` shows the new submodule SHA. If you instead rebased a feature branch onto a moved `origin/master` and hit `go.mod`/`go.sum` conflicts, note that **`--ours`/`--theirs`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'After pushing to a PR, **always check the GitHub Actions results** (`gh pr checks <pr>` or via the GitHub MCP). Do not declare the task done while any required check is failing or pending — push fixes' in text, "expected to find: " + 'After pushing to a PR, **always check the GitHub Actions results** (`gh pr checks <pr>` or via the GitHub MCP). Do not declare the task done while any required check is failing or pending — push fixes'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The key addition is `crypto/ssh/sshpiper.go`, which adds `PiperConfig` and `PiperConn` — the low-level API for intercepting SSH handshakes and piping two independent SSH connections together. This is ' in text, "expected to find: " + 'The key addition is `crypto/ssh/sshpiper.go`, which adds `PiperConfig` and `PiperConn` — the low-level API for intercepting SSH handshakes and piping two independent SSH connections together. This is '[:80]

