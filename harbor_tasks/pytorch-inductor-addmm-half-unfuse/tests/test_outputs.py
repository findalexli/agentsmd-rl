"""
Task: pytorch-inductor-addmm-half-unfuse
Repo: pytorch/pytorch @ bac7b59c6fe3241bb6d6cca89cb4bf1da0662788
PR:   #177144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: torch is not installed in the test image (too heavy / needs GPU).
We extract unfuse_bias_add_to_pointwise via AST, exec it with lightweight
mocks, and observe whether replacement proceeds or is guarded.
"""

import ast
import sys
import textwrap
import types

POST_GRAD = "/workspace/torch/_inductor/fx_passes/post_grad.py"


# ---------------------------------------------------------------------------
# Shared mock infrastructure
# ---------------------------------------------------------------------------

class DType:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"torch.{self.name}"


def _make_torch_mock():
    m = types.ModuleType("torch")
    m.bfloat16 = DType("bfloat16")
    m.float16 = DType("float16")
    m.half = m.float16
    m.float32 = DType("float32")
    m.float64 = DType("float64")
    return m


TORCH_MOCK = _make_torch_mock()


class MockInp:
    def __init__(self, dtype):
        self.meta = {"val": type("Val", (), {"dtype": dtype})()}


class MockMatch:
    def __init__(self):
        self.replaced = False

    def replace_by_example(self, *args, **kwargs):
        self.replaced = True

    def __getattr__(self, name):
        return lambda *a, **k: None


def _extract_and_exec():
    """Extract unfuse_bias_add_to_pointwise from source, exec it, return callable.
    # AST-only because: torch (and full inductor) cannot be installed in test image
    """
    with open(POST_GRAD) as f:
        source = f.read()
    src_lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            func_src = textwrap.dedent("".join(src_lines[node.lineno - 1:node.end_lineno]))
            ns = {
                "torch": TORCH_MOCK,
                "Match": type("Match", (), {}),
                "V": type("V", (), {"ops": type("ops", (), {
                    "__getattr__": lambda self, n: lambda *a, **k: None,
                })()})(),
                "__builtins__": __builtins__,
            }
            exec(func_src, ns)
            return ns["unfuse_bias_add_to_pointwise"]

    raise AssertionError("unfuse_bias_add_to_pointwise not found in source")


def _call_with_dtype(fn, dtype):
    """Call the extracted function with a mock inp of the given dtype.
    Returns True if replacement was attempted, False otherwise."""
    match = MockMatch()
    try:
        fn(match, None, None, inp=MockInp(dtype), alpha=1, beta=1)
    except Exception:
        pass  # crash after guard is OK if replace wasn't called
    return match.replaced


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """post_grad.py must parse without errors."""
    with open(POST_GRAD) as f:
        ast.parse(f.read())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bfloat16_not_unfused():
    """bfloat16 addmm must NOT be unfused (guard prevents replacement)."""
    fn = _extract_and_exec()
    replaced = _call_with_dtype(fn, TORCH_MOCK.bfloat16)
    assert not replaced, "bfloat16 was not guarded — replacement proceeded"


# [pr_diff] fail_to_pass
def test_float16_not_unfused():
    """float16 addmm must NOT be unfused (guard prevents replacement)."""
    fn = _extract_and_exec()
    replaced = _call_with_dtype(fn, TORCH_MOCK.float16)
    assert not replaced, "float16 was not guarded — replacement proceeded"


# [pr_diff] fail_to_pass
def test_guard_returns_early():
    """Guard must return early before any replacement logic runs for half dtypes.
    Tests both dtypes to ensure the guard is comprehensive, not dtype-specific."""
    fn = _extract_and_exec()
    # Both half dtypes must be guarded
    for dtype in [TORCH_MOCK.bfloat16, TORCH_MOCK.float16]:
        match = MockMatch()
        result = fn(match, None, None, inp=MockInp(dtype), alpha=1, beta=1)
        assert not match.replaced, f"{dtype} was not guarded"
        # Early return means result is None (implicit return)
        assert result is None, f"Expected None return for {dtype}, got {result}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_float32_still_unfused():
    """float32 addmm MUST still be unfused (guard must not be overbroad)."""
    fn = _extract_and_exec()
    replaced = _call_with_dtype(fn, TORCH_MOCK.float32)
    assert replaced, "float32 was incorrectly guarded — replacement did NOT proceed"


# [pr_diff] pass_to_pass
def test_float64_still_unfused():
    """float64 addmm MUST still be unfused (guard must not be overbroad)."""
    fn = _extract_and_exec()
    replaced = _call_with_dtype(fn, TORCH_MOCK.float64)
    assert replaced, "float64 was incorrectly guarded — replacement did NOT proceed"


# [static] pass_to_pass
def test_not_stub():
    """unfuse_bias_add_to_pointwise must have real logic (>= 3 top-level statements)."""
    # AST-only because: need to inspect function structure without executing
    with open(POST_GRAD) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            count = len(node.body)
            assert count >= 3, f"Only {count} top-level statements — likely a stub"
            return
    raise AssertionError("unfuse_bias_add_to_pointwise not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from agent config files
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:51 @ bac7b59c6fe3241bb6d6cca89cb4bf1da0662788
def test_no_trivial_single_use_helpers():
    """No trivial (1-2 LOC) helper functions introduced that are only used once.
    Rule: 'Don't make trivial (1-2 LOC) helper functions that are only used once
    unless it significantly improves code readability.'"""
    # AST-only because: structural check for function definitions
    with open(POST_GRAD) as f:
        source = f.read()
    tree = ast.parse(source)

    # Find unfuse_bias_add_to_pointwise and check for tiny nested functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            nested_fns = [n for n in ast.walk(node)
                          if isinstance(n, ast.FunctionDef) and n.name != "unfuse_bias_add_to_pointwise"]
            for fn_node in nested_fns:
                body_stmts = [s for s in fn_node.body
                              if not isinstance(s, (ast.Pass, ast.Expr))
                              or (isinstance(s, ast.Expr) and not isinstance(s.value, ast.Constant))]
                # "repl" is the existing replacement function — allow it
                if fn_node.name == "repl":
                    continue
                # Any other trivial nested helper with <= 2 statements is suspicious
                if len(body_stmts) <= 2:
                    # Count usages of this helper within the parent function
                    usages = sum(1 for n2 in ast.walk(node)
                                 if isinstance(n2, ast.Call)
                                 and isinstance(getattr(n2, 'func', None), ast.Name)
                                 and n2.func.id == fn_node.name)
                    assert usages > 1, (
                        f"Trivial helper '{fn_node.name}' ({len(body_stmts)} stmts) "
                        f"is only used {usages} time(s)"
                    )
            return
    raise AssertionError("unfuse_bias_add_to_pointwise not found")


# [agent_config] pass_to_pass — .claude/skills/pr-review/bc-guidelines.md:46-48 @ bac7b59c6fe3241bb6d6cca89cb4bf1da0662788
def test_python310_compat():
    """Modified function must be Python 3.10 compatible (no match/case, no ExceptionGroup).
    Rule: 'all the code must be compatible with 3.10'"""
    # AST-only because: structural syntax check
    with open(POST_GRAD) as f:
        source = f.read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
            for child in ast.walk(node):
                # match/case is ast.Match (Python 3.10 added it but we check for it
                # being used inappropriately — actually match IS 3.10, so this checks 3.9 compat)
                # ExceptionGroup syntax (except*) is 3.11+
                if hasattr(ast, 'TryStar') and isinstance(child, ast.TryStar):
                    raise AssertionError("except* (ExceptionGroup) syntax requires Python 3.11+")
            return
    raise AssertionError("unfuse_bias_add_to_pointwise not found")
