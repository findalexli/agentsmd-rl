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
def test_parse_args_default_max_num_seqs():
    """parse_known_args exposes --vllm_max_num_seqs with a reasonable int default."""
    _run("""\
known, _ = vtc.parse_known_args(['--output', '/tmp/out'])
assert hasattr(known, 'vllm_max_num_seqs'), "Missing vllm_max_num_seqs arg"
val = known.vllm_max_num_seqs
assert isinstance(val, int), f"Expected int, got {type(val)}"
assert 1 <= val <= 256, f"Default {val} not in reasonable range [1, 256]"
""")


# [pr_diff] fail_to_pass
def test_parse_args_default_gpu_memory_utilization():
    """parse_known_args exposes --vllm_gpu_memory_utilization with a reasonable float default."""
    _run("""\
known, _ = vtc.parse_known_args(['--output', '/tmp/out'])
assert hasattr(known, 'vllm_gpu_memory_utilization'), "Missing vllm_gpu_memory_utilization arg"
val = known.vllm_gpu_memory_utilization
assert isinstance(val, float), f"Expected float, got {type(val)}"
assert 0.1 <= val <= 0.95, f"Default {val} not in reasonable range [0.1, 0.95]"
""")


# [pr_diff] fail_to_pass
def test_parse_args_custom_overrides():
    """--vllm_max_num_seqs and --vllm_gpu_memory_utilization accept custom values."""
    _run("""\
known, _ = vtc.parse_known_args([
    '--output', '/tmp/out',
    '--vllm_max_num_seqs', '64',
    '--vllm_gpu_memory_utilization', '0.9',
])
assert known.vllm_max_num_seqs == 64, f"Expected 64, got {known.vllm_max_num_seqs}"
assert abs(known.vllm_gpu_memory_utilization - 0.9) < 1e-6, \\
    f"Expected 0.9, got {known.vllm_gpu_memory_utilization}"
""")


# [pr_diff] fail_to_pass
def test_build_vllm_server_kwargs():
    """A helper builds a dict of vLLM server CLI flags from parsed args."""
    _run("""\
from types import SimpleNamespace
fn = getattr(vtc, 'build_vllm_server_kwargs', None)
assert fn is not None, "build_vllm_server_kwargs function must exist"

args = SimpleNamespace(vllm_max_num_seqs=32, vllm_gpu_memory_utilization=0.72)
result = fn(args)
assert isinstance(result, dict), f"Expected dict, got {type(result)}"
# Must contain server-flag keys
assert any('max' in k and 'seq' in k for k in result), \\
    f"Missing max-num-seqs key in {list(result.keys())}"
assert any('gpu' in k and 'memory' in k for k in result), \\
    f"Missing gpu-memory-utilization key in {list(result.keys())}"
# Values must be strings (CLI args passed to vLLM server)
for k, v in result.items():
    assert isinstance(v, str), f"Value for {k} should be str, got {type(v)}"
""")


# [pr_diff] fail_to_pass
def test_build_vllm_server_kwargs_propagates_values():
    """build_vllm_server_kwargs correctly converts numeric args to string CLI flags."""
    _run("""\
from types import SimpleNamespace
fn = vtc.build_vllm_server_kwargs
for max_seqs, mem_util in [(16, 0.5), (64, 0.9), (128, 0.85)]:
    args = SimpleNamespace(vllm_max_num_seqs=max_seqs, vllm_gpu_memory_utilization=mem_util)
    result = fn(args)
    vals = list(result.values())
    assert str(max_seqs) in vals, f"Expected '{max_seqs}' in values {vals}"
    assert str(mem_util) in vals, f"Expected '{mem_util}' in values {vals}"
""")


# [pr_diff] fail_to_pass
def test_run_accepts_vllm_server_kwargs():
    """run() function accepts a vllm_server_kwargs parameter for programmatic use."""
    _run("""\
import inspect
sig = inspect.signature(vtc.run)
assert 'vllm_server_kwargs' in sig.parameters, \\
    f"run() must accept vllm_server_kwargs; params: {list(sig.parameters)}"
""")


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README must document GPU memory settings
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
def test_readme_documents_gpu_memory_settings():
    """README.md documents GPU memory constraints and vLLM tuning flags."""
    readme_content = Path(README).read_text()
    assert "vllm_max_num_seqs" in readme_content, \
        "README must document --vllm_max_num_seqs flag"
    assert "vllm_gpu_memory_utilization" in readme_content, \
        "README must document --vllm_gpu_memory_utilization flag"
    assert "16GiB" in readme_content or "CUDA out of memory" in readme_content, \
        "README must explain GPU memory constraints (16GiB or CUDA OOM)"
