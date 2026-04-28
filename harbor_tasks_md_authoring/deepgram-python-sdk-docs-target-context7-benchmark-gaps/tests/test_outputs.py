"""Behavioral checks for deepgram-python-sdk-docs-target-context7-benchmark-gaps (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/deepgram-python-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-audio-intelligence/SKILL.md')
    assert 'For a higher-level breakdown, set `utterances=True` to get pre-grouped speaker turns at `response.results.utterances`. Set `paragraphs=True` for a `paragraphs` view organised by speaker turn boundarie' in text, "expected to find: " + 'For a higher-level breakdown, set `utterances=True` to get pre-grouped speaker turns at `response.results.utterances`. Set `paragraphs=True` for a `paragraphs` view organised by speaker turn boundarie'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-audio-intelligence/SKILL.md')
    assert 'Enable speaker separation and word-level timestamps in a single request, then iterate the per-word objects to build a speaker-labelled transcript with timing.' in text, "expected to find: " + 'Enable speaker separation and word-level timestamps in a single request, then iterate the per-word objects to build a speaker-labelled transcript with timing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-audio-intelligence/SKILL.md')
    assert '| `punctuated_word` | `str \\| None` | Token with smart-formatted casing/punctuation (when `smart_format=True`) |' in text, "expected to find: " + '| `punctuated_word` | `str \\| None` | Token with smart-formatted casing/punctuation (when `smart_format=True`) |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-speech-to-text/SKILL.md')
    assert 'Pass `callback="https://your.app/webhook"` and the request **returns immediately** with a `request_id`. Deepgram processes the audio in the background and POSTs the final result to your webhook URL. T' in text, "expected to find: " + 'Pass `callback="https://your.app/webhook"` and the request **returns immediately** with a `request_id`. Deepgram processes the audio in the background and POSTs the final result to your webhook URL. T'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-speech-to-text/SKILL.md')
    assert 'Live transcription emits **interim** (partial) and **final** results. Pass `interim_results=True` and switch on `is_final` to display partial text in real time, then overwrite it with the final transc' in text, "expected to find: " + 'Live transcription emits **interim** (partial) and **final** results. Pass `interim_results=True` and switch on `is_final` to display partial text in real time, then overwrite it with the final transc'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-speech-to-text/SKILL.md')
    assert '- **`from_finalize = True`** — this final was triggered by your explicit `send_finalize()` call (vs natural endpointing). Useful to distinguish "I asked for a flush" from "the speaker paused".' in text, "expected to find: " + '- **`from_finalize = True`** — this final was triggered by your explicit `send_finalize()` call (vs natural endpointing). Useful to distinguish "I asked for a flush" from "the speaker paused".'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-voice-agent/SKILL.md')
    assert '**Reconnect after disconnect (preserve conversation context):** `Settings` cannot be re-sent on the same closed socket; open a new connection and resend the same `Settings`. To carry conversation hist' in text, "expected to find: " + '**Reconnect after disconnect (preserve conversation context):** `Settings` cannot be re-sent on the same closed socket; open a new connection and resend the same `Settings`. To carry conversation hist'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-voice-agent/SKILL.md')
    assert 'The server emits a `History` message on connect when the SDK has captured prior turns; in Python you receive this as an `AgentV1History` object (wire `type` literal: `"History"`). Persist these turns ' in text, "expected to find: " + 'The server emits a `History` message on connect when the SDK has captured prior turns; in Python you receive this as an `AgentV1History` object (wire `type` literal: `"History"`). Persist these turns '[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deepgram-python-voice-agent/SKILL.md')
    assert '**Detect disconnects:** the `EventType.CLOSE` handler fires before the `with` block exits. Catch it and trigger your reconnect logic from there. Check `EventType.ERROR` payloads for cause (network dro' in text, "expected to find: " + '**Detect disconnects:** the `EventType.CLOSE` handler fires before the `with` block exits. Catch it and trigger your reconnect logic from there. Check `EventType.ERROR` payloads for cause (network dro'[:80]

