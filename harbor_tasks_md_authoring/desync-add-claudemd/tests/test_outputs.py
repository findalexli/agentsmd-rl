"""Behavioral checks for desync-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/desync")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'desync is a Go library and CLI tool that re-implements [casync](https://github.com/systemd/casync) features for content-addressed binary distribution. It chunks large files using a rolling hash, dedup' in text, "expected to find: " + 'desync is a Go library and CLI tool that re-implements [casync](https://github.com/systemd/casync) features for content-addressed binary distribution. It chunks large files using a rolling hash, dedup'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Config file at `$HOME/.config/desync/config.json` for S3 credentials (per-endpoint with glob patterns), store options, and TLS settings. Long-running processes (chunk-server, mount-index) support dyna' in text, "expected to find: " + 'Config file at `$HOME/.config/desync/config.json` for S3 credentials (per-endpoint with glob patterns), store options, and TLS settings. Long-running processes (chunk-server, mount-index) support dyna'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Converter pipeline** (`coverter.go`): Layered data transformations applied in order for writes, reverse for reads. Currently only compression (zstd via `Compressor`), but designed for adding encrypt' in text, "expected to find: " + '**Converter pipeline** (`coverter.go`): Layered data transformations applied in order for writes, reverse for reads. Currently only compression (zstd via `Compressor`), but designed for adding encrypt'[:80]

