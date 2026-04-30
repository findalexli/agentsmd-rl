"""Behavioral checks for ai-setup-fixskills-correct-addingacommand-export-pattern (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-setup")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/adding-a-command/SKILL.md')
    assert '- Command file MUST be in `src/commands/{commandName}.ts` and export a **named** async function: `export async function {commandName}Command(options?: OptionType)`. Never use default exports — `src/cl' in text, "expected to find: " + '- Command file MUST be in `src/commands/{commandName}.ts` and export a **named** async function: `export async function {commandName}Command(options?: OptionType)`. Never use default exports — `src/cl'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/adding-a-command/SKILL.md')
    assert '- Export named async function: `export async function {commandName}Command(options?: { optionName?: type }) { ... }`' in text, "expected to find: " + '- Export named async function: `export async function {commandName}Command(options?: { optionName?: type }) { ... }`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/adding-a-command/SKILL.md')
    assert "- Always use `tracked('{kebab-name}', {commandName}Command)` wrapper in `src/cli.ts` to enable telemetry tracking." in text, "expected to find: " + "- Always use `tracked('{kebab-name}', {commandName}Command)` wrapper in `src/cli.ts` to enable telemetry tracking."[:80]

