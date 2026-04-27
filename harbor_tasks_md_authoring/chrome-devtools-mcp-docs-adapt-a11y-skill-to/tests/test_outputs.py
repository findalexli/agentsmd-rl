"""Behavioral checks for chrome-devtools-mcp-docs-adapt-a11y-skill-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chrome-devtools-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert 'node -e "const r=require(\'./report.json\'); Object.values(r.audits).filter(a=>a.score!==null && a.score<1).forEach(a=>console.log(JSON.stringify({id:a.id, title:a.title, items:a.details?.items})))"' in text, "expected to find: " + 'node -e "const r=require(\'./report.json\'); Object.values(r.audits).filter(a=>a.score!==null && a.score<1).forEach(a=>console.log(JSON.stringify({id:a.id, title:a.title, items:a.details?.items})))"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert 'Start by running a Lighthouse accessibility audit to get a comprehensive baseline. This tool provides a high-level score and lists specific failing elements with remediation advice.' in text, "expected to find: " + 'Start by running a Lighthouse accessibility audit to get a comprehensive baseline. This tool provides a high-level score and lists specific failing elements with remediation advice.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert '- **Parsing**: Do not read the entire file line-by-line. Use a CLI tool like `jq` or a Node.js one-liner to filter for failures:' in text, "expected to find: " + '- **Parsing**: Do not read the entire file line-by-line. Use a CLI tool like `jq` or a Node.js one-liner to filter for failures:'[:80]

