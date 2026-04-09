"""
Task: sglang-diffusion-dashboard-charts
Repo: sgl-project/sglang @ 9b4dd274787ce4a778b7688c65c33598282a6559
PR:   21653

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import sys
import tempfile

sys.path.insert(0, "/repo")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_run(ts, sha, cases):
    """Build a run dict matching the expected format for generate_dashboard.

    cases: {case_id: {framework: latency_float}}
    The function expects a flat 'results' list with 'latency_s' keys.
    """
    results = []
    for cid, fws in cases.items():
        for fw, v in fws.items():
            results.append({
                "case_id": cid,
                "framework": fw,
                "model": cid,
                "latency_s": v,
            })
    return {"timestamp": ts, "commit_sha": sha, "results": results}


def capture_axes(func, current, history, charts_dir):
    """Call generate_dashboard while capturing matplotlib axes."""
    captured = []
    orig = plt.subplots

    def patched(*a, **kw):
        fig, ax = orig(*a, **kw)
        captured.append(ax)
        return fig, ax

    plt.subplots = patched
    try:
        md = func(current, history, charts_dir=charts_dir)
    finally:
        plt.subplots = orig
    return md, captured


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """generate_diffusion_dashboard.py must parse without errors."""
    import py_compile
    py_compile.compile(
        "/repo/scripts/ci/utils/diffusion/generate_diffusion_dashboard.py",
        doraise=True,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_yaxis_scales_to_data_range():
    """Y-axis uses data-range-based limits instead of bottom=0."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    # Values clustered around 48-53 — y-axis should NOT start at 0
    current = make_run(
        "2025-01-15T00:00:00Z", "abc123",
        {"case1": {"sglang": 48.0, "vllm-omni": 52.0}},
    )
    history = [
        make_run(
            "2025-01-14T00:00:00Z", "def456",
            {"case1": {"sglang": 50.0, "vllm-omni": 53.0}},
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        _, axes = capture_axes(generate_dashboard, current, history, td)
        assert axes, "no axes captured"
        # Find the latency chart (first one)
        ymin, _ = axes[0].get_ylim()
        # Buggy: ymin=0 (bottom=0). Fixed: ymin should be well above 0
        assert ymin > 10, f"ymin={ymin:.2f}, expected > 10 for values in 48-53 range"


# [pr_diff] fail_to_pass
def test_yaxis_scales_high_values():
    """Y-axis adapts to a higher value range (90-100), not pinned at 0."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    current = make_run(
        "2025-02-01T00:00:00Z", "hi001",
        {"high_case": {"sglang": 95.0, "vllm-omni": 98.0}},
    )
    history = [
        make_run(
            "2025-01-31T00:00:00Z", "hi002",
            {"high_case": {"sglang": 92.0, "vllm-omni": 97.0}},
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        _, axes = capture_axes(generate_dashboard, current, history, td)
        assert axes, "no axes captured"
        ymin, _ = axes[0].get_ylim()
        assert ymin > 50, f"ymin={ymin:.2f}, expected > 50 for values in 92-98 range"


# [pr_diff] pass_to_pass
def test_yaxis_never_negative():
    """Y-axis bottom should be >= 0 even with low values near zero."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    current = make_run(
        "2025-01-15T00:00:00Z", "lo001",
        {"lo": {"sglang": 0.5, "vllm-omni": 1.0}},
    )
    history = [
        make_run(
            "2025-01-14T00:00:00Z", "lo002",
            {"lo": {"sglang": 0.8, "vllm-omni": 1.2}},
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        _, axes = capture_axes(generate_dashboard, current, history, td)
        assert axes, "no axes captured"
        ymin, _ = axes[0].get_ylim()
        assert ymin >= 0, f"ymin={ymin:.4f}, must be >= 0"


# [pr_diff] fail_to_pass
def test_legend_not_upper_right():
    """Legend moved away from upper-right to reduce data overlap."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    current = make_run(
        "2025-01-15T00:00:00Z", "leg1",
        {"case1": {"sglang": 10.0, "vllm-omni": 12.0}},
    )
    history = [
        make_run(
            "2025-01-14T00:00:00Z", "leg2",
            {"case1": {"sglang": 11.0, "vllm-omni": 13.0}},
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        _, axes = capture_axes(generate_dashboard, current, history, td)
        assert axes, "no axes captured"
        legend = axes[0].get_legend()
        assert legend, "no legend found"
        loc = legend._loc
        # matplotlib loc codes: 1=upper right (buggy default)
        assert loc != 1, f"legend still in upper right (loc={loc})"


# [pr_diff] fail_to_pass
def test_history_window_extended():
    """MAX_HISTORY_RUNS increased beyond 7 to cover ~2 weeks."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import MAX_HISTORY_RUNS

    assert MAX_HISTORY_RUNS > 7, (
        f"MAX_HISTORY_RUNS={MAX_HISTORY_RUNS}, expected > 7 for ~2 weeks of data"
    )
    # Also verify it's at least 12 (roughly 2 weeks)
    assert MAX_HISTORY_RUNS >= 12, (
        f"MAX_HISTORY_RUNS={MAX_HISTORY_RUNS}, expected >= 12 for ~2 weeks"
    )


# [pr_diff] fail_to_pass
def test_section_header_reflects_actual_count():
    """Section header says actual run count, not hardcoded '7'."""
    import re
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    # 4 history + 1 current = 5 runs
    current = make_run(
        "2025-01-15T00:00:00Z", "curr00",
        {"case1": {"sglang": 10.0}},
    )
    history = [
        make_run(
            f"2025-01-{14 - i:02d}T00:00:00Z",
            f"sha{i}",
            {"case1": {"sglang": 10.0 + i}},
        )
        for i in range(4)
    ]

    md = generate_dashboard(current, history)

    assert "Last 7 Runs" not in md, "header still hardcoded to 7"
    # Accept any dynamic count
    m = re.search(r"Last (\d+) Runs", md)
    if m:
        count = int(m.group(1))
        assert count != 7, "header hardcoded to 7"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_dashboard_generates_valid_markdown():
    """generate_dashboard returns markdown with tables, case IDs, latency values."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    current = make_run(
        "2025-01-15T00:00:00Z", "abc123def",
        {
            "wan22_ti2v": {"sglang": 45.2, "vllm-omni": 50.1},
            "flux_t2i": {"sglang": 12.5, "vllm-omni": 15.3},
        },
    )
    history = [
        make_run(
            "2025-01-14T00:00:00Z", "def456abc",
            {
                "wan22_ti2v": {"sglang": 46.0, "vllm-omni": 51.0},
                "flux_t2i": {"sglang": 13.0, "vllm-omni": 16.0},
            },
        )
    ]

    md = generate_dashboard(current, history)
    assert isinstance(md, str) and len(md) >= 200, "output too short or wrong type"
    assert "|" in md, "no table separators"
    assert "wan22_ti2v" in md, "missing case id"
    assert "abc123d" in md, "missing commit sha"
    assert "45.2" in md or "45.20" in md, "missing latency value"


# [pr_diff] pass_to_pass
def test_chart_png_files_generated():
    """Charts saved to disk as PNG when charts_dir provided."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    current = make_run(
        "2025-01-15T00:00:00Z", "png1",
        {"test_case": {"sglang": 10.0, "vllm-omni": 12.0}},
    )
    history = [
        make_run(
            "2025-01-14T00:00:00Z", "png2",
            {"test_case": {"sglang": 11.0, "vllm-omni": 13.0}},
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        generate_dashboard(current, history, charts_dir=td)
        pngs = [f for f in os.listdir(td) if f.endswith(".png")]
        assert len(pngs) >= 1, f"no PNG files in {os.listdir(td)}"
        sizes = [os.path.getsize(os.path.join(td, f)) for f in pngs]
        assert all(s > 1000 for s in sizes), f"PNG files too small: {sizes}"


# [pr_diff] pass_to_pass
def test_multiple_cases_produce_multiple_charts():
    """Each case gets its own latency chart file."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    current = make_run(
        "2025-01-15T00:00:00Z", "mc1",
        {
            "case_a": {"sglang": 10.0, "vllm-omni": 12.0},
            "case_b": {"sglang": 20.0, "vllm-omni": 22.0},
        },
    )
    history = [
        make_run(
            "2025-01-14T00:00:00Z", "mc2",
            {
                "case_a": {"sglang": 11.0, "vllm-omni": 13.0},
                "case_b": {"sglang": 21.0, "vllm-omni": 23.0},
            },
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        generate_dashboard(current, history, charts_dir=td)
        pngs = [f for f in os.listdir(td) if f.endswith(".png")]
        # At least 2 latency charts (one per case) + possibly speedup chart
        latency_pngs = [f for f in pngs if f.startswith("latency_")]
        assert len(latency_pngs) >= 2, f"expected >=2 latency charts, got {len(latency_pngs)}: {pngs}"


# [static] pass_to_pass
def test_not_stub():
    """generate_dashboard is not a stub — produces real markdown + charts."""
    from scripts.ci.utils.diffusion.generate_diffusion_dashboard import generate_dashboard

    current = make_run(
        "2025-01-15T00:00:00Z", "stub1",
        {"stub_test": {"sglang": 5.0, "vllm-omni": 7.0}},
    )
    history = [
        make_run(
            "2025-01-14T00:00:00Z", "stub2",
            {"stub_test": {"sglang": 6.0, "vllm-omni": 8.0}},
        )
    ]

    with tempfile.TemporaryDirectory() as td:
        md, axes = capture_axes(generate_dashboard, current, history, td)
        assert md and len(md) >= 100, "markdown too short"
        assert axes, "no matplotlib axes created"
        pngs = [f for f in os.listdir(td) if f.endswith(".png")]
        assert pngs, "no chart files"
