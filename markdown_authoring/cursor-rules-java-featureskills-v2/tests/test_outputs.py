"""Behavioral checks for cursor-rules-java-featureskills-v2 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cursor-rules-java")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/110-java-maven-best-practices/SKILL.md')
    assert 'description: Effective Maven usage involves robust dependency management via `<dependencyManagement>` and BOMs, adherence to the standard directory layout, and centralized plugin management. Build pro' in text, "expected to find: " + 'description: Effective Maven usage involves robust dependency management via `<dependencyManagement>` and BOMs, adherence to the standard directory layout, and centralized plugin management. Build pro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/110-java-maven-best-practices/SKILL.md')
    assert '- Maintain backward compatibility with existing build process' in text, "expected to find: " + '- Maintain backward compatibility with existing build process'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/110-java-maven-best-practices/SKILL.md')
    assert 'name: Maven Best Practices' in text, "expected to find: " + 'name: Maven Best Practices'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/111-java-maven-dependencies/SKILL.md')
    assert 'description: Treats the user as a knowledgeable partner in solving problems rather than prescribing one-size-fits-all solutions. Presents multiple approaches with clear trade-offs, asking for user inp' in text, "expected to find: " + 'description: Treats the user as a knowledgeable partner in solving problems rather than prescribing one-size-fits-all solutions. Presents multiple approaches with clear trade-offs, asking for user inp'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/111-java-maven-dependencies/SKILL.md')
    assert 'name: Add Maven dependencies for improved code quality' in text, "expected to find: " + 'name: Add Maven dependencies for improved code quality'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/111-java-maven-dependencies/SKILL.md')
    assert '- Test enhanced compiler analysis with a simple build' in text, "expected to find: " + '- Test enhanced compiler analysis with a simple build'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/hello-world/SKILL.md')
    assert '.agents/skills/hello-world/SKILL.md' in text, "expected to find: " + '.agents/skills/hello-world/SKILL.md'[:80]

