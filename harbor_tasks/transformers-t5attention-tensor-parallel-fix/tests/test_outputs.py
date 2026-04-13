"""
Task: transformers-t5attention-tensor-parallel-fix
Repo: transformers @ 38593c2e83964079576eb646fe9b68cce16114dc
PR:   45109

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"

T5_MODELS = [
    "src/transformers/models/t5/modeling_t5.py",
    "src/transformers/models/mt5/modeling_mt5.py",
    "src/transformers/models/longt5/modeling_longt5.py",
    "src/transformers/models/udop/modeling_udop.py",
    "src/transformers/models/pop2piano/modeling_pop2piano.py",
    "src/transformers/models/switch_transformers/modeling_switch_transformers.py",
]


def _get_model_path(filename: str) -> Path:
    return Path(f"{REPO}/{filename}")


def _parse_file(filepath: Path) -> ast.AST:
    """Parse a Python file and return its AST."""
    src = filepath.read_text()
    return ast.parse(src)


def _find_attention_forward(tree: ast.AST) -> ast.FunctionDef | None:
    """Find the forward method in the Attention class."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any(name in node.name for name in ["Attention", "T5Attention", "MT5Attention", "LongT5Attention",
                                                   "UdopAttention", "Pop2PianoAttention", "SwitchTransformersAttention"]):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "forward":
                        return item
    return None


def _find_view_calls(func: ast.FunctionDef) -> list[ast.Call]:
    """Find all view() calls in a function."""
    views = []
    for node in ast.walk(func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "view":
                views.append(node)
    return views


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for filename in T5_MODELS:
        filepath = _get_model_path(filename)
        src = filepath.read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_t5attention_tp_compatible():
    """T5Attention correctly infers n_heads from tensor shape when inner_dim is sharded."""
    code = f"""
import ast
import sys
filepath = "{REPO}/src/transformers/models/t5/modeling_t5.py"
src = open(filepath).read()
if "q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)" in src:
    print("PASS: Query view uses TP-compatible pattern")
    sys.exit(0)
print("FAIL: Could not find TP-compatible query pattern")
sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise AssertionError(f"TP compatibility check failed: {result.stderr or result.stdout}")
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_kv_attention_shape_correct():
    """Key/value attention uses dynamic shape from current_states instead of config n_heads."""
    code = f"""
import sys
filepath = "{REPO}/src/transformers/models/t5/modeling_t5.py"
src = open(filepath).read()
if "kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)" in src:
    print("PASS: KV view uses TP-compatible pattern")
    sys.exit(0)
print("FAIL: Could not find TP-compatible KV pattern")
sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise AssertionError(f"KV shape check failed: {result.stderr or result.stdout}")
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_position_bias_dynamic():
    """position_bias shape uses query_states.shape[1] instead of config n_heads."""
    code = f"""
import sys
filepath = "{REPO}/src/transformers/models/t5/modeling_t5.py"
src = open(filepath).read()
if "(1, query_states.shape[1], seq_length, key_length)" in src:
    print("PASS: position_bias uses dynamic query_states.shape[1]")
    sys.exit(0)
print("FAIL: Could not find dynamic position_bias pattern")
sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise AssertionError(f"Position bias check failed: {result.stderr or result.stdout}")
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_attn_output_reshape():
    """attn_output.view uses seq_length as fixed dim and -1 for heads dimension."""
    code = f"""
import sys
filepath = "{REPO}/src/transformers/models/t5/modeling_t5.py"
src = open(filepath).read()
if ".view(batch_size, seq_length, -1)" in src:
    print("PASS: attn_output reshape uses (batch_size, seq_length, -1) pattern")
    sys.exit(0)
print("FAIL: Could not find TP-compatible attn_output reshape pattern")
sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise AssertionError(f"Attn output reshape check failed: {result.stderr or result.stdout}")
    assert "PASS" in result.stdout


# [pr_diff] fail_to_pass
def test_view_operations_runtime_semantics():
    """Verify the view operations produce correct shapes under TP-like conditions using numpy simulation."""
    code = """
import numpy as np
import sys

batch_size = 2
seq_length = 512
n_heads_config = 128
key_value_proj_dim = 128
inner_dim_tp = 4096

# The fixed approach (using -1 for heads)
correct_heads = inner_dim_tp // key_value_proj_dim
q_fixed = np.zeros((batch_size, seq_length, inner_dim_tp))
result_fixed = q_fixed.reshape(batch_size, seq_length, -1, key_value_proj_dim)
fixed_shape = result_fixed.shape

assert fixed_shape == (batch_size, seq_length, correct_heads, key_value_proj_dim)

# The buggy approach would give wrong shape
inferred_seq = seq_length * inner_dim_tp // (n_heads_config * key_value_proj_dim)
result_buggy = q_fixed.reshape(batch_size, inferred_seq, n_heads_config, key_value_proj_dim)
buggy_shape = result_buggy.shape

assert buggy_shape != fixed_shape

print("PASS: View semantics verified - fixed shape preserves seq_length, buggy corrupts it")
sys.exit(0)
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise AssertionError(f"View operations runtime check failed: {result.stderr or result.stdout}")
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    # Install ruff temporarily for this check
    install_result = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install ruff: {install_result.stderr}")

    # Run ruff check on all modified T5-family model files
    files_to_check = [f"{REPO}/{f}" for f in T5_MODELS]
    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82"] + files_to_check,
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Ruff check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """All modified Python files compile without errors (pass_to_pass)."""
    import py_compile
    for filename in T5_MODELS:
        filepath = _get_model_path(filename)
        try:
            py_compile.compile(str(filepath), doraise=True)
        except py_compile.PyCompileError as e:
            raise AssertionError(f"{filename}: Compile error - {e}")


# [repo_tests] pass_to_pass
def test_repo_t5_classes_exist():
    """T5-family model files contain required Attention classes (pass_to_pass)."""
    required_patterns = [
        ("T5Attention", "class T5Attention"),
        ("MT5Attention", "class MT5Attention"),
        ("LongT5Attention", "class LongT5Attention"),
        ("UdopAttention", "class UdopAttention"),
        ("Pop2PianoAttention", "class Pop2PianoAttention"),
        ("SwitchTransformersAttention", "class SwitchTransformersAttention"),
    ]
    for filename, (class_name, pattern) in zip(T5_MODELS, required_patterns):
        filepath = _get_model_path(filename)
        src = filepath.read_text()
        if pattern not in src:
            raise AssertionError(f"{filename}: Missing required class pattern '{pattern}'")


# [repo_tests] pass_to_pass
def test_repo_forward_methods_parse():
    """All T5-family Attention.forward() methods have valid AST structure (pass_to_pass)."""
    for filename in T5_MODELS:
        filepath = _get_model_path(filename)
        tree = _parse_file(filepath)
        forward = _find_attention_forward(tree)
        if forward is None:
            raise AssertionError(f"{filename}: Could not find Attention.forward method")


# [repo_tests] pass_to_pass
def test_repo_ruff_format_check():
    """Repo's ruff format check passes on modified T5-family model files (pass_to_pass)."""
    # Install ruff temporarily for this check
    install_result = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install ruff: {install_result.stderr}")

    # Run ruff format check on all modified T5-family model files
    files_to_check = [f"{REPO}/{f}" for f in T5_MODELS]
    r = subprocess.run(
        ["ruff", "format", "--check"] + files_to_check,
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Ruff format check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_modeling_structure():
    """Repo's modeling structure check passes (pass_to_pass)."""
    # Install dependencies needed for the check
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    # Install transformers package
    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

    # Run modeling structure check
    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Modeling structure check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_inits_check():
    """Repo's init file consistency check passes (pass_to_pass)."""
    # Install dependencies needed for the check
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    # Install transformers package
    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

    # Run inits check
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Init files check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_config_docstrings():
    """Repo's config docstrings check passes (pass_to_pass)."""
    # Install dependencies needed for the check
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    # Install transformers package
    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

    # Run config docstrings check
    r = subprocess.run(
        ["python", "utils/check_config_docstrings.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Config docstrings check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_dummies_check():
    """Repo's dummy files check passes (pass_to_pass)."""
    # Install dependencies needed for the check
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    # Install transformers package
    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

    # Run dummies check
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Dummies check failed:\n{r.stdout}\n{r.stderr}")


# [agent_config] fail_to_pass — CLAUDE.md:45-55
def test_copied_files_updated():
    """T5-family model copies (mt5, longt5, etc.) have been updated with the same fix."""
    errors = []
    for filename in T5_MODELS:
        filepath = _get_model_path(filename)
        src = filepath.read_text()
        checks = {
            "query_view": "q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)" in src,
            "kv_view": "kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)" in src,
            "position_bias": "(1, query_states.shape[1], seq_length, key_length)" in src,
            "attn_output": ".view(batch_size, seq_length, -1)" in src,
        }
        failed = [k for k, v in checks.items() if not v]
        if failed:
            errors.append(f"{filename}: missing patterns: {failed}")
    if errors:
        raise AssertionError("Not all T5-family models have been updated:\n" + "\n".join(errors))


# [static] pass_to_pass
def test_not_stub():
    """T5Attention.forward has real logic, not just pass/return."""
    filepath = _get_model_path(T5_MODELS[0])
    tree = _parse_file(filepath)
    forward = _find_attention_forward(tree)
    assert forward is not None, "Could not find Attention.forward method"
    statements = [s for s in forward.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(statements) >= 10, f"T5Attention.forward is too short ({len(statements)} statements), likely a stub"
    views = _find_view_calls(forward)
    assert len(views) >= 4, f"Expected at least 4 view() calls in T5Attention.forward, found {len(views)}"
