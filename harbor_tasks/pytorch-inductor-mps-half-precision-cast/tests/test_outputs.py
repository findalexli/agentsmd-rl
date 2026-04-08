"""
Task: pytorch-inductor-mps-half-precision-cast
Repo: pytorch/pytorch @ 036b25f5a29dc58cbc62e7b976efb860ff128c3f
PR:   #176436

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO = "/repo"
MPS_FILE = str(Path(REPO) / "torch/_inductor/codegen/mps.py")


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo context."""
    env = os.environ.copy()
    env["PYTHONPATH"] = REPO
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO, env=env,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """mps.py must parse without syntax errors."""
    r = _run_python(f"import ast; ast.parse(open('{MPS_FILE}').read()); print('OK')")
    assert r.returncode == 0, f"Syntax error: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_where_casts_false_branch():
    """where() must cast the false-branch value to match the true-branch type."""
    r = _run_python(r"""
import ast, math, textwrap

src = open("/repo/torch/_inductor/codegen/mps.py").read()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

# Extract value_to_metal
vtm_src = None
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "value_to_metal":
        vtm_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        break
assert vtm_src, "value_to_metal not found"

# Extract where() from MetalOverrides
where_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MetalOverrides":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "where":
                raw = "".join(lines[item.lineno - 1 : item.end_lineno])
                where_lines = [
                    l for l in textwrap.dedent(raw).splitlines(keepends=True)
                    if not l.strip().startswith("@")
                ]
                where_src = "".join(where_lines)
                break
assert where_src, "MetalOverrides.where not found"

# Build callable
class MockTorch:
    inf = math.inf

class CSEVariable(str):
    pass

ns = {
    "math": math, "torch": MockTorch(), "CSEVariable": CSEVariable,
    "OpVarT": object, "__builtins__": __builtins__,
}
future = "from __future__ import annotations\n"
exec(compile(future + vtm_src, "<vtm>", "exec"), ns)
exec(compile(future + where_src, "<where>", "exec"), ns)
where_fn = ns["where"]

# The false-branch value must be wrapped in static_cast<decltype(true_var)>
for true_var, false_val in [("var_bf16", 0.0), ("out_half", 1.5), ("tmp_f16", -1.0)]:
    result = where_fn("cond", true_var, false_val)
    assert f"decltype({true_var})" in result, (
        f"where('cond', '{true_var}', {false_val}) = {result!r} "
        f"— missing decltype({true_var})"
    )
    assert "static_cast" in result, (
        f"where() output {result!r} missing static_cast"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_where_casts_special_values():
    """where() must cast special float values (inf, -inf, nan) with type cast."""
    r = _run_python(r"""
import ast, math, textwrap

src = open("/repo/torch/_inductor/codegen/mps.py").read()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

vtm_src = None
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "value_to_metal":
        vtm_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        break

where_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MetalOverrides":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "where":
                raw = "".join(lines[item.lineno - 1 : item.end_lineno])
                where_lines = [
                    l for l in textwrap.dedent(raw).splitlines(keepends=True)
                    if not l.strip().startswith("@")
                ]
                where_src = "".join(where_lines)
                break

class MockTorch:
    inf = math.inf

class CSEVariable(str):
    pass

ns = {
    "math": math, "torch": MockTorch(), "CSEVariable": CSEVariable,
    "OpVarT": object, "__builtins__": __builtins__,
}
future = "from __future__ import annotations\n"
exec(compile(future + vtm_src, "<vtm>", "exec"), ns)
exec(compile(future + where_src, "<where>", "exec"), ns)
where_fn = ns["where"]

for val, metal_repr in [(math.inf, "HUGE_VALF"), (-math.inf, "-HUGE_VALF"), (math.nan, "NAN")]:
    result = where_fn("mask", "x", val)
    assert metal_repr in result, (
        f"where('mask', 'x', {val}) = {result!r} — missing {metal_repr}"
    )
    assert "decltype" in result, (
        f"Special value not cast: {result!r}"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_masked_casts_both_branches():
    """masked() must add static_cast<decltype(...)> to both if-body and else-branch."""
    r = _run_python(r"""
import ast, re

src = open("/repo/torch/_inductor/codegen/mps.py").read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MetalOverrides":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "masked":
                raw_lines = src.splitlines()[item.lineno - 1 : item.end_lineno]
                clean_lines = [l for l in raw_lines if not l.strip().startswith("#")]
                clean = "\n".join(clean_lines)

                # Both branches must have type casts
                cast_count = len(re.findall(r"static_cast<decltype", clean))
                assert cast_count >= 2, (
                    f"masked() has {cast_count} static_cast<decltype casts, expected >= 2"
                )

                # Verify else-branch specifically has cast
                assert re.search(r"else.*static_cast<decltype", clean), (
                    "masked() else-branch missing static_cast<decltype cast"
                )
                print("PASS")
                break
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_value_to_metal_special_values():
    """value_to_metal() must preserve correct Metal representations for special values."""
    r = _run_python(r"""
import ast, math, textwrap

src = open("/repo/torch/_inductor/codegen/mps.py").read()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

vtm_src = None
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "value_to_metal":
        vtm_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        break

class MockTorch:
    inf = math.inf

ns = {"math": math, "torch": MockTorch(), "__builtins__": __builtins__}
future = "from __future__ import annotations\n"
exec(compile(future + vtm_src, "<vtm>", "exec"), ns)
vtm = ns["value_to_metal"]

cases = [
    (0.0, "0.0"), (1.5, "1.5"), (math.inf, "HUGE_VALF"),
    (-math.inf, "-HUGE_VALF"), (math.nan, "NAN"),
    (True, "true"), (False, "false"), (42, "42"),
]
for val, expected in cases:
    got = vtm(val)
    assert got == expected, f"value_to_metal({val!r}) = {got!r}, expected {expected!r}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """masked() and where() must not be stubs."""
    r = _run_python(r"""
import ast

src = open("/repo/torch/_inductor/codegen/mps.py").read()
tree = ast.parse(src)

for method_name in ("masked", "where"):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MetalOverrides":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    body_stmts = [
                        s for s in item.body
                        if not isinstance(s, (ast.Pass, ast.Expr))
                        or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                    ]
                    assert len(body_stmts) >= 1, (
                        f"MetalOverrides.{method_name} appears to be a stub"
                    )
                    if len(item.body) == 1 and isinstance(item.body[0], ast.Raise):
                        raise AssertionError(
                            f"MetalOverrides.{method_name} is just a raise statement"
                        )
                    break
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
