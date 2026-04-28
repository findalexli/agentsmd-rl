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


def _get_forward_source(filepath: Path) -> str:
    """Extract the source code of the Attention.forward method."""
    src = filepath.read_text()
    tree = ast.parse(src)
    forward = _find_attention_forward(tree)
    if forward is None:
        return ""
    lines = src.split('\n')
    if hasattr(forward, 'end_lineno') and forward.end_lineno is not None:
        return '\n'.join(lines[forward.lineno - 1 : forward.end_lineno])
    return '\n'.join(lines[forward.lineno - 1:])


def _view_calls_use_attr(forward_src: str, attr: str) -> bool:
    """Check if any .view() call in forward source uses the given attribute."""
    for line in forward_src.split('\n'):
        if '.view(' in line and attr in line:
            return True
    return False


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
    filepath = _get_model_path(T5_MODELS[0])
    forward_src = _get_forward_source(filepath)
    if not forward_src:
        raise AssertionError("Could not find T5Attention.forward method")

    if _view_calls_use_attr(forward_src, 'self.n_heads'):
        raise AssertionError(
            "view() calls in T5Attention.forward still use self.n_heads. "
            "Replace with -1 so heads are inferred from the actual (possibly sharded) tensor shape."
        )


# [pr_diff] fail_to_pass
def test_kv_attention_shape_correct():
    """Key/value attention uses dynamic shape from current_states instead of config n_heads."""
    filepath = _get_model_path(T5_MODELS[0])
    forward_src = _get_forward_source(filepath)
    if not forward_src:
        raise AssertionError("Could not find T5Attention.forward method")

    if 'current_states.shape[1]' not in forward_src:
        raise AssertionError(
            "KV projection view does not use current_states.shape[1] for the dynamic sequence dimension. "
            "The shape must be derived from the current_states tensor, not hardcoded."
        )


# [pr_diff] fail_to_pass
def test_position_bias_dynamic():
    """position_bias shape uses query_states.shape[1] instead of config n_heads."""
    filepath = _get_model_path(T5_MODELS[0])
    forward_src = _get_forward_source(filepath)
    if not forward_src:
        raise AssertionError("Could not find T5Attention.forward method")

    if 'query_states.shape[1]' not in forward_src:
        raise AssertionError(
            "position_bias shape does not use query_states.shape[1] for the dynamic head count. "
            "The number of heads must be derived from the query tensor, not from self.n_heads."
        )


# [pr_diff] fail_to_pass
def test_attn_output_reshape():
    """attn_output.view uses seq_length as fixed dim and -1 for heads dimension."""
    filepath = _get_model_path(T5_MODELS[0])
    forward_src = _get_forward_source(filepath)
    if not forward_src:
        raise AssertionError("Could not find T5Attention.forward method")

    if _view_calls_use_attr(forward_src, 'self.inner_dim'):
        raise AssertionError(
            "attn_output.view() still uses self.inner_dim. "
            "Replace with -1 so the inner dimension is inferred from the actual tensor shape."
        )


# [pr_diff] pass_to_pass
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

correct_heads = inner_dim_tp // key_value_proj_dim
q_fixed = np.zeros((batch_size, seq_length, inner_dim_tp))
result_fixed = q_fixed.reshape(batch_size, seq_length, -1, key_value_proj_dim)
fixed_shape = result_fixed.shape

assert fixed_shape == (batch_size, seq_length, correct_heads, key_value_proj_dim)

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
    install_result = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install ruff: {install_result.stderr}")

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
    install_result = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install ruff: {install_result.stderr}")

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
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Modeling structure check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_inits_check():
    """Repo's init file consistency check passes (pass_to_pass)."""
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Init files check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_config_docstrings():
    """Repo's config docstrings check passes (pass_to_pass)."""
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

    r = subprocess.run(
        ["python", "utils/check_config_docstrings.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if r.returncode != 0:
        raise AssertionError(f"Config docstrings check failed:\n{r.stdout}\n{r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_dummies_check():
    """Repo's dummy files check passes (pass_to_pass)."""
    install_result = subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "--quiet"],
        capture_output=True, text=True, timeout=300
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install torch: {install_result.stderr}")

    install_tf_result = subprocess.run(
        ["pip", "install", "-e", ".", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    if install_tf_result.returncode != 0:
        raise AssertionError(f"Failed to install transformers: {install_tf_result.stderr}")

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
        forward_src = _get_forward_source(filepath)
        if not forward_src:
            errors.append(f"{filename}: Could not find Attention.forward method")
            continue

        failed = []
        if _view_calls_use_attr(forward_src, 'self.n_heads'):
            failed.append("view_calls_use_self.n_heads")
        if 'current_states.shape[1]' not in forward_src:
            failed.append("missing current_states.shape[1]")
        if 'query_states.shape[1]' not in forward_src:
            failed.append("missing query_states.shape[1]")
        if _view_calls_use_attr(forward_src, 'self.inner_dim'):
            failed.append("view_calls_use_self.inner_dim")
        if failed:
            errors.append(f"{filename}: missing fix patterns: {failed}")

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
