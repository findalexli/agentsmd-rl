"""Behavioral checks for antigravity-awesome-skills-feat-add-appdeploy-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/appdeploy/SKILL.md')
    assert 'Use this when deploy_app tool call returns or when the user asks to check the deployment status of an app, or reports that the app has errors or is not working as expected. Returns deployment status (' in text, "expected to find: " + 'Use this when deploy_app tool call returns or when the user asks to check the deployment status of an app, or reports that the app has errors or is not working as expected. Returns deployment status ('[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/appdeploy/SKILL.md')
    assert "List deployable versions for an existing app. Requires app_id. Returns newest-first {name, version, timestamp} items. Display 'name' to users. DO NOT display the 'version' value to users. Timestamp va" in text, "expected to find: " + "List deployable versions for an existing app. Requires app_id. Returns newest-first {name, version, timestamp} items. Display 'name' to users. DO NOT display the 'version' value to users. Timestamp va"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/appdeploy/SKILL.md')
    assert 'Use this when you are about to call deploy_app in order to get the deployment constraints and hard rules. You must call this tool before starting to generate any code. This tool returns instructions o' in text, "expected to find: " + 'Use this when you are about to call deploy_app in order to get the deployment constraints and hard rules. You must call this tool before starting to generate any code. This tool returns instructions o'[:80]

