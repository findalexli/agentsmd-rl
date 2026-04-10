"""
Task: vllm-xpu-graph-default-disable
Repo: vllm-project/vllm @ a9213c0ffea4c6485dd1d03de5e8b3ff96dda924
PR:   38193

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/repo"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo."""
    script = Path("/tmp/_eval_harness.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) — CI commands that should pass at base commit
# ---------------------------------------------------------------------------

def test_repo_ruff_check_envs():
    """Repo's ruff linter passes on envs.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/vllm/envs.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed on envs.py:\n{r.stderr[-500:]}"


def test_repo_ruff_check_xpu():
    """Repo's ruff linter passes on xpu.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/vllm/platforms/xpu.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed on xpu.py:\n{r.stderr[-500:]}"


def test_repo_py_compile_envs():
    """Python syntax check passes on envs.py (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/vllm/envs.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax error in envs.py:\n{r.stderr[-500:]}"


def test_repo_py_compile_xpu():
    """Python syntax check passes on xpu.py (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/vllm/platforms/xpu.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax error in xpu.py:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# pass_to_pass (static) — file content checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    for f in ["vllm/envs.py", "vllm/platforms/xpu.py"]:
        source = Path(f"{REPO}/{f}").read_text()
        ast.parse(source)


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
# fail_to_pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_env_var_lambda_defaults_disabled():
    """XPU graph env var lambda defaults to disabled when unset."""
    r = _run_py("""\
import ast, os
from pathlib import Path

source = Path('/repo/vllm/envs.py').read_text()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and isinstance(key.value, str)
                    and 'XPU' in key.value and 'GRAPH' in key.value):
                expr = ast.Expression(body=value)
                ast.fix_missing_locations(expr)
                code = compile(expr, 'envs.py', 'eval')
                fn = eval(code, {'os': os, '__builtins__': __builtins__})

                os.environ.pop(key.value, None)
                result = fn()
                assert not result, f'Default should be falsy, got {result}'

                os.environ[key.value] = '0'
                result = fn()
                assert not result, f'"0" should be falsy, got {result}'

                os.environ.pop(key.value, None)
                print('PASS')
                raise SystemExit(0)

assert False, 'No XPU GRAPH env var lambda found in environment_variables dict'
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_env_var_lambda_parses_toggle_values():
    """XPU graph env var lambda parses '1'/'2' as enabled and '0' as disabled."""
    r = _run_py("""\
import ast, os
from pathlib import Path

source = Path('/repo/vllm/envs.py').read_text()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and isinstance(key.value, str)
                    and 'XPU' in key.value and 'GRAPH' in key.value):
                expr = ast.Expression(body=value)
                ast.fix_missing_locations(expr)
                code = compile(expr, 'envs.py', 'eval')
                fn = eval(code, {'os': os, '__builtins__': __builtins__})

                for val in ('1', '2', '10'):
                    os.environ[key.value] = val
                    result = fn()
                    assert result, f"'{val}' should be truthy, got {result}"

                os.environ[key.value] = '0'
                result = fn()
                assert not result, f"'0' should be falsy, got {result}"

                os.environ.pop(key.value, None)
                print('PASS')
                raise SystemExit(0)

assert False, 'No XPU GRAPH env var lambda found in environment_variables dict'
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_env_var_module_access():
    """XPU graph env var accessible via vllm.envs module, defaults disabled, toggles on."""
    r = _run_py("""\
import importlib.util, os

# Clear any XPU graph env vars
for key in list(os.environ):
    if 'XPU' in key and 'GRAPH' in key:
        del os.environ[key]

# Load envs module directly (avoid vllm/__init__.py GPU imports)
spec = importlib.util.spec_from_file_location('vllm_envs', '/repo/vllm/envs.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Discover XPU graph var from module attributes
var = None
for name in dir(mod):
    if name.startswith('VLLM') and 'XPU' in name and 'GRAPH' in name:
        var = name
        break
assert var is not None, 'No VLLM_*XPU*GRAPH* attribute found on envs module'

val = getattr(mod, var)
assert not val, f'{var} default should be falsy, got {val}'

# Test toggling on
os.environ[var] = '1'
spec2 = importlib.util.spec_from_file_location('vllm_envs2', '/repo/vllm/envs.py')
mod2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(mod2)
val2 = getattr(mod2, var)
assert val2, f'{var} should be truthy when set to "1", got {val2}'

os.environ.pop(var, None)
print('PASS')
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — xpu.py integration (AST-based)
# xpu.py imports vllm_xpu_kernels (Intel C extension unavailable in CPU env)
# ---------------------------------------------------------------------------

def test_xpu_check_and_update_config_uses_env_var():
    """check_and_update_config conditionally disables cudagraph based on XPU env var."""
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

    # Find check_and_update_config, verify env var reference and cudagraph assignment
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "check_and_update_config"
        ):
            has_env_ref = False
            has_cudagraph_assign = False
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute) and isinstance(child.attr, str):
                    if "XPU" in child.attr and "GRAPH" in child.attr:
                        has_env_ref = True
                if isinstance(child, ast.Constant) and isinstance(child.value, str):
                    if "XPU" in child.value and "GRAPH" in child.value:
                        has_env_ref = True
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and "cudagraph" in target.attr.lower()
                        ):
                            has_cudagraph_assign = True
            assert has_env_ref, "XPU graph env var not referenced in check_and_update_config"
            assert has_cudagraph_assign, (
                "No cudagraph_mode assignment in check_and_update_config"
            )
            return
    assert False, "check_and_update_config method not found in xpu.py"
