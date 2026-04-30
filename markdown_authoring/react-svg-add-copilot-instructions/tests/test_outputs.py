"""Behavioral checks for react-svg-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/react-svg")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`npm run test:react` runs all test suites against React 16.0 through 19.x. It installs dependencies per version directory under `test/react/` and takes a long time. Use `npm run test:src` for developm' in text, "expected to find: " + '`npm run test:react` runs all test suites against React 16.0 through 19.x. It installs dependencies per version directory under `test/react/` and takes a long time. Use `npm run test:src` for developm'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`ReactSVG` is a class component that manages a non-React DOM subtree. It must remain a class component — it uses lifecycle methods to coordinate with `@tanem/svg-injector`, which operates outside Reac' in text, "expected to find: " + '`ReactSVG` is a class component that manages a non-React DOM subtree. It must remain a class component — it uses lifecycle methods to coordinate with `@tanem/svg-injector`, which operates outside Reac'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`shallowDiffers` triggers full re-injection in `componentDidUpdate` — the SVG is removed and re-injected on any prop change. `_isMounted` guards against async callbacks firing after unmount.' in text, "expected to find: " + '`shallowDiffers` triggers full re-injection in `componentDidUpdate` — the SVG is removed and re-injected on any prop change. `_isMounted` guards against async callbacks firing after unmount.'[:80]

