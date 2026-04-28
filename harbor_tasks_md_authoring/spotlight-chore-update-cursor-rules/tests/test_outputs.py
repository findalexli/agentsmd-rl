"""Behavioral checks for spotlight-chore-update-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spotlight")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/.cursor/rules/routing.mdc')
    assert '.cursor/rules/.cursor/rules/routing.mdc' in text, "expected to find: " + '.cursor/rules/.cursor/rules/routing.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/general-guidelines.mdc')
    assert '.cursor/rules/general-guidelines.mdc' in text, "expected to find: " + '.cursor/rules/general-guidelines.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/.cursor/rules/overview.mdc')
    assert '- `spotlight run <command>` - Most common usage. Wraps your application, auto-detects Docker Compose or package.json scripts, sets `SENTRY_SPOTLIGHT` env var' in text, "expected to find: " + '- `spotlight run <command>` - Most common usage. Wraps your application, auto-detects Docker Compose or package.json scripts, sets `SENTRY_SPOTLIGHT` env var'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/.cursor/rules/overview.mdc')
    assert "Spotlight provides a CLI tool called `spotlight` that users run from the terminal. It's the main way developers interact with Spotlight." in text, "expected to find: " + "Spotlight provides a CLI tool called `spotlight` that users run from the terminal. It's the main way developers interact with Spotlight."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/.cursor/rules/overview.mdc')
    assert 'The `@spotlightjs/spotlight` package is a unified package containing the UI, server (sidecar), CLI, and Electron desktop application.' in text, "expected to find: " + 'The `@spotlightjs/spotlight` package is a unified package containing the UI, server (sidecar), CLI, and Electron desktop application.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/electron/.cursor/rules/electron.mdc')
    assert "dragBar.style.cssText = 'position:fixed;top:0;left:0;right:0;height:40px;-webkit-app-region:drag;z-index:99999;';" in text, "expected to find: " + "dragBar.style.cssText = 'position:fixed;top:0;left:0;right:0;height:40px;-webkit-app-region:drag;z-index:99999;';"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/electron/.cursor/rules/electron.mdc')
    assert 'Electron uses `HashRouter` instead of `BrowserRouter` because it loads from `file://` protocol:' in text, "expected to find: " + 'Electron uses `HashRouter` instead of `BrowserRouter` because it loads from `file://` protocol:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/electron/.cursor/rules/electron.mdc')
    assert 'The Spotlight desktop app packages the UI and server into a standalone Electron application.' in text, "expected to find: " + 'The Spotlight desktop app packages the UI and server into a standalone Electron application.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/.cursor/rules/server.mdc')
    assert 'The Spotlight server (sidecar) is a Node.js HTTP server built with Hono that receives, stores, and streams telemetry data.' in text, "expected to find: " + 'The Spotlight server (sidecar) is a Node.js HTTP server built with Hono that receives, stores, and streams telemetry data.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/.cursor/rules/server.mdc')
    assert 'const output = applyFormatter(humanFormatters, type, payload, envelopeHeader);' in text, "expected to find: " + 'const output = applyFormatter(humanFormatters, type, payload, envelopeHeader);'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/.cursor/rules/server.mdc')
    assert 'description: Server/sidecar development guidelines using Hono framework' in text, "expected to find: " + 'description: Server/sidecar development guidelines using Hono framework'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/cli/.cursor/rules/cli.mdc')
    assert '| `spotlight` / `spotlight server` | Starts the sidecar server (default) | `server.ts` |' in text, "expected to find: " + '| `spotlight` / `spotlight server` | Starts the sidecar server (default) | `server.ts` |'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/cli/.cursor/rules/cli.mdc')
    assert 'Entry point is `../cli.ts` which handles argument parsing and routes via `CLI_CMD_MAP`.' in text, "expected to find: " + 'Entry point is `../cli.ts` which handles argument parsing and routes via `CLI_CMD_MAP`.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/cli/.cursor/rules/cli.mdc')
    assert '| `spotlight run <cmd>` | Wraps and runs an application with Spotlight | `run.ts` |' in text, "expected to find: " + '| `spotlight run <cmd>` | Wraps and runs an application with Spotlight | `run.ts` |'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/mcp/.cursor/rules/mcp.mdc')
    assert 'The MCP server enables AI coding assistants to access Spotlight telemetry data via the Model Context Protocol.' in text, "expected to find: " + 'The MCP server enables AI coding assistants to access Spotlight telemetry data via the Model Context Protocol.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/mcp/.cursor/rules/mcp.mdc')
    assert "import { formatTraceSummary, buildSpanTree, renderSpanTree } from '../formatters/md/traces';" in text, "expected to find: " + "import { formatTraceSummary, buildSpanTree, renderSpanTree } from '../formatters/md/traces';"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/server/mcp/.cursor/rules/mcp.mdc')
    assert '- **Transport**: stdio (standard input/output) for communication with AI clients' in text, "expected to find: " + '- **Transport**: stdio (standard input/output) for communication with AI clients'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/ui/.cursor/rules/ui.mdc')
    assert '**Important**: Do NOT manage navigation state in local component state. Extract it from URL parameters.' in text, "expected to find: " + '**Important**: Do NOT manage navigation state in local component state. Extract it from URL parameters.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/ui/.cursor/rules/ui.mdc')
    assert 'Use **React Router v6** for all navigation. The URL is the source of truth for navigation state.' in text, "expected to find: " + 'Use **React Router v6** for all navigation. The URL is the source of truth for navigation state.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/spotlight/src/ui/.cursor/rules/ui.mdc')
    assert 'The Spotlight UI is a React application for visualizing telemetry data (errors, traces, logs).' in text, "expected to find: " + 'The Spotlight UI is a React application for visualizing telemetry data (errors, traces, logs).'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/website/.cursor/rules/website.mdc')
    assert '- **Components**: Astro (`.astro`) for static content, React (`.tsx`) for interactive elements' in text, "expected to find: " + '- **Components**: Astro (`.astro`) for static content, React (`.tsx`) for interactive elements'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/website/.cursor/rules/website.mdc')
    assert '- Use `@astrojs/starlight/components` for built-in components (Tabs, TabItem, etc.)' in text, "expected to find: " + '- Use `@astrojs/starlight/components` for built-in components (Tabs, TabItem, etc.)'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/website/.cursor/rules/website.mdc')
    assert 'This is the Spotlight documentation website built with Astro and Starlight.' in text, "expected to find: " + 'This is the Spotlight documentation website built with Astro and Starlight.'[:80]

