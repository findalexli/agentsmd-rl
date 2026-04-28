"""Behavioral checks for dotnet-skills-first-version-of-an-opentelemetry (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/opentelementry-dotnet-instrumentation/skill.md')
    assert 'description: Provides guidance for implementing OpenTelemetry instrumentation in .NET codebases, covering tracing (Activities/Spans), metrics, naming conventions, error handling, performance, and API ' in text, "expected to find: " + 'description: Provides guidance for implementing OpenTelemetry instrumentation in .NET codebases, covering tracing (Activities/Spans), metrics, naming conventions, error handling, performance, and API '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/opentelementry-dotnet-instrumentation/skill.md')
    assert 'Provides guidance for implementing OpenTelemetry instrumentation in .NET codebases, covering tracing (Activities/Spans), metrics, naming conventions, error handling, performance, and API design best p' in text, "expected to find: " + 'Provides guidance for implementing OpenTelemetry instrumentation in .NET codebases, covering tracing (Activities/Spans), metrics, naming conventions, error handling, performance, and API design best p'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/opentelementry-dotnet-instrumentation/skill.md')
    assert '- Follow Microsoft best practices for [distributed tracing instrumentation](https://docs.microsoft.com/en-us/dotnet/core/diagnostics/distributed-tracing-instrumentation-walkthroughs)' in text, "expected to find: " + '- Follow Microsoft best practices for [distributed tracing instrumentation](https://docs.microsoft.com/en-us/dotnet/core/diagnostics/distributed-tracing-instrumentation-walkthroughs)'[:80]

