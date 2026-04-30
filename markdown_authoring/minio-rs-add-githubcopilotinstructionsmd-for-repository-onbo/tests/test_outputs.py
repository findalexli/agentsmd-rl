"""Behavioral checks for minio-rs-add-githubcopilotinstructionsmd-for-repository-onbo (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/minio-rs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**minio-rs** is a MinIO Rust SDK for Amazon S3 compatible cloud storage. It provides a strongly-typed, async-first interface to MinIO and S3-compatible object storage APIs using a request builder patt' in text, "expected to find: " + '**minio-rs** is a MinIO Rust SDK for Amazon S3 compatible cloud storage. It provides a strongly-typed, async-first interface to MinIO and S3-compatible object storage APIs using a request builder patt'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Trust these instructions**: This information has been validated against the actual repository. Only search for additional information if these instructions are incomplete or you encounter errors not' in text, "expected to find: " + '**Trust these instructions**: This information has been validated against the actual repository. Only search for additional information if these instructions are incomplete or you encounter errors not'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Valid labels: `highlight`, `breaking-change`, `security-fix`, `enhancement`, `bug`, `cleanup-rewrite`, `regression-fix`, `codex`' in text, "expected to find: " + '- Valid labels: `highlight`, `breaking-change`, `security-fix`, `enhancement`, `bug`, `cleanup-rewrite`, `regression-fix`, `codex`'[:80]

