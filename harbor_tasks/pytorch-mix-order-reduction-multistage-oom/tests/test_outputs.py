"""
Task: pytorch-mix-order-reduction-multistage-oom
Repo: pytorch/pytorch @ 5d919bfe0f2ba7c7aabdb75ef6a20512f163e662
PR:   176495

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"
CONFIG_PY = f"{REPO}/torch/_inductor/config.py"
CODEGEN_TRITON = f"{REPO}/torch/_inductor/codegen/triton.py"
HEURISTICS_PY = f"{REPO}/torch/_inductor/runtime/triton_heuristics.py"
ATTR = "mix_order_reduction_allow_multi_stages"
ENV_VAR = "TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES"


def _run_python(code: str, timeout: int = 30, env_extra=None):
    """Execute Python code in a subprocess via temp file."""
    env = os.environ.copy()
    env.pop(ENV_VAR, None)
    if env_extra:
        env.update(env_extra)
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO, env=env,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified files (config.py, codegen/triton.py, triton_heuristics.py) parse without errors."""
    for path in [CONFIG_PY, CODEGEN_TRITON, HEURISTICS_PY]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_config_default_false():
    """New config attribute mix_order_reduction_allow_multi_stages defaults to False."""
    r = _run_python(r"""
import ast, os, types
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/config.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
        continue
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target_name, value_node = stmt.target.id, stmt.value
        elif isinstance(stmt, ast.Assign) and stmt.targets and isinstance(stmt.targets[0], ast.Name):
            target_name, value_node = stmt.targets[0].id, stmt.value
        else:
            continue
        if target_name != ATTR or value_node is None:
            continue
        expr_src = ast.get_source_segment(source, value_node)
        if not expr_src:
            continue
        fake_os = types.ModuleType("os")
        fake_os.environ = os.environ.copy()
        ns = {"os": fake_os, "__builtins__": __builtins__}
        result = eval(expr_src, ns)
        assert result is False, f"Expected False, got {result!r}"
        print("PASS")
        break
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_config_env_var_enables():
    """Setting TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES=1 enables multi-stages."""
    r_on = _run_python(r"""
import ast, os, types
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/config.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
        continue
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target_name, value_node = stmt.target.id, stmt.value
        elif isinstance(stmt, ast.Assign) and stmt.targets and isinstance(stmt.targets[0], ast.Name):
            target_name, value_node = stmt.targets[0].id, stmt.value
        else:
            continue
        if target_name != ATTR or value_node is None:
            continue
        expr_src = ast.get_source_segment(source, value_node)
        if not expr_src:
            continue
        fake_os = types.ModuleType("os")
        fake_os.environ = os.environ.copy()
        ns = {"os": fake_os, "__builtins__": __builtins__}
        result = eval(expr_src, ns)
        assert result is True, f"Expected True with env=1, got {result!r}"
        print("PASS")
        break
""", env_extra={ENV_VAR: "1"})
    assert r_on.returncode == 0, f"Failed (env=1): {r_on.stderr}"
    assert "PASS" in r_on.stdout

    r_off = _run_python(r"""
import ast, os, types
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/config.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
        continue
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target_name, value_node = stmt.target.id, stmt.value
        elif isinstance(stmt, ast.Assign) and stmt.targets and isinstance(stmt.targets[0], ast.Name):
            target_name, value_node = stmt.targets[0].id, stmt.value
        else:
            continue
        if target_name != ATTR or value_node is None:
            continue
        expr_src = ast.get_source_segment(source, value_node)
        if not expr_src:
            continue
        fake_os = types.ModuleType("os")
        fake_os.environ = os.environ.copy()
        ns = {"os": fake_os, "__builtins__": __builtins__}
        result = eval(expr_src, ns)
        assert result is False, f"Expected False with env=0, got {result!r}"
        print("PASS")
        break
""", env_extra={ENV_VAR: "0"})
    assert r_off.returncode == 0, f"Failed (env=0): {r_off.stderr}"
    assert "PASS" in r_off.stdout


# [pr_diff] fail_to_pass
def test_heuristics_single_stage_when_disabled():
    """persistent_reduction sets MAX_NUM_STAGES=1 when multi-stages disabled, regardless of rnumel."""
    r = _run_python(r"""
import ast, textwrap
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/runtime/triton_heuristics.py").read_text()
tree = ast.parse(source)

for func_node in ast.walk(tree):
    if not (isinstance(func_node, ast.FunctionDef) and func_node.name == "persistent_reduction"):
        continue
    for child in ast.walk(func_node):
        if not isinstance(child, ast.If):
            continue
        test_src = ast.get_source_segment(source, child.test)
        if not (test_src and ATTR in test_src):
            continue
        block_lines = source.splitlines()[child.lineno - 1 : child.end_lineno]
        if_src = textwrap.dedent("\n".join(block_lines))
        for rnumel in [512, 4096, 8192, 10000, 65536]:
            ns = {
                "inductor_meta": {ATTR: False},
                "rnumel_hint": rnumel,
                "num_iters": 8,
                "__builtins__": __builtins__,
            }
            exec(if_src, ns)
            max_stages = ns.get("MAX_NUM_STAGES")
            assert max_stages == 1, (
                f"MAX_NUM_STAGES should be 1 when disabled (rnumel={rnumel}), got {max_stages}"
            )
        print("PASS")
        break
    break
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_heuristics_single_stage_small_rnumel():
    """persistent_reduction sets MAX_NUM_STAGES=1 with small rnumel when disabled."""
    r = _run_python(r"""
import ast, textwrap
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/runtime/triton_heuristics.py").read_text()
tree = ast.parse(source)

for func_node in ast.walk(tree):
    if not (isinstance(func_node, ast.FunctionDef) and func_node.name == "persistent_reduction"):
        continue
    for child in ast.walk(func_node):
        if not isinstance(child, ast.If):
            continue
        test_src = ast.get_source_segment(source, child.test)
        if not (test_src and ATTR in test_src):
            continue
        block_lines = source.splitlines()[child.lineno - 1 : child.end_lineno]
        if_src = textwrap.dedent("\n".join(block_lines))
        for rnumel in [128, 256, 512, 1024]:
            ns = {
                "inductor_meta": {ATTR: False},
                "rnumel_hint": rnumel,
                "num_iters": 8,
                "__builtins__": __builtins__,
            }
            exec(if_src, ns)
            max_stages = ns.get("MAX_NUM_STAGES")
            assert max_stages == 1, (
                f"MAX_NUM_STAGES should be 1 when disabled (small rnumel={rnumel}), got {max_stages}"
            )
        print("PASS")
        break
    break
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_heuristics_multi_stage_when_enabled():
    """persistent_reduction allows >1 stages when multi-stages enabled."""
    r = _run_python(r"""
import ast, textwrap
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/runtime/triton_heuristics.py").read_text()
tree = ast.parse(source)

for func_node in ast.walk(tree):
    if not (isinstance(func_node, ast.FunctionDef) and func_node.name == "persistent_reduction"):
        continue
    for child in ast.walk(func_node):
        if not isinstance(child, ast.If):
            continue
        test_src = ast.get_source_segment(source, child.test)
        if not (test_src and ATTR in test_src):
            continue
        block_lines = source.splitlines()[child.lineno - 1 : child.end_lineno]
        if_src = textwrap.dedent("\n".join(block_lines))
        for rnumel in [1024, 4096, 8192]:
            ns = {
                "inductor_meta": {ATTR: True},
                "rnumel_hint": rnumel,
                "num_iters": 16,
                "__builtins__": __builtins__,
            }
            exec(if_src, ns)
            max_stages = ns.get("MAX_NUM_STAGES")
            assert max_stages == 3, (
                f"MAX_NUM_STAGES should be 3 for rnumel={rnumel} when enabled, got {max_stages}"
            )
        print("PASS")
        break
    break
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_heuristics_large_rnumel_caps_at_two():
    """When enabled with large rnumel (>8192), MAX_NUM_STAGES caps at 2."""
    r = _run_python(r"""
import ast, textwrap
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/runtime/triton_heuristics.py").read_text()
tree = ast.parse(source)

for func_node in ast.walk(tree):
    if not (isinstance(func_node, ast.FunctionDef) and func_node.name == "persistent_reduction"):
        continue
    for child in ast.walk(func_node):
        if not isinstance(child, ast.If):
            continue
        test_src = ast.get_source_segment(source, child.test)
        if not (test_src and ATTR in test_src):
            continue
        block_lines = source.splitlines()[child.lineno - 1 : child.end_lineno]
        if_src = textwrap.dedent("\n".join(block_lines))
        for rnumel in [8193, 16384, 65536]:
            ns = {
                "inductor_meta": {ATTR: True},
                "rnumel_hint": rnumel,
                "num_iters": 16,
                "__builtins__": __builtins__,
            }
            exec(if_src, ns)
            max_stages = ns.get("MAX_NUM_STAGES")
            assert max_stages == 2, (
                f"MAX_NUM_STAGES should be 2 for rnumel={rnumel} when enabled, got {max_stages}"
            )
        print("PASS")
        break
    break
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_codegen_propagates_config_key():
    """inductor_meta_common includes mix_order_reduction_allow_multi_stages as a dict key."""
    r = _run_python(r"""
import ast
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/codegen/triton.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "inductor_meta_common":
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and child.value == ATTR:
                print("PASS")
                break
        else:
            raise AssertionError(f"inductor_meta_common does not include {ATTR!r} as a string key")
        break
else:
    raise AssertionError("inductor_meta_common function not found in codegen/triton.py")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Modified files compile without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", CONFIG_PY, CODEGEN_TRITON, HEURISTICS_PY],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compilation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_config_imports():
    """Config module loads basic dependencies without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import sys; sys.path.insert(0, '/workspace/pytorch'); "
         "import ast; from pathlib import Path; "
         "src = Path('torch/_inductor/config.py').read_text(); "
         "tree = ast.parse(src); "
         "print('config.py parsed successfully')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Config import test failed:\n{r.stderr[-500:]}"
    assert "config.py parsed successfully" in r.stdout, "Config parsing did not complete"


# [static] pass_to_pass
def test_existing_configs_intact():
    """Existing mix_order_reduction config attributes still present."""
    source = Path(CONFIG_PY).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
            continue
        attr_names = set()
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                attr_names.add(stmt.target.id)
            elif isinstance(stmt, ast.Assign):
                for t in stmt.targets:
                    if isinstance(t, ast.Name):
                        attr_names.add(t.id)
        for attr in [
            "mix_order_reduction",
            "mix_order_reduction_autotune_split_size",
            "mix_order_reduction_non_strict_mode",
        ]:
            assert attr in attr_names, f"Existing config attribute {attr!r} is missing from triton class"
        return
    raise AssertionError("triton class not found in config.py")


# [static] pass_to_pass
def test_config_not_hardcoded_false():
    """Config reads env var, not a trivial hardcoded False."""
    r_off = _run_python(r"""
import ast, os, types
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/config.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
        continue
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target_name, value_node = stmt.target.id, stmt.value
        elif isinstance(stmt, ast.Assign) and stmt.targets and isinstance(stmt.targets[0], ast.Name):
            target_name, value_node = stmt.targets[0].id, stmt.value
        else:
            continue
        if target_name != ATTR or value_node is None:
            continue
        expr_src = ast.get_source_segment(source, value_node)
        if not expr_src:
            continue
        fake_os = types.ModuleType("os")
        fake_os.environ = os.environ.copy()
        ns = {"os": fake_os, "__builtins__": __builtins__}
        print(eval(expr_src, ns))
        break
""")
    r_on = _run_python(r"""
import ast, os, types
from pathlib import Path

ATTR = "mix_order_reduction_allow_multi_stages"
source = Path("torch/_inductor/config.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if not (isinstance(node, ast.ClassDef) and node.name == "triton"):
        continue
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target_name, value_node = stmt.target.id, stmt.value
        elif isinstance(stmt, ast.Assign) and stmt.targets and isinstance(stmt.targets[0], ast.Name):
            target_name, value_node = stmt.targets[0].id, stmt.value
        else:
            continue
        if target_name != ATTR or value_node is None:
            continue
        expr_src = ast.get_source_segment(source, value_node)
        if not expr_src:
            continue
        fake_os = types.ModuleType("os")
        fake_os.environ = os.environ.copy()
        fake_os.environ["TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES"] = "1"
        ns = {"os": fake_os, "__builtins__": __builtins__}
        print(eval(expr_src, ns))
        break
""", env_extra={ENV_VAR: "1"})
    assert r_off.returncode == 0 and r_on.returncode == 0, f"Failed: off={r_off.stderr} on={r_on.stderr}"
    assert r_off.stdout.strip() != r_on.stdout.strip(), (
        f"Config should toggle with {ENV_VAR}, but got off={r_off.stdout.strip()!r} on={r_on.stdout.strip()!r}"
    )
