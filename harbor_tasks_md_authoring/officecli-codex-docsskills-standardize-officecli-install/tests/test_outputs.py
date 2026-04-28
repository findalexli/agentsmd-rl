"""Behavioral checks for officecli-codex-docsskills-standardize-officecli-install (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/officecli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/morph-ppt/SKILL.md')
    assert 'Follow the install section in `reference/officecli-pptx-min.md` section 0.' in text, "expected to find: " + 'Follow the install section in `reference/officecli-pptx-min.md` section 0.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/morph-ppt/SKILL.md')
    assert '**FIRST: Install `officecli` if needed**' in text, "expected to find: " + '**FIRST: Install `officecli` if needed**'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/morph-ppt/reference/officecli-pptx-min.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/morph-ppt/reference/officecli-pptx-min.md')
    assert '**For comprehensive reference:** https://github.com/iOfficeAI/OfficeCLI/wiki/agent-guide' in text, "expected to find: " + '**For comprehensive reference:** https://github.com/iOfficeAI/OfficeCLI/wiki/agent-guide'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/morph-ppt/reference/officecli-pptx-min.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-academic-paper/SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-academic-paper/SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-academic-paper/SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-data-dashboard/SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-data-dashboard/SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-data-dashboard/SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-docx/SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-docx/SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-docx/SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-financial-model/SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-financial-model/SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-financial-model/SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-pitch-deck/SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-pitch-deck/SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-pitch-deck/SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-pptx/SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-pptx/SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-pptx/SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-xlsx/SKILL.md')
    assert 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.' in text, "expected to find: " + 'If `officecli` is still not found after first install, open a new terminal and run the verify command again.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-xlsx/SKILL.md')
    assert 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash' in text, "expected to find: " + 'curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/officecli-xlsx/SKILL.md')
    assert 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex' in text, "expected to find: " + 'irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex'[:80]

