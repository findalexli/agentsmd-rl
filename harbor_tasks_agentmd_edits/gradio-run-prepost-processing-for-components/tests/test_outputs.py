"""
Task: gradio-run-prepost-processing-for-components
Repo: gradio @ 835e4bd1adcaf5716283fa379e909f916a032b8a
PR:   13168

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.util
import sys
import time
from pathlib import Path

REPO = "/workspace/gradio"


def _load_profiling():
    """Load gradio.profiling directly without going through gradio.__init__."""
    spec = importlib.util.spec_from_file_location(
        "gradio.profiling", f"{REPO}/gradio/profiling.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Python files parse without syntax errors."""
    for relpath in ["gradio/profiling.py", "gradio/blocks.py"]:
        source = Path(f"{REPO}/{relpath}").read_text()
        ast.parse(source, filename=relpath)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests: profiling.py additions
# ---------------------------------------------------------------------------

def test_trace_phase_sync_exists():
    """trace_phase_sync must be a synchronous context manager in gradio.profiling."""
    mod = _load_profiling()
    assert hasattr(mod, "trace_phase_sync"), (
        "gradio.profiling must export trace_phase_sync"
    )
    # Verify it works as a context manager
    cm = mod.trace_phase_sync("test_phase")
    assert hasattr(cm, "__enter__") and hasattr(cm, "__exit__"), (
        "trace_phase_sync must return a context manager"
    )


def test_trace_phase_sync_records_timing():
    """trace_phase_sync must record timing into the current RequestTrace."""
    mod = _load_profiling()
    trace = mod.RequestTrace()
    token = mod.set_current_trace(trace)
    try:
        with mod.trace_phase_sync("preprocess_move_to_cache"):
            time.sleep(0.01)
        assert trace.preprocess_move_to_cache_ms > 0, (
            "trace_phase_sync should record timing into the trace"
        )
    finally:
        mod._current_trace.set(None)


def test_traced_sync_decorator():
    """traced_sync decorator must wrap a function to record timing."""
    mod = _load_profiling()

    # traced_sync should be callable
    assert callable(getattr(mod, "traced_sync", None)), (
        "gradio.profiling must export traced_sync"
    )

    # When PROFILING_ENABLED is False, it should be a passthrough
    # When True, it wraps with timing. Either way, the function should still work.
    @mod.traced_sync("test_phase")
    def sample_func(x):
        return x * 2

    result = sample_func(21)
    assert result == 42, "traced_sync-decorated function must return correct value"


def test_traced_async_decorator():
    """traced (async) decorator must wrap an async function to record timing."""
    import asyncio

    mod = _load_profiling()
    assert callable(getattr(mod, "traced", None)), (
        "gradio.profiling must export traced"
    )

    @mod.traced("test_async_phase")
    async def sample_async(x):
        return x + 1

    result = asyncio.get_event_loop().run_until_complete(sample_async(41))
    assert result == 42, "traced-decorated async function must return correct value"


def test_request_trace_granular_fields():
    """RequestTrace must have granular profiling fields for sub-phase timing."""
    mod = _load_profiling()
    trace = mod.RequestTrace()

    required_fields = [
        "upload_ms",
        "preprocess_move_to_cache_ms",
        "preprocess_format_image_ms",
        "postprocess_save_pil_to_cache_ms",
        "postprocess_save_bytes_to_cache_ms",
        "postprocess_move_to_cache_ms",
        "postprocess_update_state_in_config_ms",
        "save_file_to_cache_ms",
    ]

    for field_name in required_fields:
        assert hasattr(trace, field_name), (
            f"RequestTrace must have field '{field_name}'"
        )
        assert getattr(trace, field_name) == 0.0, (
            f"RequestTrace.{field_name} should default to 0.0"
        )


def test_request_trace_to_dict_includes_granular_fields():
    """RequestTrace.to_dict() must include the granular profiling fields."""
    mod = _load_profiling()
    trace = mod.RequestTrace()
    d = trace.to_dict()

    required_keys = [
        "preprocess_move_to_cache_ms",
        "postprocess_save_pil_to_cache_ms",
        "postprocess_move_to_cache_ms",
        "postprocess_update_state_in_config_ms",
        "save_file_to_cache_ms",
    ]

    for key in required_keys:
        assert key in d, f"to_dict() must include '{key}'"
        assert d[key] == 0.0, f"to_dict()['{key}'] should default to 0.0"


def test_preprocess_offloaded_to_thread():
    """blocks.py preprocess_data must offload block.preprocess to a thread via anyio."""
    source = Path(f"{REPO}/gradio/blocks.py").read_text()
    tree = ast.parse(source)

    # Find the preprocess_data method
    found_method = False
    uses_thread = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "preprocess_data":
            found_method = True
            # Check that anyio.to_thread.run_sync is called within this method
            method_source = ast.get_source_segment(source, node)
            if method_source and "anyio.to_thread.run_sync" in method_source:
                uses_thread = True
            break

    assert found_method, "blocks.py must have async preprocess_data method"
    assert uses_thread, (
        "preprocess_data must offload block.preprocess to a thread "
        "using anyio.to_thread.run_sync"
    )


def test_postprocess_offloaded_to_thread():
    """blocks.py postprocess_data must offload block.postprocess to a thread via anyio."""
    source = Path(f"{REPO}/gradio/blocks.py").read_text()
    tree = ast.parse(source)

    found_method = False
    uses_thread = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "postprocess_data":
            found_method = True
            method_source = ast.get_source_segment(source, node)
            if method_source and "anyio.to_thread.run_sync" in method_source:
                uses_thread = True
            break

    assert found_method, "blocks.py must have async postprocess_data method"
    assert uses_thread, (
        "postprocess_data must offload block.postprocess to a thread "
        "using anyio.to_thread.run_sync"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) -- benchmark README documentation update
# ---------------------------------------------------------------------------


    # Must have a results directory structure section
    assert "results directory structure" in content.lower(), (
        "README should have a 'Results Directory Structure' section"
    )

    # Must document the key output files
    assert "summary.json" in content, (
        "README should document summary.json output file"
    )
    assert "client_latencies.jsonl" in content, (
        "README should document client_latencies.jsonl output file"
    )
    assert "traces.jsonl" in content, (
        "README should document traces.jsonl output file"
    )



    # Must mention tier directories
    assert "tier_" in content, (
        "README should document tier_{N} directory structure"
    )
    # Must show the per-app directory structure
    assert "app_stem" in content or "app stem" in content.lower(), (
        "README should document per-app directory organization"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- regression check for existing functionality
# ---------------------------------------------------------------------------

def test_trace_phase_async_still_works():
    """Existing async trace_phase must still function correctly (regression)."""
    import asyncio

    mod = _load_profiling()
    trace = mod.RequestTrace()
    token = mod.set_current_trace(trace)
    try:
        async def run():
            async with mod.trace_phase("preprocess"):
                await asyncio.sleep(0.01)

        asyncio.get_event_loop().run_until_complete(run())
        assert trace.preprocess_ms > 0, (
            "Existing async trace_phase must still record timing"
        )
    finally:
        mod._current_trace.set(None)
