"""Behavioral checks for skills-rewrite-deployment-options-as-situationdriven (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-deployment-options/SKILL.md')
    assert 'description: "Guides Qdrant deployment selection. Use when someone asks \'how to deploy Qdrant\', \'Docker vs Cloud\', \'local mode\', \'embedded Qdrant\', \'Qdrant EDGE\', \'which deployment option\', \'self-host' in text, "expected to find: " + 'description: "Guides Qdrant deployment selection. Use when someone asks \'how to deploy Qdrant\', \'Docker vs Cloud\', \'local mode\', \'embedded Qdrant\', \'Qdrant EDGE\', \'which deployment option\', \'self-host'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-deployment-options/SKILL.md')
    assert '- Docker is the default deployment. Full Qdrant Open Source feature set, minimal setup. [Quick start](https://qdrant.tech/documentation/quickstart/#download-and-run)' in text, "expected to find: " + '- Docker is the default deployment. Full Qdrant Open Source feature set, minimal setup. [Quick start](https://qdrant.tech/documentation/quickstart/#download-and-run)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-deployment-options/SKILL.md')
    assert 'Start with what you need: managed ops or full control? Network latency acceptable or not? Production or prototyping? The answer narrows to one of four options.' in text, "expected to find: " + 'Start with what you need: managed ops or full control? Network latency acceptable or not? Production or prototyping? The answer narrows to one of four options.'[:80]

