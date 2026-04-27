"""Behavioral checks for antigravity-awesome-skills-feat-add-nosqlexpert-skill-for (markdown_authoring task).

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
    text = _read('skills/nosql-expert/SKILL.md')
    assert 'description: "Expert guidance for distributed NoSQL databases (Cassandra, DynamoDB). Focuses on mental models, query-first modeling, single-table design, and avoiding hot partitions in high-scale syst' in text, "expected to find: " + 'description: "Expert guidance for distributed NoSQL databases (Cassandra, DynamoDB). Focuses on mental models, query-first modeling, single-table design, and avoiding hot partitions in high-scale syst'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nosql-expert/SKILL.md')
    assert '-   [ ] **Split Partition Risk:** For any single partition (e.g., a single user\'s orders), will it grow indefinitely? (If > 10GB, you need to "shard" the partition, e.g., `USER#123#2024-01`).' in text, "expected to find: " + '-   [ ] **Split Partition Risk:** For any single partition (e.g., a single user\'s orders), will it grow indefinitely? (If > 10GB, you need to "shard" the partition, e.g., `USER#123#2024-01`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nosql-expert/SKILL.md')
    assert '❌ **Relational Modeling:** Creating `Author` and `Book` tables and trying to join them in code. (Instead, embed Book summaries in Author, or duplicate Author info in Books).' in text, "expected to find: " + '❌ **Relational Modeling:** Creating `Author` and `Book` tables and trying to join them in code. (Instead, embed Book summaries in Author, or duplicate Author info in Books).'[:80]

