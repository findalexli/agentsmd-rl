"""Behavioral checks for homebrew-dotnet-sdk-versions-update-ai-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/homebrew-dotnet-sdk-versions")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.aiskills/fix-ci/SKILL.md')
    assert 'description: Fix or update the CI workflow for homebrew-dotnet-sdk-versions. Use this skill whenever asked to fix a broken CI, investigate a CI failure, update .github/workflows/ci.yml, or sync CI cha' in text, "expected to find: " + 'description: Fix or update the CI workflow for homebrew-dotnet-sdk-versions. Use this skill whenever asked to fix a broken CI, investigate a CI failure, update .github/workflows/ci.yml, or sync CI cha'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.aiskills/fix-ci/SKILL.md')
    assert 'name: fix-ci' in text, "expected to find: " + 'name: fix-ci'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.aiskills/new-cask/SKILL.md')
    assert "description: Add a new cask to homebrew-dotnet-sdk-versions. Use this skill whenever asked to support a new .NET SDK version or feature band that doesn't have a cask yet, create a stub cask, add a new" in text, "expected to find: " + "description: Add a new cask to homebrew-dotnet-sdk-versions. Use this skill whenever asked to support a new .NET SDK version or feature band that doesn't have a cask yet, create a stub cask, add a new"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.aiskills/new-cask/SKILL.md')
    assert 'git commit -m "Add support for dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}"' in text, "expected to find: " + 'git commit -m "Add support for dotnet-sdk{MAJOR}-{MINOR}-{FEATURE}"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.aiskills/new-cask/SKILL.md')
    assert '**If you are an external contributor** (pushing to your fork):' in text, "expected to find: " + '**If you are an external contributor** (pushing to your fork):'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.aiskills/update-cask/SKILL.md')
    assert 'description: Create an update PR for an existing cask in homebrew-dotnet-sdk-versions. Use this skill whenever asked to manually bump a cask to a newer version, update sha256/url/version fields, force' in text, "expected to find: " + 'description: Create an update PR for an existing cask in homebrew-dotnet-sdk-versions. Use this skill whenever asked to manually bump a cask to a newer version, update sha256/url/version fields, force'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.aiskills/update-cask/SKILL.md')
    assert 'name: update-cask' in text, "expected to find: " + 'name: update-cask'[:80]

