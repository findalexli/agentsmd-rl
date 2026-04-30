"""Behavioral checks for workers-sdk-improve-agentsmd-files-based-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/workers-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When making architectural changes to a package (renaming files, adding entry points, changing build output), update the relevant AGENTS.md to reflect the new structure.' in text, "expected to find: " + 'When making architectural changes to a package (renaming files, adding entry points, changing build output), update the relevant AGENTS.md to reflect the new structure.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- E2E vitest configs do NOT set `globals: true` — this rule is critical there; forgetting `{ expect }` in the callback causes `ReferenceError` at runtime' in text, "expected to find: " + '- E2E vitest configs do NOT set `globals: true` — this rule is critical there; forgetting `{ expect }` in the callback causes `ReferenceError` at runtime'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Trivial/obvious code comments** → don\'t add comments that restate what the code does; comments should explain "why", not "what"' in text, "expected to find: " + '- **Trivial/obvious code comments** → don\'t add comments that restate what the code does; comments should explain "why", not "what"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/miniflare/AGENTS.md')
    assert '- `src/workers/local-explorer/openapi.local.json` — generated from `scripts/openapi-filter-config.ts`, modify the config not the output' in text, "expected to find: " + '- `src/workers/local-explorer/openapi.local.json` — generated from `scripts/openapi-filter-config.ts`, modify the config not the output'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/miniflare/AGENTS.md')
    assert "- `src/runtime/config/generated/workerd.ts` — generated Cap'n Proto types, do not edit directly" in text, "expected to find: " + "- `src/runtime/config/generated/workerd.ts` — generated Cap'n Proto types, do not edit directly"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/miniflare/AGENTS.md')
    assert '## Generated Files' in text, "expected to find: " + '## Generated Files'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/wrangler/AGENTS.md')
    assert '- When adding `expect` as a parameter to helper functions, check ALL call sites (e.g., across `deployments.test.ts`, `versions.test.ts`)' in text, "expected to find: " + '- When adding `expect` as a parameter to helper functions, check ALL call sites (e.g., across `deployments.test.ts`, `versions.test.ts`)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/wrangler/AGENTS.md')
    assert '- Never import `expect` from vitest — use test context `({ expect }) => {}`' in text, "expected to find: " + '- Never import `expect` from vitest — use test context `({ expect }) => {}`'[:80]

