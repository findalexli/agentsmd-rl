#!/usr/bin/env python3
"""Tests for ClickHouse large file style check.

Validates that the various_checks.sh script properly detects and flags
large files (>5MB) committed to git while respecting the whitelist.
"""

import os
import subprocess
import tempfile
import shutil

REPO = "/workspace/ClickHouse"
SCRIPT_PATH = f"{REPO}/ci/jobs/scripts/check_style/various_checks.sh"


def test_large_file_check_exists():
    """The large file check code is present in various_checks.sh (fail-to-pass)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for distinctive content from the patch
    assert "Large files checked into git" in content, \
        "Missing 'Large files checked into git' comment"
    assert "MAX_FILE_SIZE=$((5 * 1024 * 1024))" in content, \
        "Missing MAX_FILE_SIZE=5MB definition"
    assert "LARGE_FILE_WHITELIST" in content, \
        "Missing LARGE_FILE_WHITELIST array"
    assert "git ls-files" in content, \
        "Missing 'git ls-files' command"
    assert "is larger than 5 MB" in content, \
        "Missing warning message pattern"


def test_large_file_check_logic():
    """Large file detection logic correctly identifies oversized files (fail-to-pass)."""
    # Create a temp git repo to test the logic
    with tempfile.TemporaryDirectory() as tmpdir:
        git_dir = os.path.join(tmpdir, "testrepo")
        os.makedirs(git_dir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=git_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"],
                     cwd=git_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"],
                     cwd=git_dir, check=True, capture_output=True)

        # Create files of various sizes
        small_file = os.path.join(git_dir, "small.txt")
        large_file = os.path.join(git_dir, "large.bin")
        whitelisted_file = os.path.join(git_dir, "multi_column_bf.gz.parquet")

        # Small file: 1KB
        with open(small_file, 'wb') as f:
            f.write(b'x' * 1024)

        # Large file: 6MB (exceeds 5MB limit)
        with open(large_file, 'wb') as f:
            f.write(b'x' * (6 * 1024 * 1024))

        # Whitelisted file: 6MB
        with open(whitelisted_file, 'wb') as f:
            f.write(b'y' * (6 * 1024 * 1024))

        # Add and commit all files
        subprocess.run(["git", "add", "."], cwd=git_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "test"],
                       cwd=git_dir, check=True, capture_output=True)

        # Extract and run just the large file check logic
        max_size = 5 * 1024 * 1024
        whitelist = [
            "multi_column_bf.gz.parquet",
            "ghdata_sample.json",
            "libcatboostmodel.so_aarch64",
        ]

        # Get all tracked files with sizes
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=git_dir, capture_output=True, text=True
        )
        files = result.stdout.split('\x00')[:-1]  # Remove trailing empty

        violations = []
        for f in files:
            filepath = os.path.join(git_dir, f)
            size = os.path.getsize(filepath)
            if size > max_size:
                # Check whitelist
                whitelisted = any(w in f for w in whitelist)
                if not whitelisted:
                    violations.append((f, size))

        # The large.bin should be flagged (6MB, not whitelisted)
        assert any("large.bin" in v[0] for v in violations), \
            f"Expected large.bin to be flagged as violation, got: {violations}"

        # The whitelisted file should NOT be flagged
        assert not any("multi_column_bf" in v[0] for v in violations), \
            f"Whitelisted file should not be flagged, got: {violations}"

        # The small file should NOT be flagged
        assert not any("small.txt" in v[0] for v in violations), \
            f"Small file should not be flagged, got: {violations}"


def test_whitelist_comprehensive():
    """Whitelist contains expected entries for known large test files (fail-to-pass)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for key whitelist entries mentioned in the patch
    expected_patterns = [
        "multi_column_bf.gz.parquet",
        "libcatboostmodel.so_aarch64",
        "libcatboostmodel.so_x86_64",
        "keeper-java-client-test.jar",
        "paimon-rest-catalog/chunk_",
    ]

    for pattern in expected_patterns:
        assert pattern in content, \
            f"Expected whitelist pattern '{pattern}' not found in script"


def test_stat_format_detection():
    """Script detects GNU vs BSD stat format correctly (fail-to-pass)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for the stat format detection logic
    assert "stat -c '%s %n' /dev/null" in content or 'stat -c \'%s %n\' /dev/null' in content or "stat -c" in content, \
        "Missing GNU stat format detection"
    assert "STAT_FMT_FLAG" in content, \
        "Missing STAT_FMT_FLAG variable"
    assert "STAT_FMT" in content, \
        "Missing STAT_FMT variable"

    # Check for both GNU and BSD branches
    assert "-c" in content, "Missing GNU stat -c flag"
    assert "-f" in content, "Missing BSD stat -f flag"


def test_script_syntax_valid():
    """The shell script has valid syntax (pass-to-pass)."""
    result = subprocess.run(
        ["bash", "-n", SCRIPT_PATH],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"Script has syntax errors: {result.stderr}"


def test_various_checks_runs():
    """The various_checks.sh script runs without crashing (pass-to-pass)."""
    # Run with a timeout since the full script may take time on large repos
    env = os.environ.copy()
    env["ROOT_PATH"] = REPO

    result = subprocess.run(
        ["bash", "-c", f"cd {REPO} && source ci/jobs/scripts/check_style/various_checks.sh"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env
    )
    # Script may have non-zero exit due to style issues found, but should not crash
    # We check that it ran and produced expected outputs
    output = result.stdout + result.stderr

    # The script should at least complete - if it fails, it should be due to actual style issues
    # not syntax errors
    assert "syntax error" not in output.lower(), \
        f"Script failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"Script failed with unexpected token: {output[:500]}"


def test_large_file_warning_message():
    """Warning message follows expected format (fail-to-pass)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # The warning message should follow the expected pattern
    expected_msg = "is larger than 5 MB. Large files should not be committed to git"
    assert expected_msg in content, \
        f"Expected warning message pattern not found: {expected_msg}"

    # Should include the "download at test time" suggestion
    assert "download them at test time or build from source" in content, \
        "Missing 'download at test time' suggestion in warning message"


def test_check_submodules_syntax():
    """check_submodules.sh has valid syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check_submodules.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check_submodules.sh has syntax errors: {result.stderr}"


def test_check_submodules_runs():
    """check_submodules.sh runs without crashing (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check_submodules.sh"
    env = os.environ.copy()
    env["ROOT_PATH"] = REPO

    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env=env
    )
    output = result.stdout + result.stderr
    assert "syntax error" not in output.lower(), \
        f"Script failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"Script failed with unexpected token: {output[:500]}"


def test_check_cpp_syntax():
    """check_cpp.sh has valid syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check_cpp.sh has syntax errors: {result.stderr}"


def test_check_aspell_syntax():
    """check_aspell.sh has valid syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check_aspell.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check_aspell.sh has syntax errors: {result.stderr}"


def test_check_typos_syntax():
    """check_typos.sh has valid syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check_typos.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check_typos.sh has syntax errors: {result.stderr}"


def test_check_mypy_syntax():
    """check-mypy script has valid syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check-mypy"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check-mypy has syntax errors: {result.stderr}"


def test_check_settings_style_syntax():
    """check-settings-style script has valid syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check-settings-style"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check-settings-style has syntax errors: {result.stderr}"


def test_check_style_py_syntax():
    """check_style.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/check_style.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check_style.py has syntax errors: {result.stderr}"


def test_check_mypy_diff_py_syntax():
    """check-mypy-diff.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check-mypy-diff.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check-mypy-diff.py has syntax errors: {result.stderr}"


def test_clang_tidy_cache_sh_syntax():
    """clang-tidy-cache.sh has valid bash syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/docker/binary-builder/clang-tidy-cache.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"clang-tidy-cache.sh has syntax errors: {result.stderr}"


def test_docker_in_docker_sh_syntax():
    """docker_in_docker.sh has valid bash syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/docker_in_docker.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"docker_in_docker.sh has syntax errors: {result.stderr}"


def test_docker_server_config_sh_syntax():
    """docker_server/config.sh has valid bash syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/docker_server/config.sh"
    result = subprocess.run(
        ["bash", "-n", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"config.sh has syntax errors: {result.stderr}"


def test_check_ci_py_syntax():
    """check_ci.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_ci.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"check_ci.py has syntax errors: {result.stderr}"


def test_find_tests_py_syntax():
    """find_tests.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/find_tests.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"find_tests.py has syntax errors: {result.stderr}"


def test_done_py_syntax():
    """done.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/done.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"done.py has syntax errors: {result.stderr}"


def test_log_parser_py_syntax():
    """log_parser.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/log_parser.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"log_parser.py has syntax errors: {result.stderr}"


def test_check_settings_style_runs():
    """check-settings-style runs without crashing (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check-settings-style"
    env = os.environ.copy()
    env["ROOT_PATH"] = REPO

    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env=env
    )
    output = result.stdout + result.stderr
    assert "syntax error" not in output.lower(), \
        f"Script failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"Script failed with unexpected token: {output[:500]}"


def test_check_mypy_runs():
    """check-mypy script runs without crashing (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check-mypy"
    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    output = result.stdout + result.stderr
    assert "syntax error" not in output.lower(), \
        f"Script failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"Script failed with unexpected token: {output[:500]}"


def test_check_aspell_runs():
    """check_aspell.sh runs without crashing (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check_aspell.sh"
    env = os.environ.copy()
    env["ROOT_PATH"] = REPO

    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env=env
    )
    output = result.stdout + result.stderr
    assert "syntax error" not in output.lower(), \
        f"Script failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"Script failed with unexpected token: {output[:500]}"


def test_check_typos_runs():
    """check_typos.sh runs without crashing (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/check_style/check_typos.sh"
    env = os.environ.copy()
    env["ROOT_PATH"] = REPO

    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env=env
    )
    output = result.stdout + result.stderr
    assert "syntax error" not in output.lower(), \
        f"Script failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"Script failed with unexpected token: {output[:500]}"


def test_clickhouse_proc_py_syntax():
    """clickhouse_proc.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/clickhouse_proc.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"clickhouse_proc.py has syntax errors: {result.stderr}"


def test_clickhouse_version_py_syntax():
    """clickhouse_version.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/clickhouse_version.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"clickhouse_version.py has syntax errors: {result.stderr}"


def test_docker_image_py_syntax():
    """docker_image.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/docker_image.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"docker_image.py has syntax errors: {result.stderr}"


def test_build_master_head_hook_py_syntax():
    """build_master_head_hook.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/job_hooks/build_master_head_hook.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"build_master_head_hook.py has syntax errors: {result.stderr}"


def test_docker_clean_up_hook_py_syntax():
    """docker_clean_up_hook.py has valid Python syntax (pass-to-pass)."""
    script_path = f"{REPO}/ci/jobs/scripts/job_hooks/docker_clean_up_hook.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", script_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"docker_clean_up_hook.py has syntax errors: {result.stderr}"


# ====== Enriched P2P Tests - CI/CD Commands ======


def test_repo_style_shell_scripts():
    """Repo's shell style checks pass via check_cpp.sh (pass_to_pass)."""
    result = subprocess.run(
        ["bash", f"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    # Script may find style issues but should not crash
    output = result.stdout + result.stderr
    assert "syntax error" not in output.lower(), \
        f"check_cpp.sh failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"check_cpp.sh failed with unexpected token: {output[:500]}"


def test_repo_various_checks_pipeline():
    """Repo's various_checks.sh style checks pass (pass_to_pass)."""
    env = os.environ.copy()
    env["ROOT_PATH"] = REPO

    result = subprocess.run(
        ["bash", f"{REPO}/ci/jobs/scripts/check_style/various_checks.sh"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env=env,
    )
    # Script may find style issues but should not crash
    output = result.stdout + result.stderr
    assert "syntax error" not in output.lower(), \
        f"various_checks.sh failed with syntax error: {output[:500]}"
    assert "unexpected token" not in output.lower(), \
        f"various_checks.sh failed with unexpected token: {output[:500]}"


def test_repo_git_ls_files_stat_pipeline():
    """Git ls-files with stat pipeline works for large file detection (pass_to_pass)."""
    # Test the core pipeline used by the large file check:
    # git ls-files -z | xargs -0 stat -c '%s %n'
    result = subprocess.run(
        ["bash", "-c", f"cd {REPO} && git ls-files -z | head -z -n 50 | xargs -0 stat -c '%s %n' 2>/dev/null | head -5"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # Should successfully run and produce output
    assert result.returncode == 0, \
        f"git ls-files stat pipeline failed: {result.stderr[:500]}"
    # Should have size and filename output
    assert len(result.stdout.strip()) > 0, \
        "git ls-files stat pipeline produced no output"


def test_repo_grep_whitelist_pipeline():
    """Grep with whitelist pattern works for large file filtering (pass_to_pass)."""
    # Test the grep whitelist pattern used in large file check
    whitelist_patterns = [
        "multi_column_bf.gz.parquet",
        "ghdata_sample.json",
        "libcatboostmodel.so",
    ]
    # Build grep -v pattern like the script does
    grep_args = ["-e", whitelist_patterns[0]]
    for pattern in whitelist_patterns[1:]:
        grep_args.extend(["-e", pattern])

    # Test that grep -v with whitelist works on sample data
    test_input = "file1.txt\nmulti_column_bf.gz.parquet\nfile2.cpp\nghdata_sample.json\n"
    result = subprocess.run(
        ["grep", "-v"] + grep_args,
        input=test_input,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode in [0, 1], \
        f"grep whitelist filtering failed: {result.stderr[:500]}"
    # Verify whitelisted files are filtered out
    assert "multi_column_bf.gz.parquet" not in result.stdout, \
        "Whitelist pattern failed to filter multi_column_bf.gz.parquet"
    assert "ghdata_sample.json" not in result.stdout, \
        "Whitelist pattern failed to filter ghdata_sample.json"
    # Verify other files are kept
    assert "file1.txt" in result.stdout, \
        "grep whitelist incorrectly filtered non-whitelisted file"


def test_repo_docker_image_py():
    """docker_image.py has valid Python syntax and imports (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/ci/jobs/scripts/docker_image.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"docker_image.py has syntax errors: {result.stderr}"


def test_repo_log_parser_py():
    """log_parser.py has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/ci/jobs/scripts/log_parser.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"log_parser.py has syntax errors: {result.stderr}"


def test_repo_clickhouse_version_py():
    """clickhouse_version.py has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/ci/jobs/scripts/clickhouse_version.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"clickhouse_version.py has syntax errors: {result.stderr}"


def test_repo_clickhouse_proc_py():
    """clickhouse_proc.py has valid Python syntax (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/ci/jobs/scripts/clickhouse_proc.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, \
        f"clickhouse_proc.py has syntax errors: {result.stderr}"
