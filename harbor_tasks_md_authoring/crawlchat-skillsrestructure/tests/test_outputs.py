"""Behavioral checks for crawlchat-skillsrestructure (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/crawlchat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-collection/SKILL.md')
    assert 'docker exec crawlchat-local-database-1 mongosh --eval \'db.getSiblingDB("crawlchat").getCollection("ScrapeItem").dropIndex("ScrapeItem_knowledgeGroupId_sourcePageId_key")\'' in text, "expected to find: " + 'docker exec crawlchat-local-database-1 mongosh --eval \'db.getSiblingDB("crawlchat").getCollection("ScrapeItem").dropIndex("ScrapeItem_knowledgeGroupId_sourcePageId_key")\''[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-collection/SKILL.md')
    assert 'PrismaClientKnownRequestError: Unique constraint failed on the constraint: `ScrapeItem_knowledgeGroupId_sourcePageId_key`' in text, "expected to find: " + 'PrismaClientKnownRequestError: Unique constraint failed on the constraint: `ScrapeItem_knowledgeGroupId_sourcePageId_key`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-collection/SKILL.md')
    assert 'docker exec crawlchat-local-pgvector-1 psql -U postgres -d crawlchat -c "SELECT COUNT(*) FROM earth_embeddings;"' in text, "expected to find: " + 'docker exec crawlchat-local-pgvector-1 psql -U postgres -d crawlchat -c "SELECT COUNT(*) FROM earth_embeddings;"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-collection/setup-collection.md')
    assert 'skills/claw/setup-collection/setup-collection.md' in text, "expected to find: " + 'skills/claw/setup-collection/setup-collection.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-dev/SKILL.md')
    assert '- **Login page crashes with "RESEND_KEY must be set"**: Ensure `SELF_HOSTED=true` is in `.env` (copied from `.env.example`)' in text, "expected to find: " + '- **Login page crashes with "RESEND_KEY must be set"**: Ensure `SELF_HOSTED=true` is in `.env` (copied from `.env.example`)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-dev/SKILL.md')
    assert '**Note:** If you get `EADDRINUSE: address already in use :::3000`, kill the process first using step 1.' in text, "expected to find: " + '**Note:** If you get `EADDRINUSE: address already in use :::3000`, kill the process first using step 1.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-dev/SKILL.md')
    assert 'browser act --profile openclaw --request \'{"kind": "resize", "width": 1920, "height": 1080}\'' in text, "expected to find: " + 'browser act --profile openclaw --request \'{"kind": "resize", "width": 1920, "height": 1080}\''[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claw/setup-dev/setup-dev.md')
    assert 'skills/claw/setup-dev/setup-dev.md' in text, "expected to find: " + 'skills/claw/setup-dev/setup-dev.md'[:80]

