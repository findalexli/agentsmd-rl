"""Behavioral checks for modularity-improve-skill-tooling-allowedtools-askuserquestio (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/modularity")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/document/SKILL.md')
    assert '| A -> B      | ...                                                                                 | ...                                                                     | ...                     ' in text, "expected to find: " + '| A -> B      | ...                                                                                 | ...                                                                     | ...                     '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/document/SKILL.md')
    assert '| Concept mentioned                                                                                           | Link to                                                                 |' in text, "expected to find: " + '| Concept mentioned                                                                                           | Link to                                                                 |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/document/SKILL.md')
    assert '| Balanced coupling, the balance rule, the balance formula, `STRENGTH XOR DISTANCE`, modularity vs complexity | https://coupling.dev/posts/core-concepts/balance/                       |' in text, "expected to find: " + '| Balanced coupling, the balance rule, the balance formula, `STRENGTH XOR DISTANCE`, modularity vs complexity | https://coupling.dev/posts/core-concepts/balance/                       |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/high-level-design/SKILL.md')
    assert '| Header  | Question                                                         | Options                                                                                                                  ' in text, "expected to find: " + '| Header  | Question                                                         | Options                                                                                                                  '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/high-level-design/SKILL.md')
    assert '| Header   | Question                                                  | Options                                                                                                                        ' in text, "expected to find: " + '| Header   | Question                                                  | Options                                                                                                                        '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/high-level-design/SKILL.md')
    assert 'Use TaskCreate to track these 6 steps: Understand the Requirements, Design the Modular Architecture, Write Module Design Documents, Write Module Test Specifications, Write the Architecture Document, M' in text, "expected to find: " + 'Use TaskCreate to track these 6 steps: Understand the Requirements, Design the Modular Architecture, Write Module Design Documents, Write Module Test Specifications, Write the Architecture Document, M'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/review/SKILL.md')
    assert '**Domain classification**: Header: "Domain". First, ask the user (free text) which business areas/components are core (competitive advantage, high volatility), supporting, or generic subdomains. Do no' in text, "expected to find: " + '**Domain classification**: Header: "Domain". First, ask the user (free text) which business areas/components are core (competitive advantage, high volatility), supporting, or generic subdomains. Do no'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/review/SKILL.md')
    assert '2. Use `AskUserQuestion` to ask which parts of the codebase to analyze. Header: "Scope". Options: "Entire codebase — Analyze all components", "Specific directory — I\'ll tell you which path", "Specific' in text, "expected to find: " + '2. Use `AskUserQuestion` to ask which parts of the codebase to analyze. Header: "Scope". Options: "Entire codebase — Analyze all components", "Specific directory — I\'ll tell you which path", "Specific'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/review/SKILL.md')
    assert '**Known pain points**: Header: "Pain points". Options: "Yes — I\'ll describe them", "Not that I know of", "Not sure". If the user identifies pain points, follow up for details before proceeding.' in text, "expected to find: " + '**Known pain points**: Header: "Pain points". Options: "Yes — I\'ll describe them", "Not that I know of", "Not sure". If the user identifies pain points, follow up for details before proceeding.'[:80]

