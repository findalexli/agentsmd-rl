"""
Task: {{TASK_NAME}}
Repo: {{REPO}} @ {{BASE_COMMIT}}
PR:   {{PR_NUMBER}}

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"

# The file modified by the PR
MODIFIED_FILE = Path(f"{REPO}/python/sglang/multimodal_gen/test/server/test_server_common.py")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    # Check that the modified Python file compiles without syntax errors
    result = subprocess.run(
        ["python3", "-m", "py_compile", str(MODIFIED_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Syntax check failed:\n{result.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified function diffusion_server is not a stub (has real logic)."""
    # Check that the diffusion_server fixture function has meaningful body
    # This is a p2p test - passes on both base and fixed commits
    src = MODIFIED_FILE.read_text()
    tree = ast.parse(src)

    found_func = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "diffusion_server":
            found_func = True
            # Check it has more than just a pass statement
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(stmts) >= 5, "diffusion_server function body is a stub"
            break

    assert found_func, "diffusion_server fixture not found in modified file"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_bug_fixed():
    """LoRA GT cases use normal backend path while non-LoRA GT uses diffusers backend."""
    # The fix changes the backend selection logic to check if it is a LoRA case
    # In the fixed version, _is_lora_case() is called before forcing --backend diffusers
    src = MODIFIED_FILE.read_text()

    # Verify the fix: the _is_lora_case check should be present
    assert "_is_lora_case" in src, "Fix not applied: _is_lora_case function not found"

    # The condition should check for _is_lora_case before forcing diffusers backend
    # In GT gen mode, non-LoRA cases get --backend diffusers, LoRA cases do not
    assert "if not _is_lora_case(case) and" in src or \
           "if not _is_lora_case(case)" in src, \
        "Fix not applied: _is_lora_case check missing in GT mode logic"


# [pr_diff] fail_to_pass
def test_edge_case():
    """Dynamic LoRA loading check runs in both GT and non-GT modes."""
    # The fix removes the not is_gt_gen_mode guard from run_lora_dynamic_load_check
    src = MODIFIED_FILE.read_text()

    # Find the line with run_lora_dynamic_load_check
    lines = src.split("\n")
    found_line = None
    for line in lines:
        if "run_lora_dynamic_load_check" in line:
            found_line = line.strip()
            break

    assert found_line is not None, "run_lora_dynamic_load_check not found"

    # In the fixed version, it should NOT have and not is_gt_gen_mode or similar
    # The condition should be simply if case.run_lora_dynamic_load_check:
    assert "not is_gt_gen_mode" not in found_line, \
        "Fix not applied: GT mode guard still present in dynamic LoRA check"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream test suite (CPU-safe subset) still passes."""
    # Run a quick syntax/import check on key test files to ensure they still work
    # Since we cannot run the full test suite (requires GPU, dependencies), we
    # verify the test files are syntactically valid

    test_files = [
        "python/sglang/multimodal_gen/test/server/test_server_common.py",
        "python/sglang/multimodal_gen/test/server/test_server_utils.py",
        "python/sglang/multimodal_gen/test/server/testcase_configs.py",
    ]

    for test_file in test_files:
        file_path = Path(f"{REPO}/{test_file}")
        if not file_path.exists():
            continue
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Test file {test_file} has syntax errors:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_check():
    """Ruff linting passes on modified file (CI standard)."""
    # Install ruff if not present
    subprocess.run(["pip", "install", "ruff", "-q"], check=False, capture_output=True)
    result = subprocess.run(
        ["ruff", "check", "--select=F401,F821", str(MODIFIED_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_black_format():
    """Black formatting check passes on modified file (CI standard)."""
    # Install black if not present
    subprocess.run(["pip", "install", "black", "-q"], check=False, capture_output=True)
    result = subprocess.run(
        ["black", "--check", str(MODIFIED_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Black format check failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_isort_check():
    """isort import ordering check passes on modified file (CI standard)."""
    # Install isort if not present
    subprocess.run(["pip", "install", "isort", "-q"], check=False, capture_output=True)
    result = subprocess.run(
        ["isort", "--check-only", str(MODIFIED_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"isort check failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_codespell():
    """Codespell passes on modified file (CI standard)."""
    # Install codespell if not present
    subprocess.run(["pip", "install", "codespell", "-q"], check=False, capture_output=True)
    result = subprocess.run(
        ["codespell", "--config", f"{REPO}/.codespellrc", str(MODIFIED_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Codespell check failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_pre_commit_check_ast():
    """Pre-commit check-ast passes on modified file (CI standard)."""
    # Install pre-commit if not present
    subprocess.run(["pip", "install", "pre-commit", "-q"], check=False, capture_output=True)
    result = subprocess.run(
        ["pre-commit", "run", "check-ast", "--files", str(MODIFIED_FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Pre-commit check-ast failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_pre_commit_debug_statements():
    """Pre-commit debug-statements check passes on modified file (CI standard)."""
    # Install pre-commit if not present
    subprocess.run(["pip", "install", "pre-commit", "-q"], check=False, capture_output=True)
    result = subprocess.run(
        ["pre-commit", "run", "debug-statements", "--files", str(MODIFIED_FILE)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Pre-commit debug-statements check failed:\n{result.stderr}"
