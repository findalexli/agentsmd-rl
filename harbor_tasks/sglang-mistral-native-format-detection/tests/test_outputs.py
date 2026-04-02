"""
Task: sglang-mistral-native-format-detection
Repo: sgl-project/sglang @ b2462694441412ad209c361dfa87f3f37a3d29f3
PR:   21620

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import tempfile
import textwrap
import types
from pathlib import Path

REPO = "/repo"
TARGET_FILE = f"{REPO}/python/sglang/srt/server_args.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_function(filepath, funcname):
    """Extract a method's source from a file using AST."""
    source = Path(filepath).read_text()
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == funcname:
            return textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
    raise RuntimeError(f"{funcname} not found in {filepath}")


def _call_is_mistral_native(model_name, has_params, has_config):
    """Create a temp model dir and invoke _is_mistral_native_format."""
    func_src = _extract_function(TARGET_FILE, "_is_mistral_native_format")

    tmpdir = tempfile.mkdtemp()
    model_dir = os.path.join(tmpdir, "models", model_name)
    os.makedirs(model_dir, exist_ok=True)
    if has_params:
        Path(os.path.join(model_dir, "params.json")).write_text("{}")
    if has_config:
        Path(os.path.join(model_dir, "config.json")).write_text("{}")

    exec_ns = {"os": os, "re": __import__("re"), "__builtins__": __builtins__}
    exec(compile("import os, re\n" + func_src, "<test>", "exec"), exec_ns)
    func = exec_ns["_is_mistral_native_format"]

    mock_self = types.SimpleNamespace(model_path=model_dir)
    return func(mock_self)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """server_args.py must parse without syntax errors."""
    source = Path(TARGET_FILE).read_text()
    ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug: native models with both files must
# return True from _is_mistral_native_format
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mistral_small_4_both_files_returns_true():
    """Mistral-Small-4 with both params.json and config.json returns True."""
    assert _call_is_mistral_native("Mistral-Small-4-119B-2603", True, True) is True


# [pr_diff] fail_to_pass
def test_mistral_large_3_both_files_returns_true():
    """Mistral-Large-3 with both params.json and config.json returns True."""
    assert _call_is_mistral_native("Mistral-Large-3-2503", True, True) is True


# [pr_diff] fail_to_pass
def test_leanstral_both_files_returns_true():
    """Leanstral with both params.json and config.json returns True."""
    assert _call_is_mistral_native("Leanstral-22B-v0.1", True, True) is True


# [pr_diff] fail_to_pass
def test_mistral_small_4_variant_both_files_returns_true():
    """Mistral-Small-4 variant name with both files returns True."""
    assert _call_is_mistral_native("Mistral-Small-4-Base", True, True) is True


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: params-only always returns True
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_params_only_returns_true():
    """Any model with only params.json (no config.json) returns True."""
    assert _call_is_mistral_native("SomeMistralModel", True, False) is True


# [pr_diff] pass_to_pass
def test_mistral_7b_params_only_returns_true():
    """Mistral-7B with only params.json returns True (regression)."""
    assert _call_is_mistral_native("Mistral-7B-Instruct-v0.3", True, False) is True


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: non-native models with both files
# must still return False
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_mistral_7b_both_files_returns_false():
    """Mistral-7B-Instruct with both files returns False (not native)."""
    assert _call_is_mistral_native("Mistral-7B-Instruct-v0.3", True, True) is False


# [pr_diff] pass_to_pass
def test_codestral_mamba_both_files_returns_false():
    """Codestral-Mamba with both files returns False."""
    assert _call_is_mistral_native("Codestral-Mamba-22B-v0.1", True, True) is False


# [pr_diff] pass_to_pass
def test_pixtral_both_files_returns_false():
    """Pixtral with both files returns False."""
    assert _call_is_mistral_native("Pixtral-12B-2409", True, True) is False


# [pr_diff] pass_to_pass
def test_mistral_small_3_both_files_returns_false():
    """Mistral-Small-3 (not 4) with both files returns False."""
    assert _call_is_mistral_native("Mistral-Small-3-24B", True, True) is False


# [pr_diff] pass_to_pass
def test_mistral_nemo_both_files_returns_false():
    """Mistral-Nemo with both files returns False."""
    assert _call_is_mistral_native("Mistral-Nemo-Instruct-2407", True, True) is False


# [pr_diff] pass_to_pass
def test_no_params_json_returns_false():
    """Model with config.json only (no params.json) returns False."""
    assert _call_is_mistral_native("SomeModel", False, True) is False


# [pr_diff] pass_to_pass
def test_neither_file_returns_false():
    """Model with neither file returns False."""
    assert _call_is_mistral_native("EmptyModel", False, False) is False


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """_is_mistral_native_format has real logic, not just pass/return."""
    source = Path(TARGET_FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_is_mistral_native_format":
            # Count non-trivial statements (exclude Pass, docstrings, bare returns)
            stmts = [
                s
                for s in ast.walk(node)
                if isinstance(s, (ast.If, ast.For, ast.Call, ast.Assign, ast.Return))
            ]
            assert len(stmts) >= 3, "Function body looks like a stub"
            return
    raise AssertionError("_is_mistral_native_format not found")
