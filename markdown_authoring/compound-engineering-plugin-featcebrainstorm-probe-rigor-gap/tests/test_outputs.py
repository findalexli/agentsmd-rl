"""Behavioral checks for compound-engineering-plugin-featcebrainstorm-probe-rigor-gap (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-brainstorm/SKILL.md')
    assert '- **Rigor probes fire before Phase 2 and are prose, not menus.** Narrowing is legitimate, but Phase 1 cannot end with un-probed rigor gaps. Each scope-appropriate gap from Phase 1.2 fires as a **separ' in text, "expected to find: " + '- **Rigor probes fire before Phase 2 and are prose, not menus.** Narrowing is legitimate, but Phase 1 cannot end with un-probed rigor gaps. Each scope-appropriate gap from Phase 1.2 fires as a **separ'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-brainstorm/SKILL.md')
    assert 'This is agent-internal analysis, not a user-facing checklist. Read the opening, note which gaps actually exist, and raise only those as questions during Phase 1.3 — folded into the normal flow of dial' in text, "expected to find: " + 'This is agent-internal analysis, not a user-facing checklist. Read the opening, note which gaps actually exist, and raise only those as questions during Phase 1.3 — folded into the normal flow of dial'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-brainstorm/SKILL.md')
    assert "- **Attachment gap.** The opening treats a particular solution shape as the thing being built, rather than the value that shape is supposed to deliver, and hasn't been examined against smaller forms t" in text, "expected to find: " + "- **Attachment gap.** The opening treats a particular solution shape as the thing being built, rather than the value that shape is supposed to deliver, and hasn't been examined against smaller forms t"[:80]

