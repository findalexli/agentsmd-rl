"""Behavioral checks for ghostwriter-add-copilot-instructions-for-ghostwriter (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ghostwriter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Ghostwriter** is an offensive security operations platform for report writing, asset tracking, and assessment management. Built with Python 3.10, Django 4.2, TypeScript/React in Docker containers. ~' in text, "expected to find: " + '**Ghostwriter** is an offensive security operations platform for report writing, asset tracking, and assessment management. Built with Python 3.10, Django 4.2, TypeScript/React in Docker containers. ~'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Stack:** Django 4.2 | Python 3.10 | PostgreSQL 16.4 | Redis 6 | React/TypeScript | Vite | Hasura GraphQL v2.39.1 | Channels 4.0 WebSockets | Django-Q2 background tasks | Docker Compose | Jinja2/pyth' in text, "expected to find: " + '**Stack:** Django 4.2 | Python 3.10 | PostgreSQL 16.4 | Redis 6 | React/TypeScript | Vite | Hasura GraphQL v2.39.1 | Channels 4.0 WebSockets | Django-Q2 background tasks | Docker Compose | Jinja2/pyth'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Python:** Django 4.2, DRF 3.15.2, allauth 0.63.6 (SSO), allauth-2fa 0.11.1, Pillow 10.4.0, python-docx 1.1.2, python-pptx 1.0.2, docxtpl 0.18.0, jinja2 3.1.5, channels 4.0.0, django-q2 1.7.2, psycop' in text, "expected to find: " + '**Python:** Django 4.2, DRF 3.15.2, allauth 0.63.6 (SSO), allauth-2fa 0.11.1, Pillow 10.4.0, python-docx 1.1.2, python-pptx 1.0.2, docxtpl 0.18.0, jinja2 3.1.5, channels 4.0.0, django-q2 1.7.2, psycop'[:80]

