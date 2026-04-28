"""Behavioral checks for neo-featprreview-codify-mcptooldescription-budget-audit (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/assets/pr-review-template.md')
    assert '*(Required per guide §5.3 when the PR touches `ai/mcp/server/*/openapi.yaml` — adds a new `description:`, modifies an existing block-literal `description:`, or introduces a new tool path or operation.' in text, "expected to find: " + '*(Required per guide §5.3 when the PR touches `ai/mcp/server/*/openapi.yaml` — adds a new `description:`, modifies an existing block-literal `description:`, or introduces a new tool path or operation.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/assets/pr-review-template.md')
    assert '- [ ] No internal cross-refs (no ticket numbers, Phase sequencing, session IDs, or memory anchor names in the description payload)' in text, "expected to find: " + '- [ ] No internal cross-refs (no ticket numbers, Phase sequencing, session IDs, or memory anchor names in the description payload)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/assets/pr-review-template.md')
    assert '- [ ] No architectural narrative — descriptions describe call-site usage (what + when-to-use + when-not-to-use)' in text, "expected to find: " + '- [ ] No architectural narrative — descriptions describe call-site usage (what + when-to-use + when-not-to-use)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert "**Empirical anchor:** PR #10340's initial `task` parameter description on `mailbox/messages` was a ~600-char block-literal with internal Phase 1/Phase 2 framing and ticket cross-refs (#10334/#10313/#1" in text, "expected to find: " + "**Empirical anchor:** PR #10340's initial `task` parameter description on `mailbox/messages` was a ~600-char block-literal with internal Phase 1/Phase 2 framing and ticket cross-refs (#10334/#10313/#1"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert '**The Rule:** OpenAPI tool-parameter and operation descriptions are runtime payload, not source-code documentation. Their audience is the agent enumerating the tool surface — not the developer reading' in text, "expected to find: " + '**The Rule:** OpenAPI tool-parameter and operation descriptions are runtime payload, not source-code documentation. Their audience is the agent enumerating the tool surface — not the developer reading'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert "When a PR touches `ai/mcp/server/*/openapi.yaml`, audit each modified or added tool description for budget compliance. Tool descriptions are loaded into every consuming agent's context window when the" in text, "expected to find: " + "When a PR touches `ai/mcp/server/*/openapi.yaml`, audit each modified or added tool description for budget compliance. Tool descriptions are loaded into every consuming agent's context window when the"[:80]

