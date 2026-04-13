"""
Task: sglang-flaky-test-load-weights-fix
Repo: sglang @ df9c831ab80c78495142b4dbcb1dfa537c9e1c73
PR:   22150

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This is a GPU-dependent test, so we verify the fix via AST parsing:
1. The remote_instance_weight_loader_start_seed_via_transfer_engine parameter
   is now hardcoded to False (not conditional on backend)
2. The FIXME comment about random behavior refactoring is added
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = "test/registered/distributed/test_load_weights_from_remote_instance.py"


def get_test_file_content():
    """Read the test file content."""
    path = Path(f"{REPO}/{TEST_FILE}")
    if not path.exists():
        raise FileNotFoundError(f"Test file not found: {path}")
    return path.read_text()


def parse_test_file():
    """Parse the test file and return AST."""
    content = get_test_file_content()
    return ast.parse(content)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Test file must parse without errors."""
    content = get_test_file_content()
    tree = ast.parse(content)
    assert tree is not None, "Failed to parse test file"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base commit
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_python_syntax_check():
    """Repo's Python syntax check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linting passes (pass_to_pass)."""
    # Install ruff if needed
    install_r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert install_r.returncode == 0, f"Failed to install ruff: {install_r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black_check():
    """Repo's black formatting check passes (pass_to_pass)."""
    # Install black if needed
    install_r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert install_r.returncode == 0, f"Failed to install black: {install_r.stderr}"

    r = subprocess.run(
        ["black", "--check", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Black formatting check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_codespell_check():
    """Repo's codespell check passes (pass_to_pass)."""
    # Install codespell if needed
    install_r = subprocess.run(
        ["pip", "install", "codespell", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert install_r.returncode == 0, f"Failed to install codespell: {install_r.stderr}"

    r = subprocess.run(
        ["codespell", "--config", f"{REPO}/.codespellrc", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Codespell check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_check():
    """Repo's isort import sorting check passes (pass_to_pass)."""
    # Install isort if needed
    install_r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert install_r.returncode == 0, f"Failed to install isort: {install_r.stderr}"

    r = subprocess.run(
        ["isort", "--check", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_toml_check():
    """Repo's TOML files are valid (pass_to_pass)."""
    # Install tomli if needed (tomli is built-in for Python 3.11+, but install for safety)
    install_r = subprocess.run(
        ["pip", "install", "tomli", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert install_r.returncode == 0, f"Failed to install tomli: {install_r.stderr}"

    r = subprocess.run(
        ["python3", "-c", "import tomli; tomli.load(open('.github/linters/lychee.toml', 'rb'))"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_yaml_check():
    """Repo's YAML files are valid (pass_to_pass)."""
    # Install PyYAML if needed
    install_r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60
    )
    assert install_r.returncode == 0, f"Failed to install pyyaml: {install_r.stderr}"

    r = subprocess.run(
        ["python3", "-c", "import yaml; yaml.safe_load(open('.github/workflows/lint.yml'))"],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_ast_check():
    """Repo's Python AST check passes via pre-commit (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-ast", "--files", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Pre-commit AST check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_debug_statements():
    """Repo has no debug statements (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "debug-statements", "--files", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Debug statements check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_symlinks():
    """Repo has no broken symlinks (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-symlinks", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Symlinks check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_trailing_whitespace():
    """Repo has no trailing whitespace (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "trailing-whitespace", "--files", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Trailing whitespace check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_end_of_file_fixer():
    """Repo has proper end-of-file newlines (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "end-of-file-fixer", "--files", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"End-of-file fixer check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_check_yaml():
    """Repo's YAML files pass pre-commit check (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"YAML check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_check_toml():
    """Repo's TOML files pass pre-commit check (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-toml", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"TOML check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_check_merge_conflict():
    """Repo has no merge conflict markers (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-merge-conflict", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Merge conflict check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_transfer_engine_flag_hardcoded_false():
    """remote_instance_weight_loader_start_seed_via_transfer_engine must be hardcoded to False.

    Before: remote_instance_weight_loader_start_seed_via_transfer_engine=(
                remote_instance_loader_backend == "transfer_engine"
            )
    After:  remote_instance_weight_loader_start_seed_via_transfer_engine=False
    """
    tree = parse_test_file()

    found_engine_init = False
    found_hardcoded_false = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is an sgl.Engine call
            func_name = None
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id

            if func_name == "Engine" or func_name == "sgl" or (
                isinstance(node.func, ast.Attribute) and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == "sgl" and
                node.func.attr == "Engine"
            ):
                found_engine_init = True

                # Check for the remote_instance_weight_loader_start_seed_via_transfer_engine keyword
                for kw in node.keywords:
                    if kw.arg == "remote_instance_weight_loader_start_seed_via_transfer_engine":
                        # Check if it's a constant False
                        if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                            found_hardcoded_false = True
                        else:
                            raise AssertionError(
                                "remote_instance_weight_loader_start_seed_via_transfer_engine is not hardcoded False"
                            )

    assert found_engine_init, "Could not find sgl.Engine() call in the test file"
    assert found_hardcoded_false, (
        "remote_instance_weight_loader_start_seed_via_transfer_engine is not hardcoded to False. "
        "The fix should set it to False unconditionally, not conditional on backend type."
    )


# [pr_diff] fail_to_pass
def test_fixme_comment_added():
    """FIXME comment about random behavior must be added before the random.choice calls.

    Before: no FIXME comment
    After:  # FIXME: refactor this test to have less random behavior
    """
    content = get_test_file_content()

    # Check for the FIXME comment
    assert "# FIXME: refactor this test to have less random behavior" in content, (
        "FIXME comment about random behavior is missing. "
        "The fix should add a comment indicating the test needs refactoring."
    )


# [pr_diff] fail_to_pass
def test_no_conditional_transfer_engine_expression():
    """The conditional expression checking backend == 'transfer_engine' must be removed.

    Before: remote_instance_weight_loader_backend == "transfer_engine"
            was used as the value for remote_instance_weight_loader_start_seed_via_transfer_engine
    After:  hardcoded False
    """
    content = get_test_file_content()
    tree = ast.parse(content)

    # Find the init_process_dst function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "init_process_dst":
            # Check that there's no Compare node checking for "transfer_engine"
            for child in ast.walk(node):
                if isinstance(child, ast.Compare):
                    # Check if comparing against the string "transfer_engine"
                    if any(isinstance(comp, ast.Constant) and
                           comp.value == "transfer_engine"
                           for comp in child.comparators):
                        # This is OK if it's in the comment or elsewhere,
                        # but we should verify it's not in the Engine() call
                        pass

    # More specific check: look at the sgl.Engine call specifically
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id

            if func_name == "Engine":
                for kw in node.keywords:
                    if kw.arg == "remote_instance_weight_loader_start_seed_via_transfer_engine":
                        # Must be a constant, not a Compare expression
                        if isinstance(kw.value, ast.Compare):
                            raise AssertionError(
                                "Found conditional expression for "
                                "remote_instance_weight_loader_start_seed_via_transfer_engine. "
                                "It should be hardcoded to False."
                            )


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_structure_intact():
    """The test file should still have the expected structure."""
    tree = parse_test_file()

    # Check for key imports
    import_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            import_names.add(node.module)

    # Key imports should exist
    assert "sglang" in import_names or "sgl" in str(tree), "sglang import missing"
    assert "torch" in import_names or "torch" in str(tree), "torch import missing"

    # Check for key functions
    func_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "init_process_dst" in func_names, "init_process_dst function missing"
    assert "test_load_weights_from_remote_instance" in func_names, "Test function missing"


# [static] pass_to_pass
def test_not_stub():
    """The fix is not a stub - it has real logic changes."""
    content = get_test_file_content()

    # The fix should contain hardcoded False for the parameter
    assert "remote_instance_weight_loader_start_seed_via_transfer_engine=False" in content, (
        "The fix must hardcode False for remote_instance_weight_loader_start_seed_via_transfer_engine"
    )

    # Should NOT contain the old conditional pattern
    old_pattern = 'remote_instance_loader_backend == "transfer_engine"'
    assert old_pattern not in content, (
        f"The old conditional pattern '{old_pattern}' should be removed"
    )


# [repo_tests] pass_to_pass
def test_repo_precommit_check_added_large_files():
    """Repo has no large files added (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "check-added-large-files", "--files", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Large files check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_detect_private_key():
    """Repo has no private keys committed (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "detect-private-key", "--files", f"{REPO}/{TEST_FILE}"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Private key detection failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_destroyed_symlinks():
    """Repo has no destroyed symlinks (pass_to_pass)."""
    install_r = subprocess.run(
        ["pip", "install", "pre-commit", "-q"],
        capture_output=True, text=True, timeout=120
    )
    assert install_r.returncode == 0, f"Failed to install pre-commit: {install_r.stderr}"

    r = subprocess.run(
        ["pre-commit", "run", "destroyed-symlinks", "--all-files"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Destroyed symlinks check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
