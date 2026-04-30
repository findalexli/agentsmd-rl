"""Behavioral checks for eclipse.platform.ui-add-claudemd-for-repository-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eclipse.platform.ui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Eclipse Platform UI provides the UI building blocks for Eclipse IDE and Eclipse Rich Client Platform (RCP). This includes JFace, workbench, commands framework, data binding, dialogs, editors, views, p' in text, "expected to find: " + 'Eclipse Platform UI provides the UI building blocks for Eclipse IDE and Eclipse Rich Client Platform (RCP). This includes JFace, workbench, commands framework, data binding, dialogs, editors, views, p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**⚠️ IMPORTANT:** Use `mvn verify` (NOT `mvn test`) for Tycho projects. Due to Maven Tycho lifecycle binding, tests run in the `integration-test` phase, not the `test` phase. Running `mvn test` will N' in text, "expected to find: " + '**⚠️ IMPORTANT:** Use `mvn verify` (NOT `mvn test`) for Tycho projects. Due to Maven Tycho lifecycle binding, tests run in the `integration-test` phase, not the `test` phase. Running `mvn test` will N'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**⚠️ IMPORTANT:** Standalone `mvn clean verify` at repository root **WILL FAIL** with "Non-resolvable parent POM" error. This repository requires a parent POM from `eclipse.platform.releng.aggregator`' in text, "expected to find: " + '**⚠️ IMPORTANT:** Standalone `mvn clean verify` at repository root **WILL FAIL** with "Non-resolvable parent POM" error. This repository requires a parent POM from `eclipse.platform.releng.aggregator`'[:80]

