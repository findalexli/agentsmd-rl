"""Behavioral checks for mcp-gateway-registry-choreskill-add-testing-plan-step (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp-gateway-registry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/new-feature-design/SKILL.md')
    assert 'description: "Design and document new features with GitHub issue, low-level design (LLD), expert review, and testing plan. Creates structured documentation in .scratchpad/ with issue spec, technical d' in text, "expected to find: " + 'description: "Design and document new features with GitHub issue, low-level design (LLD), expert review, and testing plan. Creates structured documentation in .scratchpad/ with issue spec, technical d'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/new-feature-design/SKILL.md')
    assert 'Create a comprehensive testing plan document that captures **executable, copy-pasteable tests** covering every externally observable change introduced by the feature. The goal is for a reviewer or imp' in text, "expected to find: " + 'Create a comprehensive testing plan document that captures **executable, copy-pasteable tests** covering every externally observable change introduced by the feature. The goal is for a reviewer or imp'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/new-feature-design/SKILL.md')
    assert '*Include this section whenever the feature adds or modifies ANY config parameter (env var, setting, Terraform variable, secret). Otherwise replace with: "**Not Applicable** - feature introduces no new' in text, "expected to find: " + '*Include this section whenever the feature adds or modifies ANY config parameter (env var, setting, Terraform variable, secret). Otherwise replace with: "**Not Applicable** - feature introduces no new'[:80]

