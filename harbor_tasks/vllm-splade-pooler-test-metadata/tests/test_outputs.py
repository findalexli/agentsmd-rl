"""
Task: vllm-splade-pooler-test-metadata
Repo: vllm-project/vllm @ 85c0950b1f647e0b0654fbf3e91a9757b8233752
PR:   38495

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.util
import subprocess
from pathlib import Path

REPO = "/testbed"
TEST_FILE = f"{REPO}/tests/models/language/pooling/test_splade_sparse_pooler.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Test file must be valid Python."""
    src = Path(TEST_FILE).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pytest_splade_pooler():
    """SPLADE pooler unit test must pass pytest (was broken by AttributeError on metadata mock)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", TEST_FILE, "-x", "--timeout=60", "-q"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    stdout = r.stdout.decode()
    assert r.returncode == 0, (
        f"pytest failed:\n{stdout[-1000:]}\n{r.stderr.decode()[-500:]}"
    )
    # Verify tests actually ran (not vacuously 0 collected)
    assert "passed" in stdout, f"No tests passed:\n{stdout[-500:]}"


# [pr_diff] fail_to_pass
def test_forward_varied_inputs():
    """Pooler forward() produces correct [B,V] SPLADE output for diverse parameter combos."""
    import sys
    sys.path.insert(0, REPO)

    spec = importlib.util.spec_from_file_location(
        "test_splade_sparse_pooler", TEST_FILE
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fn = getattr(mod, "test_splade_pooler_matches_reference_formula", None)
    assert fn is not None, "test_splade_pooler_matches_reference_formula not found"

    # Use param combos DIFFERENT from @pytest.mark.parametrize to catch hardcoding
    for B, T, H, V in [(1, 2, 4, 8), (4, 6, 16, 32), (2, 10, 64, 100)]:
        fn(B=B, T=T, H=H, V=V)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_parametrize_preserved():
    """Test function must retain @pytest.mark.parametrize for varied B,T,H,V inputs."""
    src = Path(TEST_FILE).read_text()
    tree = ast.parse(src)
    funcs = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef)
        and n.name == "test_splade_pooler_matches_reference_formula"
    ]
    assert len(funcs) == 1, "Test function missing or duplicated"
    has_parametrize = any(
        isinstance(d, ast.Call)
        and isinstance(getattr(d, "func", None), ast.Attribute)
        and d.func.attr == "parametrize"
        for d in funcs[0].decorator_list
    )
    assert has_parametrize, "Must retain @pytest.mark.parametrize decorator"
