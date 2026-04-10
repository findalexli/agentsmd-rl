"""
Task: gradio-file-sanitize-empty-stem
Repo: gradio-app/gradio @ f1cd0644d2608b493db07cd204c0831a111f9fb2
PR:   12979

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    import py_compile

    py_compile.compile(
        f"{REPO}/client/python/gradio_client/utils.py", doraise=True
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_empty_stem_gets_fallback():
    """Filename with entirely-stripped stem preserves the extension."""
    import re
    from gradio_client.utils import strip_invalid_filename_characters

    INVALID = re.compile(r"[^a-zA-Z0-9._\-, ]")

    for fname, expected_suffix in [("#.txt", ".txt"), ("###.pdf", ".pdf"), ("@!$.csv", ".csv")]:
        result = strip_invalid_filename_characters(fname)
        p = Path(result)
        # Sanitization must have removed invalid chars
        assert not INVALID.search(result), (
            f"{fname}: invalid chars remain in {result!r}"
        )
        # Extension must be preserved
        assert p.suffix == expected_suffix, (
            f"{fname}: expected suffix {expected_suffix}, got {p.suffix!r} from {result!r}"
        )
        # Stem must not be empty
        assert p.stem != "", f"{fname}: stem should not be empty, got {result!r}"


# [pr_diff] pass_to_pass
def test_partial_strip_keeps_original_stem():
    """When some stem chars survive sanitization, no fallback is injected."""
    from gradio_client.utils import strip_invalid_filename_characters

    assert strip_invalid_filename_characters("a#.txt") == "a.txt"
    assert strip_invalid_filename_characters("1#2.csv") == "12.csv"
    assert strip_invalid_filename_characters("hello#world.py") == "helloworld.py"


# [pr_diff] fail_to_pass
def test_bare_dotfile_not_produced():
    """Result is never just the extension (a bare dotfile)."""
    import re
    from gradio_client.utils import strip_invalid_filename_characters

    INVALID = re.compile(r"[^a-zA-Z0-9._\-, ]")

    for fname in ["#.txt", "!!!.json", "&&&.tar.gz"]:
        result = strip_invalid_filename_characters(fname)
        # Must have sanitized invalid chars
        assert not INVALID.search(result), (
            f"{fname}: invalid chars remain in {result!r}"
        )
        # A bare dotfile like ".txt" has no suffix in pathlib
        assert Path(result).suffix != "", (
            f"{fname}: produced bare dotfile {result!r} (suffix is empty)"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_strip_behavior():
    """Existing sanitization cases still produce correct results."""
    from gradio_client.utils import strip_invalid_filename_characters

    cases = [
        ("abc", "abc"),
        ("$$AAabc&3", "AAabc3"),
        ("$$AAa&..b-c3_", "AAa..b-c3_"),
        ("hello world.txt", "hello world.txt"),
        ("normal-file_v2.py", "normal-file_v2.py"),
    ]
    for inp, expected in cases:
        result = strip_invalid_filename_characters(inp)
        assert result == expected, f"{inp!r}: expected {expected!r}, got {result!r}"


# [repo_tests] pass_to_pass
def test_gradio_client_utils_tests():
    """Repo's existing gradio_client utils tests pass (pass_to_pass).

    The conftest.py requires the full gradio package which isn't installed,
    so we temporarily rename it to run just the utils tests.
    """
    import subprocess
    import os

    client_dir = f"{REPO}/client/python"
    conftest = f"{client_dir}/test/conftest.py"
    conftest_bak = f"{conftest}.bak"

    # Temporarily rename conftest.py if it exists (it imports gradio which isn't installed)
    if os.path.exists(conftest):
        os.rename(conftest, conftest_bak)

    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "test/test_utils.py::test_strip_invalid_filename_characters", "-v"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=client_dir,
        )
        assert r.returncode == 0, f"gradio_client utils tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"
    finally:
        # Restore conftest.py
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# [repo_tests] pass_to_pass
def test_gradio_client_lint():
    """Repo's gradio_client code passes ruff lint (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "ruff", "check", "client/python/gradio_client"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_gradio_client_format():
    """Repo's gradio_client code passes ruff format check (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "pip", "install", "ruff", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "client/python/gradio_client"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_gradio_client_is_valid_file_type():
    """Repo's is_valid_file_type tests pass (pass_to_pass)."""
    import subprocess
    import os

    client_dir = f"{REPO}/client/python"
    conftest = f"{client_dir}/test/conftest.py"
    conftest_bak = f"{conftest}.bak"

    if os.path.exists(conftest):
        os.rename(conftest, conftest_bak)

    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "test/test_utils.py::test_is_valid_file_type", "-v"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=client_dir,
        )
        assert r.returncode == 0, f"is_valid_file_type tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    finally:
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# [repo_tests] pass_to_pass
def test_gradio_client_get_mimetype():
    """Repo's get_mimetype tests pass (pass_to_pass)."""
    import subprocess
    import os

    client_dir = f"{REPO}/client/python"
    conftest = f"{client_dir}/test/conftest.py"
    conftest_bak = f"{conftest}.bak"

    if os.path.exists(conftest):
        os.rename(conftest, conftest_bak)

    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "test/test_utils.py::test_get_mimetype", "-v"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=client_dir,
        )
        assert r.returncode == 0, f"get_mimetype tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    finally:
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# [repo_tests] pass_to_pass
def test_gradio_client_json_schema():
    """Repo's json_schema_to_python_type tests pass (pass_to_pass)."""
    import subprocess
    import os

    client_dir = f"{REPO}/client/python"
    conftest = f"{client_dir}/test/conftest.py"
    conftest_bak = f"{conftest}.bak"

    if os.path.exists(conftest):
        os.rename(conftest, conftest_bak)

    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "test/test_utils.py::test_json_schema_to_python_type", "-v"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=client_dir,
        )
        assert r.returncode == 0, f"json_schema tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    finally:
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# [repo_tests] pass_to_pass
def test_gradio_client_python_type_schema():
    """Repo's python_type_to_json_schema tests pass (pass_to_pass)."""
    import subprocess
    import os

    client_dir = f"{REPO}/client/python"
    conftest = f"{client_dir}/test/conftest.py"
    conftest_bak = f"{conftest}.bak"

    if os.path.exists(conftest):
        os.rename(conftest, conftest_bak)

    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "test/test_utils.py", "-v", "-k", "python_type_to_json_schema"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=client_dir,
        )
        assert r.returncode == 0, f"python_type_to_json_schema tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    finally:
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# [repo_tests] pass_to_pass
def test_gradio_client_construct_args():
    """Repo's construct_args tests pass (pass_to_pass)."""
    import subprocess
    import os

    client_dir = f"{REPO}/client/python"
    conftest = f"{client_dir}/test/conftest.py"
    conftest_bak = f"{conftest}.bak"

    if os.path.exists(conftest):
        os.rename(conftest, conftest_bak)

    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "test/test_utils.py::TestConstructArgs", "-v"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=client_dir,
        )
        assert r.returncode == 0, f"construct_args tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    finally:
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """strip_invalid_filename_characters has real logic, not just pass/return."""
    import ast

    src = Path(f"{REPO}/client/python/gradio_client/utils.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "strip_invalid_filename_characters":
            body_stmts = [
                n for n in node.body
                if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))
                and not isinstance(n, ast.Pass)
            ]
            assert len(body_stmts) > 2, (
                f"Function body looks stubbed ({len(body_stmts)} real stmts)"
            )
            return
    raise AssertionError("Function strip_invalid_filename_characters not found")
