"""Behavioral checks for neo-featskills-introduce-rhetoricaldrift-audit-to (markdown_authoring task).

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
    assert '*(Required when the PR carries substantive architectural prose — PR description framing, Anchor & Echo JSDoc additions, `[RETROSPECTIVE]` tags, or linked-anchor citations. Mark N/A for routine code wi' in text, "expected to find: " + '*(Required when the PR carries substantive architectural prose — PR description framing, Anchor & Echo JSDoc additions, `[RETROSPECTIVE]` tags, or linked-anchor citations. Mark N/A for routine code wi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/assets/pr-review-template.md')
    assert '*Do NOT use pre-ticked placeholder items like `- [x] All checks pass and no required changes identified.` — that reads as box-checking, not genuine review. Per guide §5 Zero-Issue PR Semantics + §7.5 ' in text, "expected to find: " + '*Do NOT use pre-ticked placeholder items like `- [x] All checks pass and no required changes identified.` — that reads as box-checking, not genuine review. Per guide §5 Zero-Issue PR Semantics + §7.5 '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/assets/pr-review-template.md')
    assert '- [ ] `[RETROSPECTIVE]` tag: accurately characterizes what shipped (no inflation of architectural significance)' in text, "expected to find: " + '- [ ] `[RETROSPECTIVE]` tag: accurately characterizes what shipped (no inflation of architectural significance)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert 'A review can hit every structural metric, document its search, pass §7.1-§7.3 — and still let through prose that drifts away from mechanical reality. **Rhetorical Drift** is the divergence of stated f' in text, "expected to find: " + 'A review can hit every structural metric, document its search, pass §7.1-§7.3 — and still let through prose that drifts away from mechanical reality. **Rhetorical Drift** is the divergence of stated f'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert '- **PR #10371** review (2026-04-26): initial Cycle 1 framing of Step 6 (A2A self-ping) and Step 7 (Sandman memory) as "redundant push-pull substrates" drifted from the mechanical reality that the subs' in text, "expected to find: " + '- **PR #10371** review (2026-04-26): initial Cycle 1 framing of Step 6 (A2A self-ping) and Step 7 (Sandman memory) as "redundant push-pull substrates" drifted from the mechanical reality that the subs'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pr-review/references/pr-review-guide.md')
    assert '- **PR #10298** (`industry-friction-radar`, 2026-04-24): initial framing claimed the radar ingests "SOTA" patterns when the implementation explicitly filters out industry standards (rationale: industr' in text, "expected to find: " + '- **PR #10298** (`industry-friction-radar`, 2026-04-24): initial framing claimed the radar ingests "SOTA" patterns when the implementation explicitly filters out industry standards (rationale: industr'[:80]

