"""Behavioral checks for dotnet-skills-mark-skills-as-invocable-or (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/aspire-configuration/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/best-practices/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/hosting-actor-patterns/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/management/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka/testing-patterns/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aspire/integration-testing/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aspire/service-defaults/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/aspnetcore/transactional-emails/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/api-design/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/coding-standards/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/concurrency-patterns/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/csharp/type-design-performance/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/database-performance/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/efcore-patterns/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet/local-tools/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet/package-management/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet/project-structure/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet/serialization/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet/slopwatch/SKILL.md')
    assert 'invocable: true' in text, "expected to find: " + 'invocable: true'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/meta/marketplace-publishing/SKILL.md')
    assert 'invocable: true' in text, "expected to find: " + 'invocable: true'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/meta/skills-index-snippets/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/microsoft-extensions/configuration/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/microsoft-extensions/dependency-injection/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/playwright/ci-caching/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing/crap-analysis/SKILL.md')
    assert 'invocable: true' in text, "expected to find: " + 'invocable: true'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing/playwright-blazor/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing/snapshot-testing/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/testing/testcontainers/SKILL.md')
    assert 'invocable: false' in text, "expected to find: " + 'invocable: false'[:80]

