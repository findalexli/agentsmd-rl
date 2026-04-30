"""Behavioral checks for claude-code-toolkit-refactor-decompose-swiftconcurrency-skil (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/SKILL.md')
    assert "Pattern catalog for Swift's structured concurrency model: async/await, Actors, TaskGroups, AsyncSequence, Sendable, and cancellation. Load the reference file matching the developer's question." in text, "expected to find: " + "Pattern catalog for Swift's structured concurrency model: async/await, Actors, TaskGroups, AsyncSequence, Sendable, and cancellation. Load the reference file matching the developer's question."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/SKILL.md')
    assert '| TaskGroup, AsyncSequence, AsyncStream, cancellation | references/task-patterns.md | Structured concurrency, rate-limited groups, streams, cancellation |' in text, "expected to find: " + '| TaskGroup, AsyncSequence, AsyncStream, cancellation | references/task-patterns.md | Structured concurrency, rate-limited groups, streams, cancellation |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/SKILL.md')
    assert '| Actor, @MainActor, nonisolated | references/actor-isolation.md | Actor isolation, MainActor UI confinement, nonisolated opt-out |' in text, "expected to find: " + '| Actor, @MainActor, nonisolated | references/actor-isolation.md | Actor isolation, MainActor UI confinement, nonisolated opt-out |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/actor-isolation.md')
    assert 'Use `nonisolated` to opt specific methods out of actor isolation when they only read immutable state or perform no state access.' in text, "expected to find: " + 'Use `nonisolated` to opt specific methods out of actor isolation when they only read immutable state or perform no state access.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/actor-isolation.md')
    assert 'Actors protect mutable state from data races. Only one task can execute on an actor at a time.' in text, "expected to find: " + 'Actors protect mutable state from data races. Only one task can execute on an actor at a time.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/actor-isolation.md')
    assert 'description: "Actor isolation, @MainActor, nonisolated patterns with code examples."' in text, "expected to find: " + 'description: "Actor isolation, @MainActor, nonisolated patterns with code examples."'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/anti-patterns.md')
    assert 'Awaiting inside an actor method yields the actor, allowing other callers to mutate state before your method resumes. Always re-validate state after an `await`.' in text, "expected to find: " + 'Awaiting inside an actor method yields the actor, allowing other callers to mutate state before your method resumes. Always re-validate state after an `await`.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/anti-patterns.md')
    assert 'Never perform synchronous blocking work on `@MainActor`. Offload heavy computation to a detached task or a background actor.' in text, "expected to find: " + 'Never perform synchronous blocking work on `@MainActor`. Offload heavy computation to a detached task or a background actor.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/anti-patterns.md')
    assert 'Creating `Task { }` without storing or cancelling it leads to leaked work that outlives its logical scope.' in text, "expected to find: " + 'Creating `Task { }` without storing or cancelling it leads to leaked work that outlives its logical scope.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/fundamentals.md')
    assert 'The `Sendable` protocol marks types safe to transfer across concurrency domains. The compiler enforces this at build time with strict concurrency checking.' in text, "expected to find: " + 'The `Sendable` protocol marks types safe to transfer across concurrency domains. The compiler enforces this at build time with strict concurrency checking.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/fundamentals.md')
    assert '`Task { }` creates unstructured work that inherits the current actor context. `Task.detached` creates work with no inherited context -- use it sparingly.' in text, "expected to find: " + '`Task { }` creates unstructured work that inherits the current actor context. `Task.detached` creates work with no inherited context -- use it sparingly.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/fundamentals.md')
    assert 'Mark functions that perform asynchronous work with `async`. Use `throws` alongside `async` for fallible operations. Call async functions with `await`.' in text, "expected to find: " + 'Mark functions that perform asynchronous work with `async`. Use `throws` alongside `async` for fallible operations. Call async functions with `await`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/task-patterns.md')
    assert '`AsyncSequence` is the async counterpart to `Sequence`. Use `AsyncStream` to bridge callback-based APIs into structured concurrency.' in text, "expected to find: " + '`AsyncSequence` is the async counterpart to `Sequence`. Use `AsyncStream` to bridge callback-based APIs into structured concurrency.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/task-patterns.md')
    assert 'Structured concurrency propagates cancellation automatically through task hierarchies. Check for cancellation in long-running work.' in text, "expected to find: " + 'Structured concurrency propagates cancellation automatically through task hierarchies. Check for cancellation in long-running work.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/swift-concurrency/references/task-patterns.md')
    assert 'for await notification in NotificationCenter.default.notifications(named: .userDidUpdate) {' in text, "expected to find: " + 'for await notification in NotificationCenter.default.notifications(named: .userDidUpdate) {'[:80]

