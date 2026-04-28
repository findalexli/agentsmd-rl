"""Behavioral checks for osprey-add-agentsmd-for-ai-coding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/osprey")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Modifying release, signing, or deploy workflows: `.github/workflows/publish-coordinator-image.yml`, `.github/workflows/release-osprey-rpc.yml`, `.github/workflows/mdbook.yml`, production Dockerfiles' in text, "expected to find: " + '- Modifying release, signing, or deploy workflows: `.github/workflows/publish-coordinator-image.yml`, `.github/workflows/release-osprey-rpc.yml`, `.github/workflows/mdbook.yml`, production Dockerfiles'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'CI runs entirely via GitHub Actions on `pull_request` and `push` to `main`. Each line below is one literal CI `run:` step, in workflow order. Run them in your shell (paste-as-is — no `&&` chaining, no' in text, "expected to find: " + 'CI runs entirely via GitHub Actions on `pull_request` and `push` to `main`. Each line below is one literal CI `run:` step, in workflow order. Run them in your shell (paste-as-is — no `&&` chaining, no'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Prerequisites: Python (version in `.python-version`), [uv](https://docs.astral.sh/uv/), Docker + Docker Compose v2, Node.js (version in `.github/workflows/code-quality.yml`, UI only), Rust stable + `p' in text, "expected to find: " + 'Prerequisites: Python (version in `.python-version`), [uv](https://docs.astral.sh/uv/), Docker + Docker Compose v2, Node.js (version in `.github/workflows/code-quality.yml`, UI only), Rust stable + `p'[:80]

