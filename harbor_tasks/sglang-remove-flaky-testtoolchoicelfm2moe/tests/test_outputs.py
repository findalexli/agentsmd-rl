"""
Task: sglang-remove-flaky-testtoolchoicelfm2moe
Repo: sgl-project/sglang @ dd49127fe612800d2f2aa258c9b7086043f103fa
PR:   22137

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = "test/registered/openai_server/function_call/test_tool_choice.py"
FULL_PATH = f"{REPO}/{TEST_FILE}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified test file must parse without syntax errors."""
    src = Path(FULL_PATH).read_text()
    # This will raise SyntaxError if the file has any syntax issues
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flaky_class_removed():
    """TestToolChoiceLfm2Moe class must be removed from the test file."""
    src = Path(FULL_PATH).read_text()

    # The TestToolChoiceLfm2Moe class should NOT exist after the fix
    assert "class TestToolChoiceLfm2Moe" not in src, \
        "TestToolChoiceLfm2Moe class still exists and should be removed"

    # Verify the model name used by the removed class is gone
    assert '"LiquidAI/LFM2-8B-A1B"' not in src, \
        "Reference to flaky LFM2-8B-A1B model still exists"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_other_test_classes_preserved():
    """Other test classes must still exist (regression check)."""
    src = Path(FULL_PATH).read_text()

    # These classes should NOT be removed
    required_classes = [
        "TestToolChoiceLlama32",
        "TestToolChoiceLfm2",  # Note: This is different from Lfm2Moe
        "TestToolChoiceQwen25",
        "TestToolChoiceMistral",
    ]

    for class_name in required_classes:
        assert f"class {class_name}" in src, \
            f"Required test class {class_name} is missing from the file"


# [static] pass_to_pass
def test_main_guard_preserved():
    """The unittest main guard must be preserved at the end of the file."""
    src = Path(FULL_PATH).read_text()

    # File should still have the main guard
    assert 'if __name__ == "__main__":' in src, \
        "Main guard is missing"
    assert "unittest.main()" in src, \
        "unittest.main() call is missing"


# [static] pass_to_pass
def test_file_structure_valid():
    """The test file must have valid Python structure after modification."""
    src = Path(FULL_PATH).read_text()
    tree = ast.parse(src)

    # Count class definitions
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    # We should have exactly these test classes:
    # TestToolChoiceLlama32, TestToolChoiceQwen25, TestToolChoiceMistral, TestToolChoiceLfm2
    # (TestToolChoiceLfm2Moe should be removed)
    # Plus any other classes that may exist

    class_names = {c.name for c in classes}

    # Verify TestToolChoiceLfm2Moe is NOT present
    assert "TestToolChoiceLfm2Moe" not in class_names, \
        "TestToolChoiceLfm2Moe should not be in the file"

    # Verify the key classes still exist
    assert "TestToolChoiceLlama32" in class_names, \
        "TestToolChoiceLlama32 base class is missing"
    assert "TestToolChoiceLfm2" in class_names, \
        "TestToolChoiceLfm2 class is missing (this is NOT the one to remove)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from repo's own pipeline
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — ruff linting check (from pre-commit)
def test_p2p_ruff_check():
    """Repo's ruff linting passes on the test file (pass_to_pass)."""
    # Install ruff and run check
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr.decode()[-200:]}"

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select=F401,F821", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — black formatting check (from pre-commit)
def test_p2p_black_check():
    """Repo's black formatting check passes on the test file (pass_to_pass)."""
    # Install black and run check
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "black", "-q"],
        capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr.decode()[-200:]}"

    r = subprocess.run(
        [sys.executable, "-m", "black", "--check", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — isort import ordering check (from pre-commit)
def test_p2p_isort_check():
    """Repo's isort import ordering passes on the test file (pass_to_pass)."""
    # Install isort and run check
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "isort", "-q"],
        capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr.decode()[-200:]}"

    r = subprocess.run(
        [sys.executable, "-m", "isort", "--check", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Isort check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — codespell check (from pre-commit)
def test_p2p_codespell_check():
    """Repo's codespell check passes on the test file (pass_to_pass)."""
    # Install codespell and run check
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "codespell", "-q"],
        capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"Failed to install codespell: {r.stderr.decode()[-200:]}"

    r = subprocess.run(
        [sys.executable, "-m", "codespell", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Codespell check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Python syntax validation (from pre-commit check-ast)
def test_p2p_py_compile():
    """Modified test file must compile without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"
