"""Behavioral checks for dotnet-skills-docs-add-actor-logging-and (markdown_authoring task).

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
    text = _read('skills/akka-best-practices/SKILL.md')
    assert 'When actors launch async operations via `PipeTo`, those operations can outlive the actor if not properly managed. Use `CancellationToken` tied to the actor lifecycle.' in text, "expected to find: " + 'When actors launch async operations via `PipeTo`, those operations can outlive the actor if not properly managed. Use `CancellationToken` tied to the actor lifecycle.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka-best-practices/SKILL.md')
    assert 'As of Akka.NET v1.5.57, `ILoggingAdapter` supports semantic/structured logging with named placeholders:' in text, "expected to find: " + 'As of Akka.NET v1.5.57, `ILoggingAdapter` supports semantic/structured logging with named placeholders:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/akka-best-practices/SKILL.md')
    assert 'In actors, use `ILoggingAdapter` from `Context.GetLogger()` instead of DI-injected `ILogger<T>`:' in text, "expected to find: " + 'In actors, use `ILoggingAdapter` from `Context.GetLogger()` instead of DI-injected `ILogger<T>`:'[:80]

