"""Behavioral checks for antigravity-awesome-skills-featzipaioptimizer-upgrade-to-v12 (markdown_authoring task).

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
    text = _read('skills/zipai-optimizer/SKILL.md')
    assert '- **MCP tool responses:** treat as structured data. Use field-level access (`result.items`, `result.pageInfo`) rather than full-object inspection. Paginate only when the target entity is not found on ' in text, "expected to find: " + '- **MCP tool responses:** treat as structured data. Use field-level access (`result.items`, `result.pageInfo`) rather than full-object inspection. Paginate only when the target entity is not found on '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/zipai-optimizer/SKILL.md')
    assert '- **MCP Pagination Truncation:** Lazy pagination stops early on first match — may miss duplicate entity names in large datasets. Override by specifying `paginate:full` explicitly in the request.' in text, "expected to find: " + '- **MCP Pagination Truncation:** Lazy pagination stops early on first match — may miss duplicate entity names in large datasets. Override by specifying `paginate:full` explicitly in the request.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/zipai-optimizer/SKILL.md')
    assert '- **Regression guard:** when modifying a function or module, explicitly check and mention if existing tests cover the changed path. If none exist, flag as `[RISK: untested path]`.' in text, "expected to find: " + '- **Regression guard:** when modifying a function or module, explicitly check and mention if existing tests cover the changed path. If none exist, flag as `[RISK: untested path]`.'[:80]

