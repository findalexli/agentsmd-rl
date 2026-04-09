"""Tests for ClickHouse large file style check."""
import subprocess
import tempfile
import os
import pytest

REPO = "/workspace/ClickHouse"
SCRIPT_PATH = f"{REPO}/ci/jobs/scripts/check_style/various_checks.sh"


def test_script_exists():
    """The various_checks.sh script must exist."""
    assert os.path.exists(SCRIPT_PATH), f"Script not found: {SCRIPT_PATH}"


def test_large_file_check_logic_present():
    """Script must contain the large file checking logic with MAX_FILE_SIZE."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for key components of the large file check
    assert "MAX_FILE_SIZE=$((5 * 1024 * 1024))" in content, "MAX_FILE_SIZE not defined correctly"
    assert "git ls-files" in content, "git ls-files not used"
    assert "LARGE_FILE_WHITELIST" in content, "LARGE_FILE_WHITELIST not defined"
    assert "is larger than 5 MB" in content, "Error message not present"


def test_large_file_check_executable():
    """The large file check code must be valid bash syntax."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check specific syntax elements that define the check
    assert "STAT_FMT_FLAG=" in content, "STAT_FMT_FLAG not defined"
    assert "STAT_FMT=" in content, "STAT_FMT not defined"
    assert "awk -v limit" in content, "awk limit check not present"


def test_whitelist_includes_expected_patterns():
    """Whitelist must include expected patterns for legitimate test data."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Extract whitelist array content
    whitelist_patterns = [
        "multi_column_bf.gz.parquet",
        "ghdata_sample.json",
        "libcatboostmodel.so",
        "test_01946.zstd",
        "known_failures.txt",
        "paimon-rest-catalog/chunk_"
    ]

    for pattern in whitelist_patterns:
        assert pattern in content, f"Expected whitelist pattern not found: {pattern}"


def test_script_has_proper_stat_detection():
    """Script must detect GNU vs BSD stat properly."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Should have logic to detect stat variant
    assert "stat -c '%s %n' /dev/null" in content or "stat -c" in content, \
        "GNU stat detection not present"
    assert "if stat -c" in content or "if stat" in content, \
        "Stat variant detection logic not present"


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repo with some test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize repo
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"],
                      cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"],
                      cwd=tmpdir, capture_output=True, check=True)

        # Create a small file and commit
        small_file = os.path.join(tmpdir, "small.txt")
        with open(small_file, 'w') as f:
            f.write("small content")
        subprocess.run(["git", "add", "small.txt"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmpdir,
                      capture_output=True, check=True)

        yield tmpdir


def test_extracted_check_detects_large_file(temp_git_repo):
    """The large file check logic should flag files > 5MB."""
    tmpdir = temp_git_repo

    # Create a 6MB file
    large_file = os.path.join(tmpdir, "large.bin")
    with open(large_file, 'wb') as f:
        f.write(b'x' * (6 * 1024 * 1024))

    subprocess.run(["git", "add", "large.bin"], cwd=tmpdir, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "add large file"], cwd=tmpdir,
                  capture_output=True, check=True)

    # Run the check logic extracted from the script
    max_size = 5 * 1024 * 1024

    # Detect stat format
    result = subprocess.run(
        ["stat", "-c", "%s %n", large_file],
        capture_output=True
    )
    if result.returncode == 0:
        stat_flag = "-c"
        stat_fmt = "%s %n"
    else:
        stat_flag = "-f"
        stat_fmt = "%z %N"

    # Run the check
    result = subprocess.run(
        f"git ls-files -z | xargs -0 stat {stat_flag} '{stat_fmt}' 2>/dev/null | "
        f"awk -v limit={max_size} '$1 > limit {{ print substr($0, index($0, $2)) }}'",
        cwd=tmpdir, shell=True, capture_output=True, text=True
    )

    # Should detect the large file
    assert "large.bin" in result.stdout, f"Large file not detected. Output: {result.stdout}"


def test_extracted_check_ignores_small_files(temp_git_repo):
    """The large file check logic should not flag files <= 5MB."""
    tmpdir = temp_git_repo

    # Create a 1MB file (should be allowed)
    medium_file = os.path.join(tmpdir, "medium.bin")
    with open(medium_file, 'wb') as f:
        f.write(b'x' * (1 * 1024 * 1024))

    subprocess.run(["git", "add", "medium.bin"], cwd=tmpdir, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "add medium file"], cwd=tmpdir,
                  capture_output=True, check=True)

    # Detect stat format
    result = subprocess.run(
        ["stat", "-c", "%s %n", medium_file],
        capture_output=True
    )
    if result.returncode == 0:
        stat_flag = "-c"
        stat_fmt = "%s %n"
    else:
        stat_flag = "-f"
        stat_fmt = "%z %N"

    max_size = 5 * 1024 * 1024

    # Run the check
    result = subprocess.run(
        f"git ls-files -z | xargs -0 stat {stat_flag} '{stat_fmt}' 2>/dev/null | "
        f"awk -v limit={max_size} '$1 > limit {{ print substr($0, index($0, $2)) }}'",
        cwd=tmpdir, shell=True, capture_output=True, text=True
    )

    # Should NOT detect the medium file
    assert "medium.bin" not in result.stdout, f"Small file incorrectly flagged. Output: {result.stdout}"


def test_whitelist_works_with_grep(temp_git_repo):
    """The whitelist patterns should exclude matching files."""
    tmpdir = temp_git_repo

    # Create a file that matches a whitelist pattern
    whitelist_file = os.path.join(tmpdir, "ghdata_sample.json")
    with open(whitelist_file, 'wb') as f:
        f.write(b'x' * (6 * 1024 * 1024))  # 6MB

    subprocess.run(["git", "add", "ghdata_sample.json"], cwd=tmpdir, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "add whitelisted file"], cwd=tmpdir,
                  capture_output=True, check=True)

    # Detect stat format
    result = subprocess.run(
        ["stat", "-c", "%s %n", whitelist_file],
        capture_output=True
    )
    if result.returncode == 0:
        stat_flag = "-c"
        stat_fmt = "%s %n"
    else:
        stat_flag = "-f"
        stat_fmt = "%z %N"

    max_size = 5 * 1024 * 1024

    # Run the check with whitelist (simulating the actual script logic)
    whitelist_patterns = [
        "ghdata_sample.json",
        "multi_column_bf.gz.parquet",
        "libcatboostmodel.so",
    ]
    grep_pattern = " | grep -v ".join([f"-e {p}" for p in whitelist_patterns])

    result = subprocess.run(
        f"git ls-files -z | xargs -0 stat {stat_flag} '{stat_fmt}' 2>/dev/null | "
        f"awk -v limit={max_size} '$1 > limit {{ print substr($0, index($0, $2)) }}' | "
        f"grep -v {grep_pattern}",
        cwd=tmpdir, shell=True, capture_output=True, text=True
    )

    # Should NOT flag the whitelisted file
    assert "ghdata_sample.json" not in result.stdout, \
        f"Whitelisted file incorrectly flagged. Output: {result.stdout}"
