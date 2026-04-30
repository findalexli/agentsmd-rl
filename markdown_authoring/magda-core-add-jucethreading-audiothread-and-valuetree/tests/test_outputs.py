"""Behavioral checks for magda-core-add-jucethreading-audiothread-and-valuetree (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/magda-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audio-thread/SKILL.md')
    assert 'description: Audio thread safety and lock-free programming patterns for JUCE/Tracktion Engine. Use when writing Plugin::applyToBuffer(), real-time audio callbacks, metering, or any code that touches t' in text, "expected to find: " + 'description: Audio thread safety and lock-free programming patterns for JUCE/Tracktion Engine. Use when writing Plugin::applyToBuffer(), real-time audio callbacks, metering, or any code that touches t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audio-thread/SKILL.md')
    assert 'The audio thread in JUCE/Tracktion Engine runs under strict real-time constraints. Any blocking or unbounded operation causes audible glitches (clicks, dropouts, silence). This skill covers what is fo' in text, "expected to find: " + 'The audio thread in JUCE/Tracktion Engine runs under strict real-time constraints. Any blocking or unbounded operation causes audible glitches (clicks, dropouts, silence). This skill covers what is fo'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/audio-thread/SKILL.md')
    assert "When a plugin is rack-wrapped (inserted into a RackType), Tracktion Engine manages the audio routing. The plugin's `applyToBuffer()` is still called on the audio thread, but the buffer routing is hand" in text, "expected to find: " + "When a plugin is rack-wrapped (inserted into a RackType), Tracktion Engine manages the audio routing. The plugin's `applyToBuffer()` is still called on the audio thread, but the buffer routing is hand"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/juce-threading/SKILL.md')
    assert 'description: JUCE threading model and component lifecycle safety. Use when writing UI components, async callbacks, timers, or any code that crosses thread boundaries. Covers destruction ordering, Safe' in text, "expected to find: " + 'description: JUCE threading model and component lifecycle safety. Use when writing UI components, async callbacks, timers, or any code that crosses thread boundaries. Covers destruction ordering, Safe'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/juce-threading/SKILL.md')
    assert 'Always use RAII classes instead of manual acquire/release patterns. This prevents resource leaks when exceptions occur or early returns are taken.' in text, "expected to find: " + 'Always use RAII classes instead of manual acquire/release patterns. This prevents resource leaks when exceptions occur or early returns are taken.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/juce-threading/SKILL.md')
    assert 'This skill covers thread safety and component lifecycle patterns critical for avoiding crashes in MAGDA.' in text, "expected to find: " + 'This skill covers thread safety and component lifecycle patterns critical for avoiding crashes in MAGDA.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/valuetree/SKILL.md')
    assert 'Listeners fire on the thread that made the change. If a property is set from the audio thread, the listener callback runs on the audio thread. Never do UI work directly in a listener that might be cal' in text, "expected to find: " + 'Listeners fire on the thread that made the change. If a property is set from the audio thread, the listener callback runs on the audio thread. Never do UI work directly in a listener that might be cal'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/valuetree/SKILL.md')
    assert 'description: JUCE ValueTree and serialization patterns for Tracktion Engine plugins. Use when working with plugin state, CachedValue properties, ValueTree listeners, or state persistence/restoration.' in text, "expected to find: " + 'description: JUCE ValueTree and serialization patterns for Tracktion Engine plugins. Use when working with plugin state, CachedValue properties, ValueTree listeners, or state persistence/restoration.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/valuetree/SKILL.md')
    assert 'ValueTree is the core data model in JUCE and Tracktion Engine. Every plugin, track, and edit stores its state as a ValueTree. This skill covers the patterns used throughout the MAGDA codebase.' in text, "expected to find: " + 'ValueTree is the core data model in JUCE and Tracktion Engine. Every plugin, track, and edit stores its state as a ValueTree. This skill covers the patterns used throughout the MAGDA codebase.'[:80]

