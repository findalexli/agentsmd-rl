"""Behavioral checks for payload-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/payload")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Valid scopes are the following regex patterns: cpa, db-\\*, db-mongodb, db-postgres, db-vercel-postgres, db-sqlite, drizzle, email-\\*, email-nodemailer, email-resend, eslint, graphql, live-preview, l' in text, "expected to find: " + '- Valid scopes are the following regex patterns: cpa, db-\\*, db-mongodb, db-postgres, db-vercel-postgres, db-sqlite, drizzle, email-\\*, email-nodemailer, email-resend, eslint, graphql, live-preview, l'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Specific dev configs for each package can be run with `pnpm dev <directory_name>`. The options are all of the top-level directories inside the `test/` directory. Ex `pnpm dev fields` which loads the' in text, "expected to find: " + '- Specific dev configs for each package can be run with `pnpm dev <directory_name>`. The options are all of the top-level directories inside the `test/` directory. Ex `pnpm dev fields` which loads the'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Any package can be built using a `pnpm build:*` script defined in the root `package.json`. These typically follow the format `pnpm build:<directory_name>`. The options are all of the top-level direc' in text, "expected to find: " + '- Any package can be built using a `pnpm build:*` script defined in the root `package.json`. These typically follow the format `pnpm build:<directory_name>`. The options are all of the top-level direc'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

