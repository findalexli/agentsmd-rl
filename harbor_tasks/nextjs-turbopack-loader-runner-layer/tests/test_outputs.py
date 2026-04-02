"""
Task: nextjs-turbopack-loader-runner-layer
Repo: vercel/next.js @ b6ff1f6079694da08af88cec5cac7381e22cea10
PR:   91727

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a Rust codebase (turbopack). The container has no Rust
toolchain, so we cannot compile or run the code. All checks are
text-based analysis of the source files — this is the only viable
approach for Rust fixes in a Python-slim container.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
TARGET = Path(REPO) / "turbopack/crates/turbopack/src/lib.rs"
MOD_FILE = Path(REPO) / "turbopack/crates/turbopack/src/module_options/mod.rs"


def _strip_rust_comments(src: str) -> str:
    """Remove Rust line comments and block comments."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _extract_function(src: str, fn_name: str, window: int = 8000) -> str:
    """Extract a window of text starting at a Rust function definition."""
    idx = src.find(f"fn {fn_name}")
    assert idx != -1, f"Function {fn_name} not found"
    return src[idx : idx + window]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_layer_name_fixed():
    """process_default_internal must use Layer::new with "webpack_loaders"."""
    src = TARGET.read_text()
    fn_body = _extract_function(src, "process_default_internal")
    fn_clean = _strip_rust_comments(fn_body)

    # Must contain the correct layer name as a string literal
    assert '"webpack_loaders"' in fn_clean, (
        'process_default_internal does not contain "webpack_loaders" literal'
    )

    # Layer::new call must be near the string literal
    layer_pos = fn_clean.find("Layer::new")
    assert layer_pos != -1, "No Layer::new call in process_default_internal"
    window = fn_clean[layer_pos : layer_pos + 300]
    assert '"webpack_loaders"' in window, (
        '"webpack_loaders" is not near a Layer::new call'
    )

    # Must also be near node_evaluate_asset_context (correct placement)
    ctx_pos = fn_clean.find("node_evaluate_asset_context")
    assert ctx_pos != -1, "node_evaluate_asset_context not found"
    ctx_window = fn_clean[ctx_pos : ctx_pos + 500]
    assert '"webpack_loaders"' in ctx_window, (
        '"webpack_loaders" is not near node_evaluate_asset_context'
    )


# [pr_diff] fail_to_pass
def test_buggy_name_removed():
    """The old buggy layer name "turbopack_use_loaders" must not appear in lib.rs."""
    src = TARGET.read_text()
    assert '"turbopack_use_loaders"' not in src, (
        'Buggy string literal "turbopack_use_loaders" still present in lib.rs'
    )


# [pr_diff] fail_to_pass
def test_cross_file_consistency():
    """Both lib.rs and module_options/mod.rs must use the same "webpack_loaders" layer name."""
    lib_clean = _strip_rust_comments(TARGET.read_text())
    mod_clean = _strip_rust_comments(MOD_FILE.read_text())

    assert '"webpack_loaders"' in lib_clean, (
        'lib.rs missing "webpack_loaders" string literal'
    )
    assert '"webpack_loaders"' in mod_clean, (
        'module_options/mod.rs missing "webpack_loaders" string literal'
    )

    # Neither file should have the buggy name
    for name, src in [("lib.rs", lib_clean), ("mod.rs", mod_clean)]:
        assert '"turbopack_use_loaders"' not in src, (
            f'Buggy "turbopack_use_loaders" still in {name}'
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """lib.rs must be substantial — not gutted or replaced with a stub."""
    src = TARGET.read_text()
    lines = src.strip().splitlines()
    assert len(lines) >= 800, (
        f"File has only {len(lines)} lines, expected 800+ (original is ~1000)"
    )


# [pr_diff] pass_to_pass
def test_loader_pipeline_preserved():
    """Key loader pipeline constructs must still exist in lib.rs."""
    src = TARGET.read_text()
    required = [
        "node_evaluate_asset_context",
        "WebpackLoaderItem",
        "WebpackLoaders",
        "loader_runner_package",
        "SourceTransforms",
    ]
    missing = [r for r in required if r not in src]
    assert not missing, f"Missing loader pipeline constructs: {missing}"


# [pr_diff] pass_to_pass
def test_other_layers_untouched():
    """Other Layer::new calls (e.g. externals-tracing) must not be removed."""
    src = TARGET.read_text()
    assert "externals-tracing" in src, (
        "externals-tracing layer missing — collateral damage from fix"
    )


# [pr_diff] pass_to_pass
def test_layer_new_call_syntax():
    """Layer::new call must use rcstr! macro with the layer name string."""
    src = TARGET.read_text()
    fn_body = _extract_function(src, "process_default_internal")
    # The Layer::new call must use rcstr! macro (Rust interned string)
    assert "Layer::new(rcstr!" in fn_body, (
        "Layer::new must use rcstr! macro for the layer name"
    )
