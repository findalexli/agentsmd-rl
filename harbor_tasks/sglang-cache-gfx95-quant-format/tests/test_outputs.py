"""
Task: sglang-cache-gfx95-quant-format
Repo: sgl-project/sglang @ 52801ff20c3d48ef594912bae3f2e49fbabe0a71
PR:   22143

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/python/sglang/srt/models/deepseek_v2.py"


def _parse_target_file():
    """Parse the target file and return the AST."""
    src = Path(TARGET_FILE).read_text()
    return ast.parse(src)


def _get_class_methods(tree, class_name):
    """Extract methods from a class in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {n.name: n for n in node.body if isinstance(n, ast.FunctionDef)}
    return {}


def _get_init_assignments(tree, class_name):
    """Extract attribute assignments from __init__ method."""
    methods = _get_class_methods(tree, class_name)
    if "__init__" not in methods:
        return {}

    init = methods["__init__"]
    assigns = {}
    for stmt in init.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                    if target.value.id == "self":
                        assigns[target.attr] = stmt
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Attribute) and isinstance(stmt.target.value, ast.Name):
                if stmt.target.value.id == "self":
                    assigns[stmt.target.attr] = stmt
    return assigns


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile
    py_compile.compile(TARGET_FILE, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cached_quant_format_attribute():
    """DeepseekV2DecoderLayer must cache _gfx95_quant_format in __init__."""
    tree = _parse_target_file()

    # Check class exists
    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")
    assert "__init__" in methods, "DeepseekV2DecoderLayer.__init__ not found"

    # Check that _gfx95_quant_format is assigned in __init__
    assigns = _get_init_assignments(tree, "DeepseekV2DecoderLayer")
    assert "_gfx95_quant_format" in assigns, (
        "_gfx95_quant_format not assigned in __init__"
    )

    # Check that it calls _detect_gfx95_quant_format()
    assign = assigns["_gfx95_quant_format"]
    assert isinstance(assign.value, ast.Call), (
        "_gfx95_quant_format assignment is not a function call"
    )
    func = assign.value.func
    assert isinstance(func, ast.Attribute), "Expected method call"
    assert func.attr == "_detect_gfx95_quant_format", (
        "_gfx95_quant_format not assigned from _detect_gfx95_quant_format()"
    )


# [pr_diff] fail_to_pass
def test_detect_gfx95_quant_format_method():
    """DeepseekV2DecoderLayer must have _detect_gfx95_quant_format method."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")
    assert "_detect_gfx95_quant_format" in methods, (
        "_detect_gfx95_quant_format method not found"
    )

    method = methods["_detect_gfx95_quant_format"]
    # Check return annotation (str)
    if method.returns:
        assert isinstance(method.returns, ast.Name) and method.returns.id == "str", (
            "Method should return str"
        )


# [pr_diff] fail_to_pass
def test_forward_uses_cached_quant_format():
    """forward() must use self._gfx95_quant_format instead of recomputing."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")
    assert "forward" in methods, "forward method not found"

    forward = methods["forward"]
    src = ast.unparse(forward)

    # Should use self._gfx95_quant_format
    assert "self._gfx95_quant_format" in src, (
        "forward() does not use self._gfx95_quant_format"
    )

    # Should NOT have the old inline quant_format computation pattern
    # (checking for the complex nested conditional that was removed)
    assert "quant_format =" not in src or "self._gfx95_quant_format" in src, (
        "forward() still has inline quant_format computation"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff lint check passes on modified file (pass_to_pass)."""
    import subprocess

    # Install ruff if not available
    try:
        subprocess.run(["pip", "install", "-q", "ruff"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_repo_ast_validity():
    """Repo's Python AST parsing passes on modified file (pass_to_pass)."""
    import ast
    src = Path(TARGET_FILE).read_text()
    # Should parse without errors
    tree = ast.parse(src)
    # Should find the expected class
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "DeepseekV2DecoderLayer" in classes, "DeepseekV2DecoderLayer class not found"


# [static] pass_to_pass
def test_repo_file_structure():
    """Modified file has proper Python file structure (pass_to_pass)."""
    import ast
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    # Check for imports section at top
    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    assert len(imports) > 0, "No imports found in file"

    # Check for class definitions
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    assert len(classes) > 0, "No class definitions found in file"

    # DeepseekV2DecoderLayer should have expected methods
    layer_class = None
    for cls in classes:
        if cls.name == "DeepseekV2DecoderLayer":
            layer_class = cls
            break

    assert layer_class is not None, "DeepseekV2DecoderLayer class not found"

    methods = [n.name for n in layer_class.body if isinstance(n, ast.FunctionDef)]
    assert "__init__" in methods, "DeepseekV2DecoderLayer.__init__ not found"
    assert "forward" in methods, "DeepseekV2DecoderLayer.forward not found"


# [repo_tests] pass_to_pass
def test_repo_black_format():
    """Repo's black format check passes on modified file (pass_to_pass)."""
    import subprocess

    try:
        subprocess.run(["pip", "install", "-q", "black"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["black", "--check", "--diff", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo's isort check passes on modified file (pass_to_pass)."""
    import subprocess

    try:
        subprocess.run(["pip", "install", "-q", "isort"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["isort", "--check-only", "--diff", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """Repo's codespell check passes on modified file (pass_to_pass)."""
    import subprocess

    try:
        subprocess.run(["pip", "install", "-q", "codespell"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["codespell", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"codespell check failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified function is not a stub (has real logic, not just pass/return)."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")
    assert "_detect_gfx95_quant_format" in methods, "Method not found"

    method = methods["_detect_gfx95_quant_format"]
    # Count non-trivial statements (not Pass, not just docstring)
    stmts = [s for s in method.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(stmts) >= 3, "Method body is a stub (too few statements)"


# [static] pass_to_pass
def test_detect_method_has_proper_logic():
    """_detect_gfx95_quant_format must have proper dtype checking logic."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")
    method = methods["_detect_gfx95_quant_format"]
    src = ast.unparse(method)

    # Check for the key logic components
    assert "torch.uint8" in src, "Missing uint8 dtype check"
    assert "float8_e4m3fn" in src or "getattr(torch" in src, (
        "Missing fp8_e4m3fn dtype check"
    )
    assert "mxfp4" in src, "Missing mxfp4 return value"
    assert "fp8" in src, "Missing fp8 return value"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------
# No agent config rules apply to this task (the SKILL.md files are for
# test writing and kernel development, not model code refactoring)
