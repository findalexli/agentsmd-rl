"""Behavioral checks for uportal-docs-create-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/uportal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Source code MUST compile under Java 8 — no Java 9+ language features or APIs. The CI matrix tests builds on both Java 8 and Java 11 JVMs across three distributions (AdoptOpenJDK Hotspot, Eclipse Temur' in text, "expected to find: " + 'Source code MUST compile under Java 8 — no Java 9+ language features or APIs. The CI matrix tests builds on both Java 8 and Java 11 JVMs across three distributions (AdoptOpenJDK Hotspot, Eclipse Temur'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains the uPortal framework source code. To actually **run** a portal instance, you need [uPortal-start](https://github.com/uPortal-Project/uPortal-start), which provides Tomcat, HS' in text, "expected to find: " + 'This repository contains the uPortal framework source code. To actually **run** a portal instance, you need [uPortal-start](https://github.com/uPortal-Project/uPortal-start), which provides Tomcat, HS'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If using CAS authentication (default in uPortal-start), the login flow redirects through `http://localhost:8080/cas/login`. The bundled CAS instance authenticates against the same local database, so t' in text, "expected to find: " + 'If using CAS authentication (default in uPortal-start), the login flow redirects through `http://localhost:8080/cas/login`. The bundled CAS instance authenticates against the same local database, so t'[:80]

