"""
Task: gradio-load-fn-recursion-oom
Repo: gradio-app/gradio @ ca84f3e36c6a3f3c3f0b57084b6f514d6cded1d4
PR:   12928

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = "/repo"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess with the repo on sys.path."""
    env = {**os.environ, "PYTHONPATH": REPO}
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO, env=env,
    )


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
    """Verify query_huggingface_inference_endpoints doesn't cause closure recursion.

    The bug is that the nested function create_endpoint_fn captures 'fn' from
    the outer scope. If the outer scope reassigns 'fn' via 'fn = kwargs.pop("fn")',
    the closure captures the wrong value.

    This test verifies the ACTUAL source code for the buggy pattern and ensures
    the fix is applied (different variable name for the popped value).
    """
    source = Path(f"{REPO}/gradio/external.py").read_text()
    tree = ast.parse(source)

    # Find from_model function
    from_model = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == "from_model"),
        None,
    )
    assert from_model is not None, "from_model function not found"

    # Find the pattern: some_var = kwargs.pop("fn", ...)
    # The fix changes 'fn' local var to 'interface_fn' or similar
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

    assert pop_var is not None, "kwargs.pop('fn', ...) assignment not found"
    # The fix renames 'fn' to something else to avoid shadowing
    # If it's still 'fn', the bug is not fixed
    assert pop_var != "fn", (
        f"Bug not fixed: local variable is still named 'fn' (causes closure shadowing). "
        f"Should use a different name like 'interface_fn'."
    )


# [pr_diff] fail_to_pass
def test_stop_iteration_handled():
    """handle_hf_error must catch StopIteration and raise an informative Error."""
    r = _run_python("""
import sys
from gradio.exceptions import Error
from gradio.external_utils import handle_hf_error

# Bare StopIteration (no message)
try:
    handle_hf_error(StopIteration())
except StopIteration:
    print("FAIL: StopIteration leaked through unhandled")
    sys.exit(1)
except Error as e:
    msg = getattr(e, 'message', str(e))
    if len(msg.strip()) < 10:
        print(f"FAIL: message too short: {msg!r}")
        sys.exit(1)

# StopIteration with a value
try:
    handle_hf_error(StopIteration("no provider"))
except StopIteration:
    print("FAIL: StopIteration leaked through unhandled")
    sys.exit(1)
except Error as e:
    msg = getattr(e, 'message', str(e))
    if len(msg.strip()) < 10:
        print(f"FAIL: message too short: {msg!r}")
        sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"StopIteration handling failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_empty_exception_non_empty_message():
    """handle_hf_error must produce a non-empty error message for exceptions
    with no string representation."""
    r = _run_python("""
import sys
from gradio.exceptions import Error
from gradio.external_utils import handle_hf_error

for exc in [Exception(), RuntimeError(), ValueError(), OSError()]:
    try:
        handle_hf_error(exc)
        print(f"FAIL: handle_hf_error should have raised for {type(exc).__name__}")
        sys.exit(1)
    except Error as e:
        msg = getattr(e, 'message', e.args[0] if e.args else "")
        if len(msg.strip()) == 0:
            print(f"FAIL: empty message for {type(exc).__name__}")
            sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Empty exception message test failed: {r.stderr}"
    assert "PASS" in r.stdout


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

    The instruction requires 'at least 2 if-branches and at least 3 raise statements'.
    This test verifies the function has actual error-handling structure.
    """
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


# [repo_tests] pass_to_pass - repo's CI: pytest test/test_external_utils.py
def test_repo_external_utils_tests():
    """Repo's external_utils tests must pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_external_utils.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"external_utils tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - repo's CI: ruff format check
def test_repo_ruff_format():
    """Modified files must pass ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "gradio/external.py", "gradio/external_utils.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - repo's CI: ruff lint check on modified files
def test_repo_ruff_lint():
    """Modified files must pass ruff lint check (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--select", "E,W", "--ignore", "E501", "gradio/external.py", "gradio/external_utils.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff lint check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - repo's CI: external.py unit tests (subset that doesn't require network)
def test_repo_external_tests():
    """Repo's external.py unit tests pass (pass_to_pass)."""
    # Run only tests that don't require network or special dependencies
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest", "test/test_external.py",
            "-v", "--tb=short",
            "-k", "not (audio_to_audio or question_answering or summarization or translation or text_classification or fill_mask or zero_shot or speech_recognition or image_classification or feature_extraction or sentence_similarity or text_to_speech or multiple_spaces or private_space or interface_load_cache or tabular or custom_component or inside_blocks or chat)",
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"external.py tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - repo's CI: gradio module import check
def test_repo_gradio_imports():
    """gradio module and key submodules remain importable (pass_to_pass)."""
    import_code = """
import sys
sys.path.insert(0, '/repo')
import gradio
import gradio.external
import gradio.external_utils
from gradio.exceptions import Error
from gradio.external_utils import handle_hf_error, TooManyRequestsError
print('All imports successful')
"""
    r = subprocess.run(
        [sys.executable, "-c", import_code],
        capture_output=True, text=True, timeout=30, cwd=REPO, env={**os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"gradio imports failed:\n{r.stderr[-500:]}"
    assert "All imports successful" in r.stdout, f"Unexpected output: {r.stdout}"


# [repo_tests] pass_to_pass - consolidated external tests
def test_repo_external_consolidated():
    """Repo's external.py and external_utils tests pass (consolidated network-independent subset)."""
    # Install required dependencies for tests
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "httpx", "huggingface-hub", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run consolidated external tests (network-independent subset)
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "test/test_external_utils.py", "test/test_external.py",
            "-v", "--tb=short",
            "-k", "not (audio_to_audio or question_answering or summarization or translation or text_classification or fill_mask or zero_shot or speech_recognition or image_classification or feature_extraction or sentence_similarity or text_to_speech or multiple_spaces or private_space or interface_load_cache or tabular or custom_component or inside_blocks or chat)",
        ],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Consolidated external tests failed:\n{r.stdout[-1500:]}{r.stderr[-500:]}"
