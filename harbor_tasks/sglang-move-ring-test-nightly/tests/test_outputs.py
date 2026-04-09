"""
Task: sglang-move-ring-test-nightly
Repo: sglang @ 233f3e31bfec68c77c17066b7b270380e773da6b
PR:   22267

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = f"{REPO}/test/registered/8-gpu-models/test_ring_2_5_1t.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified test file must parse without errors."""
    src = Path(TEST_FILE).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_test_moved_to_nightly_suite():
    """Test registration must use nightly-8-gpu-common suite with nightly=True."""
    src = Path(TEST_FILE).read_text()
    tree = ast.parse(src)

    found_correct_registration = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "register_cuda_ci":
                # Extract keyword arguments
                keywords = {kw.arg: kw for kw in node.keywords}

                # Check suite="nightly-8-gpu-common"
                if "suite" in keywords:
                    suite_value = keywords["suite"]
                    if isinstance(suite_value.value, ast.Constant):
                        suite = suite_value.value.value
                    elif isinstance(suite_value.value, ast.Str):  # Python < 3.8
                        suite = suite_value.value.s
                    else:
                        suite = None

                    if suite == "nightly-8-gpu-common":
                        # Check nightly=True
                        if "nightly" in keywords:
                            nightly_value = keywords["nightly"]
                            if isinstance(nightly_value.value, ast.Constant):
                                nightly = nightly_value.value.value
                            elif isinstance(nightly_value.value, ast.NameConstant):
                                nightly = nightly_value.value.value
                            else:
                                nightly = None

                            if nightly is True:
                                found_correct_registration = True

    assert found_correct_registration, \
        "Test must be registered with suite='nightly-8-gpu-common' and nightly=True"


# [pr_diff] fail_to_pass
def test_est_time_updated():
    """Test registration must have est_time=1800 (not 1000)."""
    src = Path(TEST_FILE).read_text()
    tree = ast.parse(src)

    found_correct_time = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "register_cuda_ci":
                # Check est_time=1800
                if node.args and len(node.args) >= 1:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.Constant) and first_arg.value == 1800:
                        found_correct_time = True
                    elif isinstance(first_arg, ast.Num) and first_arg.n == 1800:
                        found_correct_time = True

                # Also check keywords
                for kw in node.keywords:
                    if kw.arg == "est_time":
                        if isinstance(kw.value, ast.Constant) and kw.value.value == 1800:
                            found_correct_time = True
                        elif isinstance(kw.value, ast.Num) and kw.value.n == 1800:
                            found_correct_time = True

    assert found_correct_time, "Test must have est_time=1800"


# [pr_diff] fail_to_pass
def test_soft_watchdog_timeout_added():
    """Test must have --soft-watchdog-timeout 1800 in base_args."""
    src = Path(TEST_FILE).read_text()
    tree = ast.parse(src)

    found_watchdog = False

    for node in ast.walk(tree):
        if isinstance(node, ast.List):
            # Check if this list contains the watchdog arguments
            list_str = ast.unparse(node) if hasattr(ast, 'unparse') else ""
            if "--soft-watchdog-timeout" in list_str:
                found_watchdog = True
                break

            # Manual check for elements
            elements = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    elements.append(elt.value)
                elif isinstance(elt, ast.Str):
                    elements.append(elt.s)

            if "--soft-watchdog-timeout" in elements and "1800" in elements:
                found_watchdog = True
                break

    assert found_watchdog, "Test must include --soft-watchdog-timeout 1800 in base_args"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo's isort check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "isort"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr[-500:]}"

    r = subprocess.run(
        ["isort", "--check-only", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff():
    """Repo's ruff lint check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black():
    """Repo's black format check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "black"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr[-500:]}"

    r = subprocess.run(
        ["black", "--check", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"black check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """Repo's codespell check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "codespell"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install codespell: {r.stderr[-500:]}"

    r = subprocess.run(
        ["codespell", "--config", ".codespellrc", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"codespell check failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_no_old_stage_c_registration():
    """Test must not be registered in stage-c-test-8-gpu-h200 suite."""
    src = Path(TEST_FILE).read_text()

    # Should not have the old registration
    assert 'suite="stage-c-test-8-gpu-h200"' not in src, \
        "Test must not be registered in stage-c-test-8-gpu-h200"


# [static] pass_to_pass
def test_no_comment_registration():
    """Test registration must not be commented out."""
    src = Path(TEST_FILE).read_text()

    # The old PR had a commented-out line - make sure it's not still there
    lines = src.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") and "register_cuda_ci" in stripped:
            assert False, "Found commented-out register_cuda_ci call"
