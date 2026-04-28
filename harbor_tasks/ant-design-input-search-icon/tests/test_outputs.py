"""
Behavioral tests for ant-design Input.Search searchIcon scaffold.

Each `def test_*` here maps 1:1 to a check id in eval_manifest.yaml.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")

# Inlined Jest test that exercises the three behaviours we care about.
# Written into the repo's __tests__ directory at run time so we don't
# rely on patching the upstream Search.test.tsx file.
SCAFFOLD_TEST_SRC = """\
import React from 'react';
import { render } from '@testing-library/react';

import ConfigProvider from '../../config-provider';
import Search from '../Search';

describe('Input.Search searchIcon (custom benchmark)', () => {
  it('SCAFFOLD_TEST_PROP: should render custom searchIcon prop in the search button', () => {
    const { container } = render(<Search searchIcon={<div>scaffold-bamboo</div>} />);
    const btn = container.querySelector('.ant-input-search-btn');
    expect(btn).not.toBeNull();
    expect(btn).toHaveTextContent('scaffold-bamboo');
  });

  it('SCAFFOLD_TEST_CONTEXT: should render searchIcon supplied via ConfigProvider inputSearch', () => {
    const { container } = render(
      <ConfigProvider inputSearch={{ searchIcon: <div>scaffold-foobar</div> }}>
        <Search />
      </ConfigProvider>,
    );
    const btn = container.querySelector('.ant-input-search-btn');
    expect(btn).not.toBeNull();
    expect(btn).toHaveTextContent('scaffold-foobar');
  });

  it('SCAFFOLD_TEST_OVERRIDE: prop searchIcon should win over ConfigProvider searchIcon', () => {
    const { container } = render(
      <ConfigProvider inputSearch={{ searchIcon: <div>scaffold-foobar</div> }}>
        <Search searchIcon={<div>scaffold-bamboo</div>} />
      </ConfigProvider>,
    );
    const btn = container.querySelector('.ant-input-search-btn');
    expect(btn).not.toBeNull();
    expect(btn).toHaveTextContent('scaffold-bamboo');
    expect(btn).not.toHaveTextContent('scaffold-foobar');
  });
});
"""

SCAFFOLD_DEST = REPO / "components/input/__tests__/searchIconCustom.test.tsx"


def _ensure_scaffold_test_present() -> None:
    SCAFFOLD_DEST.parent.mkdir(parents=True, exist_ok=True)
    SCAFFOLD_DEST.write_text(SCAFFOLD_TEST_SRC, encoding="utf-8")


def _run_jest(test_path_pattern: str) -> dict:
    """Run jest with --json output and return the parsed JSON report."""
    json_out = Path("/tmp/jest_out.json")
    if json_out.exists():
        json_out.unlink()
    cmd = [
        "npx",
        "jest",
        "--config",
        ".jest.js",
        "--no-cache",
        "--testPathPatterns",
        test_path_pattern,
        "--json",
        "--outputFile",
        str(json_out),
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1"},
    )
    if not json_out.exists():
        raise AssertionError(
            "Jest did not produce JSON output.\n"
            f"stdout:\n{proc.stdout[-2000:]}\n"
            f"stderr:\n{proc.stderr[-2000:]}"
        )
    with json_out.open() as f:
        return json.load(f)


def _find_assertion(report: dict, title_substring: str) -> dict:
    for tr in report.get("testResults", []):
        for ar in tr.get("assertionResults", []):
            full = ar.get("fullName", "") or ""
            if title_substring in full or title_substring in ar.get("title", ""):
                return ar
    seen = [
        ar.get("fullName")
        for tr in report.get("testResults", [])
        for ar in tr.get("assertionResults", [])
    ]
    raise AssertionError(
        f"Could not find a test matching {title_substring!r} in jest report. "
        f"Saw: {seen}"
    )


# ---------------------------------------------------------------------------
# Behavioral tests (fail_to_pass)
# ---------------------------------------------------------------------------


def test_search_icon_prop_renders_in_button():
    """Custom `searchIcon` prop must render inside the search button."""
    _ensure_scaffold_test_present()
    report = _run_jest("searchIconCustom")
    assertion = _find_assertion(report, "SCAFFOLD_TEST_PROP")
    assert assertion["status"] == "passed", (
        f"Expected SCAFFOLD_TEST_PROP to pass, got status={assertion['status']}.\n"
        f"failureMessages={assertion.get('failureMessages')}"
    )


def test_search_icon_via_config_provider():
    """`ConfigProvider inputSearch={{ searchIcon }}` must propagate to Search."""
    _ensure_scaffold_test_present()
    report = _run_jest("searchIconCustom")
    assertion = _find_assertion(report, "SCAFFOLD_TEST_CONTEXT")
    assert assertion["status"] == "passed", (
        f"Expected SCAFFOLD_TEST_CONTEXT to pass, got status={assertion['status']}.\n"
        f"failureMessages={assertion.get('failureMessages')}"
    )


def test_search_icon_prop_overrides_config_provider():
    """When both prop and ConfigProvider supply searchIcon, prop must win."""
    _ensure_scaffold_test_present()
    report = _run_jest("searchIconCustom")
    assertion = _find_assertion(report, "SCAFFOLD_TEST_OVERRIDE")
    assert assertion["status"] == "passed", (
        f"Expected SCAFFOLD_TEST_OVERRIDE to pass, got status={assertion['status']}.\n"
        f"failureMessages={assertion.get('failureMessages')}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: existing Search behavior must not regress.
# ---------------------------------------------------------------------------


def test_existing_search_suite_passes():
    """Repo's own Search.test.tsx must continue to pass (regression gate)."""
    report = _run_jest("input/__tests__/Search.test.tsx")
    failed = report.get("numFailedTests", -1)
    passed = report.get("numPassedTests", 0)
    assert failed == 0, (
        f"Existing Search test suite reported {failed} failures (expected 0). "
        f"numTotalTests={report.get('numTotalTests')}"
    )
    assert passed >= 25, (
        f"Search.test.tsx ran fewer tests than expected: {passed}. "
        "Suite may have broken."
    )


# ---------------------------------------------------------------------------
# Agent-config rules — extracted from CLAUDE.md / AGENTS.md / copilot-instructions.md
# ---------------------------------------------------------------------------


def test_search_icon_documented_english():
    """index.en-US.md table row for `searchIcon` must exist (per AGENTS.md)."""
    text = (REPO / "components/input/index.en-US.md").read_text(encoding="utf-8")
    assert "| searchIcon " in text or "|searchIcon " in text, (
        "Expected an API table row for `searchIcon` in components/input/index.en-US.md"
    )


def test_search_icon_documented_chinese():
    """index.zh-CN.md table row for `searchIcon` must exist (per CLAUDE.md)."""
    text = (REPO / "components/input/index.zh-CN.md").read_text(encoding="utf-8")
    assert "| searchIcon " in text or "|searchIcon " in text, (
        "Expected an API table row for `searchIcon` in components/input/index.zh-CN.md"
    )


def test_search_icon_has_version_annotation():
    """
    CLAUDE.md: '新增属性需声明版本号' — new properties must declare a version.
    The English doc table row for `searchIcon` must include a SemVer.
    """
    text = (REPO / "components/input/index.en-US.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("| searchIcon ") or stripped.startswith("|searchIcon "):
            assert re.search(r"\b\d+\.\d+\.\d+\b", line), (
                "searchIcon row in index.en-US.md is missing a SemVer version "
                f"annotation: {line!r}"
            )
            return
    raise AssertionError(
        "No `searchIcon` API row found in components/input/index.en-US.md"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")