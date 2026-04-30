"""Behavioral checks for datadog-agent-cursor-add-rules-to-create (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/datadog-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent_corecheck.mdc')
    assert 'The annotation format `## @param name - type - required/optional - default: value` is used for documentation generation. Users will copy the example/default to `/etc/datadog-agent/conf.d/<checkname>.d' in text, "expected to find: " + 'The annotation format `## @param name - type - required/optional - default: value` is used for documentation generation. Users will copy the example/default to `/etc/datadog-agent/conf.d/<checkname>.d'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent_corecheck.mdc')
    assert "This ensures the configuration files are copied to `cmd/agent/dist/conf.d/` during the build process. Without this step, your configuration template won't be included in the agent package." in text, "expected to find: " + "This ensures the configuration files are copied to `cmd/agent/dist/conf.d/` during the build process. Without this step, your configuration template won't be included in the agent package."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent_corecheck.mdc')
    assert '- Some checks require components (e.g., tagger, telemetry, workloadmeta). Match the signature used by neighboring checks and pass the same dependencies into your `Factory` if needed.' in text, "expected to find: " + '- Some checks require components (e.g., tagger, telemetry, workloadmeta). Match the signature used by neighboring checks and pass the same dependencies into your `Factory` if needed.'[:80]

