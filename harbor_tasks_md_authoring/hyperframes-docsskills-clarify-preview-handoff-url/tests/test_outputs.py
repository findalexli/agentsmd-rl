"""Behavioral checks for hyperframes-docsskills-clarify-preview-handoff-url (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hyperframes")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hyperframes-cli/SKILL.md')
    assert 'Use the actual port from the preview output and the project directory name. For' in text, "expected to find: " + 'Use the actual port from the preview output and the project directory name. For'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hyperframes-cli/SKILL.md')
    assert 'example, after `npx hyperframes preview --port 3017` in `codex-openai-video`,' in text, "expected to find: " + 'example, after `npx hyperframes preview --port 3017` in `codex-openai-video`,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hyperframes-cli/SKILL.md')
    assert 'When handing a project back to the user, use the Studio project URL, not the' in text, "expected to find: " + 'When handing a project back to the user, use the Studio project URL, not the'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/website-to-hyperframes/SKILL.md')
    assert '**Gate:** `npx hyperframes lint` and `npx hyperframes validate` pass with zero errors, and the final response includes the active Studio project URL.' in text, "expected to find: " + '**Gate:** `npx hyperframes lint` and `npx hyperframes validate` pass with zero errors, and the final response includes the active Studio project URL.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/website-to-hyperframes/SKILL.md')
    assert '(`http://localhost:<port>/#project/<project-name>`) to the user first — only' in text, "expected to find: " + '(`http://localhost:<port>/#project/<project-name>`) to the user first — only'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/website-to-hyperframes/SKILL.md')
    assert 'Lint, validate, snapshot, preview. Deliver the localhost Studio project URL' in text, "expected to find: " + 'Lint, validate, snapshot, preview. Deliver the localhost Studio project URL'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/website-to-hyperframes/references/step-7-validate.md')
    assert 'The Studio URL is the project handoff surface. In the final response, report the' in text, "expected to find: " + 'The Studio URL is the project handoff surface. In the final response, report the'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/website-to-hyperframes/references/step-7-validate.md')
    assert 'Use the actual port selected by `hyperframes preview` and the project name shown' in text, "expected to find: " + 'Use the actual port selected by `hyperframes preview` and the project name shown'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/website-to-hyperframes/references/step-7-validate.md')
    assert 'Do **not** present `index.html` as the project link. `index.html` is the source' in text, "expected to find: " + 'Do **not** present `index.html` as the project link. `index.html` is the source'[:80]

