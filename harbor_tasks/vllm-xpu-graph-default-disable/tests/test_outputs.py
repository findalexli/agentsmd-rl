"""
Task: vllm-xpu-graph-default-disable
Repo: vllm-project/vllm @ a9213c0ffea4c6485dd1d03de5e8b3ff96dda924
PR:   38193

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.util
import os
import re
from pathlib import Path

REPO = "/repo"


def _discover_xpu_graph_var():
    """Find the VLLM_* env var controlling XPU graph in envs.py."""
    content = Path(f"{REPO}/vllm/envs.py").read_text()
    candidates = re.findall(r'"(VLLM_\w*XPU\w*GRAPH\w*)"', content)
    if not candidates:
        candidates = re.findall(r'"(VLLM_\w*GRAPH\w*XPU\w*)"', content)
    if not candidates:
        candidates = re.findall(r'"(VLLM_XPU_\w+)"', content)
    assert candidates, "No XPU graph env var found in envs.py"
    return candidates[0]


def _load_envs():
    """Import envs.py directly (avoids vllm/__init__.py GPU imports)."""
    spec = importlib.util.spec_from_file_location(
        "vllm_envs_test", f"{REPO}/vllm/envs.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_lambda(var_name):
    """Extract and compile the lambda for var_name from environment_variables dict."""
    source = Path(f"{REPO}/vllm/envs.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == var_name:
                    assert isinstance(value, ast.Lambda), (
                        f"{var_name} entry is not a lambda"
                    )
                    lambda_expr = ast.Expression(body=value)
                    ast.fix_missing_locations(lambda_expr)
                    code = compile(lambda_expr, "vllm/envs.py", "eval")
                    return eval(code, {"os": os, "__builtins__": __builtins__})
    assert False, f"Lambda for {var_name} not found in environment_variables dict"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    for f in ["vllm/envs.py", "vllm/platforms/xpu.py"]:
        source = Path(f"{REPO}/{f}").read_text()
        ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_env_var_lambda_defaults_disabled():
    """XPU graph env var lambda defaults to disabled when unset."""
    var = _discover_xpu_graph_var()
    fn = _extract_lambda(var)

    # Unset → must be falsy (os.getenv falls through to default "0")
    os.environ.pop(var, None)
    assert not fn(), f"Default (unset) should be falsy, got {fn()}"

    # Explicitly "0" → must be falsy
    os.environ[var] = "0"
    try:
        assert not fn(), f"'0' should be falsy, got {fn()}"
    finally:
        os.environ.pop(var, None)


# [pr_diff] fail_to_pass
def test_env_var_lambda_parses_toggle_values():
    """XPU graph env var lambda parses '1'/'2' as enabled and '0' as disabled."""
    var = _discover_xpu_graph_var()
    fn = _extract_lambda(var)

    try:
        # Truthy values
        for val in ("1", "2", "10"):
            os.environ[var] = val
            assert fn(), f"'{val}' should be truthy, got {fn()}"

        # Falsy value
        os.environ[var] = "0"
        assert not fn(), f"'0' should be falsy, got {fn()}"
    finally:
        os.environ.pop(var, None)


# [pr_diff] fail_to_pass
def test_env_var_module_access():
    """XPU graph env var accessible via vllm.envs module, defaults disabled, toggles on."""
    var = _discover_xpu_graph_var()

    # Default → falsy
    os.environ.pop(var, None)
    envs = _load_envs()
    val = getattr(envs, var, "__MISSING__")
    assert val != "__MISSING__", (
        f"{var} not found on envs module (not in environment_variables or TYPE_CHECKING)"
    )
    assert not val, f"Default should be falsy via module, got {val}"

    # Set to "1" → truthy
    os.environ[var] = "1"
    envs2 = _load_envs()
    val2 = getattr(envs2, var, "__MISSING__")
    assert val2, f"'1' should be truthy via module, got {val2}"

    os.environ.pop(var, None)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_env_vars_preserved():
    """Existing env vars and XPU platform class still present after changes."""
    envs_content = Path(f"{REPO}/vllm/envs.py").read_text()
    for var in ["VLLM_HOST_IP", "VLLM_CONFIGURE_LOGGING", "VLLM_TARGET_DEVICE"]:
        assert var in envs_content, f"Existing env var {var} missing from envs.py"
    assert "environment_variables" in envs_content, "environment_variables dict missing"

    xpu_content = Path(f"{REPO}/vllm/platforms/xpu.py").read_text()
    assert "class XPUPlatform" in xpu_content, "XPUPlatform class missing"
    assert "check_and_update_config" in xpu_content, "check_and_update_config missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — xpu.py integration
# AST required: xpu.py imports vllm_xpu_kernels (Intel C ext unavailable in CPU env)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_xpu_check_and_update_config_uses_env_var():
    """check_and_update_config conditionally disables cudagraph based on XPU env var."""
    var = _discover_xpu_graph_var()
    source = Path(f"{REPO}/vllm/platforms/xpu.py").read_text()
    tree = ast.parse(source)

    # Verify envs is imported
    has_envs_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "envs" in alias.name:
                    has_envs_import = True
        if isinstance(node, ast.ImportFrom) and node.module and "envs" in node.module:
            has_envs_import = True
    assert has_envs_import, "vllm.envs not imported in xpu.py"

    # Find method, verify env var reference and cudagraph assignment
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "check_and_update_config"
        ):
            has_env_ref = False
            has_cudagraph_assign = False
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute) and child.attr == var:
                    has_env_ref = True
                if (
                    isinstance(child, ast.Constant)
                    and isinstance(child.value, str)
                    and var in child.value
                ):
                    has_env_ref = True
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and "cudagraph" in target.attr.lower()
                        ):
                            has_cudagraph_assign = True
            assert has_env_ref, f"{var} not referenced in check_and_update_config"
            assert has_cudagraph_assign, (
                "No cudagraph_mode assignment in check_and_update_config"
            )
            return
    assert False, "check_and_update_config method not found in xpu.py"
