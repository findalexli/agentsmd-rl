"""Behavioral checks for ag-charts-improve-agentsmd-prompt (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ag-charts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('tools/prompts/AGENTS.md')
    assert '-   **Baseline verification:** Expect to run `nx test ag-charts-community`, `nx test ag-charts-enterprise`, and `nx e2e ag-charts-website` after meaningful chart changes.' in text, "expected to find: " + '-   **Baseline verification:** Expect to run `nx test ag-charts-community`, `nx test ag-charts-enterprise`, and `nx e2e ag-charts-website` after meaningful chart changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('tools/prompts/AGENTS.md')
    assert '-   When using the Puppeteer MCP tool, pass `allowDangerous: true`, run headless, and include `--ignore-certificate-errors` to handle the self-signed cert.' in text, "expected to find: " + '-   When using the Puppeteer MCP tool, pass `allowDangerous: true`, run headless, and include `--ignore-certificate-errors` to handle the self-signed cert.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('tools/prompts/AGENTS.md')
    assert '3. Run the relevant generation/typecheck command plus `nx validate-examples` (see [Example Validation + Building](#example-validation--building)).' in text, "expected to find: " + '3. Run the relevant generation/typecheck command plus `nx validate-examples` (see [Example Validation + Building](#example-validation--building)).'[:80]

