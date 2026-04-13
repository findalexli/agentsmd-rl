"""
Task: transformers-test-fix-integration-expectations
Repo: huggingface/transformers @ d4895f0810fd57bf5ee8cf65c3fe20d2f622cd0a
PR:   44934

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"

QWEN2_TEST_FILE = f"{REPO}/tests/models/qwen2/test_modeling_qwen2.py"
T5_TEST_FILE = f"{REPO}/tests/models/t5/test_modeling_t5.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_qwen2_test_file_parses():
    """Qwen2 test file must parse without syntax errors."""
    src = Path(QWEN2_TEST_FILE).read_text()
    ast.parse(src)


# [static] pass_to_pass
def test_t5_test_file_parses():
    """T5 test file must parse without syntax errors."""
    src = Path(T5_TEST_FILE).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check_qwen2():
    """Repo's ruff linter passes on qwen2 test file (pass_to_pass)."""
    import shutil
    if not shutil.which("ruff"):
        subprocess.run(["pip", "install", "ruff", "-q"], check=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check", QWEN2_TEST_FILE, "--ignore", "E501"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check_t5():
    """Repo's ruff linter passes on t5 test file (pass_to_pass)."""
    import shutil
    if not shutil.which("ruff"):
        subprocess.run(["pip", "install", "ruff", "-q"], check=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check", T5_TEST_FILE, "--ignore", "E501"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_check():
    """Repo's ruff format check passes on test files (pass_to_pass)."""
    import shutil
    if not shutil.which("ruff"):
        subprocess.run(["pip", "install", "ruff", "-q"], check=True, timeout=60)
    r = subprocess.run(
        ["ruff", "format", "--check", QWEN2_TEST_FILE, T5_TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check_model_dirs():
    """Repo's ruff linter passes on qwen2 and t5 model test directories (pass_to_pass)."""
    import shutil
    if not shutil.which("ruff"):
        subprocess.run(["pip", "install", "ruff", "-q"], check=True, timeout=60)
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/tests/models/qwen2/", f"{REPO}/tests/models/t5/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check on model dirs failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_qwen2_test_file_compiles():
    """Qwen2 test file must compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", QWEN2_TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Qwen2 test file compilation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_t5_test_file_compiles():
    """T5 test file must compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", T5_TEST_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"T5 test file compilation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_inits():
    """Repo's check_inits.py passes - validates model inits are consistent (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/src"},
    )
    assert r.returncode == 0, f"check_inits.py failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_check_dummies():
    """Repo's check_dummies.py passes - validates dummy objects are properly defined (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/src"},
    )
    assert r.returncode == 0, f"check_dummies.py failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_qwen2_speculative_generation_uses_consistent_model():
    """test_speculative_generation must use Qwen2-0.5B for tokenizer (not 7B)."""
    src = Path(QWEN2_TEST_FILE).read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_speculative_generation":
            # Find all string literals in the function
            for child in ast.walk(node):
                if isinstance(child, ast.Constant) and isinstance(child.value, str):
                    # Check that Qwen2-7B is NOT used for tokenizer
                    assert "Qwen/Qwen2-7B" != child.value, \
                        "Found inconsistent tokenizer model 'Qwen/Qwen2-7B' - should be 'Qwen/Qwen2-0.5B'"

            # Verify Qwen2-0.5B IS used for tokenizer by checking from_pretrained calls
            found_05b_tokenizer = False
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    # Check if this is a from_pretrained call
                    if isinstance(child.func, ast.Attribute) and child.func.attr == "from_pretrained":
                        if child.args:
                            first_arg = child.args[0]
                            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                                if first_arg.value == "Qwen/Qwen2-0.5B":
                                    found_05b_tokenizer = True
                                    break

            assert found_05b_tokenizer, \
                "test_speculative_generation must use 'Qwen/Qwen2-0.5B' for tokenizer"
            return

    raise AssertionError("Could not find test_speculative_generation function")


# [pr_diff] fail_to_pass
def test_qwen2_speculative_generation_uses_expectations():
    """test_speculative_generation must use Expectations wrapper with platform-specific expectations."""
    src = Path(QWEN2_TEST_FILE).read_text()

    # The fix wraps EXPECTED_TEXT_COMPLETION in Expectations() with platform-specific dict
    assert "Expectations(" in src, "test_speculative_generation should use Expectations wrapper"

    # Check within test_speculative_generation specifically
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_speculative_generation":
            func_src = ast.unparse(node)
            # Should use Expectations, not plain string
            assert "Expectations(" in func_src, \
                "test_speculative_generation must use Expectations wrapper for platform-specific outputs"
            # Should have device-specific expectations
            assert '("cuda",' in func_src or "get_expectation" in func_src, \
                "Expectations should include device-specific keys like ('cuda', 8)"
            return

    raise AssertionError("Could not find test_speculative_generation function")


# [pr_diff] fail_to_pass
def test_t5_compile_static_cache_uses_decode():
    """test_compile_static_cache must use tokenizer.decode(), not batch_decode()."""
    src = Path(T5_TEST_FILE).read_text()

    # Find the test_compile_static_cache method
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_compile_static_cache":
            func_src = ast.unparse(node)

            # Check that .decode() is used (for single batch items)
            assert ".decode(" in func_src, \
                "test_compile_static_cache must use tokenizer.decode() for single-item decoding"

            # Ensure batch_decode is NOT used incorrectly for single items
            assert ".batch_decode(" not in func_src, \
                "test_compile_static_cache should not use batch_decode() for single-item outputs"
            return

    raise AssertionError("Could not find test_compile_static_cache function")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_fixes_are_substantive():
    """Fixes must include actual code changes, not just comments or whitespace."""
    qwen_src = Path(QWEN2_TEST_FILE).read_text()
    t5_src = Path(T5_TEST_FILE).read_text()

    # Verify the specific expected content is in place after fix
    # Qwen2: Expectations with cuda key
    assert '("cuda", 8)' in qwen_src, "Expected device-specific Expectations in Qwen2 test"

    # T5: decode() calls in test_compile_static_cache
    tree = ast.parse(t5_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_compile_static_cache":
            func_src = ast.unparse(node)
            # Count decode calls
            decode_count = func_src.count(".decode(")
            assert decode_count >= 3, \
                f"Expected at least 3 decode() calls in test_compile_static_cache, found {decode_count}"
            return

    raise AssertionError("Could not find test_compile_static_cache function")
