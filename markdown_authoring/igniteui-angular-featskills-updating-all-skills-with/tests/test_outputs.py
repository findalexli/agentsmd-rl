"""Behavioral checks for igniteui-angular-featskills-updating-all-skills-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/igniteui-angular")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/SKILL.md')
    assert '> **Full setup instructions for VS Code, Cursor, Claude Desktop, and JetBrains IDEs are in [`references/mcp-setup.md`](./references/mcp-setup.md).** Read that file for editor-specific configuration st' in text, "expected to find: " + '> **Full setup instructions for VS Code, Cursor, Claude Desktop, and JetBrains IDEs are in [`references/mcp-setup.md`](./references/mcp-setup.md).** Read that file for editor-specific configuration st'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/SKILL.md')
    assert '- `igniteui-angular` or `@infragistics/igniteui-angular` added to the project via `ng add igniteui-angular` (or the `@infragistics` variant) or `npm install` — see [Package Variants](#package-variants' in text, "expected to find: " + '- `igniteui-angular` or `@infragistics/igniteui-angular` added to the project via `ng add igniteui-angular` (or the `@infragistics` variant) or `npm install` — see [Package Variants](#package-variants'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/SKILL.md')
    assert '- A theme applied to the application (see [`igniteui-angular-theming`](../igniteui-angular-theming/SKILL.md)).' in text, "expected to find: " + '- A theme applied to the application (see [`igniteui-angular-theming`](../igniteui-angular-theming/SKILL.md)).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/charts.md')
    assert 'This reference gives high-level guidance on when to use each chart type, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-c' in text, "expected to find: " + 'This reference gives high-level guidance on when to use each chart type, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-c'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/data-display.md')
    assert 'This reference gives high-level guidance on when to use each data display component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from' in text, "expected to find: " + 'This reference gives high-level guidance on when to use each data display component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/directives.md')
    assert 'This reference gives high-level guidance on when to use each directive, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cl' in text, "expected to find: " + 'This reference gives high-level guidance on when to use each directive, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cl'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/feedback.md')
    assert 'This reference gives high-level guidance on when to use each feedback and overlay component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_referen' in text, "expected to find: " + 'This reference gives high-level guidance on when to use each feedback and overlay component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_referen'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/form-controls.md')
    assert 'This reference gives high-level guidance on when to use each form control component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from' in text, "expected to find: " + 'This reference gives high-level guidance on when to use each form control component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/layout-manager.md')
    assert 'This reference gives high-level guidance on when to use each layout manager component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` fr' in text, "expected to find: " + 'This reference gives high-level guidance on when to use each layout manager component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` fr'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/layout.md')
    assert 'This reference gives high-level guidance on when to use each layout component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igni' in text, "expected to find: " + 'This reference gives high-level guidance on when to use each layout component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igni'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/mcp-setup.md')
    assert 'The Ignite UI CLI MCP server enables AI assistants to discover Ignite UI components, access component documentation, and support related Ignite UI workflows. It must be configured in your editor befor' in text, "expected to find: " + 'The Ignite UI CLI MCP server enables AI assistants to discover Ignite UI components, access component documentation, and support related Ignite UI workflows. It must be configured in your editor befor'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/mcp-setup.md')
    assert 'This works whether `igniteui-cli` is installed locally in `node_modules` or needs to be pulled from the npm registry — `npx -y` handles both cases.' in text, "expected to find: " + 'This works whether `igniteui-cli` is installed locally in `node_modules` or needs to be pulled from the npm registry — `npx -y` handles both cases.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/igniteui-angular-components/references/mcp-setup.md')
    assert 'If the MCP server is running, the `list_components` tool will return all available components for the detected framework.' in text, "expected to find: " + 'If the MCP server is running, the `list_components` tool will return all available components for the detected framework.'[:80]

