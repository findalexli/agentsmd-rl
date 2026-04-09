"""
Task: areal-fsdp-pipeline-weight-sync
Repo: inclusionAI/AReaL @ 61281ba8851e6d1cf8c30794a5391359b4e324b7

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests use subprocess.run() to execute Python code that verifies the
pipelining refactor. The code under test requires NCCL multi-rank runtime,
so behavioral tests exec extracted class definitions and compile the module
rather than importing it directly.
"""

import subprocess
from pathlib import Path

REPO = "/repo"
FILE = Path(f"{REPO}/areal/engine/fsdp_engine.py")


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """fsdp_engine.py must compile as valid Python."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(FILE)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Compile failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linting passes on areal/engine/ (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "areal/engine/fsdp_engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff formatting passes on areal/engine/fsdp_engine.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "format", "--check", "areal/engine/fsdp_engine.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ast_parse():
    """Repo's fsdp_engine.py parses as valid AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import ast; ast.parse(open('areal/engine/fsdp_engine.py').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_pipelined_main_loop():
    """Main update loop overlaps bucket broadcast with next bucket preparation.

    Verifies the deferred-wait pattern: a variable is assigned from an async
    dispatch method AND read back within the same loop (draining the previous
    bucket while preparing the next). Also checks try/finally for error safety
    and anti-stub minimum complexity.
    """
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_update_weights_from_distributed':
                # Must have try/finally
                tries = [n for n in ast.walk(item) if isinstance(n, ast.Try) and n.finalbody]
                assert tries, "No try/finally in main method"

                # Finally must have real drain logic (not just pass)
                for t in tries:
                    drain_calls = [
                        s for s in ast.walk(ast.Module(body=t.finalbody, type_ignores=[]))
                        if isinstance(s, ast.Call)
                    ]
                    assert drain_calls, "Finally block has no calls - drain is empty"

                # Must have for loop with deferred-wait pattern
                for_loops = [n for n in ast.walk(item) if isinstance(n, ast.For)]
                assert for_loops, "No for loop - not iterating over buckets"
                main_for = for_loops[0]

                # Pipeline: a variable assigned from self.method() AND read in same loop
                assigns = set()
                for stmt in ast.walk(main_for):
                    if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                        if isinstance(stmt.value.func, ast.Attribute):
                            if isinstance(stmt.value.func.value, ast.Name) and stmt.value.func.value.id == "self":
                                for tgt in stmt.targets:
                                    if isinstance(tgt, ast.Name):
                                        assigns.add(tgt.id)

                reads = {
                    n.id for n in ast.walk(main_for)
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in assigns
                }
                assert reads, "No deferred-wait pattern: variable dispatched but never read in loop"

                # Anti-stub: method must be substantial
                meaningful = sum(
                    1 for n in ast.walk(item)
                    if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.With, ast.Try, ast.Return, ast.Call))
                )
                assert meaningful >= 15, f"Method too simple ({meaningful} nodes) - likely stubbed"

                print("PASS")
                exit(0)

print("FAIL: _update_weights_from_distributed not found or missing pipeline pattern")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_async_bucket_method():
    """Async bucket broadcast method exists that returns pending state with real distributed logic.

    The method must have a 'stream' parameter, return a non-None value,
    and contain async_op broadcast calls.
    """
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            # Looking for the async variant (name contains 'async')
            if 'async' not in item.name.lower():
                continue
            if 'weight' not in item.name.lower() and 'bucket' not in item.name.lower():
                continue

            # Must have stream parameter
            all_args = item.args.args + item.args.kwonlyargs
            param_names = [a.arg for a in all_args]
            assert 'stream' in param_names, f"No 'stream' param in {item.name}: {param_names}"

            # Must return non-None
            returns = [
                n for n in ast.walk(item)
                if isinstance(n, ast.Return) and n.value is not None
                and not (isinstance(n.value, ast.Constant) and n.value.value is None)
            ]
            assert returns, f"{item.name} never returns a non-None value"

            # Must have distributed logic (async_op broadcasts)
            has_dist = any(
                isinstance(n, ast.keyword) and n.arg == 'async_op'
                for n in ast.walk(item)
            )
            assert has_dist, f"{item.name} has no async_op usage - missing distributed logic"

            # Anti-stub: must be substantial
            meaningful = sum(
                1 for n in ast.walk(item)
                if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.With, ast.Try, ast.Return, ast.Call))
            )
            assert meaningful >= 8, f"{item.name} too simple ({meaningful} nodes) - likely stubbed"

            print("PASS")
            exit(0)

print("FAIL: No async bucket broadcast method with distributed logic found")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_pending_state_dataclass():
    """Data structure with >=3 fields tracks in-flight broadcast state.

    Extracts the _PendingWeightUpdateBucket class from source, exec's it
    as a real dataclass, and instantiates it to verify it works as a
    concrete Python object.
    """
    r = _run_py("""
import ast, dataclasses
from typing import Any

source = open("areal/engine/fsdp_engine.py").read()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == '_PendingWeightUpdateBucket':
        found = True

        # Verify dataclass decorator
        has_dc = any(
            (isinstance(d, ast.Name) and 'dataclass' in d.id)
            or (isinstance(d, ast.Attribute) and d.attr == 'dataclass')
            for d in node.decorator_list
        )
        assert has_dc, "_PendingWeightUpdateBucket not decorated with @dataclass"

        # Extract field names from annotations
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.append(item.target.id)

        assert len(fields) >= 3, f"Only {len(fields)} fields: {fields}"

        # Behavioral: exec the dataclass source and instantiate a real object
        lines = source.splitlines()
        # Include decorator lines (they come before the class definition)
        start_line = node.lineno - 1
        while start_line > 0 and lines[start_line - 1].strip().startswith('@'):
            start_line -= 1
        class_src = '\\n'.join(lines[start_line : node.end_lineno])

        import torch
        from concurrent.futures import Future

        ns = {
            'dataclasses': dataclasses,
            'Any': Any,
            'torch': torch,
            'Future': Future,
            'list': list, 'tuple': tuple, 'str': str,
        }
        exec(class_src, ns)

        # Instantiate the real class - this exercises the actual dataclass code
        Cls = ns['_PendingWeightUpdateBucket']
        obj = Cls(handles=[], fut=Future(), named_tensors=[], stream=None)
        assert hasattr(obj, 'handles')
        assert hasattr(obj, 'fut')
        assert hasattr(obj, 'named_tensors')
        assert hasattr(obj, 'stream')
        assert dataclasses.is_dataclass(obj)

        print("PASS")
        break

if not found:
    print("FAIL: _PendingWeightUpdateBucket class not found in fsdp_engine.py")
    exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_error_safety_drain():
    """try/finally in main method drains pending broadcasts on error.

    The finally block must call a self._wait method on the pending bucket,
    ensuring broadcasts are drained even when exceptions occur.
    """
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_update_weights_from_distributed':
                for child in ast.walk(item):
                    if isinstance(child, ast.Try) and child.finalbody:
                        # Finally must call self._wait* on pending bucket
                        has_drain = any(
                            isinstance(s, ast.Call)
                            and isinstance(s.func, ast.Attribute)
                            and 'wait' in s.func.attr
                            for s in ast.walk(ast.Module(body=child.finalbody, type_ignores=[]))
                        )
                        if has_drain:
                            print("PASS")
                            exit(0)

print("FAIL: No error-safety drain (self._wait* in finally) in _update_weights_from_distributed")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_cuda_stream_usage():
    """CUDA stream used for broadcast overlap in weight update methods.

    The fix must create a torch.cuda.Stream() and use it when broadcasting
    bucket weights, enabling overlap of communication with computation.
    """
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        found_stream = False
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            for child in ast.walk(item):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr == 'Stream':
                        found_stream = True

        assert found_stream, "No torch.cuda.Stream() creation in FSDPEngine methods"
        print("PASS")
        exit(0)

print("FAIL: FSDPEngine class not found")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_sync_wrapper_preserved():
    """_update_bucket_weights_from_distributed still exists with a real body."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_update_bucket_weights_from_distributed':
                body = [s for s in item.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
                assert len(body) >= 2, f"Only {len(body)} statements - method appears stubbed"
                print("PASS")
                exit(0)

print("FAIL: _update_bucket_weights_from_distributed not found - backward compat broken")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_init_method_preserved():
    """_init_weight_update_from_distributed still present with real body."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_init_weight_update_from_distributed':
                meaningful = sum(
                    1 for n in ast.walk(item)
                    if isinstance(n, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.With, ast.Try, ast.Return, ast.Call))
                )
                assert meaningful >= 3, "Method appears stubbed"
                print("PASS")
                exit(0)

print("FAIL: _init_weight_update_from_distributed not found")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass
def test_no_wildcard_imports():
    """No wildcard imports (from x import *)."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())
wildcards = [
    (node.module, alias.name)
    for node in ast.walk(tree)
    if isinstance(node, ast.ImportFrom)
    for alias in node.names
    if alias.name == "*"
]
if wildcards:
    print(f"FAIL: Wildcard imports found: {wildcards}")
    exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] pass_to_pass
def test_broadcast_explicit_src():
    """All broadcast() calls specify src rank explicitly."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

found_any = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "broadcast":
        found_any = True
        kw_names = [kw.arg for kw in node.keywords]
        assert "src" in kw_names or len(node.args) >= 2, "broadcast() without explicit src"

if not found_any:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if "broadcast" in node.func.attr.lower():
                print("PASS")
                exit(0)
    print("FAIL: No broadcast calls found")
    exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] pass_to_pass
def test_no_print_calls():
    """No bare print() calls."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())
prints = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            prints.append(node.lineno)
if prints:
    print(f"FAIL: print() calls found at lines {prints}")
    exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] pass_to_pass
def test_no_module_level_process_groups():
    """No global process group creation at module level."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in tree.body:
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
    elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
        call = node.value
    else:
        continue
    func = call.func
    if isinstance(func, ast.Attribute) and func.attr in ("new_group", "init_process_group"):
        assert False, f"Module-level process group creation: {func.attr}() at line {node.lineno}"

print("PASS")
exit(0)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] pass_to_pass
def test_no_gpu_cpu_sync_in_weight_update():
    """No .item() or .tolist() in weight update methods (GPU-CPU sync in hot paths)."""
    r = _run_py("""
import ast

tree = ast.parse(open("areal/engine/fsdp_engine.py").read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FSDPEngine':
        violations = []
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if "update" not in item.name.lower() or "weight" not in item.name.lower():
                continue
            for child in ast.walk(item):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr in ("item", "tolist"):
                        violations.append(f"{item.name}:{child.lineno} .{child.func.attr}()")
        if violations:
            print(f"FAIL: GPU-CPU sync in weight update hot paths: {violations}")
            exit(1)
        print("PASS")
        exit(0)

print("FAIL: FSDPEngine not found")
exit(1)
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
