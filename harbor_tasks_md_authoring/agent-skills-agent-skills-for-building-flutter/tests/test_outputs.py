"""Behavioral checks for agent-skills-agent-skills-for-building-flutter (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/SKILL.md')
    assert '| Flutter (Dart) | Gemini Developer API | [flutter_setup.md](references/flutter_setup.md) |' in text, "expected to find: " + '| Flutter (Dart) | Gemini Developer API | [flutter_setup.md](references/flutter_setup.md) |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/SKILL.md')
    assert '[Flutter SDK code examples and usage patterns](references/flutter_setup.md)' in text, "expected to find: " + '[Flutter SDK code examples and usage patterns](references/flutter_setup.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/references/flutter_setup.md')
    assert '> **Choose the Right API Provider:** Always use `FirebaseAI.googleAI` (Gemini Developer API) as the default for prototyping and standard use. Avoid using the Vertex AI Gemini API unless your applicati' in text, "expected to find: " + '> **Choose the Right API Provider:** Always use `FirebaseAI.googleAI` (Gemini Developer API) as the default for prototyping and standard use. Avoid using the Vertex AI Gemini API unless your applicati'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/references/flutter_setup.md')
    assert '> 1. **Review Foundation:** Before implementing platform-specific code, ALWAYS review the foundational `firebase-basics` skill to ensure familiarity with core workflows.' in text, "expected to find: " + '> 1. **Review Foundation:** Before implementing platform-specific code, ALWAYS review the foundational `firebase-basics` skill to ensure familiarity with core workflows.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-ai-logic-basics/references/flutter_setup.md')
    assert '> 2. **Backend Provisioning via CLI:** Use the Firebase CLI for backend setup. Running `npx firebase-tools init ailogic` automatically enables the Gemini Developer API.' in text, "expected to find: " + '> 2. **Backend Provisioning via CLI:** Use the Firebase CLI for backend setup. Running `npx firebase-tools init ailogic` automatically enables the Gemini Developer API.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firebase-auth-basics/SKILL.md')
    assert 'See [references/flutter_setup.md](references/flutter_setup.md).' in text, "expected to find: " + 'See [references/flutter_setup.md](references/flutter_setup.md).'[:80]

