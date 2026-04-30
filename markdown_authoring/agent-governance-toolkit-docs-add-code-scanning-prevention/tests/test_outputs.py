"""Behavioral checks for agent-governance-toolkit-docs-add-code-scanning-prevention (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-governance-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- To look up a Docker image digest: `docker pull python:3.12-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.12-slim`" in text, "expected to find: " + "- To look up a Docker image digest: `docker pull python:3.12-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.12-slim`"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- To look up a GitHub Action SHA: `gh api repos/{owner}/{repo}/git/ref/tags/{tag} --jq '.object.sha'`" in text, "expected to find: " + "- To look up a GitHub Action SHA: `gh api repos/{owner}/{repo}/git/ref/tags/{tag} --jq '.object.sha'`"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- ✅ `FROM python:3.12-slim@sha256:804ddf3251a60bbf9c92e73b7566c40428d54d0e79d3428194edf40da6521286`' in text, "expected to find: " + '- ✅ `FROM python:3.12-slim@sha256:804ddf3251a60bbf9c92e73b7566c40428d54d0e79d3428194edf40da6521286`'[:80]

