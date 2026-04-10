"""
Task: sglang-eagle3-infer-beta-test
Repo: sglang @ 6c2a759a04232ef4cb0c845528d75516ddbd9fe2
PR:   22303

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/test/registered/spec/eagle/test_eagle_infer_beta.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified test file must parse without errors."""
    src = Path(TARGET_FILE).read_text()
    ast.parse(src)  # Will raise SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_imports_use_eagle3():
    """Imports must use EAGLE3 constants instead of EAGLE."""
    src = Path(TARGET_FILE).read_text()

    # Should import EAGLE3 constants, not EAGLE
    assert "DEFAULT_DRAFT_MODEL_EAGLE3" in src, \
        "Must import DEFAULT_DRAFT_MODEL_EAGLE3"
    assert "DEFAULT_TARGET_MODEL_EAGLE3" in src, \
        "Must import DEFAULT_TARGET_MODEL_EAGLE3"

    # Should NOT use old EAGLE constants (except in comments if any)
    lines = src.split('\n')
    for i, line in enumerate(lines, 1):
        if 'import' in line or 'from' in line:
            assert 'DEFAULT_DRAFT_MODEL_EAGLE,' not in line, \
                f"Line {i}: Must not import old DEFAULT_DRAFT_MODEL_EAGLE"
            assert 'DEFAULT_TARGET_MODEL_EAGLE,' not in line, \
                f"Line {i}: Must not import old DEFAULT_TARGET_MODEL_EAGLE"


# [pr_diff] fail_to_pass
def test_class_names_updated():
    """Class names must be updated from TestEagle* to TestEagle3*."""
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    class_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_names.append(node.name)

    # Should have EAGLE3 class names
    assert "TestEagle3ServerBase" in class_names, \
        "Must define TestEagle3ServerBase class"
    assert "TestEagle3ServerPage" in class_names, \
        "Must define TestEagle3ServerPage class"

    # Should NOT have old EAGLE class names
    assert "TestEagleServerBase" not in class_names, \
        "Must not have old TestEagleServerBase class"
    assert "TestEagleServerPage" not in class_names, \
        "Must not have old TestEagleServerPage class"


# [pr_diff] fail_to_pass
def test_speculative_algorithm_eagle3():
    """Speculative algorithm must be set to EAGLE3."""
    src = Path(TARGET_FILE).read_text()

    # Should use EAGLE3 algorithm
    assert '"EAGLE3"' in src or "'EAGLE3'" in src, \
        "Must set speculative-algorithm to EAGLE3"

    # Should NOT use old EAGLE algorithm (except possibly in comments)
    lines = src.split('\n')
    for i, line in enumerate(lines, 1):
        if 'speculative-algorithm' in line and 'launch_args' in src:
            assert 'EAGLE3' in line or 'EAGLE3' in src, \
                f"Line {i}: Must use EAGLE3, not EAGLE"


# [pr_diff] fail_to_pass
def test_new_args_added():
    """New arguments --dtype, --chunked-prefill-size must be added."""
    src = Path(TARGET_FILE).read_text()

    # Check for --dtype=float16
    assert '"--dtype=float16"' in src or "'--dtype=float16'" in src, \
        "Must add --dtype=float16 argument"

    # Check for --chunked-prefill-size
    assert 'chunked-prefill-size' in src, \
        "Must add --chunked-prefill-size argument"

    # Check for value 1024 after chunked-prefill-size
    lines = src.split('\n')
    for i, line in enumerate(lines):
        if 'chunked-prefill-size' in line and '--chunked-prefill-size' in line:
            # Check next line or same line for 1024
            next_lines = ' '.join(lines[i:min(i+3, len(lines))])
            assert '1024' in next_lines, \
                "Must set chunked-prefill-size to 1024"


# [pr_diff] fail_to_pass
def test_env_override_added():
    """SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN env override must be added."""
    src = Path(TARGET_FILE).read_text()

    assert "SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN" in src, \
        "Must add SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN environment override"
    assert "override(" in src, \
        "Must use envs.SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN.override(True)"


# [pr_diff] fail_to_pass
def test_name_updated():
    """Test print statement must use TestEagle3LargeBS."""
    src = Path(TARGET_FILE).read_text()

    # Check for updated test name in print statement
    assert "TestEagle3LargeBS" in src, \
        "Must update print statement to use TestEagle3LargeBS"

    # Should not use old name
    assert "TestEagleLargeBS" not in src, \
        "Must not use old TestEagleLargeBS name"


# [pr_diff] fail_to_pass
def test_score_threshold_updated():
    """Score threshold must be updated from 0.22 to 0.7."""
    src = Path(TARGET_FILE).read_text()

    # Find the assertGreater for metrics["score"]
    assert '0.7' in src, \
        "Must update score threshold to 0.7"

    # Check that old threshold is gone
    lines = src.split('\n')
    for i, line in enumerate(lines, 1):
        if 'assertGreater' in line and 'score' in src:
            # Look for old threshold in nearby lines
            context = '\n'.join(lines[max(0, i-5):min(len(lines), i+5)])
            assert '0.22' not in context, \
                f"Line {i}: Must not use old threshold 0.22"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub verification
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified file is not a stub (has real test logic)."""
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    # Check that class has meaningful methods (not just pass)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestEagle3ServerBase":
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            assert len(methods) >= 2, "TestEagle3ServerBase must have at least 2 methods"

            # Check setUpClass has meaningful content
            setup_methods = [m for m in methods if m.name == "setUpClass"]
            if setup_methods:
                body = [s for s in setup_methods[0].body if not isinstance(s, (ast.Pass, ast.Expr))]
                assert len(body) >= 3, "setUpClass must have meaningful implementation"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_py_compile():
    """Repo's Python files compile without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_test_directory_syntax():
    """All Python files in test/registered/spec/eagle compile (pass_to_pass)."""
    eagle_dir = Path(REPO) / "test" / "registered" / "spec" / "eagle"
    failed = []

    for pyfile in eagle_dir.glob("*.py"):
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(pyfile)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        if r.returncode != 0:
            failed.append(f"{pyfile.name}: {r.stderr[:200]}")

    assert not failed, f"Syntax errors found:\n" + "\n".join(failed[:5])


# [repo_tests] pass_to_pass
def test_repo_python_sglang_syntax():
    """Sample of Python files in python/sglang compile (pass_to_pass)."""
    # Check a representative sample of Python files
    sample_files = [
        "python/sglang/srt/utils.py",
        "python/sglang/srt/managers/io_struct.py",
        "python/sglang/srt/configs/model_config.py",
        "python/sglang/test/test_utils.py",
        "python/sglang/check_env.py",
    ]

    failed = []
    for rel_path in sample_files:
        full_path = Path(REPO) / rel_path
        if not full_path.exists():
            continue
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(full_path)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        if r.returncode != 0:
            failed.append(f"{rel_path}: {r.stderr[:200]}")

    assert not failed, f"Syntax errors found:\n" + "\n".join(failed)
