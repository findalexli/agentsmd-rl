"""Behavioral checks for orchestkit-feat-update-claude-skills-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/orchestkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/database-engineer.md')
    assert '6. Ensure PostgreSQL 18 modern features are used' in text, "expected to find: " + '6. Ensure PostgreSQL 18 modern features are used'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-design-framework/examples/skillforge-api-design.md')
    assert '# PostgreSQL 18 generates UUID v7 via server_default=text("uuidv7()")' in text, "expected to find: " + '# PostgreSQL 18 generates UUID v7 via server_default=text("uuidv7()")'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-design-framework/examples/skillforge-api-design.md')
    assert 'analysis_id=analysis_uuid,  # None → DB generates UUID v7' in text, "expected to find: " + 'analysis_id=analysis_uuid,  # None → DB generates UUID v7'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/api-design-framework/examples/skillforge-api-design.md')
    assert '# 2. Normalize custom analysis_id if provided (optional)' in text, "expected to find: " + '# 2. Normalize custom analysis_id if provided (optional)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/langgraph-human-in-loop/SKILL.md')
    assert 'import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)' in text, "expected to find: " + 'import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/langgraph-human-in-loop/SKILL.md')
    assert 'config = {"configurable": {"thread_id": str(uuid_utils.uuid7())}}' in text, "expected to find: " + 'config = {"configurable": {"thread_id": str(uuid_utils.uuid7())}}'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/langgraph-supervisor/examples/skillforge-analysis-workflow.md')
    assert 'async def analyze_content(url: str, content: str, db: AsyncSession = Depends(get_db)):' in text, "expected to find: " + 'async def analyze_content(url: str, content: str, db: AsyncSession = Depends(get_db)):'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/langgraph-supervisor/examples/skillforge-analysis-workflow.md')
    assert '# Create analysis record - PostgreSQL 18 generates UUID v7 via server_default' in text, "expected to find: " + '# Create analysis record - PostgreSQL 18 generates UUID v7 via server_default'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/langgraph-supervisor/examples/skillforge-analysis-workflow.md')
    assert 'analysis = Analysis(url=url, content_type="article", status="pending")' in text, "expected to find: " + 'analysis = Analysis(url=url, content_type="article", status="pending")'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/observability-monitoring/SKILL.md')
    assert 'correlation_id = request.headers.get("X-Correlation-ID") or str(uuid_utils.uuid7())' in text, "expected to find: " + 'correlation_id = request.headers.get("X-Correlation-ID") or str(uuid_utils.uuid7())'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/observability-monitoring/SKILL.md')
    assert '# Get or generate correlation ID (UUID v7 for time-ordering in distributed traces)' in text, "expected to find: " + '# Get or generate correlation ID (UUID v7 for time-ordering in distributed traces)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/observability-monitoring/SKILL.md')
    assert 'import uuid_utils  # pip install uuid-utils (UUID v7 support for Python < 3.14)' in text, "expected to find: " + 'import uuid_utils  # pip install uuid-utils (UUID v7 support for Python < 3.14)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/observability-monitoring/checklists/monitoring-implementation-checklist.md')
    assert 'correlation_id = request.headers.get("X-Correlation-ID") or str(uuid_utils.uuid7())' in text, "expected to find: " + 'correlation_id = request.headers.get("X-Correlation-ID") or str(uuid_utils.uuid7())'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/observability-monitoring/checklists/monitoring-implementation-checklist.md')
    assert 'import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)' in text, "expected to find: " + 'import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/observability-monitoring/checklists/monitoring-implementation-checklist.md')
    assert '# Get or generate correlation ID (UUID v7 for time-ordering in traces)' in text, "expected to find: " + '# Get or generate correlation ID (UUID v7 for time-ordering in traces)'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pgvector-search/references/metadata-filtering.md')
    assert 'import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)' in text, "expected to find: " + 'import uuid_utils  # pip install uuid-utils (UUID v7 for Python < 3.14)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pgvector-search/references/metadata-filtering.md')
    assert 'id=uuid_utils.uuid7(),' in text, "expected to find: " + 'id=uuid_utils.uuid7(),'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/unit-testing/examples/skillforge-test-strategy.md')
    assert 'image: pgvector/pgvector:pg18' in text, "expected to find: " + 'image: pgvector/pgvector:pg18'[:80]

