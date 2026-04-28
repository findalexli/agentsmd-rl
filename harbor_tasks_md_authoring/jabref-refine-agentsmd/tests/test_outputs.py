"""Behavioral checks for jabref-refine-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jabref")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For a new feature or significant bug fix, **at minimum add the requirement** to the appropriate `docs/requirements/<area>.md` file. Full tracing (`Needs: impl` + implementation comments) is encouraged' in text, "expected to find: " + 'For a new feature or significant bug fix, **at minimum add the requirement** to the appropriate `docs/requirements/<area>.md` file. Full tracing (`Needs: impl` + implementation comments) is encouraged'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'See [ADR-0000](docs/decisions/0000-use-markdown-architectural-decision-records.md) for the rationale and [adr-template.md](docs/decisions/adr-template.md) for the full template.' in text, "expected to find: " + 'See [ADR-0000](docs/decisions/0000-use-markdown-architectural-decision-records.md) for the rationale and [adr-template.md](docs/decisions/adr-template.md) for the full template.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The identifier must follow the heading with no blank line between them. Add `<!-- markdownlint-disable-file MD022 -->` at the end of the file.' in text, "expected to find: " + 'The identifier must follow the heading with no blank line between them. Add `<!-- markdownlint-disable-file MD022 -->` at the end of the file.'[:80]

