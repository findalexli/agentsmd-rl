"""Behavioral checks for opencost-create-comprehensive-claudemd-documentation-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opencost")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'OpenCost is an open source Kubernetes cost monitoring tool maintained by the Cloud Native Computing Foundation (CNCF). It provides real-time cost allocation, asset tracking, and cloud cost monitoring ' in text, "expected to find: " + 'OpenCost is an open source Kubernetes cost monitoring tool maintained by the Cloud Native Computing Foundation (CNCF). It provides real-time cost allocation, asset tracking, and cloud cost monitoring '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Multi-cloud cost monitoring (AWS, Azure, GCP, Alibaba, Oracle, OTC, DigitalOcean, Scaleway)' in text, "expected to find: " + '- Multi-cloud cost monitoring (AWS, Azure, GCP, Alibaba, Oracle, OTC, DigitalOcean, Scaleway)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This document provides guidance for AI assistants working with the OpenCost codebase.' in text, "expected to find: " + 'This document provides guidance for AI assistants working with the OpenCost codebase.'[:80]

