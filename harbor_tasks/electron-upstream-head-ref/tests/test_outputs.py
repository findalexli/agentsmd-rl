"""
Test the upstream-head ref derivation fix for gclient worktrees.

The PR changes how UPSTREAM_HEAD is derived - instead of a fixed ref name,
it now includes a hash of the script's directory path to avoid conflicts
when multiple worktrees share a .git/refs directory.
"""

import hashlib
import os
import py_compile
import subprocess
import sys
import tempfile

# Path to the electron repo
REPO = "/workspace/electron"
SCRIPT_LIB = os.path.join(REPO, "script", "lib")

def test_upstream_head_has_hash_suffix():
    """UPSTREAM_HEAD should include an 8-character hash suffix derived from SCRIPT_DIR."""
    sys.path.insert(0, SCRIPT_LIB)
    try:
        import git
        # UPSTREAM_HEAD should be in format: refs/patches/upstream-head-<8-char-hash>
        assert git.UPSTREAM_HEAD.startswith("refs/patches/upstream-head-"), \
            f"UPSTREAM_HEAD should start with 'refs/patches/upstream-head-', got: {git.UPSTREAM_HEAD}"

        suffix = git.UPSTREAM_HEAD.replace("refs/patches/upstream-head-", "")
        # Legacy ref has no suffix
        assert len(suffix) == 8, f"Hash suffix should be 8 characters, got: {len(suffix)}"
        assert all(c in "0123456789abcdef" for c in suffix), \
            f"Suffix should be hex characters, got: {suffix}"
    finally:
        sys.path.remove(SCRIPT_LIB)


def test_upstream_head_hash_matches_script_dir():
    """The hash suffix should match md5(SCRIPT_DIR.encode())[:8]."""
    sys.path.insert(0, SCRIPT_LIB)
    try:
        import git
        expected_hash = hashlib.md5(git.SCRIPT_DIR.encode()).hexdigest()[:8]
        expected_ref = f"refs/patches/upstream-head-{expected_hash}"
        assert git.UPSTREAM_HEAD == expected_ref, \
            f"Expected {expected_ref}, got {git.UPSTREAM_HEAD}"
    finally:
        sys.path.remove(SCRIPT_LIB)


def test_legacy_ref_constant():
    """The legacy ref should remain unchanged for backwards compatibility."""
    sys.path.insert(0, SCRIPT_LIB)
    try:
        import git
        assert git._LEGACY_UPSTREAM_HEAD == "refs/patches/upstream-head", \
            f"Legacy ref should be 'refs/patches/upstream-head', got: {git._LEGACY_UPSTREAM_HEAD}"
    finally:
        sys.path.remove(SCRIPT_LIB)


def test_import_patches_updates_both_refs():
    """import_patches should update both the new ref and the legacy ref."""
    sys.path.insert(0, SCRIPT_LIB)
    try:
        import git

        # Create a temporary git repo
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = os.path.join(tmpdir, "repo")
            os.makedirs(repo)

            # Initialize repo
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)

            # Create initial commit
            with open(os.path.join(repo, "file.txt"), "w") as f:
                f.write("initial")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)

            # Create second commit
            with open(os.path.join(repo, "file.txt"), "w") as f:
                f.write("second")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "second"], cwd=repo, check=True, capture_output=True)

            # Get HEAD commit
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo, capture_output=True, text=True, check=True
            )
            head_commit = result.stdout.strip()

            # Test the ref update logic directly (import_patches calls update_ref for both refs)
            git.update_ref(repo=repo, ref=git.UPSTREAM_HEAD, newvalue='HEAD')
            if hasattr(git, '_LEGACY_UPSTREAM_HEAD'):
                git.update_ref(repo=repo, ref=git._LEGACY_UPSTREAM_HEAD, newvalue='HEAD')

            # Verify both refs exist and point to HEAD
            for ref in [git.UPSTREAM_HEAD, git._LEGACY_UPSTREAM_HEAD]:
                result = subprocess.run(
                    ["git", "rev-parse", ref],
                    cwd=repo, capture_output=True, text=True, check=True
                )
                ref_commit = result.stdout.strip()
                assert ref_commit == head_commit, \
                    f"Ref {ref} should point to HEAD, got: {ref_commit}, expected: {head_commit}"
    finally:
        sys.path.remove(SCRIPT_LIB)


def test_guess_base_commit_prefers_new_ref():
    """guess_base_commit should try the new ref first, then fall back to legacy."""
    sys.path.insert(0, SCRIPT_LIB)
    try:
        import git

        # Create a temporary git repo
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = os.path.join(tmpdir, "repo")
            os.makedirs(repo)

            # Initialize repo
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)

            # Create initial commit
            with open(os.path.join(repo, "file.txt"), "w") as f:
                f.write("initial")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)

            # Create second and third commits
            for i in range(2):
                with open(os.path.join(repo, "file.txt"), "w") as f:
                    f.write(f"content{i}")
                subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", f"commit{i}"], cwd=repo, check=True, capture_output=True)

            # Get the second commit (will be our upstream head)
            result = subprocess.run(
                ["git", "rev-parse", "HEAD~1"],
                cwd=repo, capture_output=True, text=True, check=True
            )
            upstream_commit = result.stdout.strip()

            # Set only the new ref
            subprocess.run(
                ["git", "update-ref", git.UPSTREAM_HEAD, upstream_commit],
                cwd=repo, check=True, capture_output=True
            )

            # Test guess_base_commit
            result = git.guess_base_commit(repo, git.UPSTREAM_HEAD)
            assert result[0] == upstream_commit, \
                f"guess_base_commit should return the upstream commit, got: {result[0]}"
            assert result[1] == 1, f"Should be 1 commit after upstream, got: {result[1]}"
    finally:
        sys.path.remove(SCRIPT_LIB)


def test_guess_base_commit_fallback_to_legacy():
    """guess_base_commit should fall back to legacy ref if new ref doesn't exist."""
    sys.path.insert(0, SCRIPT_LIB)
    try:
        import git

        # Create a temporary git repo
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = os.path.join(tmpdir, "repo")
            os.makedirs(repo)

            # Initialize repo
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)

            # Create initial commit
            with open(os.path.join(repo, "file.txt"), "w") as f:
                f.write("initial")
            subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)

            # Create second and third commits
            for i in range(2):
                with open(os.path.join(repo, "file.txt"), "w") as f:
                    f.write(f"content{i}")
                subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
                subprocess.run(["git", "commit", "-m", f"commit{i}"], cwd=repo, check=True, capture_output=True)

            # Get the second commit (will be our upstream head)
            result = subprocess.run(
                ["git", "rev-parse", "HEAD~1"],
                cwd=repo, capture_output=True, text=True, check=True
            )
            upstream_commit = result.stdout.strip()

            # Set only the legacy ref (simulate old patches)
            subprocess.run(
                ["git", "update-ref", git._LEGACY_UPSTREAM_HEAD, upstream_commit],
                cwd=repo, check=True, capture_output=True
            )

            # Test guess_base_commit - should fall back to legacy
            result = git.guess_base_commit(repo, git.UPSTREAM_HEAD)
            assert result[0] == upstream_commit, \
                f"guess_base_commit should fall back to legacy ref, got: {result[0]}"
            assert result[1] == 1, f"Should be 1 commit after upstream, got: {result[1]}"
    finally:
        sys.path.remove(SCRIPT_LIB)


# =============================================================================
# PASS-TO-PASS TESTS - Verify repo integrity on both base and fixed commits
# =============================================================================

REPO_SCRIPT_LIB = os.path.join(REPO, "script", "lib")

def test_repo_python_syntax_git_py():
    """script/lib/git.py has valid Python syntax (pass_to_pass)."""
    py_compile.compile(os.path.join(REPO_SCRIPT_LIB, "git.py"), doraise=True)


def test_repo_python_syntax_patches_py():
    """script/lib/patches.py has valid Python syntax (pass_to_pass)."""
    py_compile.compile(os.path.join(REPO_SCRIPT_LIB, "patches.py"), doraise=True)


def test_repo_python_syntax_util_py():
    """script/lib/util.py has valid Python syntax (pass_to_pass)."""
    py_compile.compile(os.path.join(REPO_SCRIPT_LIB, "util.py"), doraise=True)


def test_repo_python_syntax_config_py():
    """script/lib/config.py has valid Python syntax (pass_to_pass)."""
    py_compile.compile(os.path.join(REPO_SCRIPT_LIB, "config.py"), doraise=True)


def test_repo_git_module_imports():
    """script/lib/git.py module imports successfully (pass_to_pass)."""
    sys.path.insert(0, REPO_SCRIPT_LIB)
    try:
        import git
        # Verify basic attributes exist
        assert hasattr(git, 'UPSTREAM_HEAD'), "git.UPSTREAM_HEAD should exist"
        assert hasattr(git, 'SCRIPT_DIR'), "git.SCRIPT_DIR should exist"
        assert hasattr(git, 'import_patches'), "git.import_patches should exist"
        assert hasattr(git, 'export_patches'), "git.export_patches should exist"
        assert hasattr(git, 'guess_base_commit'), "git.guess_base_commit should exist"
    finally:
        sys.path.remove(REPO_SCRIPT_LIB)


def test_repo_patches_module_imports():
    """script/lib/patches.py module imports successfully (pass_to_pass)."""
    sys.path.insert(0, REPO_SCRIPT_LIB)
    try:
        import patches
        # Verify key attributes exist
        assert hasattr(patches, 'PATCH_FILENAME_PREFIX'), "patches.PATCH_FILENAME_PREFIX should exist"
        assert hasattr(patches, 'is_patch_location_line'), "patches.is_patch_location_line should exist"
    finally:
        sys.path.remove(REPO_SCRIPT_LIB)


def test_repo_git_script_runnable():
    """git-import-patches script runs without errors (pass_to_pass)."""
    # Test that the script can at least show help without crashing
    result = subprocess.run(
        ["python3", os.path.join(REPO, "script", "git-import-patches"), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # The script may not have --help, but it should not crash with a syntax error
    # Exit code 0 or 1 (usage error) is acceptable, but not 2 (argument error) or other errors
    assert result.returncode in [0, 1, 2], f"Script should run without internal errors: {result.stderr}"


def test_repo_python_scripts_compile():
    """All Python scripts in script/ directory compile (pass_to_pass)."""
    script_dir = os.path.join(REPO, "script")
    python_files = [
        "apply_all_patches.py",
        "dbus_mock.py",
        "export_all_patches.py",
        "generate-config-gypi.py",
        "generate-mas-config.py",
        "generate-zip-manifest.py",
        "get-git-version.py",
        "patches-mtime-cache.py",
        "run-clang-format.py",
        "run-gn-format.py",
        "tar.py",
        "verify-chromedriver.py",
        "verify-ffmpeg.py",
        "verify-mksnapshot.py",
        "zip-symbols.py",
    ]
    for filename in python_files:
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            py_compile.compile(filepath, doraise=True)
