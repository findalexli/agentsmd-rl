"""Behavioral checks for wheels-update-the-use-of-orm (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wheels")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/CLAUDE.md')
    assert 'return findAll(where="createdat >= \'#local.startOfMonth#\'");' in text, "expected to find: " + 'return findAll(where="createdat >= \'#local.startOfMonth#\'");'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/controllers/CLAUDE.md')
    assert 'local.where = "name LIKE \'%#params.q#%\' OR description LIKE \'%#params.q#%\'";' in text, "expected to find: " + 'local.where = "name LIKE \'%#params.q#%\' OR description LIKE \'%#params.q#%\'";'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/controllers/CLAUDE.md')
    assert 'where="name LIKE \'%#params.q#%\' OR description LIKE \'%#params.q#%\'",' in text, "expected to find: " + 'where="name LIKE \'%#params.q#%\' OR description LIKE \'%#params.q#%\'",'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/controllers/CLAUDE.md')
    assert 'products = model("Product").findAll(where = local.where);' in text, "expected to find: " + 'products = model("Product").findAll(where = local.where);'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/jobs/CLAUDE.md')
    assert 'where="status = \'pending\' AND runAt <= now()",' in text, "expected to find: " + 'where="status = \'pending\' AND runAt <= now()",'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/jobs/CLAUDE.md')
    assert 'where="createdAt < \'#arguments.cutoffDate#\'"' in text, "expected to find: " + 'where="createdAt < \'#arguments.cutoffDate#\'"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/jobs/CLAUDE.md')
    assert 'where="enabled = true AND nextRun <= now()"' in text, "expected to find: " + 'where="enabled = true AND nextRun <= now()"'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/lib/CLAUDE.md')
    assert 'while (model("Article").findOne(where = "slug = \'#this.slug#\' AND id != #this.id ?: 0#")) {' in text, "expected to find: " + 'while (model("Article").findOne(where = "slug = \'#this.slug#\' AND id != #this.id ?: 0#")) {'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/mailers/CLAUDE.md')
    assert 'local.user = model("User").findOne(where = "email = \'#params.email#\'");' in text, "expected to find: " + 'local.user = model("User").findOne(where = "email = \'#params.email#\'");'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/mailers/CLAUDE.md')
    assert 'where = "active = true AND subscriptionType IN (\'newsletter\',\'all\')"' in text, "expected to find: " + 'where = "active = true AND subscriptionType IN (\'newsletter\',\'all\')"'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/models/CLAUDE.md')
    assert 'where="(email = \'#arguments.identifier#\' OR username = \'#arguments.identifier#\') AND deletedat IS NULL"' in text, "expected to find: " + 'where="(email = \'#arguments.identifier#\' OR username = \'#arguments.identifier#\') AND deletedat IS NULL"'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/models/CLAUDE.md')
    assert 'return findAll(where="publishedAt BETWEEN \'#arguments.startDate#\' AND \'#arguments.endDate#\'");' in text, "expected to find: " + 'return findAll(where="publishedAt BETWEEN \'#arguments.startDate#\' AND \'#arguments.endDate#\'");'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('templates/base/src/app/models/CLAUDE.md')
    assert 'while (model("Product").exists(where="slug = \'#local.slug#\' AND id != \'#this.id ?: 0#\'")) {' in text, "expected to find: " + 'while (model("Product").exists(where="slug = \'#local.slug#\' AND id != \'#this.id ?: 0#\'")) {'[:80]

