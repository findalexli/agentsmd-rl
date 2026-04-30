"""Behavioral checks for quarkus-improve-agentsmd-and-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/quarkus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/building-and-testing/SKILL.md')
    assert './mvnw verify -Dstart-containers -Dtest-containers -Dtest=fully.qualified.ClassName#methodName' in text, "expected to find: " + './mvnw verify -Dstart-containers -Dtest-containers -Dtest=fully.qualified.ClassName#methodName'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/building-and-testing/SKILL.md')
    assert './mvnw test -f integration-tests/<name>/ -Dstart-containers -Dtest-containers -Dtest=MyTest' in text, "expected to find: " + './mvnw test -f integration-tests/<name>/ -Dstart-containers -Dtest-containers -Dtest=MyTest'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/building-and-testing/SKILL.md')
    assert './mvnw verify -f integration-tests/<name>/ -Dstart-containers -Dtest-containers -Dnative' in text, "expected to find: " + './mvnw verify -f integration-tests/<name>/ -Dstart-containers -Dtest-containers -Dnative'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/coding-style/SKILL.md')
    assert '- The project enforces formatting via `formatter-maven-plugin` and `impsort-maven-plugin`,' in text, "expected to find: " + '- The project enforces formatting via `formatter-maven-plugin` and `impsort-maven-plugin`,'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/coding-style/SKILL.md')
    assert 'let the formatting plugins do their work, never use `-Dno-format`' in text, "expected to find: " + 'let the formatting plugins do their work, never use `-Dno-format`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/coding-style/SKILL.md')
    assert '- Update existing code comments if your changes make them invalid' in text, "expected to find: " + '- Update existing code comments if your changes make them invalid'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/writing-tests/SKILL.md')
    assert '- **Prefer AssertJ** (`org.assertj.core.api.Assertions.assertThat`) over JUnit 5' in text, "expected to find: " + '- **Prefer AssertJ** (`org.assertj.core.api.Assertions.assertThat`) over JUnit 5'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/writing-tests/SKILL.md')
    assert 'assertions (`org.junit.jupiter.api.Assertions`). AssertJ provides fluent,' in text, "expected to find: " + 'assertions (`org.junit.jupiter.api.Assertions`). AssertJ provides fluent,'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/writing-tests/SKILL.md')
    assert 'readable assertions and better failure messages.' in text, "expected to find: " + 'readable assertions and better failure messages.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert './mvnw -Dquickly                                                                          # Quick full build (skip tests/docs/native)' in text, "expected to find: " + './mvnw -Dquickly                                                                          # Quick full build (skip tests/docs/native)'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert './mvnw install -f extensions/<name>/                                                      # Build one extension' in text, "expected to find: " + './mvnw install -f extensions/<name>/                                                      # Build one extension'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert './mvnw verify -f extensions/<name>/ -Dtest-containers -Dstart-containers                  # Run extension tests' in text, "expected to find: " + './mvnw verify -f extensions/<name>/ -Dtest-containers -Dstart-containers                  # Run extension tests'[:80]

