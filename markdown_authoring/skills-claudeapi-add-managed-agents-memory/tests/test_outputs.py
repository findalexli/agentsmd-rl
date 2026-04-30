"""Behavioral checks for skills-claudeapi-add-managed-agents-memory (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/SKILL.md')
    assert '**Reading guide:** Start with `shared/managed-agents-overview.md`, then the topical `shared/managed-agents-*.md` files (core, environments, tools, events, memory, client-patterns, onboarding, api-refe' in text, "expected to find: " + '**Reading guide:** Start with `shared/managed-agents-overview.md`, then the topical `shared/managed-agents-*.md` files (core, environments, tools, events, memory, client-patterns, onboarding, api-refe'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/SKILL.md')
    assert '**Beta headers:** `managed-agents-2026-04-01` — the SDK sets this automatically for all `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` calls. Skills API uses `skills-2025-10-02` a' in text, "expected to find: " + '**Beta headers:** `managed-agents-2026-04-01` — the SDK sets this automatically for all `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` calls. Skills API uses `skills-2025-10-02` a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-api-reference.md')
    assert 'Individual text documents inside a store (≤ 100KB each). `create` creates at a `path` and returns `409` (`memory_path_conflict_error`, with `conflicting_memory_id`) if the path is occupied; `update` m' in text, "expected to find: " + 'Individual text documents inside a store (≤ 100KB each). `create` creates at a `path` and returns `409` (`memory_path_conflict_error`, with `conflicting_memory_id`) if the path is occupied; `update` m'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-api-reference.md')
    assert '- Agents have **no delete** — only `archive`. Archive is **permanent**: the agent becomes read-only, new sessions cannot reference it, and there is no unarchive. Confirm with the user before archiving' in text, "expected to find: " + '- Agents have **no delete** — only `archive`. Archive is **permanent**: the agent becomes read-only, new sessions cannot reference it, and there is no unarchive. Confirm with the user before archiving'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-api-reference.md')
    assert 'Workspace-scoped persistent memory that survives across sessions. Attach to a session via a `{"type": "memory_store", "memory_store_id": ...}` entry in `resources[]` (session-create time only). See `s' in text, "expected to find: " + 'Workspace-scoped persistent memory that survives across sessions. Attach to a session via a `{"type": "memory_store", "memory_store_id": ...}` entry in `resources[]` (session-create time only). See `s'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-core.md')
    assert '| `resources`     | array    | No       | Files, GitHub repos, or memory stores, attached to the container at startup. Memory stores are session-create-only (not addable via `resources.add()`). |' in text, "expected to find: " + '| `resources`     | array    | No       | Files, GitHub repos, or memory stores, attached to the container at startup. Memory stores are session-create-only (not addable via `resources.add()`). |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-core.md')
    assert '| `resources` | array | Attached files, repos, and memory stores |' in text, "expected to find: " + '| `resources` | array | Attached files, repos, and memory stores |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-core.md')
    assert '├── Resources (files, repos, memory stores — attached at startup)' in text, "expected to find: " + '├── Resources (files, repos, memory stores — attached at startup)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-environments.md')
    assert "Attach files, GitHub repositories, and memory stores to a session. **Session creation blocks until all resources are mounted** — the container won't go `running` until every file and repo is in place." in text, "expected to find: " + "Attach files, GitHub repositories, and memory stores to a session. **Session creation blocks until all resources are mounted** — the container won't go `running` until every file and repo is in place."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-memory.md')
    assert 'Each attached store is mounted in the session container at `/mnt/memory/<store-name>/`. The agent interacts with it using the standard file tools (`bash`, `read`, `write`, `edit`, `glob`, `grep`) — th' in text, "expected to find: " + 'Each attached store is mounted in the session container at `/mnt/memory/<store-name>/`. The agent interacts with it using the standard file tools (`bash`, `read`, `write`, `edit`, `glob`, `grep`) — th'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-memory.md')
    assert 'Returns `Memory | MemoryPrefix` entries — a `MemoryPrefix` (`type: "memory_prefix"`, just a `path`) is a directory-like node when listing hierarchically. Use `path_prefix` to scope (include a trailing' in text, "expected to find: " + 'Returns `Memory | MemoryPrefix` entries — a `MemoryPrefix` (`type: "memory_prefix"`, just a `path`) is a directory-like node when listing hierarchically. Use `path_prefix` to scope (include a trailing'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-memory.md')
    assert 'Sessions are ephemeral by default — when one ends, anything the agent learned is gone. A **memory store** is a workspace-scoped collection of small text documents that persists across sessions. When a' in text, "expected to find: " + 'Sessions are ephemeral by default — when one ends, anything the agent learned is gone. A **memory store** is a workspace-scoped collection of small text documents that persists across sessions. When a'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-overview.md')
    assert '**Which beta header goes where:** The SDK sets `managed-agents-2026-04-01` automatically on `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` calls, and `files-api-2025-04-14` / `ski' in text, "expected to find: " + '**Which beta header goes where:** The SDK sets `managed-agents-2026-04-01` automatically on `client.beta.{agents,environments,sessions,vaults,memory_stores}.*` calls, and `files-api-2025-04-14` / `ski'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-overview.md')
    assert '- **Archive is permanent on every resource** — archiving an agent, environment, session, vault, credential, or memory store makes it read-only with no unarchive. For agents, environments, and memory s' in text, "expected to find: " + '- **Archive is permanent on every resource** — archiving an agent, environment, session, vault, credential, or memory store makes it read-only with no unarchive. For agents, environments, and memory s'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/claude-api/shared/managed-agents-overview.md')
    assert '| Give agents persistent memory across sessions | `shared/managed-agents-memory.md` — memory stores, `memory_store` session resource, preconditions, versions/redact |' in text, "expected to find: " + '| Give agents persistent memory across sessions | `shared/managed-agents-memory.md` — memory stores, `memory_store` session resource, preconditions, versions/redact |'[:80]

