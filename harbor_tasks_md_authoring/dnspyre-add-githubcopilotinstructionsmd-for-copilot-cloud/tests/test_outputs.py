"""Behavioral checks for dnspyre-add-githubcopilotinstructionsmd-for-copilot-cloud (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dnspyre")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`dnspyre` is a command-line DNS benchmark tool written in Go. It stress-tests and measures the performance of DNS servers, supporting plain DNS (UDP/TCP), DoT (DNS over TLS), DoH (DNS over HTTPS), and' in text, "expected to find: " + '`dnspyre` is a command-line DNS benchmark tool written in Go. It stress-tests and measures the performance of DNS servers, supporting plain DNS (UDP/TCP), DoT (DNS over TLS), DoH (DNS over HTTPS), and'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Documentation is in `docs/` and built with MkDocs (deployed to GitHub Pages). Each feature has its own `.md` file (e.g., `docs/doh.md`, `docs/doq.md`, `docs/randomizing.md`). When adding or changing u' in text, "expected to find: " + 'Documentation is in `docs/` and built with MkDocs (deployed to GitHub Pages). Each feature has its own `.md` file (e.g., `docs/doh.md`, `docs/doq.md`, `docs/randomizing.md`). When adding or changing u'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Releases are cut by pushing a Git tag (e.g., `v3.x.y`). GoReleaser builds binaries for all platforms, publishes a GitHub release with checksums and cosign signatures, and pushes a Docker image. The pu' in text, "expected to find: " + 'Releases are cut by pushing a Git tag (e.g., `v3.x.y`). GoReleaser builds binaries for all platforms, publishes a GitHub release with checksums and cosign signatures, and pushes a Docker image. The pu'[:80]

