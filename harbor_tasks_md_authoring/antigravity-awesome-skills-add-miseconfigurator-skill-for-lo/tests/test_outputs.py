"""Behavioral checks for antigravity-awesome-skills-add-miseconfigurator-skill-for-lo (markdown_authoring task).

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
    text = _read('skills/mise-configurator/SKILL.md')
    assert 'It helps standardize runtime versions, simplify onboarding, replace legacy version managers like `asdf`, `nvm`, and `pyenv`, and create reproducible multi-language environments with minimal setup effo' in text, "expected to find: " + 'It helps standardize runtime versions, simplify onboarding, replace legacy version managers like `asdf`, `nvm`, and `pyenv`, and create reproducible multi-language environments with minimal setup effo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mise-configurator/SKILL.md')
    assert 'description: "Generate production-ready mise.toml setups for local development, CI/CD pipelines, and toolchain standardization."' in text, "expected to find: " + 'description: "Generate production-ready mise.toml setups for local development, CI/CD pipelines, and toolchain standardization."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mise-configurator/SKILL.md')
    assert 'This skill generates clean, production-ready `mise.toml` configurations for local development environments and CI/CD pipelines.' in text, "expected to find: " + 'This skill generates clean, production-ready `mise.toml` configurations for local development environments and CI/CD pipelines.'[:80]

