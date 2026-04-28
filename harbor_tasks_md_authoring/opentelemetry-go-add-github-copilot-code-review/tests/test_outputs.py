"""Behavioral checks for opentelemetry-go-add-github-copilot-code-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opentelemetry-go")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Preserve resilience and concurrency safety. Telemetry must not unexpectedly interfere with the host application; make lifecycle, synchronization, and failure-mode invariants explicit in code and tes' in text, "expected to find: " + '- Preserve resilience and concurrency safety. Telemetry must not unexpectedly interfere with the host application; make lifecycle, synchronization, and failure-mode invariants explicit in code and tes'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Prefer designs that keep telemetry easy to use and loosely coupled. Choose sensible defaults, avoid vendor-specific APIs or behavior, and do not force unrelated components to depend on each other.' in text, "expected to find: " + '- Prefer designs that keep telemetry easy to use and loosely coupled. Choose sensible defaults, avoid vendor-specific APIs or behavior, and do not force unrelated components to depend on each other.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Follow the OpenTelemetry specification and semantic conventions. Match span, metric, log, attribute, event, resource, and instrumentation scope behavior to the spec and existing package behavior.' in text, "expected to find: " + '- Follow the OpenTelemetry specification and semantic conventions. Match span, metric, log, attribute, event, resource, and instrumentation scope behavior to the spec and existing package behavior.'[:80]

