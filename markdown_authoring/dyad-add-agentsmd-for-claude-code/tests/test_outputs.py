"""Behavioral checks for dyad-add-agentsmd-for-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dyad")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Wrap reads in `useQuery`, providing a stable `queryKey`, async `queryFn` that calls the relevant `IpcClient` method, and conditionally use `enabled`/`initialData`/`meta` as needed.' in text, "expected to find: " + '- Wrap reads in `useQuery`, providing a stable `queryKey`, async `queryFn` that calls the relevant `IpcClient` method, and conditionally use `enabled`/`initialData`/`meta` as needed.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Wrap writes in `useMutation`; validate inputs locally, call the IPC client, and invalidate related queries on success. Use shared utilities (e.g., toast helpers) in `onError`.' in text, "expected to find: " + '- Wrap writes in `useMutation`; validate inputs locally, call the IPC client, and invalidate related queries on success. Use shared utilities (e.g., toast helpers) in `onError`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. `src/ipc/ipc_host.ts` registers handlers that live in files under `src/ipc/handlers/` (e.g., `app_handlers.ts`, `chat_stream_handlers.ts`, `settings_handlers.ts`).' in text, "expected to find: " + '3. `src/ipc/ipc_host.ts` registers handlers that live in files under `src/ipc/handlers/` (e.g., `app_handlers.ts`, `chat_stream_handlers.ts`, `settings_handlers.ts`).'[:80]

