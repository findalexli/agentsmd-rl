"""Behavioral checks for skills-trim-docsrecreation-from-monitoring-setup (markdown_authoring task).

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
    text = _read('skills/qdrant-monitoring/setup/SKILL.md')
    assert '- Use `/healthz`, `/livez`, `/readyz` for basic status, liveness, and readiness [Kubernetes health endpoints](https://qdrant.tech/documentation/guides/monitoring/#kubernetes-health-endpoints)' in text, "expected to find: " + '- Use `/healthz`, `/livez`, `/readyz` for basic status, liveness, and readiness [Kubernetes health endpoints](https://qdrant.tech/documentation/guides/monitoring/#kubernetes-health-endpoints)'[:80]

