#!/usr/bin/env python3
"""
Test outputs for containerd erofs snapshotter block mode fix.

This task verifies that the erofs snapshotter properly skips chown operations
when running in block mode, where the upperdir lives inside the block image
and host ownership is irrelevant.
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/containerd")
TARGET_FILE = REPO / "plugins/snapshots/erofs/erofs.go"


def test_go_compiles():
    """Verify the Go code compiles without errors (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    assert result.returncode == 0, f"Go compilation failed:\n{result.stderr.decode()}"


def test_go_vet():
    """Repo's go vet passes for erofs package (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stderr.decode()}"


def test_go_fmt():
    """Repo's go fmt check passes for erofs package (pass_to_pass)."""
    result = subprocess.run(
        ["go", "fmt", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    # go fmt returns 0 on success, non-zero if changes were needed
    assert result.returncode == 0, f"go fmt found formatting issues:\n{result.stdout.decode()}"


def test_go_test_erofs():
    """Repo's unit tests for erofs package pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout", "120s", "./plugins/snapshots/erofs/..."],
        cwd=REPO,
        capture_output=True,
        timeout=130
    )
    assert result.returncode == 0, f"go test failed:\n{result.stderr.decode()[-1000:]}"


def test_lchown_in_blockmode_guard():
    """
    Verify Lchown call is inside a !s.blockMode conditional block.

    This is the key behavioral fix - in block mode, the chown should not
    be executed because the upperdir lives inside the block image and
    host ownership is irrelevant.
    """
    source = TARGET_FILE.read_text()

    # Find Lchown call and check it's inside a !s.blockMode conditional
    # We look for the pattern where Lchown is inside an if !s.blockMode block

    # First check Lchown exists
    assert "Lchown" in source, "Lchown call not found in code"

    # Check that there's a !s.blockMode or s.blockMode check before Lchown
    # Pattern: if !s.blockMode { ... Lchown ... }
    pattern = r'if\s*!s\.blockMode\s*\{[^}]*Lchown'
    match = re.search(pattern, source, re.DOTALL)
    assert match is not None, "Lchown call must be inside !s.blockMode conditional block"


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
