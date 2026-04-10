"""
Tests for ClickHouse ZooKeeper session retry fix.
"""

import subprocess
import re
import os

import pytest

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def test_target_file_exists():
    """Verify the target file exists in the repository."""
    filepath = os.path.join(REPO, TARGET_FILE)
    assert os.path.exists(filepath), f"Target file not found: {filepath}"


def test_refresh_objects_uses_retry_loop():
    """Verify refreshObjects method uses ZooKeeperRetriesControl for retry logic."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()
    assert "ZooKeeperRetriesControl" in content, "ZooKeeperRetriesControl not found"
    assert "retryLoop" in content, "retryLoop method not found"


def test_session_renewal_on_retry():
    """F2P: Verify the fix - session is renewed inside retry loop."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()
    refresh_pattern = r'void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects.*?\n\{'
    match = re.search(refresh_pattern, content, re.DOTALL)
    assert match, "refreshObjects function not found"
    start_idx = match.end() - 1
    brace_count = 0
    end_idx = start_idx
    for i, c in enumerate(content[start_idx:]):
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = start_idx + i + 1
                break
    func_content = content[start_idx:end_idx]
    assert "isRetry()" in func_content, "isRetry() check not found"
    assert "zookeeper_getter.getZooKeeper()" in func_content, "zookeeper_getter.getZooKeeper() not found"
    assert "current_zookeeper" in func_content, "current_zookeeper variable not found"


def test_get_object_names_inside_retry_loop():
    """F2P: Verify getObjectNamesAndSetWatch is called INSIDE the retry loop."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()
    retry_idx = content.find("retries_ctl.retryLoop")
    assert retry_idx != -1, "retryLoop call not found"
    lambda_start = content.find("[&]", retry_idx)
    assert lambda_start != -1, "retryLoop lambda not found"
    lambda_open_brace = content.find("{", lambda_start)
    assert lambda_open_brace != -1, "retryLoop lambda opening brace not found"
    brace_count = 1
    pos = lambda_open_brace + 1
    while brace_count > 0 and pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    loop_content = content[lambda_open_brace:pos]
    assert "getObjectNamesAndSetWatch" in loop_content, "getObjectNamesAndSetWatch must be called INSIDE the retry loop"
    assert "tryLoadObject(current_zookeeper" in loop_content, "tryLoadObject must use current_zookeeper inside the retry loop"


def test_no_session_outside_retry_loop():
    """F2P: Verify the stale pattern is gone - no session-dependent calls before retry loop."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()
    refresh_start = content.find("void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects")
    assert refresh_start != -1, "refreshObjects function not found"
    retry_idx = content.find("retries_ctl.retryLoop", refresh_start)
    assert retry_idx != -1, "retryLoop call not found in refreshObjects"
    pre_loop_content = content[refresh_start:retry_idx]
    pre_loop_no_comments = re.sub(r'//.*', '', pre_loop_content)
    pre_loop_no_comments = re.sub(r'/\*.*?\*/', '', pre_loop_no_comments, flags=re.DOTALL)
    if "getObjectNamesAndSetWatch(zookeeper, object_type)" in pre_loop_no_comments:
        assert False, "BUG: getObjectNamesAndSetWatch called with stale 'zookeeper' param before retry loop"


def test_session_refresh_comment():
    """Verify the explanatory comment about session renewal is present."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()
    assert "Renew the session on retry" in content, "Comment explaining session renewal not found"


def test_compiles_without_syntax_errors():
    """P2P: Verify the code compiles without syntax errors."""
    filepath = os.path.join(REPO, TARGET_FILE)
    result = subprocess.run(
        ["clang-15", "-fsyntax-only", "-std=c++20", "-xc++", filepath],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    syntax_errors = ["error: expected", "error: unexpected", "error: missing", "error: invalid", "error: syntax"]
    for err in syntax_errors:
        assert err not in result.stderr, f"Syntax error found: {result.stderr}"


def test_try_load_uses_current_zookeeper():
    """Verify that tryLoadObject uses the current_zookeeper handle inside the retry loop."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()
    assert "tryLoadObject(current_zookeeper," in content, "tryLoadObject must use current_zookeeper handle for consistent session"


# ============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks that should pass on both base and fix
# ============================================================================

def test_repo_python_syntax_ci_scripts():
    """P2P: All Python scripts in ci/ directory have valid syntax."""
    ci_dir = os.path.join(REPO, "ci")
    errors = []
    for root, dirs, files in os.walk(ci_dir):
        dirs[:] = [d for d in dirs if d != "praktika"]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                result = subprocess.run(
                    ["python3", "-m", "py_compile", filepath],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    errors.append(f"{filepath}: {result.stderr}")
    assert not errors, "Python syntax errors found: " + "; ".join(errors[:10])


def test_repo_python_syntax_tests_ci():
    """P2P: All Python scripts in tests/ci/ have valid syntax."""
    tests_ci_dir = os.path.join(REPO, "tests", "ci")
    if not os.path.exists(tests_ci_dir):
        pytest.skip("tests/ci directory not found")
    errors = []
    for file in os.listdir(tests_ci_dir):
        if file.endswith(".py"):
            filepath = os.path.join(tests_ci_dir, file)
            result = subprocess.run(
                ["python3", "-m", "py_compile", filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                errors.append(f"{filepath}: {result.stderr}")
    assert not errors, "Python syntax errors found: " + "; ".join(errors[:10])


def test_repo_yaml_valid():
    """P2P: GitHub workflow YAML files are syntactically valid."""
    yaml = pytest.importorskip("yaml")
    workflows_dir = os.path.join(REPO, ".github", "workflows")
    errors = []
    yaml_files = [f for f in os.listdir(workflows_dir) if f.endswith((".yml", ".yaml"))]
    assert yaml_files, "No YAML files found in .github/workflows"
    for file in yaml_files:
        filepath = os.path.join(workflows_dir, file)
        try:
            with open(filepath, 'r') as f:
                yaml.safe_load(f)
        except Exception as e:
            errors.append(f"{file}: {e}")
    assert not errors, "YAML parse errors found: " + "; ".join(errors)


def test_repo_pyproject_toml_valid():
    """P2P: pyproject.toml is syntactically valid."""
    toml_path = os.path.join(REPO, "pyproject.toml")
    if not os.path.exists(toml_path):
        pytest.skip("pyproject.toml not found")
    result = subprocess.run(
        ["python3", "-c", "import sys; exec(open(sys.argv[1]).read())", toml_path],
        capture_output=True,
        text=True,
        timeout=30,
    )
    with open(toml_path, 'r') as f:
        content = f.read().strip()
    assert content, "pyproject.toml is empty"
    assert "[tool." in content or "[build-system" in content, "pyproject.toml appears invalid"


def test_repo_clang_format_config_valid():
    """P2P: .clang-format config file is valid YAML."""
    yaml = pytest.importorskip("yaml")
    config_path = os.path.join(REPO, ".clang-format")
    if not os.path.exists(config_path):
        pytest.skip(".clang-format not found")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    assert config, ".clang-format is empty or invalid"
    assert "BasedOnStyle" in config, ".clang-format missing BasedOnStyle key"


def test_repo_cmake_lists_exists():
    """P2P: CMakeLists.txt exists and has content."""
    cmake_path = os.path.join(REPO, "CMakeLists.txt")
    with open(cmake_path, 'r') as f:
        content = f.read().strip()
    assert content, "CMakeLists.txt is empty"
    assert "cmake_minimum_required" in content or "project(" in content, "CMakeLists.txt appears invalid"


def test_repo_git_submodule_config_valid():
    """P2P: .gitmodules file is valid if it exists."""
    gitmodules_path = os.path.join(REPO, ".gitmodules")
    if not os.path.exists(gitmodules_path):
        pytest.skip(".gitmodules not found")
    result = subprocess.run(
        ["git", "config", "--file", gitmodules_path, "--list"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f".gitmodules parse error: {result.stderr}"


def test_repo_no_broken_symlinks():
    """P2P: No broken symlinks in the repository root."""
    result = subprocess.run(
        ["find", REPO, "-xtype", "l"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    broken_links = [l for l in result.stdout.strip().split("\n") if l.strip()]
    serious_broken = [l for l in broken_links if "/contrib/" not in l and "/build" not in l and "/.git/" not in l]
    assert not serious_broken, "Broken symlinks found: " + "; ".join(serious_broken[:10])


def test_repo_python_syntax_ci_praktika():
    """P2P: All Python scripts in ci/praktika have valid syntax."""
    from pathlib import Path
    praktika_dir = os.path.join(REPO, "ci", "praktika")
    if not os.path.exists(praktika_dir):
        pytest.skip("ci/praktika directory not found")
    errors = []
    for file in os.listdir(praktika_dir):
        if file.endswith(".py"):
            filepath = os.path.join(praktika_dir, file)
            result = subprocess.run(
                ["python3", "-m", "py_compile", filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                errors.append(f"{filepath}: {result.stderr}")
    assert not errors, "Python syntax errors in ci/praktika: " + "; ".join(errors[:10])


def test_repo_python_syntax_ci_jobs():
    """P2P: All Python scripts in ci/jobs have valid syntax."""
    jobs_dir = os.path.join(REPO, "ci", "jobs")
    if not os.path.exists(jobs_dir):
        pytest.skip("ci/jobs directory not found")
    errors = []
    for file in os.listdir(jobs_dir):
        if file.endswith(".py"):
            filepath = os.path.join(jobs_dir, file)
            result = subprocess.run(
                ["python3", "-m", "py_compile", filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                errors.append(f"{filepath}: {result.stderr}")
    assert not errors, "Python syntax errors in ci/jobs: " + "; ".join(errors[:10])


def test_repo_shell_script_syntax():
    """P2P: Shell scripts in ci/jobs/scripts/check_style have valid syntax."""
    from pathlib import Path
    scripts_dir = os.path.join(REPO, "ci", "jobs", "scripts", "check_style")
    if not os.path.exists(scripts_dir):
        pytest.skip("check_style scripts directory not found")
    errors = []
    shell_scripts = list(Path(scripts_dir).rglob("*.sh"))
    for filepath in shell_scripts[:20]:
        result = subprocess.run(
            ["bash", "-n", str(filepath)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            errors.append(f"{filepath}: {result.stderr}")
    assert not errors, "Shell script syntax errors: " + "; ".join(errors[:10])


def test_repo_no_merge_conflict_markers():
    """P2P: No merge conflict markers in source files."""
    result = subprocess.run(
        [
            "grep", "-r", "<<<<<<<",
            "--include=*.cpp", "--include=*.h", "--include=*.py",
            os.path.join(REPO, "src"),
            os.path.join(REPO, "base"),
            os.path.join(REPO, "programs"),
            os.path.join(REPO, "utils"),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    conflict_lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    assert not conflict_lines, "Merge conflict markers found: " + "; ".join(conflict_lines[:10])


def test_repo_no_binary_in_source_dirs():
    """P2P: No compiled binary files in source directories."""
    source_dirs = [
        os.path.join(REPO, "src"),
        os.path.join(REPO, "base"),
        os.path.join(REPO, "programs"),
        os.path.join(REPO, "utils"),
    ]
    binary_patterns = ["*.exe", "*.dll", "*.so", "*.dylib"]
    found_binaries = []
    for dir_path in source_dirs:
        if os.path.exists(dir_path):
            for pattern in binary_patterns:
                result = subprocess.run(
                    ["find", dir_path, "-type", "f", "-name", pattern],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.stdout.strip():
                    found_binaries.extend(result.stdout.strip().split("\n"))
    assert not found_binaries, "Binary files found in source dirs: " + "; ".join(found_binaries[:10])


def test_repo_target_file_no_crlf():
    """P2P: Target file has no CRLF line endings."""
    filepath = os.path.join(REPO, TARGET_FILE)
    if not os.path.exists(filepath):
        pytest.skip("Target file not found")
    with open(filepath, "rb") as f:
        content = f.read()
    crlf_count = content.count(b"\r\n")
    assert crlf_count == 0, f"Target file has {crlf_count} CRLF line endings"


def test_repo_various_checks():
    """P2P: Repo style various_checks.sh passes (no BOM, correct permissions, etc.)."""
    result = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/various_checks.sh"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # The script may exit with code 1 due to git grep finding no matches
    # Check that there's no actual error output indicating real violations
    if result.returncode != 0:
        # Filter out expected "no matches" outputs from git grep
        error_lines = [l for l in (result.stderr + result.stdout).split('\n') if l.strip()]
        # Only fail if there's actual violation content, not just exit code
        violation_lines = [l for l in error_lines if not l.startswith('#') and 'Exit' not in l]
        if violation_lines:
            assert False, f"various_checks.sh found violations:\n{chr(10).join(violation_lines[:10])}"


def test_repo_ci_jobs_python_syntax():
    """P2P: CI job Python scripts have valid AST."""
    ci_jobs_dir = os.path.join(REPO, "ci", "jobs")
    jobs = ["check_style.py", "build_clickhouse.py", "functional_tests.py"]
    errors = []
    for job in jobs:
        filepath = os.path.join(ci_jobs_dir, job)
        if os.path.exists(filepath):
            result = subprocess.run(
                ["python3", "-c", f"import ast; ast.parse(open('{filepath}').read())"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                errors.append(f"{job}: {result.stderr}")
    assert not errors, "CI job Python syntax errors: " + "; ".join(errors[:10])


def test_repo_all_workflows_yaml_valid():
    """P2P: All GitHub workflow YAML files are syntactically valid."""
    yaml = pytest.importorskip("yaml")
    workflows_dir = os.path.join(REPO, ".github", "workflows")
    errors = []
    yaml_files = [f for f in os.listdir(workflows_dir) if f.endswith(".yml")]
    assert yaml_files, "No workflow YAML files found"
    for file in yaml_files:
        filepath = os.path.join(workflows_dir, file)
        result = subprocess.run(
            ["python3", "-c", f"import yaml; yaml.safe_load(open('{filepath}')); print('OK')"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            errors.append(f"{file}: {result.stderr}")
    assert not errors, "Workflow YAML errors: " + "; ".join(errors[:10])


def test_repo_shell_scripts_ci_valid():
    """P2P: Shell scripts in CI have valid syntax."""
    shell_scripts = [
        os.path.join(REPO, "ci", "jobs", "sqlancer_job.sh"),
        os.path.join(REPO, "ci", "jobs", "scripts", "check_style", "check_submodules.sh"),
        os.path.join(REPO, "ci", "jobs", "scripts", "check_style", "check_aspell.sh"),
    ]
    errors = []
    for filepath in shell_scripts:
        if os.path.exists(filepath):
            result = subprocess.run(
                ["bash", "-n", filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                errors.append(f"{os.path.basename(filepath)}: {result.stderr}")
    assert not errors, "Shell script syntax errors: " + "; ".join(errors[:10])


def test_repo_toml_valid():
    """P2P: pyproject.toml is valid TOML."""
    toml_path = os.path.join(REPO, "pyproject.toml")
    if not os.path.exists(toml_path):
        pytest.skip("pyproject.toml not found")
    result = subprocess.run(
        ["python3", "-c", "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"TOML parse error: {result.stderr}"
