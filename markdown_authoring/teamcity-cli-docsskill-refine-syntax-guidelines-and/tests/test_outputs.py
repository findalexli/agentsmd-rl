"""Behavioral checks for teamcity-cli-docsskill-refine-syntax-guidelines-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/teamcity-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/teamcity-cli/SKILL.md')
    assert "**Do not guess subcommands, flags, or syntax.** Only use commands and flags documented in the [Command Reference](references/commands.md) or shown by `tc <command> --help`. If a command doesn't suppor" in text, "expected to find: " + "**Do not guess subcommands, flags, or syntax.** Only use commands and flags documented in the [Command Reference](references/commands.md) or shown by `tc <command> --help`. If a command doesn't suppor"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/teamcity-cli/SKILL.md')
    assert '**Terminology:** There is no `build`, `pipeline`, or `config` subcommand. Builds are **runs** (`tc run`). Build configurations are **jobs** (`tc job`).' in text, "expected to find: " + '**Terminology:** There is no `build`, `pipeline`, or `config` subcommand. Builds are **runs** (`tc run`). Build configurations are **jobs** (`tc job`).'[:80]

