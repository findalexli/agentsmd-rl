"""Behavioral checks for observal-docs-update-agentsmd-files-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/observal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The web frontend is a Next.js 16 / React 19 app in `web/`. It uses four route groups: `(auth)` for login, `(registry)` for the public-facing agent browser, component library, and agent builder, `(admi' in text, "expected to find: " + 'The web frontend is a Next.js 16 / React 19 app in `web/`. It uses four route groups: `(auth)` for login, `(registry)` for the public-facing agent browser, component library, and agent builder, `(admi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Auth is API key based. Keys are SHA-256 hashed before storage. The `X-API-Key` header is checked on every authenticated request via `get_current_user` dependency. User onboarding uses self-registrat' in text, "expected to find: " + '- Auth is API key based. Keys are SHA-256 hashed before storage. The `X-API-Key` header is checked on every authenticated request via `get_current_user` dependency. User onboarding uses self-registrat'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- The `observal scan` command reads existing IDE config files, bulk-registers found MCP servers via `POST /api/v1/scan`, and rewrites configs to wrap commands with `observal-shim`. It creates timestam' in text, "expected to find: " + '- The `observal scan` command reads existing IDE config files, bulk-registers found MCP servers via `POST /api/v1/scan`, and rewrites configs to wrap commands with `observal-shim`. It creates timestam'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('ee/AGENTS.md')
    assert '**Critical constraint:** Core must NEVER import from `ee/`. Dependency is strictly one-way: `ee/` imports core, never the reverse. The open-source edition must be fully functional without `ee/`.' in text, "expected to find: " + '**Critical constraint:** Core must NEVER import from `ee/`. Dependency is strictly one-way: `ee/` imports core, never the reverse. The open-source edition must be fully functional without `ee/`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('ee/AGENTS.md')
    assert '**License:** Separate enterprise license (`ee/LICENSE`). Commercial license required for production. Community contributions NOT accepted into this directory.' in text, "expected to find: " + '**License:** Separate enterprise license (`ee/LICENSE`). Commercial license required for production. Community contributions NOT accepted into this directory.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('ee/AGENTS.md')
    assert 'Each event → row in ClickHouse `audit_log` table with actor info, resource details, HTTP metadata, and freeform detail JSON.' in text, "expected to find: " + 'Each event → row in ClickHouse `audit_log` table with actor info, resource details, HTTP metadata, and freeform detail JSON.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('web/AGENTS.md')
    assert '- **Design system:** OKLCH color space with 5 themes (light, dark, midnight, forest, sunset). Typography: Archivo (display), Albert Sans (body), JetBrains Mono (code). 4pt spacing scale. Defined in `g' in text, "expected to find: " + '- **Design system:** OKLCH color space with 5 themes (light, dark, midnight, forest, sunset). Typography: Archivo (display), Albert Sans (body), JetBrains Mono (code). 4pt spacing scale. Defined in `g'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('web/AGENTS.md')
    assert '├── registry/      # AgentCard, ComponentCard, PullCommand, InstallDialog, StatusBadge, SubmitComponentDialog, RegistryTable, RegistryDetail, ReviewForm' in text, "expected to find: " + '├── registry/      # AgentCard, ComponentCard, PullCommand, InstallDialog, StatusBadge, SubmitComponentDialog, RegistryTable, RegistryDetail, ReviewForm'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('web/AGENTS.md')
    assert '- **UI:** shadcn/ui (`src/components/ui/`), Recharts 3 for charts, TanStack Query for data fetching, TanStack Table for sortable/filterable tables' in text, "expected to find: " + '- **UI:** shadcn/ui (`src/components/ui/`), Recharts 3 for charts, TanStack Query for data fetching, TanStack Table for sortable/filterable tables'[:80]

