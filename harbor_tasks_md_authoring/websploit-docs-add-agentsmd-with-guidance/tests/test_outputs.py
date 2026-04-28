"""Behavioral checks for websploit-docs-add-agentsmd-with-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/websploit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'WebSploit Labs is an **intentionally vulnerable** training environment by Omar Santos. It bundles classic OWASP apps (WebGoat, Juice Shop, DVWA), several CTF challenges, and a set of custom Flask-base' in text, "expected to find: " + 'WebSploit Labs is an **intentionally vulnerable** training environment by Omar Santos. It bundles classic OWASP apps (WebGoat, Juice Shop, DVWA), several CTF challenges, and a set of custom Flask-base'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- The workspace-level `codeguard-*` security rules describe best practices that **apply to tooling, infrastructure, CI, and any non-vulnerable code** (e.g., `install.sh`, `docker-compose.yml`, helper ' in text, "expected to find: " + '- The workspace-level `codeguard-*` security rules describe best practices that **apply to tooling, infrastructure, CI, and any non-vulnerable code** (e.g., `install.sh`, `docker-compose.yml`, helper '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `pyproject.toml` declares Python `>=3.13` and `flask>=3.1.2`. `uv.lock` is checked in, suggesting `uv` for environment management at the top level. Individual labs have their own `requirements.txt` ' in text, "expected to find: " + '- `pyproject.toml` declares Python `>=3.13` and `flask>=3.1.2`. `uv.lock` is checked in, suggesting `uv` for environment management at the top level. Individual labs have their own `requirements.txt` '[:80]

