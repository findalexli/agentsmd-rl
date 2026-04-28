"""Behavioral checks for appwrite-feat-create-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/appwrite")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Appwrite is a self-hosted Backend-as-a-Service (BaaS) platform that provides developers with a set of APIs and tools to build secure, scalable applications. The project uses a hybrid monolithic-micros' in text, "expected to find: " + 'Appwrite is a self-hosted Backend-as-a-Service (BaaS) platform that provides developers with a set of APIs and tools to build secure, scalable applications. The project uses a hybrid monolithic-micros'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When a collection has a combination of `resourceType`, `resourceId`, and/or `resourceInternalId`, the value of `resourceType` MUST always be **plural** - for example: `functions`, `sites`, `deployment' in text, "expected to find: " + 'When a collection has a combination of `resourceType`, `resourceId`, and/or `resourceInternalId`, the value of `resourceType` MUST always be **plural** - for example: `functions`, `sites`, `deployment'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Appwrite is an end-to-end backend server for web, mobile, native, and backend apps. This guide provides context and instructions for AI coding agents working on the Appwrite codebase.' in text, "expected to find: " + 'Appwrite is an end-to-end backend server for web, mobile, native, and backend apps. This guide provides context and instructions for AI coding agents working on the Appwrite codebase.'[:80]

