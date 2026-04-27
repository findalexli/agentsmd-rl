"""Behavioral tests for the chart-composition class -> function refactor."""
import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/superset")
SRC = REPO / "superset-frontend/packages/superset-ui-core/src/chart-composition"
HARNESS = Path("/test_harness")
TARGET_FILES = [
    SRC / "ChartFrame.tsx",
    SRC / "legend/WithLegend.tsx",
    SRC / "tooltip/TooltipFrame.tsx",
]


@pytest.fixture(scope="module")
def harness_output():
    """Run the Node harness once and parse its JSON output."""
    proc = subprocess.run(
        ["node", "/test_harness/run.cjs"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        pytest.fail(
            f"Harness failed (exit {proc.returncode}).\n"
            f"STDERR:\n{proc.stderr[-2000:]}\n"
            f"STDOUT:\n{proc.stdout[-2000:]}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"Harness produced non-JSON output: {e}\n"
            f"STDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass: structural conversion of components
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("component", ["ChartFrame", "WithLegend", "TooltipFrame"])
def test_component_default_export_is_memo_wrapped(harness_output, component):
    """Each default export must be wrapped via React.memo()."""
    info = harness_output["components"].get(component)
    assert info, f"Harness produced no entry for {component}"
    assert "error" not in info, f"Component load error: {info.get('error')}"
    assert info["is_memo"] is True, (
        f"{component} default export is not a memo() result; got {info!r}"
    )


@pytest.mark.parametrize("component", ["ChartFrame", "WithLegend", "TooltipFrame"])
def test_component_inner_is_function_not_class(harness_output, component):
    """Inner component (after unwrapping memo) must be a function, not a class."""
    info = harness_output["components"].get(component)
    assert info, f"No harness entry for {component}"
    assert "error" not in info, f"Component load error: {info.get('error')}"
    assert info["inner_is_class"] is False, (
        f"{component} inner type is still a class component"
    )
    assert info["inner_is_pure_class"] is False, (
        f"{component} inner type still extends PureComponent"
    )
    assert info["inner_typeof"] == "function", (
        f"{component} inner is not a plain function: {info!r}"
    )


@pytest.mark.parametrize("component", ["ChartFrame", "WithLegend", "TooltipFrame"])
def test_component_source_no_purecomponent(harness_output, component):
    """Source files must not import or reference PureComponent."""
    info = harness_output["components"].get(component)
    assert info, f"No harness entry for {component}"
    assert info.get("source_uses_purecomponent") is False, (
        f"{component} source still references PureComponent"
    )
    assert info.get("source_uses_class_keyword") is False, (
        f"{component} source still defines a class with that name"
    )


# ---------------------------------------------------------------------------
# Behavioral parity: components still render correctly
# ---------------------------------------------------------------------------

def test_chartframe_renders_default_without_throwing(harness_output):
    """ChartFrame must render even when renderContent prop is omitted."""
    r = harness_output["renders"]["ChartFrame_default_render"]
    assert r["ok"] is True, f"Render threw: {r.get('error')}"


def test_chartframe_renders_content_when_fits(harness_output):
    """When content fits in frame, the renderContent output must be present."""
    r = harness_output["renders"]["ChartFrame_fits"]
    assert r["ok"] is True, f"Render threw: {r.get('error')}"
    assert "200x200" in r["html"], f"renderContent output missing: {r['html']!r}"


def test_chartframe_overflow_wraps_in_scroll_div(harness_output):
    """When contentWidth > width, frame must wrap in a div with overflowX:auto."""
    r = harness_output["renders"]["ChartFrame_overflowX"]
    assert r["ok"] is True, f"Render threw: {r.get('error')}"
    assert "overflow-x:auto" in r["html"].replace(" ", "").lower(), (
        f"Expected scroll wrapper missing: {r['html']!r}"
    )
    # Content size should be at least frame width (300 here, since contentWidth=300)
    assert "300x" in r["html"], f"Expected content sized at 300: {r['html']!r}"


def test_tooltipframe_renders_children(harness_output):
    """TooltipFrame must render its children inside a div."""
    r = harness_output["renders"]["TooltipFrame_default"]
    assert r["ok"] is True, f"Render threw: {r.get('error')}"
    assert "<span>inner</span>" in r["html"], f"Children missing: {r['html']!r}"


def test_tooltipframe_applies_classname(harness_output):
    """TooltipFrame must apply provided className to the outer div."""
    r = harness_output["renders"]["TooltipFrame_with_class"]
    assert r["ok"] is True, f"Render threw: {r.get('error')}"
    html = r["html"]
    assert 'class="tt"' in html, f"className not applied: {html!r}"


def test_withlegend_renders_smoke(harness_output):
    """WithLegend must render without throwing in a smoke test."""
    r = harness_output["renders"]["WithLegend_smoke"]
    assert r["ok"] is True, f"Render threw: {r.get('error')}"
    assert "with-legend" in r["html"], f"Container class missing: {r['html']!r}"


def test_withlegend_renders_legend_section(harness_output):
    """When renderLegend is provided, the legend container must appear."""
    r = harness_output["renders"]["WithLegend_with_legend"]
    assert r["ok"] is True, f"Render threw: {r.get('error')}"
    html = r["html"]
    assert "legend-container" in html, f"legend-container missing: {html!r}"
    # 'left' position => horizontal => legend direction 'column'
    assert "legend-column" in html, f"legend direction missing: {html!r}"


# ---------------------------------------------------------------------------
# Pass-to-pass: agent-config rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

def test_target_files_have_apache_license_header():
    """AGENTS.md: 'New files require ASF license headers'.
    These are existing files; they must keep their license header.
    """
    for f in TARGET_FILES:
        assert f.exists(), f"{f} does not exist"
        head = f.read_text()[:1500]
        assert "Licensed to the Apache Software Foundation" in head, (
            f"License header missing in {f}"
        )
        assert "Apache License, Version 2.0" in head, (
            f"License version missing in {f}"
        )


def test_target_files_no_any_type():
    """AGENTS.md/CLAUDE.md: 'NO `any` types - Use proper TypeScript types'.
    The 3 target files must not introduce explicit `any` annotations.
    """
    for f in TARGET_FILES:
        content = f.read_text()
        # Look for `: any`, `<any>`, `as any`. Must not introduce these.
        assert ": any" not in content, f"`: any` annotation found in {f}"
        assert "as any" not in content, f"`as any` cast found in {f}"
        assert "<any>" not in content, f"`<any>` annotation found in {f}"


def test_target_files_have_no_time_specific_comments():
    """AGENTS.md: 'Avoid time-specific language' in code comments.
    The 3 target files' comments must not introduce 'now', 'currently', 'today'.
    """
    bad_words = (" now ", " currently ", " today ")
    for f in TARGET_FILES:
        # Check only single/multi-line comments to avoid hitting strings/identifiers
        text = f.read_text().lower()
        # Naive: scan only lines that look like comments
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
                for w in bad_words:
                    assert w not in (" " + stripped + " "), (
                        f"Time-specific word {w.strip()!r} found in comment in {f}: {line!r}"
                    )


def test_target_files_compile_without_typeerror():
    """Repo CI runs the TypeScript compiler. The 3 target files must parse
    cleanly via esbuild's TypeScript loader (a fast structural sanity check)."""
    for f in TARGET_FILES:
        r = subprocess.run(
            [
                "node",
                "-e",
                f"require('esbuild').transformSync(require('fs').readFileSync({json.dumps(str(f))}, 'utf8'), {{loader: 'tsx', jsx: 'automatic'}})",
            ],
            cwd="/test_harness",
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, (
            f"{f.name} failed to parse as TSX:\n{r.stderr}"
        )
