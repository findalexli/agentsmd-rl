"""Behavioral checks for pipelines-docs-add-an-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pipelines")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If you change commands, file paths, Make targets, environment variables, or workflows in this repo, update this guide in the relevant sections (Local development, Local testing, Local execution, Reg' in text, "expected to find: " + '- If you change commands, file paths, Make targets, environment variables, or workflows in this repo, update this guide in the relevant sections (Local development, Local testing, Local execution, Reg'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Examples: `e2e-test.yml`, `sdk-execution.yml`, `upgrade-test.yml`, `periodic.yml`, `kfp-kubernetes-execution-tests.yml`, `kfp-webhooks.yml`, `kfp-samples.yml`, `api-server-tests.yml`, and frontend i' in text, "expected to find: " + '- Examples: `e2e-test.yml`, `sdk-execution.yml`, `upgrade-test.yml`, `periodic.yml`, `kfp-kubernetes-execution-tests.yml`, `kfp-webhooks.yml`, `kfp-samples.yml`, `api-server-tests.yml`, and frontend i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Start with inspecting the architectural diagram found here `images/kfp-cluster-wide-architecture.drawio.xml` (rendered format can be found here: `images/kfp-cluster-wide-architecture.png`).' in text, "expected to find: " + '- Start with inspecting the architectural diagram found here `images/kfp-cluster-wide-architecture.drawio.xml` (rendered format can be found here: `images/kfp-cluster-wide-architecture.png`).'[:80]

