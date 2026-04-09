"""
Task: transformers-t5attention-tensor-parallel-fix
Repo: transformers @ 38593c2e83964079576eb646fe9b68cce16114dc
PR:   45109

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
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
            # Check if this is an Attention class (various names in different models)
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
        # This will raise SyntaxError if parsing fails
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_t5attention_tp_compatible():
    """T5Attention correctly infers n_heads from tensor shape when inner_dim is sharded."""
    filepath = _get_model_path(T5_MODELS[0])  # T5 is the base model
    tree = _parse_file(filepath)
    forward = _find_attention_forward(tree)
    assert forward is not None, "Could not find Attention.forward method"

    views = _find_view_calls(forward)

    # Find the query view - should be (batch_size, seq_length, -1, key_value_proj_dim)
    found_query_fix = False
    for view in views:
        if isinstance(view.args, list) and len(view.args) >= 1:
            # Check if it's using q_input_shape or unpacked tuple
            if isinstance(view.args[0], ast.Starred):
                # Check if the variable name is q_input_shape
                if isinstance(view.args[0].value, ast.Name):
                    if "q_input_shape" in view.args[0].value.id:
                        found_query_fix = True

    # Alternative: check for seq_length in the view arguments (not -1 as first dimension after batch)
    # The fixed pattern should have seq_length as the 2nd element, -1 as 3rd element
    if not found_query_fix:
        # Look for the pattern: view(batch_size, seq_length, -1, self.key_value_proj_dim)
        src = filepath.read_text()
        # The fix introduces q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)
        if "q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)" in src:
            found_query_fix = True

    assert found_query_fix, "T5Attention query view does not use TP-compatible pattern (batch_size, seq_length, -1, ...)"


# [pr_diff] fail_to_pass
def test_kv_attention_shape_correct():
    """Key/value attention uses dynamic shape from current_states instead of config n_heads."""
    filepath = _get_model_path(T5_MODELS[0])
    tree = _parse_file(filepath)
    forward = _find_attention_forward(tree)
    assert forward is not None, "Could not find Attention.forward method"

    src = filepath.read_text()

    # Check for kv_input_shape pattern
    found_kv_fix = "kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)" in src

    assert found_kv_fix, "T5Attention key/value views do not use TP-compatible pattern (batch_size, current_states.shape[1], -1, ...)"


# [pr_diff] fail_to_pass
def test_position_bias_dynamic():
    """position_bias shape uses query_states.shape[1] instead of config n_heads."""
    filepath = _get_model_path(T5_MODELS[0])
    src = filepath.read_text()

    # Look for the fixed pattern: (1, query_states.shape[1], seq_length, key_length)
    found_fix = "(1, query_states.shape[1], seq_length, key_length)" in src

    assert found_fix, "position_bias does not use query_states.shape[1] for dynamic head count"


# [pr_diff] fail_to_pass
def test_attn_output_reshape():
    """attn_output.view uses seq_length as fixed dim and -1 for heads dimension."""
    filepath = _get_model_path(T5_MODELS[0])
    src = filepath.read_text()

    # Look for the fixed pattern: attn_output.view(batch_size, seq_length, -1)
    # This should appear after the transpose operation
    found_fix = ".view(batch_size, seq_length, -1)" in src

    assert found_fix, "attn_output reshape does not use (batch_size, seq_length, -1) pattern"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:45-55
def test_copied_files_updated():
    """T5-family model copies (mt5, longt5, etc.) have been updated with the same fix."""
    # Check that all 6 files have the TP-compatible patterns

    errors = []
    for filename in T5_MODELS:
        filepath = _get_model_path(filename)
        src = filepath.read_text()

        # Check for the 4 key patterns
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

    # Count non-trivial statements
    statements = [s for s in forward.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(statements) >= 10, f"T5Attention.forward is too short ({len(statements)} statements), likely a stub"

    # Check for view calls (core functionality)
    views = _find_view_calls(forward)
    assert len(views) >= 4, f"Expected at least 4 view() calls in T5Attention.forward, found {len(views)}"
