"""Behavioral checks for airweave-cursorrules-add-connectormonke-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/airweave")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/connector-development-end-to-end.mdc')
    assert 'This is the **master guide** for building a complete, production-ready source connector for Airweave. It combines source implementation with comprehensive E2E testing using the Monke framework.' in text, "expected to find: " + 'This is the **master guide** for building a complete, production-ready source connector for Airweave. It combines source implementation with comprehensive E2E testing using the Monke framework.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/connector-development-end-to-end.mdc')
    assert "**The key to success:** Test comprehensively. Don't just test tasks—test comments, files, and all nested entities. If your connector syncs it, your tests should verify it." in text, "expected to find: " + "**The key to success:** Test comprehensively. Don't just test tasks—test comments, files, and all nested entities. If your connector syncs it, your tests should verify it."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/connector-development-end-to-end.mdc')
    assert '**Note:** The human has already set up the authentication portion of this config (either Composio or direct auth).' in text, "expected to find: " + '**Note:** The human has already set up the authentication portion of this config (either Composio or direct auth).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/monke-testing-guide.mdc')
    assert "**Monke** is Airweave's end-to-end testing framework for source connectors. It creates real test data in external systems, triggers syncs, and verifies data appears correctly in the search index." in text, "expected to find: " + "**Monke** is Airweave's end-to-end testing framework for source connectors. It creates real test data in external systems, triggers syncs, and verifies data appears correctly in the search index."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/monke-testing-guide.mdc')
    assert '**Note:** The Asana example creates comments but does NOT verify them. This is a bug that should be fixed. Your implementation should verify ALL entity types.' in text, "expected to find: " + '**Note:** The Asana example creates comments but does NOT verify them. This is a bug that should be fixed. Your implementation should verify ALL entity types.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/monke-testing-guide.mdc')
    assert '**Problem:** Many connector tests only verify top-level entities (e.g., tasks) but ignore nested entities (e.g., comments, files).' in text, "expected to find: " + '**Problem:** Many connector tests only verify top-level entities (e.g., tasks) but ignore nested entities (e.g., comments, files).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/source-connector-implementation.mdc')
    assert 'A **source connector** in Airweave is a Python module that extracts data from an external service and transforms it into searchable entities. This guide covers everything you need to build a productio' in text, "expected to find: " + 'A **source connector** in Airweave is a Python module that extracts data from an external service and transforms it into searchable entities. This guide covers everything you need to build a productio'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/source-connector-implementation.mdc')
    assert '**Note:** The human has already set up OAuth credentials here. This configuration exists and contains the client_id, client_secret, and scopes for your connector.' in text, "expected to find: " + '**Note:** The human has already set up OAuth credentials here. This configuration exists and contains the client_id, client_secret, and scopes for your connector.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/source-connector-implementation.mdc')
    assert "1. **Forgetting timestamps** - Without `is_created_at` or `is_updated_at`, incremental sync won't work" in text, "expected to find: " + "1. **Forgetting timestamps** - Without `is_created_at` or `is_updated_at`, incremental sync won't work"[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/source-integration-rules.mdc')
    assert '.cursor/rules/source-integration-rules.mdc' in text, "expected to find: " + '.cursor/rules/source-integration-rules.mdc'[:80]

