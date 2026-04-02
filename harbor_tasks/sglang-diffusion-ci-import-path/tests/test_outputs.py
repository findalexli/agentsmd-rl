"""
Task: sglang-diffusion-ci-import-path
Repo: sgl-project/sglang @ 35720d9969ef404566c0d5801c072bf0085255d1
PR:   #21449

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import inspect
import subprocess
import sys
from pathlib import Path

REPO = "/repo"
FILE1 = f"{REPO}/scripts/ci/utils/diffusion/publish_comparison_results.py"
FILE2 = f"{REPO}/scripts/ci/utils/diffusion/publish_diffusion_gt.py"

REQUIRED_HELPERS = [
    "create_blobs",
    "create_commit",
    "create_tree",
    "get_branch_sha",
    "get_tree_sha",
    "is_permission_error",
    "is_rate_limit_error",
    "update_branch_ref",
    "verify_token_permissions",
]


def _load_module(name, path):
    """Load a Python file as a module, tolerating SystemExit from missing env vars."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass  # Script exits early due to missing env vars — import still succeeded
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    for path in [FILE1, FILE2]:
        r = subprocess.run(
            ["python3", "-c", f"import py_compile; py_compile.compile({path!r}, doraise=True)"],
            capture_output=True, timeout=15,
        )
        assert r.returncode == 0, f"Syntax error in {path}:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_comparison_results_standalone_import():
    """publish_comparison_results.py can be imported as a standalone script
    and exposes all required helper functions from publish_traces."""
    mod = _load_module("publish_comparison_results", FILE1)
    missing = [h for h in REQUIRED_HELPERS if not hasattr(mod, h)]
    assert not missing, f"Missing attributes after import: {missing}"


# [pr_diff] fail_to_pass
def test_diffusion_gt_standalone_import():
    """publish_diffusion_gt.py can be imported as a standalone script
    and exposes all required helper functions from publish_traces."""
    mod = _load_module("publish_diffusion_gt", FILE2)
    missing = [h for h in REQUIRED_HELPERS if not hasattr(mod, h)]
    assert not missing, f"Missing attributes after import: {missing}"


# [pr_diff] fail_to_pass
def test_helpers_are_real_callables():
    """Imported helper functions from publish_comparison_results are actual
    callable functions with real implementations (not stubs)."""
    mod = _load_module("publish_comparison_results", FILE1)
    for name in REQUIRED_HELPERS:
        fn = getattr(mod, name, None)
        assert fn is not None, f"{name} is None"
        assert callable(fn), f"{name} is not callable"
        try:
            src = inspect.getsource(fn)
            body_lines = [
                l.strip() for l in src.splitlines()
                if l.strip()
                and not l.strip().startswith("#")
                and not l.strip().startswith("def ")
                and not l.strip().startswith('"""')
                and l.strip() not in ("pass", "return None")
            ]
            assert len(body_lines) >= 2, f"{name} appears to be a stub"
        except (TypeError, OSError):
            pass  # builtins or C extensions — OK


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_publish_traces_importable():
    """The upstream publish_traces.py module still imports and has all helpers."""
    sys.path.insert(0, f"{REPO}/scripts/ci/utils")
    try:
        import publish_traces
        missing = [h for h in REQUIRED_HELPERS if not hasattr(publish_traces, h)]
        assert not missing, f"publish_traces missing: {missing}"
    finally:
        sys.path.pop(0)


# [pr_diff] fail_to_pass
def test_comparison_has_publish_function():
    """publish_comparison_results still has its core publish_comparison function."""
    mod = _load_module("publish_comparison_results", FILE1)
    assert hasattr(mod, "publish_comparison"), "publish_comparison function missing"
    assert callable(mod.publish_comparison), "publish_comparison is not callable"


# [pr_diff] fail_to_pass
def test_diffusion_gt_has_core_functions():
    """publish_diffusion_gt still has its core publish and collect_images functions."""
    mod = _load_module("publish_diffusion_gt", FILE2)
    for fn_name in ["publish", "collect_images"]:
        assert hasattr(mod, fn_name), f"{fn_name} function missing"
        assert callable(getattr(mod, fn_name)), f"{fn_name} is not callable"


# [static] pass_to_pass
def test_files_not_stubbed():
    """Modified files still contain substantial logic (not gutted/replaced with stubs)."""
    for path in [FILE1, FILE2]:
        content = Path(path).read_text()
        # Must reference key helper functions
        for fn in ["create_blobs", "create_commit", "get_branch_sha"]:
            assert fn in content, f"{path} missing reference to {fn}"
        # Must have argparse (core script logic)
        assert "argparse" in content or "ArgumentParser" in content, (
            f"{path} missing argparse — file may have been gutted"
        )
        assert len(content) >= 500, f"{path} is suspiciously short ({len(content)} chars)"
