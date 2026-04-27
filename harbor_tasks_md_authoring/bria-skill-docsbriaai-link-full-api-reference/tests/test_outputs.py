"""Behavioral checks for bria-skill-docsbriaai-link-full-api-reference (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bria-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert 'If you are stuck on request shapes, parameters, or endpoints not covered here, **fetch the full agent-oriented API reference** at [docs.bria.ai/llms.txt](https://docs.bria.ai/llms.txt) — it is the can' in text, "expected to find: " + 'If you are stuck on request shapes, parameters, or endpoints not covered here, **fetch the full agent-oriented API reference** at [docs.bria.ai/llms.txt](https://docs.bria.ai/llms.txt) — it is the can'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert 'For the **complete** Bria API (all endpoints, fields, and behaviors), use **[docs.bria.ai/llms.txt](https://docs.bria.ai/llms.txt)** — agent-ready docs meant for assistants implementing the API. Reach' in text, "expected to find: " + 'For the **complete** Bria API (all endpoints, fields, and behaviors), use **[docs.bria.ai/llms.txt](https://docs.bria.ai/llms.txt)** — agent-ready docs meant for assistants implementing the API. Reach'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bria-ai/SKILL.md')
    assert 'See `references/api-endpoints.md` for complete endpoint documentation with request/response formats for all 20+ endpoints (in-repo companion to the quick reference above).' in text, "expected to find: " + 'See `references/api-endpoints.md` for complete endpoint documentation with request/response formats for all 20+ endpoints (in-repo companion to the quick reference above).'[:80]

