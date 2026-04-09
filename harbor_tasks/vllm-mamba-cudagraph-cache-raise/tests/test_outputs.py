"""
Task: vllm-mamba-cudagraph-cache-raise
Repo: vllm-project/vllm @ 03ac6ca8954d491dc39ae169c2623e8ccffba7c6
PR:   #38270

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"
RUNNER = f"{REPO}/vllm/v1/worker/gpu_model_runner.py"
CONFIG = f"{REPO}/vllm/config/compilation.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files (gpu_model_runner.py, compilation.py) must parse without errors."""
    for path in [RUNNER, CONFIG]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_silent_capping_method_removed():
    """adjust_cudagraph_sizes_for_mamba_cache must be removed from CompilationConfig."""
    r = _run_py("""
import ast
source = open("vllm/config/compilation.py").read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CompilationConfig":
        method_names = [
            item.name
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "adjust_cudagraph_sizes_for_mamba_cache" not in method_names, (
            "CompilationConfig still has adjust_cudagraph_sizes_for_mamba_cache "
            "- silent capping not eliminated"
        )
        print("PASS")
        break
else:
    raise AssertionError("CompilationConfig class not found")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_raises_on_insufficient_mamba_blocks():
    """_check_and_update_cudagraph_mode must raise ValueError when max_num_seqs > num_blocks."""
    r = _run_py("""
import ast
source = open("vllm/v1/worker/gpu_model_runner.py").read()
tree = ast.parse(source)

target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_check_and_update_cudagraph_mode":
        target = node
        break
assert target is not None, "_check_and_update_cudagraph_mode not found"

func_lines = source.splitlines()
func_text = "\\n".join(func_lines[target.lineno - 1 : target.end_lineno])

# Must NOT call the silent capping method
assert "adjust_cudagraph_sizes_for_mamba_cache" not in func_text, (
    "Still calls adjust_cudagraph_sizes_for_mamba_cache (silent capping)"
)

# Find the if-block that compares max_num_reqs > num_blocks
# and verify its body contains a Raise with ValueError
found_conditional_raise = False
for child in ast.walk(target):
    if isinstance(child, ast.If):
        test_src = "\\n".join(func_lines[child.lineno - 1 : child.end_lineno])
        if "max_num_reqs" in test_src and "num_blocks" in test_src:
            for body_node in child.body:
                if isinstance(body_node, ast.Raise) and body_node.exc is not None:
                    raise_src = "\\n".join(
                        func_lines[body_node.lineno - 1 : body_node.end_lineno]
                    )
                    assert "ValueError" in raise_src, (
                        f"Raise exists but not ValueError: {raise_src}"
                    )
                    assert "max_num_seqs" in raise_src, (
                        "Error message doesn't reference max_num_seqs"
                    )
                    assert "block" in raise_src.lower(), (
                        "Error message doesn't reference cache blocks"
                    )
                    found_conditional_raise = True
                    break

assert found_conditional_raise, (
    "No conditional raise found comparing max_num_reqs > num_blocks"
)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_profiling_skips_mamba_validation():
    """_init_minimal_kv_cache_for_profiling must signal profiling to skip validation."""
    r = _run_py("""
import ast
source = open("vllm/v1/worker/gpu_model_runner.py").read()
tree = ast.parse(source)

target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_init_minimal_kv_cache_for_profiling":
        target = node
        break
assert target is not None, "_init_minimal_kv_cache_for_profiling not found"

# Find the call to initialize_kv_cache and verify profiling signal
for child in ast.walk(target):
    if isinstance(child, ast.Call):
        func = child.func
        if isinstance(func, ast.Attribute) and func.attr == "initialize_kv_cache":
            # Buggy: exactly 1 positional arg, no keywords
            # Fixed: extra arg or keyword signaling profiling
            has_extra = len(child.args) > 1 or len(child.keywords) > 0
            assert has_extra, (
                "initialize_kv_cache called without profiling signal"
            )
            # Verify a profiling keyword is present
            kw_names = [kw.arg for kw in child.keywords if kw.arg]
            has_profiling_kw = any("profil" in k.lower() for k in kw_names)
            assert has_profiling_kw or len(child.args) > 1, (
                "No profiling keyword argument found"
            )
            print("PASS")
            break
else:
    raise AssertionError(
        "No call to initialize_kv_cache found in _init_minimal_kv_cache_for_profiling"
    )
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_silent_cap_reference_in_runner():
    """gpu_model_runner.py must not reference adjust_cudagraph_sizes_for_mamba_cache."""
    r = _run_py("""
content = open("vllm/v1/worker/gpu_model_runner.py").read()
assert "adjust_cudagraph_sizes_for_mamba_cache" not in content, (
    "Runner still references adjust_cudagraph_sizes_for_mamba_cache"
)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_is_profiling_param_threaded():
    """is_profiling parameter accepted by initialize_kv_cache, initialize_attn_backend,
    and _check_and_update_cudagraph_mode."""
    r = _run_py("""
import ast
source = open("vllm/v1/worker/gpu_model_runner.py").read()
tree = ast.parse(source)

target_methods = {
    "initialize_kv_cache",
    "initialize_attn_backend",
    "_check_and_update_cudagraph_mode",
}
found = {}

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name in target_methods:
            all_params = (
                [a.arg for a in node.args.args]
                + [a.arg for a in node.args.kwonlyargs]
            )
            found[node.name] = any("profil" in p for p in all_params)

missing = target_methods - set(found.keys())
assert not missing, f"Methods not found: {missing}"

no_profiling = [m for m, has in found.items() if not has]
assert not no_profiling, f"Methods missing profiling parameter: {no_profiling}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_kv_cache_forwards_profiling_to_attn_backend():
    """initialize_kv_cache must forward profiling signal to initialize_attn_backend."""
    r = _run_py("""
import ast
source = open("vllm/v1/worker/gpu_model_runner.py").read()
tree = ast.parse(source)

target = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_kv_cache":
        target = node
        break
assert target is not None, "initialize_kv_cache not found"

for child in ast.walk(target):
    if isinstance(child, ast.Call):
        func = child.func
        if isinstance(func, ast.Attribute) and func.attr == "initialize_attn_backend":
            has_extra = len(child.args) > 1 or len(child.keywords) > 0
            assert has_extra, (
                "initialize_attn_backend called without profiling signal "
                "in initialize_kv_cache"
            )
            kw_names = [kw.arg for kw in child.keywords if kw.arg]
            has_profiling = any("profil" in k.lower() for k in kw_names)
            assert has_profiling or len(child.args) > 1, (
                "No profiling keyword forwarded to initialize_attn_backend"
            )
            print("PASS")
            break
else:
    raise AssertionError(
        "No call to initialize_attn_backend found in initialize_kv_cache"
    )
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Modified files must pass ruff linting per pyproject.toml config (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Full lint rules from pyproject.toml tool.ruff.lint
    # select: E, F, UP, B, ISC, SIM, I, G
    # ignore: F405, F403, E731, B905, B007, UP032
    r = subprocess.run(
        [
            "ruff", "check", RUNNER, CONFIG,
            "--select=E,F,UP,B,ISC,SIM,I,G",
            "--ignore=F405,F403,E731,B905,B007,UP032",
            "--output-format=concise",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Modified files must be formatted (ruff format check) (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", RUNNER, CONFIG],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_spdx_headers():
    """Modified files must have SPDX license headers (pass_to_pass)."""
    r = subprocess.run(
        ["python", "tools/pre_commit/check_spdx_header.py", RUNNER, CONFIG],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"SPDX header check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_typos():
    """Modified files must have no typos (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "typos", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["typos", RUNNER, CONFIG],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_no_regressions_compilation_config():
    """CompilationConfig class structure preserved (pass_to_pass)."""
    source = Path(CONFIG).read_text()
    tree = ast.parse(source)

    found_class = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CompilationConfig":
            found_class = True
            # Count methods
            methods = [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            assert len(methods) >= 5, f"CompilationConfig has only {len(methods)} methods, expected >= 5"
            break
    assert found_class, "CompilationConfig class not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_spec_decode_adjustment_preserved():
    """adjust_cudagraph_sizes_for_spec_decode must still exist in CompilationConfig."""
    source = Path(CONFIG).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CompilationConfig":
            method_names = [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            assert "adjust_cudagraph_sizes_for_spec_decode" in method_names, (
                "adjust_cudagraph_sizes_for_spec_decode was removed"
            )
            return
    raise AssertionError("CompilationConfig not found")


# [static] pass_to_pass
def test_core_methods_preserved():
    """Key methods preserved in gpu_model_runner.py."""
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)

    required = {
        "_check_and_update_cudagraph_mode",
        "initialize_kv_cache",
        "initialize_attn_backend",
        "_init_minimal_kv_cache_for_profiling",
    }
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in required:
                found.add(node.name)

    missing = required - found
    assert not missing, f"Missing methods: {missing}"


# [static] pass_to_pass
def test_check_cudagraph_mode_not_stub():
    """_check_and_update_cudagraph_mode has real logic, not a stub."""
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_check_and_update_cudagraph_mode":
            meaningful = sum(
                1
                for child in ast.walk(node)
                if isinstance(
                    child,
                    (ast.Assign, ast.AugAssign, ast.AnnAssign,
                     ast.If, ast.For, ast.While, ast.Return,
                     ast.Raise, ast.Expr),
                )
            )
            assert meaningful >= 10, (
                f"_check_and_update_cudagraph_mode appears stubbed "
                f"({meaningful} statements, expected >=10)"
            )
            return
    raise AssertionError("_check_and_update_cudagraph_mode not found")
