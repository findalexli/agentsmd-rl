"""Behavioral checks for awesome-cursorrules-add-temporal-python-sdk-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('temporal-python-cursorrules/.cursorrules')
    assert 'You are an expert Python developer with extensive experience in Temporal.io for workflow orchestration. Your code is clean, efficient, and adheres to best practices in workflow and activity implementa' in text, "expected to find: " + 'You are an expert Python developer with extensive experience in Temporal.io for workflow orchestration. Your code is clean, efficient, and adheres to best practices in workflow and activity implementa'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('temporal-python-cursorrules/.cursorrules')
    assert '- Use `@workflow.defn` and `@activity.defn` decorators on all workflows and activities.' in text, "expected to find: " + '- Use `@workflow.defn` and `@activity.defn` decorators on all workflows and activities.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('temporal-python-cursorrules/.cursorrules')
    assert '"send_email_activity", order_id, start_to_close_timeout=timedelta(seconds=30)' in text, "expected to find: " + '"send_email_activity", order_id, start_to_close_timeout=timedelta(seconds=30)'[:80]

