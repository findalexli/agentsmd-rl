"""Behavioral checks for nanoclaw-add-official-qodo-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/SKILL.md')
    assert 'description: "Loads org- and repo-level coding rules from Qodo before code tasks begin, ensuring all generation and modification follows team standards. Use before any code generation or modification ' in text, "expected to find: " + 'description: "Loads org- and repo-level coding rules from Qodo before code tasks begin, ensuring all generation and modification follows team standards. Use before any code generation or modification '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/SKILL.md')
    assert '- **Environment name**: Read from `~/.qodo/config.json` (`ENVIRONMENT_NAME` field), with `QODO_ENVIRONMENT_NAME` environment variable taking precedence. If not found, inform the user that an API key i' in text, "expected to find: " + '- **Environment name**: Read from `~/.qodo/config.json` (`ENVIRONMENT_NAME` field), with `QODO_ENVIRONMENT_NAME` environment variable taking precedence. If not found, inform the user that an API key i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/SKILL.md')
    assert 'Fetches repository-specific coding rules from the Qodo platform API before code generation or modification tasks. Rules include security requirements, coding standards, quality guidelines, and team co' in text, "expected to find: " + 'Fetches repository-specific coding rules from the Qodo platform API before code generation or modification tasks. Rules include security requirements, coding standards, quality guidelines, and team co'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/output-format.md')
    assert 'Rules loaded: **{TOTAL_RULES}** (universal, org level, repo level, and path level rules)' in text, "expected to find: " + 'Rules loaded: **{TOTAL_RULES}** (universal, org level, repo level, and path level rules)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/output-format.md')
    assert 'These rules must be applied during code generation based on severity:' in text, "expected to find: " + 'These rules must be applied during code generation based on severity:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/output-format.md')
    assert 'Group rules into three sections and print each non-empty section:' in text, "expected to find: " + 'Group rules into three sections and print each non-empty section:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/pagination.md')
    assert 'If total rules == 0, inform the user no rules are configured for the repository scope and exit gracefully.' in text, "expected to find: " + 'If total rules == 0, inform the user no rules are configured for the repository scope and exit gracefully.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/pagination.md')
    assert 'The API returns rules in pages of 50. All pages must be fetched to ensure no rules are missed.' in text, "expected to find: " + 'The API returns rules in pages of 50. All pages must be fetched to ensure no rules are missed.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/pagination.md')
    assert '2. Request: `GET {API_URL}/rules?scopes={ENCODED_SCOPE}&state=active&page={PAGE}&page_size=50`' in text, "expected to find: " + '2. Request: `GET {API_URL}/rules?scopes={ENCODED_SCOPE}&state=active&page={PAGE}&page_size=50`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/repository-scope.md')
    assert 'If the current working directory is inside a `modules/*` subdirectory relative to the repository root, use it as the query scope:' in text, "expected to find: " + 'If the current working directory is inside a `modules/*` subdirectory relative to the repository root, use it as the query scope:'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/repository-scope.md')
    assert 'If no remote is found, exit silently. If the URL cannot be parsed, inform the user and exit gracefully.' in text, "expected to find: " + 'If no remote is found, exit silently. If the URL cannot be parsed, inform the user and exit gracefully.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/get-qodo-rules/references/repository-scope.md')
    assert 'Parse the `origin` remote URL to derive the scope path. Both URL formats are supported:' in text, "expected to find: " + 'Parse the `origin` remote URL to derive the scope path. Both URL formats are supported:'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qodo-pr-resolver/SKILL.md')
    assert '- Implement the fix by **executing the Qodo agent prompt as a direct instruction**. The agent prompt is the fix specification — follow it literally, do not reinterpret or improvise a different solutio' in text, "expected to find: " + '- Implement the fix by **executing the Qodo agent prompt as a direct instruction**. The agent prompt is the fix specification — follow it literally, do not reinterpret or improvise a different solutio'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qodo-pr-resolver/SKILL.md')
    assert '**CRITICAL:** Single validation only - do NOT show the diff separately and then ask. Combine the diff display and the question into ONE message. The user should see: brief context → current code → pro' in text, "expected to find: " + '**CRITICAL:** Single validation only - do NOT show the diff separately and then ask. Combine the diff display and the question into ONE message. The user should see: brief context → current code → pro'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qodo-pr-resolver/SKILL.md')
    assert '- If yes: Use appropriate CLI to create PR/MR (see [providers.md § Create PR/MR](./resources/providers.md#create-prmr-special-case)), then inform "PR created! Qodo will review it shortly. Run this ski' in text, "expected to find: " + '- If yes: Use appropriate CLI to create PR/MR (see [providers.md § Create PR/MR](./resources/providers.md#create-prmr-special-case)), then inform "PR created! Qodo will review it shortly. Run this ski'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qodo-pr-resolver/resources/providers.md')
    assert 'This document contains all provider-specific CLI commands and API interactions for the Qodo PR Resolver skill. Reference this file when implementing provider-specific operations.' in text, "expected to find: " + 'This document contains all provider-specific CLI commands and API interactions for the Qodo PR Resolver skill. Reference this file when implementing provider-specific operations.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qodo-pr-resolver/resources/providers.md')
    assert '- **Authenticate:** `az login` then `az devops configure --defaults organization=https://dev.azure.com/yourorg project=yourproject`' in text, "expected to find: " + '- **Authenticate:** `az login` then `az devops configure --defaults organization=https://dev.azure.com/yourorg project=yourproject`'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qodo-pr-resolver/resources/providers.md')
    assert '- **Install:** `brew install azure-cli` or [docs.microsoft.com/cli/azure](https://docs.microsoft.com/cli/azure)' in text, "expected to find: " + '- **Install:** `brew install azure-cli` or [docs.microsoft.com/cli/azure](https://docs.microsoft.com/cli/azure)'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `/get-qodo-rules` | Load org- and repo-level coding rules from Qodo before code tasks |' in text, "expected to find: " + '| `/get-qodo-rules` | Load org- and repo-level coding rules from Qodo before code tasks |'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `/qodo-pr-resolver` | Fetch and fix Qodo PR review issues interactively or in batch |' in text, "expected to find: " + '| `/qodo-pr-resolver` | Fetch and fix Qodo PR review issues interactively or in batch |'[:80]

