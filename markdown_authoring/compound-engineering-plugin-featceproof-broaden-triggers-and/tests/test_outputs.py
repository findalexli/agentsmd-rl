"""Behavioral checks for compound-engineering-plugin-featceproof-broaden-triggers-and (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-proof/SKILL.md')
    assert 'description: Create, share, view, comment on, edit, and run human-in-the-loop review loops over markdown documents via Proof — the collaborative markdown editor and renderer at proofeditor.ai (also ca' in text, "expected to find: " + 'description: Create, share, view, comment on, edit, and run human-in-the-loop review loops over markdown documents via Proof — the collaborative markdown editor and renderer at proofeditor.ai (also ca'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-proof/SKILL.md')
    assert '- **Direct user request** — a bare user phrase naming a local markdown file and asking to iterate collaboratively via Proof: "share this to proof so we can iterate", "iterate with proof on this doc", ' in text, "expected to find: " + '- **Direct user request** — a bare user phrase naming a local markdown file and asking to iterate collaboratively via Proof: "share this to proof so we can iterate", "iterate with proof on this doc", '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-proof/SKILL.md')
    assert "Human-in-the-loop iteration over an existing local markdown file: upload to Proof, let the user annotate in Proof's web UI, ingest feedback as in-thread replies and tracked edits, and sync the final d" in text, "expected to find: " + "Human-in-the-loop iteration over an existing local markdown file: upload to Proof, let the user annotate in Proof's web UI, ingest feedback as in-thread replies and tracked edits, and sync the final d"[:80]

