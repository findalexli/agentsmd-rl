"""Behavioral checks for narrator-ai-cli-skill-featskill-doc-improvements (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/narrator-ai-cli-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '> ⚠️ **Language linkage**: Once the dubbing voice is confirmed, the narration script language must match. If the selected voice is **not Chinese (普通话)**, the agent MUST set the `language` parameter in' in text, "expected to find: " + '> ⚠️ **Language linkage**: Once the dubbing voice is confirmed, the narration script language must match. If the selected voice is **not Chinese (普通话)**, the agent MUST set the `language` parameter in'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '> ⚠️ **Agent behavior — mandatory pre-submission confirmation**: Before running any `magic-video` create command, the agent MUST display the full request parameters to the user in a readable format (t' in text, "expected to find: " + '> ⚠️ **Agent behavior — mandatory pre-submission confirmation**: Before running any `magic-video` create command, the agent MUST display the full request parameters to the user in a readable format (t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '> 4. **This rule applies even when the user does not explicitly mention language.** The target language flows through the entire pipeline as a single chain: **dubbing voice language → narration script' in text, "expected to find: " + '> 4. **This rule applies even when the user does not explicitly mention language.** The target language flows through the entire pipeline as a single chain: **dubbing voice language → narration script'[:80]

