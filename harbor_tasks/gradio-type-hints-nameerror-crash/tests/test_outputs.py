"""
Task: gradio-type-hints-nameerror-crash
Repo: gradio-app/gradio @ c13daab68aa40cb58f2c643a650b5db48e986935
PR:   #13161

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/repo"

if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _install_if_needed(package: str, import_name: str | None = None) -> None:
    """Install a package if its import is not available."""
    import_name = import_name or package
    try:
        __import__(import_name)
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", package],
            check=True,
            capture_output=True,
        )


def _install_ruff() -> None:
    """Install ruff if not already available."""
    _install_if_needed("ruff")


def _install_test_deps() -> None:
    """Install test dependencies (pytest, hypothesis) if not available."""
    _install_if_needed("pytest")
    _install_if_needed("hypothesis")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI/CD checks that must pass before AND after
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on gradio/utils.py and test/test_utils.py (pass_to_pass)."""
    _install_ruff()
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/utils.py", "test/test_utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on gradio/utils.py and test/test_utils.py (pass_to_pass)."""
    _install_ruff()
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/utils.py", "test/test_utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's TestGetTypeHints unit tests pass (pass_to_pass)."""
    _install_test_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::TestGetTypeHints", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_check_function_inputs_match():
    """Repo's TestCheckFunctionInputsMatch unit tests pass (pass_to_pass)."""
    _install_test_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::TestCheckFunctionInputsMatch", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Check function inputs match tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_function_params():
    """Repo's TestFunctionParams unit tests pass (pass_to_pass)."""
    _install_test_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_utils.py::TestFunctionParams", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Function params tests failed:\n{r.stderr[-1000:]}"




# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gradio/utils.py must parse without syntax errors."""
    import ast

    src = Path(f"{REPO}/gradio/utils.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
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
# Pass-to-pass (pr_diff) - regression + anti-stub
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
