"""Behavioral checks for esp-miner-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/esp-miner")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **API Type Safety**: The `SystemInfo` API uses a numeric 0/1 pattern for many boolean-like status fields (e.g., `overclockEnabled`, `overheat_mode`). In the backend, use `cJSON_AddNumberToObject(roo' in text, "expected to find: " + '- **API Type Safety**: The `SystemInfo` API uses a numeric 0/1 pattern for many boolean-like status fields (e.g., `overclockEnabled`, `overheat_mode`). In the backend, use `cJSON_AddNumberToObject(roo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Mock Data Parity**: When updating `openapi.yaml` and regenerating the API, you **must** update the mock data in `main/http_server/axe-os/src/app/services/system.service.ts`. The TypeScript compile' in text, "expected to find: " + '- **Mock Data Parity**: When updating `openapi.yaml` and regenerating the API, you **must** update the mock data in `main/http_server/axe-os/src/app/services/system.service.ts`. The TypeScript compile'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **API Generation**: If you modify `openapi.yaml`, you **must** run `npm run generate:api` in the `axe-os` directory to update the TypeScript services. This is also automatically handled by `npm run ' in text, "expected to find: " + '- **API Generation**: If you modify `openapi.yaml`, you **must** run `npm run generate:api` in the `axe-os` directory to update the TypeScript services. This is also automatically handled by `npm run '[:80]

