"""Behavioral checks for github-copilot-for-azure-fix-use-folded-scalar-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/github-copilot-for-azure")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sensei/references/SCORING.md')
    assert 'Plain unquoted descriptions with `: ` patterns (e.g., `USE FOR:`, `Azure AI:`) cause YAML parse errors in many skill loaders:' in text, "expected to find: " + 'Plain unquoted descriptions with `: ` patterns (e.g., `USE FOR:`, `Azure AI:`) cause YAML parse errors in many skill loaders:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sensei/references/SCORING.md')
    assert '| Over 200 chars uses `>-` | `description: >-` (multi-line) | `description: Very long plain text...` |' in text, "expected to find: " + '| Over 200 chars uses `>-` | `description: >-` (multi-line) | `description: Very long plain text...` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/sensei/references/SCORING.md')
    assert 'Descriptions containing YAML special characters (especially `: ` colon-space) **must** use either:' in text, "expected to find: " + 'Descriptions containing YAML special characters (especially `: ` colon-space) **must** use either:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-observability/SKILL.md')
    assert 'Azure Observability Services including Azure Monitor, Application Insights, Log Analytics, Alerts, and Workbooks. Provides metrics, APM, distributed tracing, KQL queries, and interactive reports.' in text, "expected to find: " + 'Azure Observability Services including Azure Monitor, Application Insights, Log Analytics, Alerts, and Workbooks. Provides metrics, APM, distributed tracing, KQL queries, and interactive reports.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-observability/SKILL.md')
    assert 'USE FOR: Azure Monitor, Application Insights, Log Analytics, Alerts, Workbooks, metrics, APM, distributed tracing, KQL queries, interactive reports, observability, monitoring dashboards.' in text, "expected to find: " + 'USE FOR: Azure Monitor, Application Insights, Log Analytics, Alerts, Workbooks, metrics, APM, distributed tracing, KQL queries, interactive reports, observability, monitoring dashboards.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-observability/SKILL.md')
    assert 'DO NOT USE FOR: instrumenting apps with App Insights SDK (use appinsights-instrumentation), querying Kusto/ADX clusters (use azure-kusto), cost analysis (use azure-cost-optimization).' in text, "expected to find: " + 'DO NOT USE FOR: instrumenting apps with App Insights SDK (use appinsights-instrumentation), querying Kusto/ADX clusters (use azure-kusto), cost analysis (use azure-cost-optimization).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-postgres/SKILL.md')
    assert 'Create new Azure Database for PostgreSQL Flexible Server instances and configure passwordless authentication with Microsoft Entra ID. Set up developer access, managed identities for apps, group-based ' in text, "expected to find: " + 'Create new Azure Database for PostgreSQL Flexible Server instances and configure passwordless authentication with Microsoft Entra ID. Set up developer access, managed identities for apps, group-based '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-postgres/SKILL.md')
    assert 'USE FOR: passwordless for postgres, entra id postgres, azure ad postgres authentication, postgres managed identity, migrate postgres to passwordless, create postgres server, configure postgres auth.' in text, "expected to find: " + 'USE FOR: passwordless for postgres, entra id postgres, azure ad postgres authentication, postgres managed identity, migrate postgres to passwordless, create postgres server, configure postgres auth.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-postgres/SKILL.md')
    assert 'DO NOT USE FOR: MySQL databases (use azure-prepare), Cosmos DB (use azure-prepare), general Azure resource creation (use azure-prepare).' in text, "expected to find: " + 'DO NOT USE FOR: MySQL databases (use azure-prepare), Cosmos DB (use azure-prepare), general Azure resource creation (use azure-prepare).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-storage/SKILL.md')
    assert 'Azure Storage Services including Blob Storage, File Shares, Queue Storage, Table Storage, and Data Lake. Provides object storage, SMB file shares, async messaging, NoSQL key-value, and big data analyt' in text, "expected to find: " + 'Azure Storage Services including Blob Storage, File Shares, Queue Storage, Table Storage, and Data Lake. Provides object storage, SMB file shares, async messaging, NoSQL key-value, and big data analyt'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-storage/SKILL.md')
    assert 'USE FOR: blob storage, file shares, queue storage, table storage, data lake, upload files, download blobs, storage accounts, access tiers, lifecycle management.' in text, "expected to find: " + 'USE FOR: blob storage, file shares, queue storage, table storage, data lake, upload files, download blobs, storage accounts, access tiers, lifecycle management.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-storage/SKILL.md')
    assert 'DO NOT USE FOR: SQL databases (use azure-postgres), Cosmos DB (use azure-prepare), messaging with Event Hubs or Service Bus (use azure-messaging).' in text, "expected to find: " + 'DO NOT USE FOR: SQL databases (use azure-postgres), Cosmos DB (use azure-prepare), messaging with Event Hubs or Service Bus (use azure-messaging).'[:80]

