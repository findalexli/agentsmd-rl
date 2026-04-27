"""Behavioral checks for antigravity-awesome-skills-feat-add-android-modern-developme (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/android-jetpack-compose-expert/SKILL.md')
    assert '**Solution:** Check if you are creating new object instances (like `List` or `Modifier`) inside the composition without `remember`, or if you are updating state inside the composition phase instead of' in text, "expected to find: " + '**Solution:** Check if you are creating new object instances (like `List` or `Modifier`) inside the composition without `remember`, or if you are updating state inside the composition phase instead of'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/android-jetpack-compose-expert/SKILL.md')
    assert 'A comprehensive guide for building production-quality Android applications using Jetpack Compose. This skill covers architectural patterns, state management with ViewModels, navigation type-safety, an' in text, "expected to find: " + 'A comprehensive guide for building production-quality Android applications using Jetpack Compose. This skill covers architectural patterns, state management with ViewModels, navigation type-safety, an'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/android-jetpack-compose-expert/SKILL.md')
    assert '- ✅ **Do:** Mark data classes used in UI state as `@Immutable` or `@Stable` if they contain `List` or other unstable types to enable smart recomposition skipping.' in text, "expected to find: " + '- ✅ **Do:** Mark data classes used in UI state as `@Immutable` or `@Stable` if they contain `List` or other unstable types to enable smart recomposition skipping.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines-expert/SKILL.md')
    assert 'A guide to mastering asynchronous programming with Kotlin Coroutines. Covers advanced topics like structured concurrency, `Flow` transformations, exception handling, and testing strategies.' in text, "expected to find: " + 'A guide to mastering asynchronous programming with Kotlin Coroutines. Covers advanced topics like structured concurrency, `Flow` transformations, exception handling, and testing strategies.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines-expert/SKILL.md')
    assert 'Always launch coroutines within a defined `CoroutineScope`. Use `coroutineScope` or `supervisorScope` to group concurrent tasks.' in text, "expected to find: " + 'Always launch coroutines within a defined `CoroutineScope`. Use `coroutineScope` or `supervisorScope` to group concurrent tasks.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotlin-coroutines-expert/SKILL.md')
    assert 'Use `CoroutineExceptionHandler` for top-level scopes, but rely on `try-catch` within suspending functions for granular control.' in text, "expected to find: " + 'Use `CoroutineExceptionHandler` for top-level scopes, but rely on `try-catch` within suspending functions for granular control.'[:80]

