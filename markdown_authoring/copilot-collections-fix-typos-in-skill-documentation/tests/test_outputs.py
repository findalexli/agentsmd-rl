"""Behavioral checks for copilot-collections-fix-typos-in-skill-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/copilot-collections")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/architecture-design/SKILL.md')
    assert 'Your goal is to design a solution that is not overengineered and easy to comprehend by developers, that is at the same time scalable, secure and easy to maintain.' in text, "expected to find: " + 'Your goal is to design a solution that is not overengineered and easy to comprehend by developers, that is at the same time scalable, secure and easy to maintain.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/architecture-design/SKILL.md')
    assert '- [ ] Step 5: Create an implementation plan document' in text, "expected to find: " + '- [ ] Step 5: Create an implementation plan document'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/architecture-design/SKILL.md')
    assert '- [ ] Step 3: Ask questions about ambiguous parts' in text, "expected to find: " + '- [ ] Step 3: Ask questions about ambiguous parts'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/code-review/SKILL.md')
    assert '- [ ] Step 7: Run static code analysis tools and formatting tools' in text, "expected to find: " + '- [ ] Step 7: Run static code analysis tools and formatting tools'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/code-review/SKILL.md')
    assert '**Step 7: Run static code analysis tools and formatting tools**' in text, "expected to find: " + '**Step 7: Run static code analysis tools and formatting tools**'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/code-review/SKILL.md')
    assert '- [ ] Step 9: Validate the solution is scalable' in text, "expected to find: " + '- [ ] Step 9: Validate the solution is scalable'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/task-analysis/SKILL.md')
    assert 'Generate a report following the `./research.example.md` structure. Make sure to provide all necessary information that you gathered, all findings and all answered questions.' in text, "expected to find: " + 'Generate a report following the `./research.example.md` structure. Make sure to provide all necessary information that you gathered, all findings and all answered questions.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/task-analysis/SKILL.md')
    assert '- [ ] Step 4: Based on the answers and gathered information finalize the research report' in text, "expected to find: " + '- [ ] Step 4: Based on the answers and gathered information finalize the research report'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/task-analysis/SKILL.md')
    assert '**Step 4: Based on the answers and gathered information finalize the research report**' in text, "expected to find: " + '**Step 4: Based on the answers and gathered information finalize the research report**'[:80]

