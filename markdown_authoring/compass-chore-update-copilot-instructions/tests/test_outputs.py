"""Behavioral checks for compass-chore-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The `connect` function introduces a deliberate level of indirection, allowing you to write presentational-style components that receive all their values as props without being specifically dependent o' in text, "expected to find: " + 'The `connect` function introduces a deliberate level of indirection, allowing you to write presentational-style components that receive all their values as props without being specifically dependent o'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Not all state belongs in the Redux store - see [redux - organizing state FAQ](https://redux.js.org/faq/organizing-state#do-i-have-to-put-all-my-state-into-redux-should-i-ever-use-reacts-usestate-or-us' in text, "expected to find: " + 'Not all state belongs in the Redux store - see [redux - organizing state FAQ](https://redux.js.org/faq/organizing-state#do-i-have-to-put-all-my-state-into-redux-should-i-ever-use-reacts-usestate-or-us'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Components inside feature module boundaries must use the `connect` function to access store data, not Redux hooks like `useSelector` or `useDispatch`.' in text, "expected to find: " + 'Components inside feature module boundaries must use the `connect` function to access store data, not Redux hooks like `useSelector` or `useDispatch`.'[:80]

