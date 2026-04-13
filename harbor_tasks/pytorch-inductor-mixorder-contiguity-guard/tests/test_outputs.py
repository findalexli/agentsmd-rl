"""
Task: pytorch-inductor-mixorder-contiguity-guard
Repo: pytorch/pytorch @ 63fcbe1040ffef63e82abd4e66da1d7554d23aa4
PR:   #176131

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
import typing
from pathlib import Path

SCHEDULER = "/workspace/torch/_inductor/scheduler.py"
REPO = "/workspace"


# ---------------------------------------------------------------------------
# In-process helpers (for pass_to_pass / agent_config tests)
# AST-only because: torch/_inductor requires full torch install + GPU runtime
# ---------------------------------------------------------------------------

def _extract_method(cls_name: str, method_name: str) -> str | None:
    """Extract a method's source from scheduler.py by class and method name."""
    source = Path(SCHEDULER).read_text()
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
    return None


class _OrderedSet(set):
    def union(self, *others):
        out = _OrderedSet(self)
        for o in others:
            out.update(o)
        return out


class _MockNode:
    def __init__(self, contiguous, is_red=False, ancestors=None, names=None):
        self._contiguous = contiguous
        self._is_red = is_red
        self.ancestors = _OrderedSet(ancestors or [])
        self._names = _OrderedSet(names or [])

    def is_reduction(self):
        return self._is_red

    def get_operation_names(self):
        return self._names


class _MixOrderReduction:
    @classmethod
    def is_contiguous_node(cls, node):
        return getattr(node, "_contiguous", False)


class _FusedMixOrderReductions:
    pass


class _MockScheduler:
    def __init__(self, can_fuse_result=True, score=999999):
        self._can_fuse_result = can_fuse_result
        self._score = score

    def can_fuse(self, n1, n2, allow_mix_order_reduction=False):
        return self._can_fuse_result

    def score_fusion_memory(self, n1, n2, count_bytes=False):
        return self._score


class _MockSelf:
    def __init__(self, can_fuse_result=True, score=999999, numel=100):
        self.scheduler = _MockScheduler(can_fuse_result, score)
        self.numel = numel


def _compile_sub_node_can_fuse():
    """Extract and compile sub_node_can_fuse, returning the callable."""
    func_src = _extract_method("FusedMixOrderReductions", "sub_node_can_fuse")
    assert func_src is not None, "sub_node_can_fuse not found in FusedMixOrderReductions"
    ns = {
        "MixOrderReduction": _MixOrderReduction,
        "FusedMixOrderReductions": _FusedMixOrderReductions,
        "OrderedSet": _OrderedSet,
        "typing": typing,
        "__builtins__": __builtins__,
    }
    exec("from __future__ import annotations\n" + func_src, ns)
    return ns["sub_node_can_fuse"]


# ---------------------------------------------------------------------------
# Subprocess helper for fail_to_pass tests
# ---------------------------------------------------------------------------

# Mock infrastructure reproduced for subprocess isolation.
# torch/_inductor requires full torch install + GPU, so we extract the method
# via AST and execute it against lightweight mocks in a subprocess.
_SUBPROCESS_PREAMBLE = '''\
import ast, textwrap, typing, sys

SCHEDULER = "/workspace/torch/_inductor/scheduler.py"

def _extract_method(cls_name, method_name):
    source = open(SCHEDULER).read()
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return textwrap.dedent("".join(lines[item.lineno - 1 : item.end_lineno]))
    return None

class _OrderedSet(set):
    def union(self, *others):
        out = _OrderedSet(self)
        for o in others:
            out.update(o)
        return out

class _MockNode:
    def __init__(self, contiguous, is_red=False, ancestors=None, names=None):
        self._contiguous = contiguous
        self._is_red = is_red
        self.ancestors = _OrderedSet(ancestors or [])
        self._names = _OrderedSet(names or [])
    def is_reduction(self):
        return self._is_red
    def get_operation_names(self):
        return self._names

class _MixOrderReduction:
    @classmethod
    def is_contiguous_node(cls, node):
        return getattr(node, "_contiguous", False)

class _FusedMixOrderReductions:
    pass

class _MockScheduler:
    def __init__(self, can_fuse_result=True, score=999999):
        self._can_fuse_result = can_fuse_result
        self._score = score
    def can_fuse(self, n1, n2, allow_mix_order_reduction=False):
        return self._can_fuse_result
    def score_fusion_memory(self, n1, n2, count_bytes=False):
        return self._score

class _MockSelf:
    def __init__(self, can_fuse_result=True, score=999999, numel=100):
        self.scheduler = _MockScheduler(can_fuse_result, score)
        self.numel = numel

def _compile():
    func_src = _extract_method("FusedMixOrderReductions", "sub_node_can_fuse")
    assert func_src is not None, "sub_node_can_fuse not found in FusedMixOrderReductions"
    ns = {
        "MixOrderReduction": _MixOrderReduction,
        "FusedMixOrderReductions": _FusedMixOrderReductions,
        "OrderedSet": _OrderedSet,
        "typing": typing,
        "__builtins__": __builtins__,
    }
    exec("from __future__ import annotations\\n" + func_src, ns)
    return ns["sub_node_can_fuse"]
'''


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run Python code in a subprocess with the shared mock infrastructure."""
    full_code = _SUBPROCESS_PREAMBLE + "\n" + code
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(full_code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """scheduler.py must be valid Python."""
    import py_compile
    py_compile.compile(SCHEDULER, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_contiguity_guard_rejects_noncontiguous_pointwise():
    """sub_node_can_fuse must reject fusion when node1 is contiguous but node2 is non-contiguous pointwise."""
    r = _run_py('''\
func = _compile()
for score, numel in [(999999, 100), (1, 50000), (500, 1)]:
    mock_self = _MockSelf(score=score, numel=numel)
    node1 = _MockNode(contiguous=True)
    node2 = _MockNode(contiguous=False, is_red=False)
    result = func(mock_self, node1, node2, ())
    assert result is False, (
        f"Expected False for contiguous + non-contiguous pointwise "
        f"(score={score}, numel={numel}), got {result!r}"
    )
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_contiguity_guard_rejects_noncontiguous_reduction():
    """sub_node_can_fuse must reject non-contiguous reduction when node1 is contiguous, regardless of score."""
    r = _run_py('''\
func = _compile()
for score, numel in [(999999, 100), (0, 1), (42, 99999)]:
    mock_self = _MockSelf(score=score, numel=numel)
    node1 = _MockNode(contiguous=True)
    node2 = _MockNode(contiguous=False, is_red=True)
    result = func(mock_self, node1, node2, ())
    assert result is False, (
        f"Expected False for contiguous + non-contiguous reduction "
        f"(score={numel}), got {result!r}"
    )
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_contiguity_guard_with_ancestors_and_other_nodes():
    """Guard must reject even when nodes have ancestors and other_nodes are present."""
    r = _run_py('''\
func = _compile()
mock_self = _MockSelf()
node1 = _MockNode(contiguous=True, ancestors=["op_x", "op_y"])
node2 = _MockNode(contiguous=False, is_red=False, ancestors=["op_z"])
other = _MockNode(contiguous=True, names=["op_unrelated"])
result = func(mock_self, node1, node2, (other,))
assert result is False, f"Expected False for contiguous + non-contiguous with ancestors, got {result!r}"
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests for valid fusions
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_both_contiguous_fusion_allowed():
    """Both contiguous nodes should be allowed to fuse (guard must not over-reject)."""
    func = _compile_sub_node_can_fuse()
    for is_red in [False, True]:
        mock_self = _MockSelf()
        node1 = _MockNode(contiguous=True)
        node2 = _MockNode(contiguous=True, is_red=is_red)
        result = func(mock_self, node1, node2, ())
        assert result, f"Expected truthy for contiguous + contiguous (is_red={is_red}), got {result!r}"


# [pr_diff] pass_to_pass
def test_noncontiguous_node1_contiguous_node2_allowed():
    """Non-contiguous node1 + contiguous node2 should still fuse."""
    func = _compile_sub_node_can_fuse()
    for is_red in [False, True]:
        mock_self = _MockSelf()
        node1 = _MockNode(contiguous=False)
        node2 = _MockNode(contiguous=True, is_red=is_red)
        result = func(mock_self, node1, node2, ())
        assert result, f"Expected truthy for non-contiguous + contiguous (is_red={is_red}), got {result!r}"


# [pr_diff] pass_to_pass
def test_both_noncontiguous_allowed():
    """Both non-contiguous nodes should still be allowed (guard only fires when node1 IS contiguous)."""
    func = _compile_sub_node_can_fuse()
    mock_self = _MockSelf()
    node1 = _MockNode(contiguous=False)
    node2 = _MockNode(contiguous=False, is_red=False)
    result = func(mock_self, node1, node2, ())
    assert result, f"Expected truthy for non-contiguous + non-contiguous, got {result!r}"


# [pr_diff] pass_to_pass
def test_ancestor_cycle_still_rejected():
    """Ancestor/operation-name cycle detection must still work after contiguity guard."""
    func = _compile_sub_node_can_fuse()
    mock_self = _MockSelf()
    node1 = _MockNode(contiguous=True, ancestors=["op_a"])
    node2 = _MockNode(contiguous=True, is_red=False)
    other_node = _MockNode(contiguous=True, names=["op_a"])
    result = func(mock_self, node1, node2, (other_node,))
    assert result is False, f"Expected False due to ancestor cycle, got {result!r}"


# [pr_diff] pass_to_pass
def test_can_fuse_false_still_rejected():
    """When scheduler.can_fuse returns False, fusion is rejected regardless of contiguity."""
    func = _compile_sub_node_can_fuse()
    for c1, c2 in [(True, True), (True, False), (False, True), (False, False)]:
        mock_self = _MockSelf(can_fuse_result=False)
        node1 = _MockNode(contiguous=c1)
        node2 = _MockNode(contiguous=c2, is_red=False)
        result = func(mock_self, node1, node2, ())
        assert result is False, (
            f"Expected False when can_fuse=False (c1={c1}, c2={c2}), got {result!r}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural preservation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_sub_node_can_fuse_not_stub():
    """sub_node_can_fuse must have real logic (>= 5 top-level statements)."""
    source = Path(SCHEDULER).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "sub_node_can_fuse":
                    assert len(item.body) >= 5, f"sub_node_can_fuse appears stubbed ({len(item.body)} stmts)"
                    return
    raise AssertionError("sub_node_can_fuse not found in FusedMixOrderReductions")


# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_fuse_with_method_preserved():
    """fuse_with method must still exist in FusedMixOrderReductions."""
    source = Path(SCHEDULER).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
            methods = [i.name for i in node.body if isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef))]
            assert "fuse_with" in methods, f"fuse_with missing; found: {methods}"
            return
    raise AssertionError("FusedMixOrderReductions class not found")


# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_init_contiguity_assertion_preserved():
    """FusedMixOrderReductions.__init__ must still assert contiguity invariant."""
    source = Path(SCHEDULER).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "FusedMixOrderReductions":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                    for sub in ast.walk(item):
                        if isinstance(sub, ast.Assert) and "is_contiguous_node" in ast.dump(sub):
                            return
    raise AssertionError("__init__ contiguity assertion missing or FusedMixOrderReductions not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax/AST checks (in-process file reads)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_repo_inductor_syntax():
    """All torch/_inductor/*.py files must have valid Python syntax (pass_to_pass)."""
    import py_compile
    inductor_dir = Path(REPO) / "torch" / "_inductor"
    py_files = list(inductor_dir.glob("*.py"))
    assert py_files, f"No Python files found in {inductor_dir}"
    for f in py_files:
        py_compile.compile(str(f), doraise=True)


# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_repo_scheduler_ast():
    """scheduler.py must have valid AST structure (pass_to_pass)."""
    source = Path(SCHEDULER).read_text()
    tree = ast.parse(source)  # noqa: F841 - validates parse succeeds


# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_repo_inductor_compileall():
    """All torch/_inductor/*.py files must compile without errors (pass_to_pass)."""
    import compileall
    inductor_dir = Path(REPO) / "torch" / "_inductor"
    result = compileall.compile_dir(str(inductor_dir), quiet=True)
    assert result, f"compileall failed for {inductor_dir}"


# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_repo_scheduler_structure():
    """scheduler.py must contain MixOrderReduction and FusedMixOrderReductions classes (pass_to_pass)."""
    source = Path(SCHEDULER).read_text()
    tree = ast.parse(source)

    found_classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [item.name for item in node.body
                      if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
            found_classes[node.name] = methods

    assert "MixOrderReduction" in found_classes, "MixOrderReduction class not found"
    assert "FusedMixOrderReductions" in found_classes, "FusedMixOrderReductions class not found"
    assert "sub_node_can_fuse" in found_classes.get("FusedMixOrderReductions", []), \
        "sub_node_can_fuse method not found in FusedMixOrderReductions"


# [static] pass_to_pass
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_repo_torch_package_syntax():
    """All torch/*.py files must have valid Python syntax (pass_to_pass)."""
    import py_compile
    torch_dir = Path(REPO) / "torch"
    py_files = list(torch_dir.glob("*.py"))
    assert py_files, f"No Python files found in {torch_dir}"
    errors = []
    for f in py_files:
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{f.name}: {e}")
    assert not errors, f"Syntax errors found:\n" + "\n".join(errors)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks (actual subprocess commands)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
# CI: Python syntax check via subprocess for scheduler.py (from lint.yml quick-checks)
def test_repo_ci_scheduler_syntax():
    """scheduler.py must pass Python syntax check via subprocess (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "torch/_inductor/scheduler.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
# CI: Full compileall on torch/_inductor via subprocess (from Makefile/setup)
def test_repo_ci_inductor_compileall():
    """All torch/_inductor files must compile via compileall subprocess (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "compileall", "torch/_inductor/", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"compileall failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
# CI: CUDA kernel launch check (from lint.yml quick-checks job)
def test_repo_ci_kernel_launch_check():
    """CUDA kernel launch patterns must be valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "torch/testing/_internal/check_kernel_launches.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Kernel launch check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
# CI: ciflow labels validation (from lint.yml quick-checks job)
def test_repo_ci_ciflow_labels():
    """CI flow labels must be valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", ".github/scripts/collect_ciflow_labels.py", "--validate-tags"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ciflow labels validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
# CI: Related test file syntax check via subprocess
def test_repo_ci_mix_order_test_syntax():
    """test_mix_order_reduction.py must have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "test/inductor/test_mix_order_reduction.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test file syntax check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:53-56 @ 63fcbe1040ffef63e82abd4e66da1d7554d23aa4
# AST-only because: torch/_inductor requires full torch install + GPU runtime
def test_no_dynamic_setattr_in_fix():
    """Fix must not use dynamic setattr/getattr (CLAUDE.md: explicit state management)."""
    func_src = _extract_method("FusedMixOrderReductions", "sub_node_can_fuse")
    assert func_src is not None
    tree = ast.parse(func_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in ("setattr", "getattr"), (
                f"sub_node_can_fuse uses dynamic {node.func.id}; "
                "CLAUDE.md requires explicit state management"
            )
