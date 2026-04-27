"""Behavioral checks for claude-code-plugins-plus-skills-featsupabasepack-build-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/supabase-pack/skills/supabase-cost-tuning/SKILL.md')
    assert 'Reduce Supabase spend by auditing usage against plan limits, eliminating database and storage waste, and right-sizing compute resources. The three biggest levers: database optimization (vacuum, index ' in text, "expected to find: " + 'Reduce Supabase spend by auditing usage against plan limits, eliminating database and storage waste, and right-sizing compute resources. The three biggest levers: database optimization (vacuum, index '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/supabase-pack/skills/supabase-cost-tuning/SKILL.md')
    assert '**Decision framework:** Read replicas ($25/mo each) beat scaling up when reads dominate and you need geographic distribution. Connection pooling (Supavisor, free) reduces compute pressure from idle co' in text, "expected to find: " + '**Decision framework:** Read replicas ($25/mo each) beat scaling up when reads dominate and you need geographic distribution. Connection pooling (Supavisor, free) reduces compute pressure from idle co'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/supabase-pack/skills/supabase-cost-tuning/SKILL.md')
    assert '| VACUUM not reclaiming space | Long-running transactions holding locks | Check `pg_stat_activity` for idle-in-transaction; terminate stale sessions |' in text, "expected to find: " + '| VACUUM not reclaiming space | Long-running transactions holding locks | Check `pg_stat_activity` for idle-in-transaction; terminate stale sessions |'[:80]

