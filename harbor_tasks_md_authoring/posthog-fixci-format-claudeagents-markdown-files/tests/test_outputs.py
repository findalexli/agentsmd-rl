"""Behavioral checks for posthog-fixci-format-claudeagents-markdown-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/posthog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ingestion/pipeline-composition-doctor.md')
    assert 'return Promise.resolve(inputs.filter(isValid).map((input) => ok(transform(input))))' in text, "expected to find: " + 'return Promise.resolve(inputs.filter(isValid).map((input) => ok(transform(input))))'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ingestion/pipeline-composition-doctor.md')
    assert 'return Promise.resolve(inputs.map((input) => ok(transform(input))))' in text, "expected to find: " + 'return Promise.resolve(inputs.map((input) => ok(transform(input))))'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ingestion/pipeline-composition-doctor.md')
    assert 'return function batchStep(inputs) {' in text, "expected to find: " + 'return function batchStep(inputs) {'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ingestion/pipeline-step-doctor.md')
    assert 'return function parseStep(input: T): Promise<PipelineResult<T & { parsed: boolean }>> {' in text, "expected to find: " + 'return function parseStep(input: T): Promise<PipelineResult<T & { parsed: boolean }>> {'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ingestion/pipeline-step-doctor.md')
    assert 'return Promise.resolve(ok({ ...input, parsed: true }))' in text, "expected to find: " + 'return Promise.resolve(ok({ ...input, parsed: true }))'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/ingestion/pipeline-step-doctor.md')
    assert 'return function lookupStep(input) {' in text, "expected to find: " + 'return function lookupStep(input) {'[:80]

