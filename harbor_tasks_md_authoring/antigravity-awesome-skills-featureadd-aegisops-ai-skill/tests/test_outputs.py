"""Behavioral checks for antigravity-awesome-skills-featureadd-aegisops-ai-skill (markdown_authoring task).

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
    text = _read('skills/aegisops-ai/SKILL.md')
    assert '* **Intelligent Cost Synthesis:** Processes raw Terraform plan diffs through a financial reasoning model to detect high-risk resource escalations and "silent" fiscal drifts.' in text, "expected to find: " + '* **Intelligent Cost Synthesis:** Processes raw Terraform plan diffs through a financial reasoning model to detect high-risk resource escalations and "silent" fiscal drifts.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aegisops-ai/SKILL.md')
    assert '* **Neural Patch Analysis:** Performs semantic code reviews of Linux Kernel patches, moving beyond simple pattern matching to understand complex memory state logic.' in text, "expected to find: " + '* **Neural Patch Analysis:** Performs semantic code reviews of Linux Kernel patches, moving beyond simple pattern matching to understand complex memory state logic.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aegisops-ai/SKILL.md')
    assert '* **Solution:** Translates natural language security requirements into production-ready, hardened YAML manifests (Read-only root FS, Non-root enforcement, etc.).' in text, "expected to find: " + '* **Solution:** Translates natural language security requirements into production-ready, hardened YAML manifests (Read-only root FS, Non-root enforcement, etc.).'[:80]

