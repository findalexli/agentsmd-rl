"""Behavioral checks for kaggle-environments-consolidate-visualizer-related-agent-ski (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kaggle-environments")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-environment/SKILL.md')
    assert 'Follow the `create-visualizer` skill to build a web-based replay visualizer for this environment.' in text, "expected to find: " + 'Follow the `create-visualizer` skill to build a web-based replay visualizer for this environment.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-environment/SKILL.md')
    assert '## Step 6: Add a visualizer (optional)' in text, "expected to find: " + '## Step 6: Add a visualizer (optional)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-open-spiel-visualizer/SKILL.md')
    assert '.agents/skills/create-open-spiel-visualizer/SKILL.md' in text, "expected to find: " + '.agents/skills/create-open-spiel-visualizer/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-visualizer/SKILL.md')
    assert '**Observation string is empty (OpenSpiel):** Some games use `information_state_string()` instead of `observation_string()`. The framework handles this automatically -- check the game type in the OpenS' in text, "expected to find: " + '**Observation string is empty (OpenSpiel):** Some games use `information_state_string()` instead of `observation_string()`. The framework handles this automatically -- check the game type in the OpenS'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-visualizer/SKILL.md')
    assert "**Canvas is blank:** Check the browser console for errors. Common issues: incorrect CSS (canvas has 0 height), parse function returning null because the observation string format doesn't match expecta" in text, "expected to find: " + "**Canvas is blank:** Check the browser console for errors. Common issues: incorrect CSS (canvas has 0 height), parse function returning null because the observation string format doesn't match expecta"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-visualizer/SKILL.md')
    assert 'For **perfect information** games, both players get the same observation. For **imperfect information** games, each player gets a different JSON object containing only their private view -- parse both' in text, "expected to find: " + 'For **perfect information** games, both players get the same observation. For **imperfect information** games, each player gets a different JSON object containing only their private view -- parse both'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-visualizer/visualizer-style-guide.md')
    assert '5. **Two typefaces.** Use **Inter** (sans-serif) for all UI text -- player names, scores, labels, controls. Use **Mynerve** (cursive) as an optional accent font for annotations, commentary, and decora' in text, "expected to find: " + '5. **Two typefaces.** Use **Inter** (sans-serif) for all UI text -- player names, scores, labels, controls. Use **Mynerve** (cursive) as an optional accent font for annotations, commentary, and decora'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-visualizer/visualizer-style-guide.md')
    assert '4. **High-resolution text.** Prefer **DOM elements** for all text, labels, and status displays rather than canvas text. Canvas `fillText` cannot use web fonts reliably. Use canvas only for the game bo' in text, "expected to find: " + '4. **High-resolution text.** Prefer **DOM elements** for all text, labels, and status displays rather than canvas text. Canvas `fillText` cannot use web fonts reliably. Use canvas only for the game bo'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-visualizer/visualizer-style-guide.md')
    assert '7. **Responsive sizing.** Use CSS container queries (`@container (max-width: 680px)`) for responsive layout adjustments. Set `container-type: inline-size` on the main wrapper. The **680px** breakpoint' in text, "expected to find: " + '7. **Responsive sizing.** Use CSS container queries (`@container (max-width: 680px)`) for responsive layout adjustments. Set `container-type: inline-size` on the main wrapper. The **680px** breakpoint'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/onboard-open-spiel-game/SKILL.md')
    assert 'All three approaches can optionally include a **visualizer** (see `create-visualizer` skill) and/or **support files** (openings, presets).' in text, "expected to find: " + 'All three approaches can optionally include a **visualizer** (see `create-visualizer` skill) and/or **support files** (openings, presets).'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/onboard-open-spiel-game/SKILL.md')
    assert '- `create-visualizer` -- for adding a web visualizer (covers both regular and OpenSpiel games)' in text, "expected to find: " + '- `create-visualizer` -- for adding a web visualizer (covers both regular and OpenSpiel games)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/onboard-open-spiel-game/SKILL.md')
    assert '**Related skills:**' in text, "expected to find: " + '**Related skills:**'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **create-visualizer** -- step-by-step guide for building a web visualizer for any game (regular or OpenSpiel)' in text, "expected to find: " + '- **create-visualizer** -- step-by-step guide for building a web visualizer for any game (regular or OpenSpiel)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **create-environment** -- step-by-step guide for building a new game environment (Python backend)' in text, "expected to find: " + '- **create-environment** -- step-by-step guide for building a new game environment (Python backend)'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **onboard-open-spiel-game** -- step-by-step guide for adding an OpenSpiel game (Python backend)' in text, "expected to find: " + '- **onboard-open-spiel-game** -- step-by-step guide for adding an OpenSpiel game (Python backend)'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `create-visualizer` -- building a web visualizer for any game (regular or OpenSpiel)' in text, "expected to find: " + '- `create-visualizer` -- building a web visualizer for any game (regular or OpenSpiel)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `onboard-open-spiel-game` -- adding an OpenSpiel game (Python backend)' in text, "expected to find: " + '- `onboard-open-spiel-game` -- adding an OpenSpiel game (Python backend)'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `create-environment` -- building a game environment (Python backend)' in text, "expected to find: " + '- `create-environment` -- building a game environment (Python backend)'[:80]

