"""Behavioral checks for workerd-add-typings-guidance-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/workerd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **NEVER** use generic names for top-level ambient types in `types/defines/` (e.g., `Identity`, `Preview`, `Config`); always prefix with the product/feature name (e.g., `CloudflareAccessIdentity`, `T' in text, "expected to find: " + '- **NEVER** use generic names for top-level ambient types in `types/defines/` (e.g., `Identity`, `Preview`, `Config`); always prefix with the product/feature name (e.g., `CloudflareAccessIdentity`, `T'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| Task                   | Location                                                      | Notes                                                                                                        ' in text, "expected to find: " + '| Task                   | Location                                                      | Notes                                                                                                        '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| Add/modify JS API      | `src/workerd/api/`                                            | C++ with JSG macros; see `jsg/jsg.h` for binding system                                                      ' in text, "expected to find: " + '| Add/modify JS API      | `src/workerd/api/`                                            | C++ with JSG macros; see `jsg/jsg.h` for binding system                                                      '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('types/AGENTS.md')
    assert '- **Index signatures (`[key: string]: unknown`) need justification.** Only add them when forward-compatibility is genuinely required (e.g., the API frequently adds new fields across releases). Documen' in text, "expected to find: " + '- **Index signatures (`[key: string]: unknown`) need justification.** Only add them when forward-compatibility is genuinely required (e.g., the API frequently adds new fields across releases). Documen'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('types/AGENTS.md')
    assert '- **Follow the existing convention** for the relevant product. Check the existing `defines/` file for that product (e.g., `cf.d.ts` uses `IncomingRequestCfProperties*`, `d1.d.ts` uses `D1*`, `ai-searc' in text, "expected to find: " + '- **Follow the existing convention** for the relevant product. Check the existing `defines/` file for that product (e.g., `cf.d.ts` uses `IncomingRequestCfProperties*`, `d1.d.ts` uses `D1*`, `ai-searc'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('types/AGENTS.md')
    assert 'Do **not** edit files in `generated-snapshot/` directly — they are overwritten by `just generate-types`. If the generated output looks wrong, fix the source layer (C++ RTTI, `JSG_TS_OVERRIDE`, or `def' in text, "expected to find: " + 'Do **not** edit files in `generated-snapshot/` directly — they are overwritten by `just generate-types`. If the generated output looks wrong, fix the source layer (C++ RTTI, `JSG_TS_OVERRIDE`, or `def'[:80]

