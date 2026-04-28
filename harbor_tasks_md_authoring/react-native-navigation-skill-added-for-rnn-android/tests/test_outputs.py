"""Behavioral checks for react-native-navigation-skill-added-for-rnn-android (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/react-native-navigation")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/rnn-codebase/SKILL.md')
    assert 'description: Navigate and work with the react-native-navigation (RNN) codebase. Use when fixing bugs, adding features, tracing command flows, understanding options resolution, or working across JS/iOS' in text, "expected to find: " + 'description: Navigate and work with the react-native-navigation (RNN) codebase. Use when fixing bugs, adding features, tracing command flows, understanding options resolution, or working across JS/iOS'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/rnn-codebase/SKILL.md')
    assert '- **`android/src/main/java/com/reactnativenavigation/`** — All Java/Kotlin native code. See [android/ARCHITECTURE.md](../../android/ARCHITECTURE.md)' in text, "expected to find: " + '- **`android/src/main/java/com/reactnativenavigation/`** — All Java/Kotlin native code. See [android/ARCHITECTURE.md](../../android/ARCHITECTURE.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/rnn-codebase/SKILL.md')
    assert '| Animations | `src/interfaces/Options.ts` (AnimationOptions) | `ios/ScreenAnimationController.mm` | `viewcontrollers/stack/StackAnimator.kt` |' in text, "expected to find: " + '| Animations | `src/interfaces/Options.ts` (AnimationOptions) | `ios/ScreenAnimationController.mm` | `viewcontrollers/stack/StackAnimator.kt` |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/rnn-codebase/SKILL.md')
    assert 'description: Navigate and work with the react-native-navigation (RNN) codebase. Use when fixing bugs, adding features, tracing command flows, understanding options resolution, or working across JS/iOS' in text, "expected to find: " + 'description: Navigate and work with the react-native-navigation (RNN) codebase. Use when fixing bugs, adding features, tracing command flows, understanding options resolution, or working across JS/iOS'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/rnn-codebase/SKILL.md')
    assert '- **`android/src/main/java/com/reactnativenavigation/`** — All Java/Kotlin native code. See [android/ARCHITECTURE.md](../../android/ARCHITECTURE.md)' in text, "expected to find: " + '- **`android/src/main/java/com/reactnativenavigation/`** — All Java/Kotlin native code. See [android/ARCHITECTURE.md](../../android/ARCHITECTURE.md)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/rnn-codebase/SKILL.md')
    assert '| Animations | `src/interfaces/Options.ts` (AnimationOptions) | `ios/ScreenAnimationController.mm` | `viewcontrollers/stack/StackAnimator.kt` |' in text, "expected to find: " + '| Animations | `src/interfaces/Options.ts` (AnimationOptions) | `ios/ScreenAnimationController.mm` | `viewcontrollers/stack/StackAnimator.kt` |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/rnn-codebase/SKILL.md')
    assert 'description: Navigate and work with the react-native-navigation (RNN) codebase. Use when fixing bugs, adding features, tracing command flows, understanding options resolution, or working across JS/iOS' in text, "expected to find: " + 'description: Navigate and work with the react-native-navigation (RNN) codebase. Use when fixing bugs, adding features, tracing command flows, understanding options resolution, or working across JS/iOS'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/rnn-codebase/SKILL.md')
    assert '- **`android/src/main/java/com/reactnativenavigation/`** — All Java/Kotlin native code. See [android/ARCHITECTURE.md](../../../android/ARCHITECTURE.md)' in text, "expected to find: " + '- **`android/src/main/java/com/reactnativenavigation/`** — All Java/Kotlin native code. See [android/ARCHITECTURE.md](../../../android/ARCHITECTURE.md)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/rnn-codebase/SKILL.md')
    assert '| Animations | `src/interfaces/Options.ts` (AnimationOptions) | `ios/ScreenAnimationController.mm` | `viewcontrollers/stack/StackAnimator.kt` |' in text, "expected to find: " + '| Animations | `src/interfaces/Options.ts` (AnimationOptions) | `ios/ScreenAnimationController.mm` | `viewcontrollers/stack/StackAnimator.kt` |'[:80]

