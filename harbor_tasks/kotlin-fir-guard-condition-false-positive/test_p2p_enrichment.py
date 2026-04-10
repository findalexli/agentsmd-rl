"""
Additional pass_to_pass tests for Kotlin FIR false positive fix.

These tests validate the repository structure and CI functionality using
actual subprocess.run() commands as required for origin: repo_tests.
"""

import subprocess
import os

REPO = "/workspace/kotlin"


def test_repo_git_status_clean():
    """
    Repo git status is clean at base commit (pass_to_pass).
    Runs actual git command via subprocess.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    assert r.stdout == "", f"git status not clean: {r.stdout}"


def test_repo_git_log_contains_test_commit():
    """
    Repo contains the test data commit for KT-85244 (pass_to_pass).
    Runs actual git log command via subprocess.
    """
    r = subprocess.run(
        ["git", "log", "--oneline", "-n", "5"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    assert "KT-85244" in r.stdout, f"Expected KT-85244 in git log, got: {r.stdout}"


def test_repo_gradle_wrapper_executable():
    """
    Gradle wrapper script exists and is executable (pass_to_pass).
    Verifies gradle wrapper is present.
    """
    r = subprocess.run(
        ["test", "-x", "./gradlew"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Gradle wrapper not executable at ./gradlew"


def test_repo_testdata_kt85244_file_exists():
    """
    Test data file for KT-85244 exists in expected location (pass_to_pass).
    Uses shell command to verify file existence.
    """
    test_file = os.path.join(
        REPO,
        "compiler/fir/analysis-tests/testData/resolve/when/falsePositiveDuplicateCodition.kt"
    )
    r = subprocess.run(
        ["test", "-f", test_file],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test data file not found: {test_file}"


def test_repo_checker_file_valid_kotlin():
    """
    Checker file has valid Kotlin syntax structure (pass_to_pass).
    Validates balanced braces and parentheses using Python parser via subprocess.
    """
    checker_file = os.path.join(
        REPO,
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt"
    )

    r = subprocess.run(
        ["python3", "-c",
         f"import sys; content=open('{checker_file}').read(); "
         f"sys.exit(0 if content.count('{{') == content.count('}}') and "
         f"content.count('(') == content.count(')') else 1)"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Checker file has unbalanced braces/parentheses"


def test_repo_testdata_has_required_directives():
    """
    Test data file has required directives (ISSUE, RUN_PIPELINE_TILL) (pass_to_pass).
    Validates test data structure using grep.
    """
    test_file = "compiler/fir/analysis-tests/testData/resolve/when/falsePositiveDuplicateCodition.kt"

    r = subprocess.run(
        ["grep", "-q", "ISSUE: KT-85244", test_file],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test data missing ISSUE: KT-85244 directive"

    r = subprocess.run(
        ["grep", "-q", "RUN_PIPELINE_TILL:", test_file],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test data missing RUN_PIPELINE_TILL directive"


def test_repo_checker_file_exists():
    """
    Checker file FirWhenConditionChecker.kt exists (pass_to_pass).
    Uses shell test command to verify file existence.
    """
    checker_file = os.path.join(
        REPO,
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt"
    )
    r = subprocess.run(
        ["test", "-f", checker_file],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Checker file not found: {checker_file}"


def test_repo_build_gradle_exists():
    """
    Build gradle file exists and contains analysis tests config (pass_to_pass).
    Verifies gradle project structure is valid.
    """
    build_file = os.path.join(REPO, "compiler/fir/analysis-tests/build.gradle.kts")

    r = subprocess.run(
        ["test", "-f", build_file],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Build file not found: {build_file}"

    r = subprocess.run(
        ["grep", "-q", "project-tests-convention", build_file],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Build file missing project-tests-convention plugin"


def test_repo_testdata_when_directory_exists():
    """
    When test data directory exists with .kt files (pass_to_pass).
    Uses shell commands to verify directory structure.
    """
    when_dir = os.path.join(REPO, "compiler/fir/analysis-tests/testData/resolve/when")

    r = subprocess.run(
        ["test", "-d", when_dir],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"When directory not found: {when_dir}"

    # Check for at least one .kt file
    r = subprocess.run(
        ["sh", "-c", f"ls {when_dir}/*.kt 2>/dev/null | head -1 | grep -q ."],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO,
    )
    assert r.returncode == 0, f"No .kt files found in {when_dir}"
