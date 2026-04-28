"""Behavioral checks for copilot-collections-refactorskills-rename-and-expand-java (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/copilot-collections")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/tsh-implementing-backend/SKILL.md')
    assert '- **Java**: See `./references/java-spring-boot-patterns.md` — Spring IoC, JUnit/REST Assured testing, SLF4J/Logback logging, Hibernate ORM, springdoc-openapi, Spring Cloud Stream async messaging.' in text, "expected to find: " + '- **Java**: See `./references/java-spring-boot-patterns.md` — Spring IoC, JUnit/REST Assured testing, SLF4J/Logback logging, Hibernate ORM, springdoc-openapi, Spring Cloud Stream async messaging.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/tsh-implementing-backend/references/java-patterns.md')
    assert '.github/skills/tsh-implementing-backend/references/java-patterns.md' in text, "expected to find: " + '.github/skills/tsh-implementing-backend/references/java-patterns.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/tsh-implementing-backend/references/java-spring-boot-patterns.md')
    assert '- **Always declare `spring.cloud.function.definition`** in `application.yml` — list all Consumer/Supplier/Function bean names separated by semicolons. Without it, Spring Cloud Stream may fail to recog' in text, "expected to find: " + '- **Always declare `spring.cloud.function.definition`** in `application.yml` — list all Consumer/Supplier/Function bean names separated by semicolons. Without it, Spring Cloud Stream may fail to recog'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/tsh-implementing-backend/references/java-spring-boot-patterns.md')
    assert '**Critical:** Always declare `spring.cloud.function.definition` to explicitly register function beans (Consumer, Supplier, Function). Without it, Spring Cloud Stream cannot distinguish your handlers f' in text, "expected to find: " + '**Critical:** Always declare `spring.cloud.function.definition` to explicitly register function beans (Consumer, Supplier, Function). Without it, Spring Cloud Stream cannot distinguish your handlers f'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/tsh-implementing-backend/references/java-spring-boot-patterns.md')
    assert 'Native compilation produces a standalone binary with ~10× faster startup and lower memory footprint. Use it for short-lived workloads (serverless, CLIs, high-density containers) or when cold-start lat' in text, "expected to find: " + 'Native compilation produces a standalone binary with ~10× faster startup and lower memory footprint. Use it for short-lived workloads (serverless, CLIs, high-density containers) or when cold-start lat'[:80]

