"""
Task: gradio-profiling-sync-trace-benchmark-docs
Repo: gradio @ 835e4bd1adcaf5716283fa379e909f916a032b8a
PR:   13168

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"


def _load_profiling_and_run(test_code: str, profiling_enabled: bool = True) -> subprocess.CompletedProcess:
    """Run a test script that imports gradio.profiling directly via importlib."""
    env_line = 'os.environ["GRADIO_PROFILING"] = "1"' if profiling_enabled else ""
    script = f"""
import os
{env_line}
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("profiling", "{REPO}/gradio/profiling.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

{test_code}

print("OK")
"""
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=30,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files parse without errors."""
    import ast
    for relpath in ["gradio/profiling.py", "scripts/benchmark/README.md"]:
        fpath = Path(REPO) / relpath
        assert fpath.exists(), f"{relpath} not found"
    src = (Path(REPO) / "gradio" / "profiling.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_trace_phase_sync_records_timing():
    """trace_phase_sync context manager must record timing into the current RequestTrace."""
    r = _load_profiling_and_run("""
import time

trace = mod.RequestTrace(event_id="t1", fn_name="test_fn")
token = mod._current_trace.set(trace)
try:
    with mod.trace_phase_sync("preprocess"):
        time.sleep(0.02)
    assert trace.preprocess_ms >= 15, f"Expected >=15ms, got {trace.preprocess_ms}"
    assert trace.preprocess_ms < 5000, f"Unexpectedly high: {trace.preprocess_ms}"
finally:
    mod._current_trace.reset(token)
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_traced_sync_decorator_records_timing():
    """traced_sync decorator must wrap a function and record phase timing."""
    r = _load_profiling_and_run("""
import time

@mod.traced_sync("postprocess")
def slow_fn(x):
    time.sleep(0.02)
    return x * 2

trace = mod.RequestTrace(event_id="t2", fn_name="dec_test")
token = mod._current_trace.set(trace)
try:
    result = slow_fn(21)
    assert result == 42, f"Expected 42, got {result}"
    assert trace.postprocess_ms >= 15, f"Expected >=15ms, got {trace.postprocess_ms}"
finally:
    mod._current_trace.reset(token)
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_request_trace_has_new_phase_fields():
    """RequestTrace must have upload_ms and component-specific phase fields."""
    r = _load_profiling_and_run("""
trace = mod.RequestTrace()
new_fields = [
    "upload_ms",
    "preprocess_move_to_cache_ms",
    "preprocess_format_image_ms",
    "postprocess_save_audio_to_cache_ms",
    "preprocess_video_ms",
    "postprocess_video_ms",
    "postprocess_save_pil_to_cache_ms",
    "postprocess_save_bytes_to_cache_ms",
    "save_file_to_cache_ms",
]
for field_name in new_fields:
    assert hasattr(trace, field_name), f"RequestTrace missing field: {field_name}"
    assert getattr(trace, field_name) == 0.0, f"{field_name} should default to 0.0"
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_to_dict_includes_new_phase_keys():
    """RequestTrace.to_dict() must include the new component-level phase keys."""
    r = _load_profiling_and_run("""
import json

trace = mod.RequestTrace(event_id="t3", fn_name="dict_test")
d = trace.to_dict()
required_keys = [
    "preprocess_move_to_cache_ms",
    "postprocess_save_img_array_to_cache_ms",
    "preprocess_audio_from_file_ms",
    "postprocess_video_convert_video_to_playable_mp4_ms",
    "postprocess_update_state_in_config_ms",
    "postprocess_move_to_cache_ms",
    "save_file_to_cache_ms",
]
for key in required_keys:
    assert key in d, f"to_dict() missing key: {key}"
    assert d[key] == 0.0, f"{key} should be 0.0 in fresh trace, got {d[key]}"

# Verify original keys still present
assert "queue_wait_ms" in d
assert "fn_call_ms" in d
assert "total_ms" in d
print(json.dumps(d))
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "OK" in r.stdout
    # Verify the JSON output is parseable and has the right keys
    lines = r.stdout.strip().split("\n")
    data = json.loads(lines[0])
    assert "postprocess_video_convert_video_to_playable_mp4_ms" in data


# [pr_diff] fail_to_pass
def test_trace_phase_sync_no_trace_noop():
    """trace_phase_sync must be a no-op when no current trace is set (no crash)."""
    r = _load_profiling_and_run("""
# No trace set — should not raise
with mod.trace_phase_sync("preprocess"):
    x = 1 + 1
assert x == 2
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_benchmark_readme_documents_results_directory_structure():
    """scripts/benchmark/README.md must document the results directory structure with tier details."""
    readme = Path(REPO) / "scripts" / "benchmark" / "README.md"
    content = readme.read_text()
    assert "Results Directory Structure" in content, \
        "README should have a 'Results Directory Structure' section"
    assert "tier_1" in content and "tier_10" in content and "tier_100" in content, \
        "README should document tier_1, tier_10, tier_100 subdirectories"
    assert "client_latencies.jsonl" in content, \
        "README should mention client_latencies.jsonl output file"
    assert "traces.jsonl" in content, \
        "README should mention traces.jsonl output file"


# [pr_diff] fail_to_pass
def test_benchmark_readme_documents_ab_test_structure():
    """scripts/benchmark/README.md must explain A/B test directory layout."""
    readme = Path(REPO) / "scripts" / "benchmark" / "README.md"
    content = readme.read_text()
    assert "{compare_branch}" in content or "compare_branch" in content, \
        "README should document the compare_branch directory in A/B tests"
    assert "{app_stem}" in content or "app_stem" in content, \
        "README should document the per-app directory structure"
    assert "tier_{N}" in content or "tier_{n}" in content.lower(), \
        "README should explain the tier_{N} directory naming convention"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_trace_phase_async_still_exists():
    """Existing async trace_phase function must still work."""
    r = _load_profiling_and_run("""
import asyncio
import time

async def run():
    trace = mod.RequestTrace(event_id="t4", fn_name="async_test")
    token = mod._current_trace.set(trace)
    try:
        async with mod.trace_phase("fn_call"):
            await asyncio.sleep(0.01)
        assert trace.fn_call_ms > 0, f"Expected >0, got {trace.fn_call_ms}"
    finally:
        mod._current_trace.reset(token)

asyncio.run(run())
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "OK" in r.stdout


# [static] pass_to_pass
def test_set_phase_accumulates():
    """RequestTrace.set_phase must accumulate values across multiple calls."""
    r = _load_profiling_and_run("""
trace = mod.RequestTrace()
trace.set_phase("preprocess", 10.0)
trace.set_phase("preprocess", 5.0)
assert trace.preprocess_ms == 15.0, f"Expected 15.0, got {trace.preprocess_ms}"
""", profiling_enabled=False)
    assert r.returncode == 0, f"Script failed:\n{r.stderr}"
    assert "OK" in r.stdout
