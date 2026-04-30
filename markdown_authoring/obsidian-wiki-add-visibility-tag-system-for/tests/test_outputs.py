"""Behavioral checks for obsidian-wiki-add-visibility-tag-system-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-wiki")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/tag-taxonomy/SKILL.md')
    assert '`visibility/` is a reserved tag group with special rules. These tags are **not** domain or type tags and are managed separately from the taxonomy vocabulary:' in text, "expected to find: " + '`visibility/` is a reserved tag group with special rules. These tags are **not** domain or type tags and are managed separately from the taxonomy vocabulary:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/tag-taxonomy/SKILL.md')
    assert '- Never add `visibility/internal` just because content is technical; use it only for genuinely team-restricted knowledge' in text, "expected to find: " + '- Never add `visibility/internal` just because content is technical; use it only for genuinely team-restricted knowledge'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/tag-taxonomy/SKILL.md')
    assert '- When running a tag audit, report `visibility/` tag usage separately — do not flag them as unknown or non-canonical' in text, "expected to find: " + '- When running a tag audit, report `visibility/` tag usage separately — do not flag them as unknown or non-canonical'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-export/SKILL.md')
    assert 'Glob all `.md` files in the vault (excluding `_archives/`, `_raw/`, `.obsidian/`, `index.md`, `log.md`, `_insights.md`). In filtered mode, also skip pages whose tags contain `visibility/internal` or `' in text, "expected to find: " + 'Glob all `.md` files in the vault (excluding `_archives/`, `_raw/`, `.obsidian/`, `index.md`, `log.md`, `_insights.md`). In filtered mode, also skip pages whose tags contain `visibility/internal` or `'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-export/SKILL.md')
    assert 'If the user requests a filtered export — phrases like **"public export"**, **"user-facing export"**, **"exclude internal"**, **"no internal pages"** — activate **filtered mode**:' in text, "expected to find: " + 'If the user requests a filtered export — phrases like **"public export"**, **"user-facing export"**, **"exclude internal"**, **"no internal pages"** — activate **filtered mode**:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-export/SKILL.md')
    assert 'By default, **all pages are exported** regardless of visibility tags. This preserves existing behavior.' in text, "expected to find: " + 'By default, **all pages are exported** regardless of visibility tags. This preserves existing behavior.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-ingest/SKILL.md')
    assert '`visibility/` tags are system tags and do **not** count toward the 5-tag limit. When in doubt, omit — untagged pages are treated as public. Never add a visibility tag just because a topic sounds techn' in text, "expected to find: " + '`visibility/` tags are system tags and do **not** count toward the 5-tag limit. When in doubt, omit — untagged pages are treated as public. Never add a visibility tag just because a topic sounds techn'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-ingest/SKILL.md')
    assert '- `visibility/pii` — content that references personal data, user records, or sensitive identifiers' in text, "expected to find: " + '- `visibility/pii` — content that references personal data, user records, or sensitive identifiers'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-ingest/SKILL.md')
    assert '- `visibility/internal` — architecture internals, system credentials patterns, team-only context' in text, "expected to find: " + '- `visibility/internal` — architecture internals, system credentials patterns, team-only context'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-query/SKILL.md')
    assert 'If the user\'s query includes phrases like **"public only"**, **"user-facing"**, **"no internal content"**, **"as a user would see it"**, or **"exclude internal"**, activate **filtered mode**:' in text, "expected to find: " + 'If the user\'s query includes phrases like **"public only"**, **"user-facing"**, **"no internal content"**, **"as a user would see it"**, or **"exclude internal"**, activate **filtered mode**:'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-query/SKILL.md')
    assert 'By default, **all pages are returned** regardless of visibility tags. This preserves existing behavior — nothing changes unless the user asks for it.' in text, "expected to find: " + 'By default, **all pages are returned** regardless of visibility tags. This preserves existing behavior — nothing changes unless the user asks for it.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-query/SKILL.md')
    assert '- [TIMESTAMP] QUERY query="the user\'s question" result_pages=N mode=normal|index_only|filtered escalated=true|false' in text, "expected to find: " + '- [TIMESTAMP] QUERY query="the user\'s question" result_pages=N mode=normal|index_only|filtered escalated=true|false'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Pages can carry a `visibility/` tag to mark their intended reach. **This is entirely optional** — untagged pages behave exactly as they always have (visible everywhere). The system stays single-vault,' in text, "expected to find: " + 'Pages can carry a `visibility/` tag to mark their intended reach. **This is entirely optional** — untagged pages behave exactly as they always have (visible everywhere). The system stays single-vault,'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Filtered mode** is opt-in, triggered by phrases like "public only", "user-facing answer", "no internal content", or "as a user would see it" in a query. Default mode shows everything.' in text, "expected to find: " + '**Filtered mode** is opt-in, triggered by phrases like "public only", "user-facing answer", "no internal content", or "as a user would see it" in a query. Default mode shows everything.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "`visibility/` tags are **system tags** — they don't count toward the 5-tag limit and are listed separately from domain/type tags in the taxonomy." in text, "expected to find: " + "`visibility/` tags are **system tags** — they don't count toward the 5-tag limit and are listed separately from domain/type tags in the taxonomy."[:80]

