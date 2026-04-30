"""Behavioral checks for 24pullrequests-add-agentsmd-repository-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/24pullrequests")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Ask first before editing `Gemfile*`, `db/migrate/*`, `Dockerfile`/`docker-compose.yml`, or `.github/workflows/*`.' in text, "expected to find: " + '- Ask first before editing `Gemfile*`, `db/migrate/*`, `Dockerfile`/`docker-compose.yml`, or `.github/workflows/*`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Optional localization check: `bundle exec i18n-tasks health` (locale files live under `config/locales/`).' in text, "expected to find: " + '- Optional localization check: `bundle exec i18n-tasks health` (locale files live under `config/locales/`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'stub_request(:get, "https://api.github.com/repos/ORG/REPO/contributors?per_page=100").' in text, "expected to find: " + 'stub_request(:get, "https://api.github.com/repos/ORG/REPO/contributors?per_page=100").'[:80]

