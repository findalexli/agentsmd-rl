"""Behavioral checks for prefect-docs-document-breadcrumbscoping-pattern-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert '**Strict mode on detail pages**: When asserting the name of a resource on its detail page (e.g., a task run or flow run), the name can appear in multiple places — the breadcrumb, the page heading, and' in text, "expected to find: " + '**Strict mode on detail pages**: When asserting the name of a resource on its detail page (e.g., a task run or flow run), the name can appear in multiple places — the breadcrumb, the page heading, and'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert '// ❌ Bad - strict mode violation once logs load and the name appears a second time' in text, "expected to find: " + '// ❌ Bad - strict mode violation once logs load and the name appears a second time'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/e2e/AGENTS.md')
    assert '// ✅ Good - scoped to breadcrumb; avoids matching log metadata that loads later' in text, "expected to find: " + '// ✅ Good - scoped to breadcrumb; avoids matching log metadata that loads later'[:80]

