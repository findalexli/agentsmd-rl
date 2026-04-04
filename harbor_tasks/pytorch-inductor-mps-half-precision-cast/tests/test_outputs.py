"""
Task: pytorch-inductor-mps-half-precision-cast
Repo: pytorch/pytorch @ 036b25f5a29dc58cbc62e7b976efb860ff128c3f
PR:   #176436

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import math
import textwrap
from pathlib import Path

REPO = "/repo"
MPS_FILE = Path(REPO) / "torch/_inductor/codegen/mps.py"


def _load_mps_source():
    """Read mps.py and return (source_text, ast_tree)."""
    src = MPS_FILE.read_text()
    return src, ast.parse(src)


def _extract_function(src, tree, class_name, func_name):
    """Extract a function's source from a class in the AST."""
    lines = src.splitlines(keepends=True)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == func_name:
                    raw = "".join(lines[item.lineno - 1 : item.end_lineno])
                    return raw, item
    return None, None


def _build_where_callable():
    """Extract where() and value_to_metal(), return callable where function."""
    src, tree = _load_mps_source()
    lines = src.splitlines(keepends=True)

    # Extract value_to_metal (top-level function)
    vtm_src = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "value_to_metal":
            vtm_src = textwrap.dedent(
                "".join(lines[node.lineno - 1 : node.end_lineno])
            )
            break
    assert vtm_src is not None, "Could not find value_to_metal function"

    # Extract where() from MetalOverrides
    where_raw, _ = _extract_function(src, tree, "MetalOverrides", "where")
    assert where_raw is not None, "Could not find MetalOverrides.where method"

    # Strip decorator lines and dedent
    where_lines = [
        l
        for l in textwrap.dedent(where_raw).splitlines(keepends=True)
        if not l.strip().startswith("@")
    ]
    where_src = "".join(where_lines)

    class MockTorch:
        inf = math.inf

    class CSEVariable(str):
        pass

    ns = {
        "math": math,
        "torch": MockTorch(),
        "CSEVariable": CSEVariable,
        "OpVarT": object,
        "__builtins__": __builtins__,
    }
    # The source file uses `from __future__ import annotations` + TYPE_CHECKING
    # imports (Union, OpVarT). Prepend the future import so annotations stay as
    # strings and don't trigger NameError during exec.
    future = "from __future__ import annotations\n"
    exec(compile(future + vtm_src, "<vtm>", "exec"), ns)
    exec(compile(future + where_src, "<where>", "exec"), ns)
    return ns["where"], ns["value_to_metal"]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """mps.py must parse without syntax errors."""
    src = MPS_FILE.read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_where_casts_false_branch():
    """where() must cast the false-branch value to match the true-branch type."""
    where_fn, _ = _build_where_callable()

    # Test with multiple variable names to ensure the cast references the correct operand
    for true_var, false_val in [("var_bf16", 0.0), ("out_half", 1.5), ("tmp_f16", -1.0)]:
        result = where_fn("cond", true_var, false_val)
        assert f"decltype({true_var})" in result, (
            f"where('cond', '{true_var}', {false_val}) = {result!r} — "
            f"missing decltype cast referencing '{true_var}'"
        )
        assert "static_cast" in result, (
            f"where() output {result!r} missing static_cast"
        )


# [pr_diff] fail_to_pass
def test_where_casts_special_values():
    """where() must cast special float values (inf, -inf, nan) with type cast."""
    where_fn, _ = _build_where_callable()

    test_cases = [
        (math.inf, "HUGE_VALF"),
        (-math.inf, "-HUGE_VALF"),
        (math.nan, "NAN"),
    ]
    for val, metal_repr in test_cases:
        result = where_fn("mask", "x", val)
        assert metal_repr in result, (
            f"where('mask', 'x', {val}) = {result!r} — missing {metal_repr}"
        )
        assert "decltype" in result, (
            f"where('mask', 'x', {val}) = {result!r} — special value not cast"
        )


# [pr_diff] fail_to_pass
def test_masked_casts_both_branches():
    """masked() must add static_cast<decltype(...)> to both if-body and else-branch."""
    # AST-only because: masked() deeply couples with V.kernel.compute (indent/splice/writeline)
    # which requires the full inductor kernel context to execute
    src, tree = _load_mps_source()
    raw, node = _extract_function(src, tree, "MetalOverrides", "masked")
    assert raw is not None, "Could not find MetalOverrides.masked method"

    import re

    # Strip comments to prevent gaming
    lines = [l for l in raw.splitlines() if not l.strip().startswith("#")]
    clean = "\n".join(lines)

    # Both the if-body and else-branch must have type casts
    cast_count = len(re.findall(r"static_cast<decltype", clean))
    assert cast_count >= 2, (
        f"masked() has {cast_count} static_cast<decltype(...) casts, expected >= 2 "
        f"(one for if-body assignment, one for else-branch)"
    )

    # Specifically verify the else-branch is cast (not just two casts in one branch)
    assert re.search(r"else.*static_cast<decltype", clean), (
        "masked() else-branch missing static_cast<decltype cast"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_value_to_metal_special_values():
    """value_to_metal() must preserve correct Metal representations for special values."""
    _, vtm = _build_where_callable()

    cases = [
        (0.0, "0.0"),
        (1.5, "1.5"),
        (math.inf, "HUGE_VALF"),
        (-math.inf, "-HUGE_VALF"),
        (math.nan, "NAN"),
        (True, "true"),
        (False, "false"),
        (42, "42"),
    ]
    for val, expected in cases:
        got = vtm(val)
        assert got == expected, (
            f"value_to_metal({val!r}) = {got!r}, expected {expected!r}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """masked() and where() must not be stubs."""
    src, tree = _load_mps_source()

    for method_name in ("masked", "where"):
        _, node = _extract_function(src, tree, "MetalOverrides", method_name)
        assert node is not None, f"MetalOverrides.{method_name} not found"

        # Check body isn't trivially empty
        body_stmts = [
            s
            for s in node.body
            if not isinstance(s, (ast.Pass, ast.Expr))
            or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
        ]
        assert len(body_stmts) >= 1, (
            f"MetalOverrides.{method_name} appears to be a stub"
        )

        # Check it's not just a raise
        if len(node.body) == 1 and isinstance(node.body[0], ast.Raise):
            raise AssertionError(
                f"MetalOverrides.{method_name} is just a raise statement"
            )
