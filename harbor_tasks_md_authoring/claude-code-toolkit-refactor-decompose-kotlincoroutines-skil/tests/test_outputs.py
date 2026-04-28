"""Behavioral checks for claude-code-toolkit-refactor-decompose-kotlincoroutines-skil (markdown_authoring task).

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
    text = _read('skills/kotlin-coroutines/SKILL.md')
    assert '3. **Always rethrow CancellationException** -- rethrow it immediately or use specific exception types instead of catching `Exception`.' in text, "expected to find: " + '3. **Always rethrow CancellationException** -- rethrow it immediately or use specific exception types instead of catching `Exception`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/SKILL.md')
    assert '| Concurrency | `references/concurrency-patterns.md` | Scopes, cancellation, dispatchers, exception handling |' in text, "expected to find: " + '| Concurrency | `references/concurrency-patterns.md` | Scopes, cancellation, dispatchers, exception handling |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/SKILL.md')
    assert '| Anti-patterns | `references/anti-patterns.md` | GlobalScope, unstructured launch, CancellationException |' in text, "expected to find: " + '| Anti-patterns | `references/anti-patterns.md` | GlobalScope, unstructured launch, CancellationException |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/anti-patterns.md')
    assert 'Always rethrow CancellationException. Catching `Exception` broadly swallows the cancellation signal, preventing the coroutine tree from shutting down properly.' in text, "expected to find: " + 'Always rethrow CancellationException. Catching `Exception` broadly swallows the cancellation signal, preventing the coroutine tree from shutting down properly.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/anti-patterns.md')
    assert 'GlobalScope has no lifecycle, no cancellation, and no structured concurrency. Pass a scope from your application framework instead.' in text, "expected to find: " + 'GlobalScope has no lifecycle, no cancellation, and no structured concurrency. Pass a scope from your application framework instead.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/anti-patterns.md')
    assert 'description: "Kotlin coroutine anti-patterns: GlobalScope, unstructured launch, CancellationException swallowing."' in text, "expected to find: " + 'description: "Kotlin coroutine anti-patterns: GlobalScope, unstructured launch, CancellationException swallowing."'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/channel-patterns.md')
    assert 'Channels are hot -- they exist independently of consumers. Use them for producer-consumer patterns and inter-coroutine communication.' in text, "expected to find: " + 'Channels are hot -- they exist independently of consumers. Use them for producer-consumer patterns and inter-coroutine communication.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/channel-patterns.md')
    assert 'description: "Kotlin Channel types, fan-in/fan-out, and producer-consumer patterns."' in text, "expected to find: " + 'description: "Kotlin Channel types, fan-in/fan-out, and producer-consumer patterns."'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/channel-patterns.md')
    assert 'fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {' in text, "expected to find: " + 'fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/concurrency-patterns.md')
    assert 'Every coroutine must belong to a scope. The scope defines the lifetime -- when the scope is cancelled, all its children are cancelled. Tie every coroutine to a scope.' in text, "expected to find: " + 'Every coroutine must belong to a scope. The scope defines the lifetime -- when the scope is cancelled, all its children are cancelled. Tie every coroutine to a scope.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/concurrency-patterns.md')
    assert 'Coroutines use cooperative cancellation. Long-running work must check `isActive` or call suspending functions that respect cancellation.' in text, "expected to find: " + 'Coroutines use cooperative cancellation. Long-running work must check `isActive` or call suspending functions that respect cancellation.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/concurrency-patterns.md')
    assert 'description: "Kotlin structured concurrency: coroutineScope, supervisorScope, cancellation, dispatchers, exception handling."' in text, "expected to find: " + 'description: "Kotlin structured concurrency: coroutineScope, supervisorScope, cancellation, dispatchers, exception handling."'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/flow-patterns.md')
    assert 'Flow is cold -- it does not produce values until collected. Each collector gets its own execution of the flow body.' in text, "expected to find: " + 'Flow is cold -- it does not produce values until collected. Each collector gets its own execution of the flow body.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/flow-patterns.md')
    assert 'description: "Kotlin Flow patterns: cold streams, StateFlow, SharedFlow comparison and usage."' in text, "expected to find: " + 'description: "Kotlin Flow patterns: cold streams, StateFlow, SharedFlow comparison and usage."'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines/references/flow-patterns.md')
    assert '// StateFlow: holds a SINGLE current value, replays latest to new collectors.' in text, "expected to find: " + '// StateFlow: holds a SINGLE current value, replays latest to new collectors.'[:80]

