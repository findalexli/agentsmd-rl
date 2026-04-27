"""Behavioral checks for dataverse-skills-improve-metadata-overview-and-pythonsdk (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dataverse-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/metadata/SKILL.md')
    assert '**Mitigation:** Add a 3-5 second delay after table creation before adding columns. After creating lookup columns, wait 5-10 seconds before inserting records that use `@odata.bind` on those lookups. If' in text, "expected to find: " + '**Mitigation:** Add a 3-5 second delay after table creation before adding columns. After creating lookup columns, wait 5-10 seconds before inserting records that use `@odata.bind` on those lookups. If'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/metadata/SKILL.md')
    assert '**Valid FormatName values for StringAttributeMetadata:** `Text`, `TextArea`, `Url`, `TickerSymbol`, `PhoneticGuide`, `VersionNumber`, `Phone`. Note: `Email` is **not** a valid FormatName despite being' in text, "expected to find: " + '**Valid FormatName values for StringAttributeMetadata:** `Text`, `TextArea`, `Url`, `TickerSymbol`, `PhoneticGuide`, `VersionNumber`, `Phone`. Note: `Email` is **not** a valid FormatName despite being'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/metadata/SKILL.md')
    assert "After creating columns (via Web API or MCP), **always report the actual logical names** to the user. Column names may be normalized or prefixed in ways the user doesn't expect. Summarize in a table:" in text, "expected to find: " + "After creating columns (via Web API or MCP), **always report the actual logical names** to the user. Column names may be normalized or prefixed in ways the user doesn't expect. Summarize in a table:"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert '**Do not proceed until the user explicitly confirms.** This is the single most important safety check in the plugin. Skipping it risks making irreversible changes to the wrong environment.' in text, "expected to find: " + '**Do not proceed until the user explicitly confirms.** This is the single most important safety check in the plugin. Skipping it risks making irreversible changes to the wrong environment.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert '**Before the FIRST operation that touches a specific environment** — creating a table, deploying a plugin, pushing a solution, inserting data — you MUST:' in text, "expected to find: " + '**Before the FIRST operation that touches a specific environment** — creating a table, deploying a plugin, pushing a solution, inserting data — you MUST:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert 'Creating metadata without a solution means it exists only in the default solution and cannot be cleanly exported or deployed. Always solution-first.' in text, "expected to find: " + 'Creating metadata without a solution means it exists only in the default solution and cannot be cleanly exported or deployed. Always solution-first.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/python-sdk/SKILL.md')
    assert '- If a record insert fails with "Invalid property", verify the lookup column\'s logical name and navigation property name by querying `EntityDefinitions(LogicalName=\'...\')/Attributes`.' in text, "expected to find: " + '- If a record insert fails with "Invalid property", verify the lookup column\'s logical name and navigation property name by querying `EntityDefinitions(LogicalName=\'...\')/Attributes`.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/python-sdk/SKILL.md')
    assert '- If you just created lookup columns, wait 5-10 seconds before inserting records that reference them. Metadata propagation delays can cause "Invalid property" errors.' in text, "expected to find: " + '- If you just created lookup columns, wait 5-10 seconds before inserting records that reference them. Metadata propagation delays can cause "Invalid property" errors.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/python-sdk/SKILL.md')
    assert '- Choice (picklist) columns use integer values, not strings: `"new_status": 100000000` (not `"Draft"`).' in text, "expected to find: " + '- Choice (picklist) columns use integer values, not strings: `"new_status": 100000000` (not `"Draft"`).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/solution/SKILL.md')
    assert "If the header was misspelled or the solution doesn't exist, components will be created in the default solution instead — silently. Always verify." in text, "expected to find: " + "If the header was misspelled or the solution doesn't exist, components will be created in the default solution instead — silently. Always verify."[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/solution/SKILL.md')
    assert 'When creating metadata via the Web API, include the `MSCRM.SolutionName` header to auto-add components to the solution:' in text, "expected to find: " + 'When creating metadata via the Web API, include the `MSCRM.SolutionName` header to auto-add components to the solution:'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/solution/SKILL.md')
    assert '**Important:** After using this approach, verify components were added by listing them:' in text, "expected to find: " + '**Important:** After using this approach, verify components were added by listing them:'[:80]

