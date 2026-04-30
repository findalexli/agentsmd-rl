"""Behavioral checks for dataverse-skills-improve-init-ux-auth-prompts (markdown_authoring task).

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
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert '- `TENANT_ID`: Auto-discover from the `DATAVERSE_URL` using the curl method (see Scenario A step 2). This is preferred over `pac org who` because it derives the tenant directly from the URL — no PAC C' in text, "expected to find: " + '- `TENANT_ID`: Auto-discover from the `DATAVERSE_URL` using the curl method (see Scenario A step 2). This is preferred over `pac org who` because it derives the tenant directly from the URL — no PAC C'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert '- `DATAVERSE_URL`: "What is your Dataverse environment URL?" (e.g., `https://myorg.crm10.dynamics.com`). If the Environment Discovery flow already determined this, use it directly — do not re-ask.' in text, "expected to find: " + '- `DATAVERSE_URL`: "What is your Dataverse environment URL?" (e.g., `https://myorg.crm10.dynamics.com`). If the Environment Discovery flow already determined this, use it directly — do not re-ask.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/init/SKILL.md')
    assert "> 1. **Interactive login (recommended for personal use)** — Sign in via your browser. No app registration needed. You'll authenticate once and the token stays cached across sessions." in text, "expected to find: " + "> 1. **Interactive login (recommended for personal use)** — Sign in via your browser. No app registration needed. You'll authenticate once and the token stays cached across sessions."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert 'Separately from tenant-level consent, each Dataverse environment must explicitly allow the MCP client. This is a **one-time** action per environment and does **NOT** require Azure AD admin permissions' in text, "expected to find: " + 'Separately from tenant-level consent, each Dataverse environment must explicitly allow the MCP client. This is a **one-time** action per environment and does **NOT** require Azure AD admin permissions'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert 'The MCP client app registration must be granted admin consent on the Azure AD tenant. This is a **one-time** action per tenant — once done, it applies to all Dataverse environments in that tenant. It ' in text, "expected to find: " + 'The MCP client app registration must be granted admin consent on the Azure AD tenant. This is a **one-time** action per tenant — once done, it applies to all Dataverse environments in that tenant. It '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/mcp-configure/SKILL.md')
    assert '- **Tenant-level admin consent** has been granted for the MCP client app. This is a one-time per-tenant action requiring an Azure AD admin. Without it, authentication succeeds but the app is denied ac' in text, "expected to find: " + '- **Tenant-level admin consent** has been granted for the MCP client app. This is a one-time per-tenant action requiring an Azure AD admin. Without it, authentication succeeds but the app is denied ac'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/plugins/dataverse/skills/overview/SKILL.md')
    assert '- If EITHER is missing: **Automatically run the init flow** (see the init skill). Do NOT ask the user whether to initialize — just do it. Do not create your own `.env`, `requirements.txt`, `.env.examp' in text, "expected to find: " + '- If EITHER is missing: **Automatically run the init flow** (see the init skill). Do NOT ask the user whether to initialize — just do it. Do not create your own `.env`, `requirements.txt`, `.env.examp'[:80]

