#!/usr/bin/env python3
"""
Test outputs for containerd erofs snapshotter block mode fix.

This task verifies that the erofs snapshotter properly skips chown operations
when running in block mode, where the upperdir lives inside the block image
and host ownership is irrelevant.
"""

import subprocess
import re
import os
from pathlib import Path

REPO = Path("/workspace/containerd")
TARGET_FILE = REPO / "plugins/snapshots/erofs/erofs.go"

# Environment with GOTOOLCHAIN=auto to handle go.mod requiring newer Go version
GO_ENV = os.environ.copy()
GO_ENV["GOTOOLCHAIN"] = "auto"


def test_go_compiles():
    """Verify the Go code compiles without errors (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=120,
        env=GO_ENV
    )
    assert result.returncode == 0, f"Go compilation failed:\n{result.stderr.decode()}"


def test_go_vet():
    """Repo's go vet passes for erofs package (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=120,
        env=GO_ENV
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stderr.decode()}"


def test_go_fmt():
    """Repo's go fmt check passes for erofs package (pass_to_pass)."""
    result = subprocess.run(
        ["go", "fmt", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=60,
        env=GO_ENV
    )
    # go fmt returns 0 on success, non-zero if changes were needed
    assert result.returncode == 0, f"go fmt found formatting issues:\n{result.stdout.decode()}"


def test_go_test_erofs():
    """Repo's unit tests for erofs package pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout", "120s", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=150,
        env=GO_ENV
    )
    assert result.returncode == 0, f"go test failed:\n{result.stderr.decode()[-1000:]}"


def test_go_mod_verify():
    """Repo's go modules verify passes (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
        env=GO_ENV
    )
    assert result.returncode == 0, f"go mod verify failed:\n{result.stderr.decode()}"


def test_go_mod_tidy():
    """Repo's go.mod is tidy (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "tidy"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
        env=GO_ENV
    )
    assert result.returncode == 0, f"go mod tidy failed:\n{result.stderr.decode()}"

    # Check if go.mod or go.sum changed (indicating they were not tidy)
    result_diff = subprocess.run(
        ["git", "diff", "--stat"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
        env=GO_ENV
    )
    diff_output = result_diff.stdout.decode()
    assert "go.mod" not in diff_output and "go.sum" not in diff_output, \
        f"go.mod/go.sum were not tidy. Changes:\n{diff_output}"


def test_lchown_in_blockmode_guard():
    """
    Verify Lchown call is inside a !s.blockMode conditional block.

    This is the key behavioral fix - in block mode, the chown should not
    be executed because the upperdir lives inside the block image and
    host ownership is irrelevant.
    """
    source = TARGET_FILE.read_text()

    # First check Lchown exists
    assert "Lchown" in source, "Lchown call not found in code"

    # Find the if !s.blockMode block and check Lchown is inside it
    # The block starts with "if !s.blockMode {" and contains nested blocks
    # Lchown should be inside this block (at any nesting level)

    # Find the position of if !s.blockMode (the one in createSnapshot function)
    # We need to find the specific one that wraps the Lchown logic
    # Look for the pattern near the "In block mode the upperdir" comment
    comment_pos = source.find("In block mode the upperdir lives inside the block image")
    assert comment_pos != -1, "Block mode comment not found"
    
    # Find if !s.blockMode after the comment
    block_start = source.find("if !s.blockMode {", comment_pos)
    assert block_start != -1, "if !s.blockMode block not found after comment"

    # Find the corresponding closing brace for this block
    # Count braces to find the matching closing brace
    brace_count = 0
    block_end = block_start
    for i in range(block_start, len(source)):
        if source[i] == '{':
            brace_count += 1
        elif source[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                block_end = i
                break

    # Check Lchown is inside this block
    lchown_pos = source.find("os.Lchown", block_start)
    assert lchown_pos != -1 and lchown_pos < block_end, \
        "Lchown call must be inside !s.blockMode conditional block"


def test_blockmode_comment_present():
    """
    Verify the explanatory comment about block mode is present.

    The comment should explain why chown is skipped in block mode.
    """
    source = TARGET_FILE.read_text()

    # Check for the explanatory comment
    assert "In block mode the upperdir lives inside the block image" in source, \
        "Expected explanatory comment about block mode not found"
    assert "host ownership is irrelevant" in source, \
        "Expected 'host ownership is irrelevant' comment not found"


def test_createSnapshot_function_exists():
    """
    Verify createSnapshot function still exists with proper structure.

    This is a p2p test to ensure we haven't broken the function entirely.
    """
    source = TARGET_FILE.read_text()

    assert "func (s *snapshotter) createSnapshot(" in source, \
        "createSnapshot method not found"


def test_remap_logic_structure():
    """
    Verify the UID/GID remapping logic structure is present.

    The code should still have the mapping logic variables and flow.
    """
    source = TARGET_FILE.read_text()

    # Check that the key variables are still declared
    assert "mappedUID" in source, "mappedUID variable not found"
    assert "mappedGID" in source, "mappedGID variable not found"
    assert "needsRemap" in source, "needsRemap variable not found"

    # Check that the label checks are present
    assert "LabelSnapshotUIDMapping" in source, "UID mapping label check not found"
    assert "LabelSnapshotGIDMapping" in source, "GID mapping label check not found"


def test_parent_ownership_fallback():
    """
    Verify parent ownership fallback logic is preserved.

    The fallback to copy ownership from parent should still exist.
    """
    source = TARGET_FILE.read_text()

    assert "getParentOwnership" in source, "getParentOwnership call not found"
    assert "snap.ParentIDs" in source, "ParentIDs reference not found"


def test_repo_make_binaries():
    """Repo's make binaries passes (pass_to_pass)."""
    result = subprocess.run(
        ["make", "binaries"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
        env=GO_ENV
    )
    assert result.returncode == 0, f"make binaries failed:\n{result.stderr.decode()}"

def test_go_test_erofs_TestErofs():
    """Repo's TestErofs unit test function runs (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "^TestErofs$", "./plugins/snapshots/erofs/...", "-test.root"],
        cwd=REPO,
        capture_output=True,
        timeout=150,
        env=GO_ENV
    )
    assert result.returncode == 0, f"TestErofs failed:\n{result.stderr.decode()[-1000:]}"

def test_go_test_erofs_TestErofsWithQuota():
    """Repo's TestErofsWithQuota unit test function runs (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "^TestErofsWithQuota$", "./plugins/snapshots/erofs/...", "-test.root"],
        cwd=REPO,
        capture_output=True,
        timeout=150,
        env=GO_ENV
    )
    assert result.returncode == 0, f"TestErofsWithQuota failed:\n{result.stderr.decode()[-1000:]}"

def test_go_test_erofs_TestErofsFsverity():
    """Repo's TestErofsFsverity unit test function runs (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "^TestErofsFsverity$", "./plugins/snapshots/erofs/...", "-test.root"],
        cwd=REPO,
        capture_output=True,
        timeout=150,
        env=GO_ENV
    )
    assert result.returncode == 0, f"TestErofsFsverity failed:\n{result.stderr.decode()[-1000:]}"

def test_go_test_erofs_TestErofsDifferWithTarIndexMode():
    """Repo's TestErofsDifferWithTarIndexMode unit test function runs (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "^TestErofsDifferWithTarIndexMode$", "./plugins/snapshots/erofs/...", "-test.root"],
        cwd=REPO,
        capture_output=True,
        timeout=150,
        env=GO_ENV
    )
    assert result.returncode == 0, f"TestErofsDifferWithTarIndexMode failed:\n{result.stderr.decode()[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
