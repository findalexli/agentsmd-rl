"""Behavioral checks for cdxgen-add-agentsmd-and-githubcopilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cdxgen")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'cdxgen is a universal polyglot CycloneDX SBOM/BOM generator written in **pure ESM JavaScript** targeting Node.js ≥ 20 (with optional Bun/Deno support). It produces CycloneDX JSON documents for dozens ' in text, "expected to find: " + 'cdxgen is a universal polyglot CycloneDX SBOM/BOM generator written in **pure ESM JavaScript** targeting Node.js ≥ 20 (with optional Bun/Deno support). It produces CycloneDX JSON documents for dozens '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The project uses **ES modules only** (`"type": "module"`). Never generate `require()` calls or `module.exports`. The single CJS file (`index.cjs`) is auto-generated — do not edit it.' in text, "expected to find: " + 'The project uses **ES modules only** (`"type": "module"`). Never generate `require()` calls or `module.exports`. The single CJS file (`index.cjs`) is auto-generated — do not edit it.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'All public functions accept a single `options` plain object passed from the CLI. Never read `process.argv` inside library code — always use `options`:' in text, "expected to find: " + 'All public functions accept a single `options` plain object passed from the CLI. Never read `process.argv` inside library code — always use `options`:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Every public function accepts a single `options` plain object. It is created by the CLI argument parser in `bin/cdxgen.js` and threaded through the entire call chain without mutation. When adding new ' in text, "expected to find: " + 'Every public function accepts a single `options` plain object. It is created by the CLI argument parser in `bin/cdxgen.js` and threaded through the entire call chain without mutation. When adding new '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**cdxgen** is a universal, polyglot CycloneDX Bill-of-Materials (BOM) generator. It produces SBOM, CBOM, OBOM, SaaSBOM, CDXA, and VDR documents in CycloneDX JSON format. It is distributed as an npm pa' in text, "expected to find: " + '**cdxgen** is a universal, polyglot CycloneDX Bill-of-Materials (BOM) generator. It produces SBOM, CBOM, OBOM, SaaSBOM, CDXA, and VDR documents in CycloneDX JSON format. It is distributed as an npm pa'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'All outbound HTTP is done through `cdxgenAgent` (a `got` instance with retries, timeout, and proxy support), exported from `lib/helpers/utils.js`. Never import `got` directly in new code — use `cdxgen' in text, "expected to find: " + 'All outbound HTTP is done through `cdxgenAgent` (a `got` instance with retries, timeout, and proxy support), exported from `lib/helpers/utils.js`. Never import `got` directly in new code — use `cdxgen'[:80]

