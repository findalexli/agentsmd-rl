"""Behavioral checks for awesome-copilot-fix-links-in-skillmd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-copilot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-spring-boot-java-project/SKILL.md')
    assert '- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](#download-spring-boot-project-template)' in text, "expected to find: " + '- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](#download-spring-boot-project-template)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-spring-boot-java-project/SKILL.md')
    assert '- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](#download-spring-boot-project-template)' in text, "expected to find: " + '- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](#download-spring-boot-project-template)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-spring-boot-kotlin-project/SKILL.md')
    assert '- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](#download-spring-boot-project-template)' in text, "expected to find: " + '- If you need to custom the project name, please change the `artifactId` and the `packageName` in [download-spring-boot-project-template](#download-spring-boot-project-template)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/create-spring-boot-kotlin-project/SKILL.md')
    assert '- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](#download-spring-boot-project-template)' in text, "expected to find: " + '- If you need to update the Spring Boot version, please change the `bootVersion` in [download-spring-boot-project-template](#download-spring-boot-project-template)'[:80]

