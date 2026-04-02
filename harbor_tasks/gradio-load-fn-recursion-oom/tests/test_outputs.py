"""
Task: gradio-load-fn-recursion-oom
Repo: gradio-app/gradio @ ca84f3e36c6a3f3c3f0b57084b6f514d6cded1d4
PR:   12928

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO = "/repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files (external.py, external_utils.py) must parse without syntax errors."""
    for path in ["gradio/external.py", "gradio/external_utils.py"]:
        source = Path(f"{REPO}/{path}").read_text()
        ast.parse(source)  # Raises SyntaxError if broken


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_closure_no_self_recursion():
    """fn variable in from_model must not shadow the closure, preventing infinite recursion.
    AST-only because: from_model requires HuggingFace API access to call directly."""
    source = Path(f"{REPO}/gradio/external.py").read_text()
    tree = ast.parse(source)

    # Find from_model function
    from_model = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == "from_model"),
        None,
    )
    assert from_model is not None, "from_model function not found in external.py"

    # Find: <var> = <...>.pop("fn", ...)
    pop_var = None
    for node in ast.walk(from_model):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "pop"
            and node.value.args
            and isinstance(node.value.args[0], ast.Constant)
            and node.value.args[0].value == "fn"
            and node.targets
            and isinstance(node.targets[0], ast.Name)
        ):
            pop_var = node.targets[0].id
            break

    assert pop_var is not None, "kwargs.pop('fn', ...) assignment not found in from_model"

    # Behaviorally verify: simulate the closure pattern with the actual variable name.
    # In from_model, `fn` is the pipeline function captured by the query closure.
    # If kwargs.pop("fn") is assigned back to `fn`, the closure calls itself → recursion.
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50)
    try:
        ns = {}
        exec(
            f"def pipeline(*data): return 'pipeline_result'\n"
            f"fn = pipeline\n"
            f"def query(*data): return fn(*data)\n"
            f"kwargs = {{'fn': query}}\n"
            f"{pop_var} = kwargs.pop('fn', None)\n"
            f"result = query('test_input')\n",
            ns,
        )
        assert ns["result"] == "pipeline_result", (
            f"Closure returned {ns['result']!r}, expected 'pipeline_result'"
        )
    except RecursionError:
        raise AssertionError(
            f"Variable '{pop_var}' shadows the closure — query() recurses infinitely"
        )
    finally:
        sys.setrecursionlimit(old_limit)


# [pr_diff] fail_to_pass
def test_stop_iteration_handled():
    """handle_hf_error must catch StopIteration and raise an informative Error."""
    sys.path.insert(0, REPO)
    from gradio.exceptions import Error
    from gradio.external_utils import handle_hf_error

    # Bare StopIteration (no message)
    with pytest.raises(Error, match=r".{10,}"):
        handle_hf_error(StopIteration())

    # StopIteration with a value
    with pytest.raises(Error, match=r".{10,}"):
        handle_hf_error(StopIteration("no provider"))

    # Must NOT leak as a raw StopIteration
    try:
        handle_hf_error(StopIteration())
    except Error:
        pass  # correct
    except StopIteration:
        pytest.fail("StopIteration leaked through unhandled")


# [pr_diff] fail_to_pass
def test_empty_exception_non_empty_message():
    """handle_hf_error must produce a non-empty error message for exceptions
    with no string representation."""
    sys.path.insert(0, REPO)
    from gradio.exceptions import Error
    from gradio.external_utils import handle_hf_error

    for exc in [Exception(), RuntimeError(), ValueError(), OSError()]:
        try:
            handle_hf_error(exc)
            pytest.fail(f"handle_hf_error should have raised for {type(exc).__name__}")
        except Error as e:
            # Use e.message (raw string), not str(e) which Gradio wraps in quotes
            msg = getattr(e, "message", e.args[0] if e.args else "")
            assert len(msg.strip()) > 0, (
                f"Empty error message for {type(exc).__name__}"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_modules_importable():
    """gradio.external and gradio.external_utils remain importable."""
    sys.path.insert(0, REPO)
    import importlib
    import gradio.external
    import gradio.external_utils
    importlib.reload(gradio.external)
    importlib.reload(gradio.external_utils)


# [repo_tests] pass_to_pass
def test_401_error_still_handled():
    """handle_hf_error still raises auth error for 401 responses."""
    sys.path.insert(0, REPO)
    from gradio.exceptions import Error
    from gradio.external_utils import handle_hf_error

    for exc_msg in ["401 Unauthorized", "You must provide an api_key"]:
        with pytest.raises(Error, match=r"(?i)(unauthorized|signed in)"):
            handle_hf_error(Exception(exc_msg))


# [repo_tests] pass_to_pass
def test_too_many_requests_still_handled():
    """handle_hf_error still raises TooManyRequestsError for 429 responses."""
    sys.path.insert(0, REPO)
    from gradio.external_utils import handle_hf_error

    try:
        handle_hf_error(Exception("429"))
        pytest.fail("handle_hf_error should have raised for 429")
    except Exception as e:
        assert "TooManyRequests" in type(e).__name__, (
            f"Expected TooManyRequestsError, got {type(e).__name__}: {e}"
        )


# [static] pass_to_pass
def test_handle_hf_error_not_stub():
    """handle_hf_error has real branching logic, not just pass/return.
    AST-only because: checking structural complexity of function body."""
    source = Path(f"{REPO}/gradio/external_utils.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "handle_hf_error":
            ifs = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))
            raises = sum(1 for n in ast.walk(node) if isinstance(n, ast.Raise))
            assert ifs >= 2, f"handle_hf_error has {ifs} if-branches, expected >=2"
            assert raises >= 3, f"handle_hf_error has {raises} raise stmts, expected >=3"
            return
    pytest.fail("handle_hf_error function not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ ca84f3e
def test_ruff_lint_modified_files():
    """Python code must pass ruff linting (AGENTS.md line 43: 'Python code is formatted with ruff')."""
    for path in ["gradio/external.py", "gradio/external_utils.py"]:
        r = subprocess.run(
            ["ruff", "check", "--select", "E,W", "--ignore", "E501", path, "--quiet"],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"ruff lint failed on {path}:\n{r.stdout.decode()}\n{r.stderr.decode()}"
        )
