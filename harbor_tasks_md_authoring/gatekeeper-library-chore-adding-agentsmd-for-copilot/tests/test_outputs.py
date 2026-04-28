"""Behavioral checks for gatekeeper-library-chore-adding-agentsmd-for-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gatekeeper-library")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**OPA Gatekeeper Library** is a community-owned library of policies for the [OPA Gatekeeper project](https://open-policy-agent.github.io/gatekeeper/website/docs/). This repository contains **validatio' in text, "expected to find: " + '**OPA Gatekeeper Library** is a community-owned library of policies for the [OPA Gatekeeper project](https://open-policy-agent.github.io/gatekeeper/website/docs/). This repository contains **validatio'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Trust these instructions completely.** Only search the codebase if information here is incomplete or incorrect. Always run the complete validation sequence before claiming success. The CI pipeline i' in text, "expected to find: " + '**Trust these instructions completely.** Only search the codebase if information here is incomplete or incorrect. Always run the complete validation sequence before claiming success. The CI pipeline i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Languages:** Rego (policy logic), Go (tooling/scripts), YAML (Kubernetes manifests), Gomplate (templating), **CEL (Common Expression Language for K8sNativeValidation)**' in text, "expected to find: " + '- **Languages:** Rego (policy logic), Go (tooling/scripts), YAML (Kubernetes manifests), Gomplate (templating), **CEL (Common Expression Language for K8sNativeValidation)**'[:80]

