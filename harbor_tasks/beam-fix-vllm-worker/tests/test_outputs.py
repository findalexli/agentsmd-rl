#!/usr/bin/env python3
"""
Task: beam-fix-vllm-worker
Repo: apache/beam @ c8e45e79c699ef6df8847824833aeefab3b5767a
PR:   38008

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
from pathlib import Path

REPO = "/workspace/beam"
VLLM_COMPLETION = f"{REPO}/sdks/python/apache_beam/examples/inference/vllm_text_completion.py"
VLLM_INFERENCE = f"{REPO}/sdks/python/apache_beam/ml/inference/vllm_inference.py"
README = f"{REPO}/sdks/python/apache_beam/examples/inference/README.md"

# Mock preamble: stubs out apache_beam so we can import vllm_text_completion.py
# without installing the full Beam framework or vLLM/OpenAI deps.
_MOCK_PREAMBLE = """\
import sys
from unittest.mock import MagicMock

for _m in [
    'apache_beam', 'apache_beam.ml', 'apache_beam.ml.inference',
    'apache_beam.ml.inference.base', 'apache_beam.ml.inference.vllm_inference',
    'apache_beam.options', 'apache_beam.options.pipeline_options',
    'apache_beam.runners', 'apache_beam.runners.runner',
]:
    sys.modules[_m] = MagicMock()

# beam.DoFn must be a real class so PostProcessor(beam.DoFn) works
class _DoFn: pass
sys.modules['apache_beam'].DoFn = _DoFn

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "vllm_text_completion",
    "/workspace/beam/sdks/python/apache_beam/examples/inference/vllm_text_completion.py"
)
vtc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vtc)
"""


def _run(script: str, timeout: int = 30) -> str:
    """Run a Python script (with mock preamble) in a subprocess."""
    full = _MOCK_PREAMBLE + "\n" + script
    r = subprocess.run(
        ["python3", "-c", full],
        capture_output=True, timeout=timeout,
    )
    assert r.returncode == 0, (
        f"Script failed (rc={r.returncode}):\n"
        f"STDOUT: {r.stdout.decode()}\nSTDERR: {r.stderr.decode()}"
    )
    return r.stdout.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [VLLM_COMPLETION, VLLM_INFERENCE]:
        src = Path(path).read_text()
        ast.parse(src)


# [repo_tests] pass_to_pass - Repo syntax validation via subprocess
def test_repo_ast_parsing_vllm_completion():
    """vllm_text_completion.py parses as valid Python AST (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-c",
            f"import ast; ast.parse(open('{VLLM_COMPLETION}').read())"
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parsing failed for vllm_text_completion.py:\n{r.stderr}"


# [repo_tests] pass_to_pass - Repo syntax validation via subprocess
def test_repo_ast_parsing_vllm_inference():
    """vllm_inference.py parses as valid Python AST (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-c",
            f"import ast; ast.parse(open('{VLLM_INFERENCE}').read())"
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parsing failed for vllm_inference.py:\n{r.stderr}"


# [repo_tests] pass_to_pass - Git repo validation
def test_repo_git_commit():
    """Repo is at the expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git rev-parse failed:\n{r.stderr}"
    commit = r.stdout.strip()
    assert commit == "c8e45e79c699ef6df8847824833aeefab3b5767a", \
        f"Expected base commit c8e45e79c699ef6df8847824833aeefab3b5767a, got {commit}"


# [repo_tests] pass_to_pass - py_compile validation
def test_repo_py_compile_vllm_completion():
    """vllm_text_completion.py compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", VLLM_COMPLETION],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed for vllm_text_completion.py:\n{r.stderr}"


# [repo_tests] pass_to_pass - py_compile validation
def test_repo_py_compile_vllm_inference():
    """vllm_inference.py compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", VLLM_INFERENCE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed for vllm_inference.py:\n{r.stderr}"


# [repo_tests] pass_to_pass - flake8 syntax validation
def test_repo_flake8_syntax_vllm_completion():
    """vllm_text_completion.py has no syntax errors (flake8 E9) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install flake8 failed: {r.stderr}"
    r = subprocess.run(
        ["flake8", "--select=E9", VLLM_COMPLETION],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"flake8 syntax check failed: {r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - flake8 syntax validation
def test_repo_flake8_syntax_vllm_inference():
    """vllm_inference.py has no syntax errors (flake8 E9) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install flake8 failed: {r.stderr}"
    r = subprocess.run(
        ["flake8", "--select=E9", VLLM_INFERENCE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"flake8 syntax check failed: {r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - pycodestyle blank line validation
def test_repo_pycodestyle_blank_lines_vllm_completion():
    """vllm_text_completion.py has correct blank lines (E3) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pycodestyle", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install pycodestyle failed: {r.stderr}"
    r = subprocess.run(
        ["pycodestyle", "--select=E3", VLLM_COMPLETION],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pycodestyle blank line check failed: {r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - pycodestyle blank line validation
def test_repo_pycodestyle_blank_lines_vllm_inference():
    """vllm_inference.py has correct blank lines (E3) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pycodestyle", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install pycodestyle failed: {r.stderr}"
    r = subprocess.run(
        ["pycodestyle", "--select=E3", VLLM_INFERENCE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pycodestyle blank line check failed: {r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - yapf format validation
def test_repo_yapf_format_vllm_completion():
    """vllm_text_completion.py follows yapf formatting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "yapf", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install yapf failed: {r.stderr}"
    r = subprocess.run(
        ["yapf", "--diff", VLLM_COMPLETION],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/sdks/python",
    )
    assert r.returncode == 0, f"yapf format check failed: {r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - yapf format validation
def test_repo_yapf_format_vllm_inference():
    """vllm_inference.py follows yapf formatting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "yapf", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install yapf failed: {r.stderr}"
    r = subprocess.run(
        ["yapf", "--diff", VLLM_INFERENCE],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/sdks/python",
    )
    assert r.returncode == 0, f"yapf format check failed: {r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - pylint errors validation
def test_repo_pylint_errors_vllm_completion():
    """vllm_text_completion.py has no pylint errors (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pylint", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install pylint failed: {r.stderr}"
    r = subprocess.run(
        ["pylint", "-j2", VLLM_COMPLETION, "--errors-only"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/sdks/python",
    )
    assert r.returncode == 0, f"pylint errors check failed: {r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass - pylint errors validation
def test_repo_pylint_errors_vllm_inference():
    """vllm_inference.py has no pylint errors (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pylint", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"pip install pylint failed: {r.stderr}"
    r = subprocess.run(
        ["pylint", "-j2", VLLM_INFERENCE, "--errors-only"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/sdks/python",
    )
    assert r.returncode == 0, f"pylint errors check failed: {r.stdout}{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — vllm_text_completion: new CLI args + kwargs builder
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_args_accepts_max_num_seqs_flag():
    """parse_known_args() accepts a custom max-num-seqs flag and parses it as int."""
    _run("""\
known, _ = vtc.parse_known_args(['--vllm_max_num_seqs', '64', '--output', '/tmp/out'])
assert hasattr(known, 'vllm_max_num_seqs'), "Missing vllm_max_num_seqs arg"
val = known.vllm_max_num_seqs
assert isinstance(val, int), f"Expected int, got {type(val)}"
assert val == 64, f"Expected 64, got {val}"
""")


# [pr_diff] fail_to_pass
def test_parse_args_accepts_gpu_memory_utilization_flag():
    """parse_known_args() accepts a custom gpu_memory_utilization flag and parses it as float."""
    _run("""\
known, _ = vtc.parse_known_args(['--vllm_gpu_memory_utilization', '0.85', '--output', '/tmp/out'])
assert hasattr(known, 'vllm_gpu_memory_utilization'), "Missing vllm_gpu_memory_utilization arg"
val = known.vllm_gpu_memory_utilization
assert isinstance(val, float), f"Expected float, got {type(val)}"
assert abs(val - 0.85) < 1e-6, f"Expected 0.85, got {val}"
""")


# [pr_diff] fail_to_pass
def test_parse_args_provides_sensible_defaults():
    """parse_known_args() provides sensible defaults when flags are not provided."""
    _run("""\
known, _ = vtc.parse_known_args(['--output', '/tmp/out'])
# Both flags must be present and have reasonable default values
assert hasattr(known, 'vllm_max_num_seqs'), "Missing vllm_max_num_seqs arg"
max_seqs = known.vllm_max_num_seqs
assert isinstance(max_seqs, int), f"vllm_max_num_seqs should be int, got {type(max_seqs)}"
assert 1 <= max_seqs <= 256, f"Default max_seqs={max_seqs} not in range [1, 256]"

assert hasattr(known, 'vllm_gpu_memory_utilization'), "Missing vllm_gpu_memory_utilization arg"
mem_util = known.vllm_gpu_memory_utilization
assert isinstance(mem_util, float), f"vllm_gpu_memory_utilization should be float, got {type(mem_util)}"
assert 0.1 <= mem_util <= 0.95, f"Default mem_util={mem_util} not in range [0.1, 0.95]"
""")


# [pr_diff] fail_to_pass
def test_kwargs_helper_returns_dict_with_server_flags():
    """A helper returns a dict mapping vLLM server flag names to string values."""
    _run("""\
from types import SimpleNamespace

# Find any function that accepts an object with max_num_seqs and gpu_memory_utilization
# and returns a dict with vLLM server flags
candidates = [name for name in dir(vtc) if not name.startswith('_')]
fn = None
for name in candidates:
    obj = getattr(vtc, name)
    if callable(obj) and not name.startswith('parse_') and not name.startswith('run'):
        # Quick check: call with dummy args
        try:
            args = SimpleNamespace(vllm_max_num_seqs=32, vllm_gpu_memory_utilization=0.72)
            result = obj(args)
            if isinstance(result, dict) and len(result) >= 2:
                # Looks like the right function
                fn = obj
                break
        except Exception:
            pass

assert fn is not None, f"No function found that accepts args and returns dict with server flags. Candidates: {candidates}"
result = fn(SimpleNamespace(vllm_max_num_seqs=32, vllm_gpu_memory_utilization=0.72))

assert isinstance(result, dict), f"Expected dict, got {type(result)}"
# Must contain at least two keys for max-num-seqs and gpu-memory-utilization
assert len(result) >= 2, f"Expected at least 2 keys, got {len(result)}"
# All values must be strings
for k, v in result.items():
    assert isinstance(v, str), f"Value for {k} should be str, got {type(v)}"
# Check for max-num related key
keys_lower = {k.lower(): k for k in result}
has_max = any('max' in k.lower() and 'seq' in k.lower() for k in result)
has_gpu = any('gpu' in k.lower() and 'memory' in k.lower() for k in result)
assert has_max, f"Missing max-num related key in {list(result.keys())}"
assert has_gpu, f"Missing gpu-memory related key in {list(result.keys())}"
""")


# [pr_diff] fail_to_pass
def test_kwargs_helper_converts_numeric_values_to_strings():
    """The kwargs helper correctly converts numeric args to string CLI flags."""
    _run("""\
from types import SimpleNamespace

# Find the helper function
candidates = [name for name in dir(vtc) if not name.startswith('_')]
fn = None
for name in candidates:
    obj = getattr(vtc, name)
    if callable(obj) and not name.startswith('parse_') and not name.startswith('run'):
        try:
            args = SimpleNamespace(vllm_max_num_seqs=32, vllm_gpu_memory_utilization=0.72)
            result = obj(args)
            if isinstance(result, dict) and len(result) >= 2:
                fn = obj
                break
        except Exception:
            pass

assert fn is not None, "Helper function not found"

# Test that numeric values are converted to string values
test_cases = [(16, 0.5), (64, 0.9), (128, 0.85)]
for max_seqs, mem_util in test_cases:
    args = SimpleNamespace(vllm_max_num_seqs=max_seqs, vllm_gpu_memory_utilization=mem_util)
    result = fn(args)
    vals = list(result.values())
    str_seqs = str(max_seqs)
    str_mem = str(mem_util)
    assert any(str_seqs in v for v in vals), f"Expected '{str_seqs}' in values {vals}"
    assert any(str_mem in v for v in vals), f"Expected '{str_mem}' in values {vals}"
""")


# [pr_diff] fail_to_pass
def test_run_function_supports_external_kwargs():
    """run() function accepts a parameter for programmatic vllm_server_kwargs override."""
    _run("""\
import inspect
sig = inspect.signature(vtc.run)
# The run() function must accept some form of vLLM server kwargs override
# Check for a parameter whose name suggests vLLM server kwargs
params = list(sig.parameters)
has_vllm_kwarg = any('vllm' in p.lower() and 'kwarg' in p.lower() for p in params)
has_vllm_server_kwarg = any('vllm_server_kwargs' in p for p in params)
assert has_vllm_kwarg or has_vllm_server_kwarg, \
    f"run() must accept vllm_server_kwargs or similar parameter; params: {params}"
""")


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README must document GPU memory settings
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
def test_readme_documents_gpu_memory_constraints():
    """README.md explains GPU memory constraints for ~16GiB GPUs."""
    readme_content = Path(README).read_text()
    # Must mention GPU memory constraints for smaller GPUs
    assert "CUDA out of memory" in readme_content or "16GiB" in readme_content or "T4" in readme_content, \
        "README must explain GPU memory constraints (16GiB, T4, or CUDA OOM)"
    # Must document that defaults exist (without hardcoding flag names)
    lines = readme_content.split('\n')
    # Look for a paragraph that explains default behavior for small GPUs
    has_conservative_defaults = any(
        'default' in line.lower() and ('gpu' in line.lower() or 'memory' in line.lower())
        for line in lines
    )
    assert has_conservative_defaults, \
        "README must document that conservative default values are provided for small GPUs"
