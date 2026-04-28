"""Outcome tests for OpenHands PR #14000 — Tavily search key moved to MCP settings.

Runs the project's own vitest suite once (per session) on the two affected
test files and exposes one Python test per relevant vitest case.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/openhands")
FRONTEND = REPO / "frontend"

# ANSI escape stripper — vitest writes ANSI in JSON `failureMessages` even with
# the JSON reporter, but the JSON envelope itself is plain.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _run_vitest() -> dict[str, str]:
    """Run vitest on the two changed test files, return {fullName: status}."""
    cmd = [
        "npx", "vitest", "run",
        "__tests__/routes/llm-settings.test.tsx",
        "__tests__/routes/mcp-settings.test.tsx",
        "--reporter=json",
    ]
    proc = subprocess.run(
        cmd, cwd=FRONTEND, capture_output=True, text=True, timeout=600,
    )
    raw = _ANSI_RE.sub("", proc.stdout)
    # Find the top-level JSON envelope (vitest may print warnings before it).
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end < 0:
        raise AssertionError(
            f"vitest produced no JSON envelope.\n"
            f"stdout (last 800):\n{proc.stdout[-800:]}\n"
            f"stderr (last 800):\n{proc.stderr[-800:]}"
        )
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"vitest JSON parse failed: {e}\n"
            f"stdout (last 800):\n{proc.stdout[-800:]}"
        )
    by_name: dict[str, str] = {}
    for tr in data.get("testResults", []):
        for ar in tr.get("assertionResults", []):
            by_name[ar["fullName"]] = ar["status"]
    return by_name


@pytest.fixture(scope="session")
def vitest_results() -> dict[str, str]:
    return _run_vitest()


def _assert_passed(results: dict[str, str], full_name: str) -> None:
    status = results.get(full_name)
    if status is None:
        # Surface a few sample names to help debugging.
        sample = list(results.keys())[:6]
        raise AssertionError(
            f"vitest case not found: {full_name!r}.\n"
            f"Sample available cases: {sample}"
        )
    assert status == "passed", (
        f"vitest case {full_name!r} reported status={status!r} (expected 'passed')."
    )


# ─────────────────────── fail-to-pass tests ─────────────────────────────────

def test_llm_save_excludes_search_api_key(vitest_results):
    """LLM settings save payload must not include `search_api_key`."""
    _assert_passed(
        vitest_results,
        "LlmSettingsScreen does not include search API key updates when saving basic LLM settings",
    )


def test_llm_advanced_view_omits_search_api_key_input(vitest_results):
    """Advanced LLM view must not render the `search-api-key-input` element."""
    _assert_passed(
        vitest_results,
        "LlmSettingsScreen does not render the search API key input in advanced LLM settings",
    )


def test_llm_save_preserves_mcp_owned_search_key_on_refetch(vitest_results):
    """Saving LLM settings must not flip into all-fields view when the
    refetched settings still carry an MCP-owned `search_api_key`."""
    _assert_passed(
        vitest_results,
        "LlmSettingsScreen does not reveal all-only fields after save when refetch includes an MCP-owned search API key",
    )


def test_mcp_settings_renders_and_saves_tavily(vitest_results):
    """The MCP settings screen must render the built-in Tavily search section
    and persist edits to `search_api_key` on save."""
    _assert_passed(
        vitest_results,
        "MCPSettingsScreen renders and saves the built-in Tavily search settings on the MCP page",
    )


# ─────────────────────── pass-to-pass tests (project CI) ────────────────────

def test_mcp_delete_flow_still_works(vitest_results):
    """p2p: existing MCP server delete flow must continue to pass."""
    _assert_passed(
        vitest_results,
        "MCPSettingsScreen removes a newly added MCP server after the delete flow completes",
    )


def test_no_unrelated_vitest_regressions(vitest_results):
    """p2p: no test in either suite should regress.

    There are 46 cases across the two files. All must pass; otherwise the
    change broke an unrelated assertion.
    """
    failed = sorted(name for name, status in vitest_results.items() if status != "passed")
    assert not failed, "vitest regressions:\n  - " + "\n  - ".join(failed)


def test_repo_lint_passes():
    """p2p: repo's `npm run lint` (typecheck + eslint + prettier) must pass.

    AGENTS.md mandates that frontend changes pass `npm run lint:fix && npm run build`.
    `lint` covers typecheck + eslint + prettier --check.
    """
    proc = subprocess.run(
        ["npm", "run", "lint"], cwd=FRONTEND,
        capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, (
        f"`npm run lint` failed (exit {proc.returncode}).\n"
        f"stdout tail:\n{proc.stdout[-1500:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )

# === bash -lc CI/CD-style test (Dimension 1) ===

def test_repo_lint_via_bash():
    """p2p: repo's lint must also pass when invoked through a login shell
    (closer to what CI/CD `run:` steps actually execute)."""
    proc = subprocess.run(
        ["bash", "-lc", "npm run lint"], cwd=FRONTEND,
        capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, (
        f"`bash -lc 'npm run lint'` failed (exit {proc.returncode}).\n"
        f"stdout tail:\n{proc.stdout[-1500:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )
