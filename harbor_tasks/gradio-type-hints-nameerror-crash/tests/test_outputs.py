"""
Task: gradio-type-hints-nameerror-crash
Repo: gradio-app/gradio @ c13daab68aa40cb58f2c643a650b5db48e986935
PR:   #13161

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys
from pathlib import Path

REPO = "/repo"

if REPO not in sys.path:
    sys.path.insert(0, REPO)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gradio/utils.py must parse without syntax errors."""
    import ast

    src = Path(f"{REPO}/gradio/utils.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nameerror_returns_empty_dict():
    """get_type_hints returns {} when annotation triggers NameError."""
    from gradio.utils import get_type_hints

    # Single unresolvable return annotation
    def func_with_bad_ref(x: str) -> "NonExistentType":
        return x

    # Dotted forward ref
    def another_bad_ref(a: "MissingModule.Cls", b: int) -> str:
        return str(b)

    # Multiple unresolvable annotations (params + return)
    def all_bad(a: "X", b: "Y") -> "Z":
        pass

    result1 = get_type_hints(func_with_bad_ref)
    assert result1 == {}, f"Expected empty dict, got {result1}"

    result2 = get_type_hints(another_bad_ref)
    assert result2 == {}, f"Expected empty dict, got {result2}"

    result3 = get_type_hints(all_bad)
    assert result3 == {}, f"Expected empty dict, got {result3}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_normal_function_hints():
    """get_type_hints returns correct hints for normally annotated functions."""
    from gradio.utils import get_type_hints

    def fn_a(x: str, y: int) -> float:
        return float(x) + y

    def fn_b(name: bytes) -> list:
        return [name]

    hints_a = get_type_hints(fn_a)
    assert isinstance(hints_a, dict)
    assert hints_a["x"] is str
    assert hints_a["y"] is int
    assert hints_a["return"] is float

    hints_b = get_type_hints(fn_b)
    assert hints_b["name"] is bytes
    assert hints_b["return"] is list


# [pr_diff] pass_to_pass
def test_callable_object_hints():
    """get_type_hints works for callable objects with __call__ annotations."""
    from gradio.utils import get_type_hints

    class MyCallable:
        def __call__(self, x: str, y: int) -> bool:
            return len(x) > y

    hints = get_type_hints(MyCallable())
    assert isinstance(hints, dict)
    assert hints["x"] is str
    assert hints["y"] is int
    assert hints["return"] is bool


# [pr_diff] pass_to_pass
def test_non_callable_returns_empty():
    """get_type_hints returns {} for non-callable inputs."""
    from gradio.utils import get_type_hints

    assert get_type_hints("not_callable") == {}
    assert get_type_hints(42) == {}
    assert get_type_hints(None) == {}


# [pr_diff] pass_to_pass
def test_unannotated_returns_empty():
    """get_type_hints returns {} for functions with no annotations."""
    from gradio.utils import get_type_hints

    def no_annotations(x, y):
        return x + y

    hints = get_type_hints(no_annotations)
    assert isinstance(hints, dict)
    assert len(hints) == 0


# [static] pass_to_pass
def test_not_stub():
    """get_type_hints function has real logic, not just pass/return."""
    import ast

    src = Path(f"{REPO}/gradio/utils.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_type_hints":
            body_stmts = [
                s
                for s in node.body
                if not isinstance(s, ast.Expr)
                or not isinstance(getattr(s, "value", None), ast.Constant)
            ]
            assert len(body_stmts) >= 2, (
                f"Function body too simple ({len(body_stmts)} stmts)"
            )
            return
    assert False, "get_type_hints function not found in utils.py"
