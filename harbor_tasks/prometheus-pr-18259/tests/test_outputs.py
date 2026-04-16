"""Tests for prometheus file discovery atomic write fix.

This tests that the file discovery tests use atomic file writes to avoid
race conditions with fsnotify where the watcher could read an empty/truncated
file between truncate and write operations.
"""

import subprocess
import sys
import os

REPO = "/workspace/prometheus"
TEST_FILE = f"{REPO}/discovery/file/file_test.go"


def test_atomicwrite_function_exists():
    """The atomicWrite helper function must exist in file_test.go (fail_to_pass)."""
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # Check for atomicWrite function definition
    assert "func (t *testRunner) atomicWrite" in content, \
        "atomicWrite helper function not found in file_test.go"

    # Check that it uses os.CreateTemp
    assert "os.CreateTemp" in content, \
        "atomicWrite should use os.CreateTemp for temporary files"

    # Check that it uses os.Rename for atomic operation
    assert "os.Rename" in content, \
        "atomicWrite should use os.Rename for atomic file replacement"


def test_copyfileto_uses_atomicwrite():
    """copyFileTo must use atomicWrite instead of os.WriteFile (fail_to_pass)."""
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # Find the copyFileTo function and check it uses atomicWrite
    assert "t.atomicWrite(dst, content)" in content, \
        "copyFileTo should call t.atomicWrite instead of os.WriteFile"

    # Should not use os.WriteFile directly anymore
    # Note: We check the function context - the old code had os.WriteFile in copyFileTo
    lines = content.split('\n')
    in_copyfileto = False
    found_atomicwrite_call = False
    found_direct_writefile = False

    for line in lines:
        if 'func (t *testRunner) copyFileTo' in line:
            in_copyfileto = True
        elif in_copyfileto and line.startswith('func '):
            in_copyfileto = False
        elif in_copyfileto:
            if 'atomicWrite' in line:
                found_atomicwrite_call = True
            if 'os.WriteFile' in line:
                found_direct_writefile = True

    assert found_atomicwrite_call, \
        "copyFileTo must call atomicWrite for atomic file operations"
    assert not found_direct_writefile, \
        "copyFileTo should not use os.WriteFile directly (not atomic)"


def test_writestring_uses_atomicwrite():
    """writeString must use atomicWrite instead of os.WriteFile (fail_to_pass)."""
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # Find the writeString function and check it uses atomicWrite
    assert "t.atomicWrite(file, []byte(data))" in content, \
        "writeString should call t.atomicWrite instead of os.WriteFile"

    # Check context - should not use os.WriteFile directly in writeString
    lines = content.split('\n')
    in_writestring = False
    found_atomicwrite_call = False
    found_direct_writefile = False

    for line in lines:
        if 'func (t *testRunner) writeString' in line:
            in_writestring = True
        elif in_writestring and line.startswith('func '):
            in_writestring = False
        elif in_writestring:
            if 'atomicWrite' in line:
                found_atomicwrite_call = True
            if 'os.WriteFile' in line:
                found_direct_writefile = True

    assert found_atomicwrite_call, \
        "writeString must call atomicWrite for atomic file operations"
    assert not found_direct_writefile, \
        "writeString should not use os.WriteFile directly (not atomic)"


def test_atomicwrite_has_retry_logic():
    """atomicWrite must have retry logic for Windows compatibility (fail_to_pass)."""
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # Check for retry loop
    assert "for retries := 0; ; retries++" in content, \
        "atomicWrite should have a retry loop for Windows file handle issues"

    # Check for retry limit
    assert "retries >= 5" in content, \
        "atomicWrite should retry up to 5 times"

    # Check for sleep between retries
    assert "time.Sleep(50 * time.Millisecond)" in content, \
        "atomicWrite should sleep between retries"


def test_atomicwrite_uses_tempdir():
    """atomicWrite must create temp files in t.TempDir() not t.dir (fail_to_pass)."""
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # The fix specifically uses t.TempDir() instead of t.dir to avoid
    # triggering fsnotify events on the watched directory
    assert "os.CreateTemp(t.TempDir()" in content, \
        "atomicWrite must use t.TempDir() for temp file location (not t.dir)"


def test_file_sd_tests_compile():
    """The file discovery tests must compile (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./discovery/file/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"File discovery tests should compile:\n{result.stderr}"


def test_file_sd_tests_run():
    """The file discovery tests must pass (fail_to_pass)."""
    # Run a quick subset of tests that use the file operations
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestInitialUpdate|TestFileUpdate|TestNoopFileUpdate", "./discovery/file/", "-timeout", "60s"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"File discovery tests should pass:\n{result.stdout}\n{result.stderr}"


def test_go_vet_passes():
    """Go vet should pass on the modified code (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./discovery/file/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Go vet should pass:\n{result.stderr}"


def test_go_fmt_passes():
    """Go fmt should pass on the modified code (pass_to_pass)."""
    result = subprocess.run(
        ["go", "fmt", "./discovery/file/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Go fmt should pass:\n{result.stderr}"


def test_go_mod_verify():
    """Go modules should verify correctly (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Go mod verify should pass:\n{result.stderr}"


def test_file_sd_quick_tests():
    """Quick subset of file discovery tests should pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestInitialUpdate|TestFileUpdate|TestNoopFileUpdate", "./discovery/file/", "-timeout", "60s"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Quick file discovery tests should pass:\n{result.stdout}\n{result.stderr}"
