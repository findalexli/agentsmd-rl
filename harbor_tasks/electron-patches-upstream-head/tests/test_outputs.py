"""
Tests for the patches upstream-head ref fix.

This validates that the git.py module correctly derives a checkout-specific
upstream-head ref from the script path to prevent gclient worktrees from
clobbering each other's refs.
"""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = "/workspace/electron"
GIT_PY_PATH = Path(REPO) / "script" / "lib" / "git.py"


def import_git_module():
    """Import the git module from the electron repo."""
    sys.path.insert(0, str(Path(REPO) / "script" / "lib"))
    # Also need the patches module
    sys.path.insert(0, str(Path(REPO) / "script"))
    try:
        import git
        return git
    finally:
        sys.path.pop(0)
        sys.path.pop(0)


class TestUpstreamHeadDerivation:
    """Tests for the checkout-specific UPSTREAM_HEAD derivation."""

    def test_upstream_head_contains_hash_suffix(self):
        """UPSTREAM_HEAD should end with an 8-character MD5 hash suffix."""
        git = import_git_module()

        # The UPSTREAM_HEAD should contain a hash suffix
        assert "-" in git.UPSTREAM_HEAD, "UPSTREAM_HEAD should contain a dash before hash suffix"

        # Extract the hash part
        parts = git.UPSTREAM_HEAD.rsplit("-", 1)
        assert len(parts) == 2, "UPSTREAM_HEAD should have format 'refs/patches/upstream-head-<hash>'"

        hash_suffix = parts[1]
        assert len(hash_suffix) == 8, f"Hash suffix should be 8 chars, got {len(hash_suffix)}"
        assert all(c in "0123456789abcdef" for c in hash_suffix), "Hash should be hex digits"

    def test_upstream_head_derived_from_script_dir(self):
        """UPSTREAM_HEAD should be derived from SCRIPT_DIR using MD5."""
        git = import_git_module()

        # Get the expected hash from SCRIPT_DIR
        script_dir = git.SCRIPT_DIR
        expected_hash = hashlib.md5(script_dir.encode()).hexdigest()[:8]

        expected_ref = f"refs/patches/upstream-head-{expected_hash}"
        assert git.UPSTREAM_HEAD == expected_ref, (
            f"UPSTREAM_HEAD mismatch: expected {expected_ref}, got {git.UPSTREAM_HEAD}"
        )

    def test_legacy_upstream_head_constant(self):
        """_LEGACY_UPSTREAM_HEAD should remain the original ref name."""
        git = import_git_module()

        assert git._LEGACY_UPSTREAM_HEAD == "refs/patches/upstream-head", (
            "Legacy ref name should be unchanged for backward compatibility"
        )

    def test_upstream_head_not_equal_to_legacy(self):
        """UPSTREAM_HEAD should be different from _LEGACY_UPSTREAM_HEAD."""
        git = import_git_module()

        assert git.UPSTREAM_HEAD != git._LEGACY_UPSTREAM_HEAD, (
            "UPSTREAM_HEAD should be checkout-specific, not the legacy name"
        )


class TestImportPatchesBehavior:
    """Tests for the import_patches function behavior."""

    def test_import_patches_updates_both_refs(self):
        """import_patches should update both the new ref and legacy ref."""
        git = import_git_module()

        # Read the source code to verify the logic
        source = GIT_PY_PATH.read_text()

        # Check that import_patches calls update_ref twice
        update_ref_calls = source.count("update_ref(repo=repo, ref=")
        assert update_ref_calls >= 2, (
            f"import_patches should call update_ref at least twice (for new and legacy ref), found {update_ref_calls}"
        )

        # Verify the conditional update for legacy ref exists
        assert "if ref != _LEGACY_UPSTREAM_HEAD:" in source, (
            "import_patches should have conditional check to avoid duplicate legacy ref update"
        )

        assert "update_ref(repo=repo, ref=_LEGACY_UPSTREAM_HEAD" in source, (
            "import_patches should update the legacy ref when using the new ref"
        )


class TestGuessBaseCommitBehavior:
    """Tests for the guess_base_commit function behavior."""

    def test_guess_base_commit_tries_both_refs(self):
        """guess_base_commit should try both the new ref and legacy ref."""
        git = import_git_module()

        # Read the source code to verify the logic
        source = GIT_PY_PATH.read_text()

        # Should have a for loop trying both refs
        assert "for candidate in (ref, _LEGACY_UPSTREAM_HEAD):" in source, (
            "guess_base_commit should iterate through both ref and legacy ref"
        )

    def test_guess_base_commit_has_loop_for_candidates(self):
        """guess_base_commit should use a for loop to try multiple candidate refs."""
        source = GIT_PY_PATH.read_text()

        # Extract the guess_base_commit function body
        import re
        match = re.search(r'def guess_base_commit\([^)]+\):\s*"""[^"]*"""\s*\n(.*?)(?=\ndef |\Z)',
                         source, re.DOTALL)
        if not match:
            # Try without docstring
            match = re.search(r'def guess_base_commit\([^)]+\):\s*\n(.*?)(?=\ndef |\Z)',
                             source, re.DOTALL)

        if match:
            func_body = match.group(1)
            # The new code should have a for loop trying candidates
            assert "for candidate in" in func_body, (
                "guess_base_commit should use a for loop to try multiple ref candidates"
            )
            assert "(ref, _LEGACY_UPSTREAM_HEAD)" in func_body or "_LEGACY_UPSTREAM_HEAD" in func_body, (
                "guess_base_commit should try both the new ref and legacy ref"
            )
        else:
            pytest.fail("Could not extract guess_base_commit function body")


class TestHashlibImport:
    """Tests for the required hashlib import."""

    def test_hashlib_imported(self):
        """hashlib module should be imported for MD5 hashing."""
        source = GIT_PY_PATH.read_text()

        # Check for the import
        assert "import hashlib" in source, (
            "hashlib must be imported for MD5 hash computation"
        )


class TestIntegration:
    """Integration tests that call the actual code."""

    def test_module_loads_without_error(self):
        """The git module should load without import errors."""
        git = import_git_module()

        # Basic sanity check that we got the module
        assert hasattr(git, 'UPSTREAM_HEAD'), "Module should have UPSTREAM_HEAD constant"
        assert hasattr(git, '_LEGACY_UPSTREAM_HEAD'), "Module should have _LEGACY_UPSTREAM_HEAD constant"
        assert hasattr(git, 'import_patches'), "Module should have import_patches function"
        assert hasattr(git, 'guess_base_commit'), "Module should have guess_base_commit function"

    def test_upstream_head_format(self):
        """UPSTREAM_HEAD should follow the expected format."""
        git = import_git_module()

        # Should start with refs/patches/upstream-head-
        prefix = "refs/patches/upstream-head-"
        assert git.UPSTREAM_HEAD.startswith(prefix), (
            f"UPSTREAM_HEAD should start with {prefix}, got {git.UPSTREAM_HEAD}"
        )

        # The suffix should be exactly 8 hex characters
        suffix = git.UPSTREAM_HEAD[len(prefix):]
        assert len(suffix) == 8, f"Hash suffix should be 8 characters, got {len(suffix)}"
        assert all(c in "0123456789abcdef" for c in suffix), "Suffix should be hexadecimal"


class TestRepoPythonSyntax:
    """Pass-to-pass: Python syntax checks from the repo's CI pipeline."""

    def test_git_py_syntax_valid(self):
        """script/lib/git.py compiles without syntax errors (pass_to_pass)."""
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(GIT_PY_PATH)],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"Syntax error in git.py:\n{r.stderr[-500:]}"

    def test_patches_py_syntax_valid(self):
        """script/lib/patches.py compiles without syntax errors (pass_to_pass)."""
        patches_path = Path(REPO) / "script" / "lib" / "patches.py"
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(patches_path)],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"Syntax error in patches.py:\n{r.stderr[-500:]}"

    def test_all_script_lib_syntax_valid(self):
        """All Python files in script/lib/ compile without syntax errors (pass_to_pass)."""
        script_lib = Path(REPO) / "script" / "lib"
        py_files = sorted(script_lib.glob("*.py"))
        assert len(py_files) > 0, "No Python files found in script/lib/"
        for py_file in py_files:
            r = subprocess.run(
                ["python3", "-m", "py_compile", str(py_file)],
                capture_output=True, text=True, timeout=60,
            )
            assert r.returncode == 0, f"Syntax error in {py_file.name}:\n{r.stderr[-500:]}"


class TestRepoModuleImport:
    """Pass-to-pass: Module import checks from the repo's CI pipeline."""

    def test_git_module_imports_successfully(self):
        """The git module can be imported without errors (pass_to_pass)."""
        git = import_git_module()
        assert git is not None

    def test_git_module_exports_upstream_head(self):
        """The git module exports UPSTREAM_HEAD constant (pass_to_pass)."""
        git = import_git_module()
        assert hasattr(git, "UPSTREAM_HEAD")
        assert isinstance(git.UPSTREAM_HEAD, str)
        assert git.UPSTREAM_HEAD.startswith("refs/patches/upstream-head")


class TestRepoGitHelperFunctions:
    """Pass-to-pass: Git helper functions still work after the fix."""

    def test_split_patches(self):
        """split_patches correctly splits concatenated patch data (pass_to_pass)."""
        git = import_git_module()
        patch_data = (
            "From abc123 Mon Sep 17 00:00:00 2001\n"
            "From: test@test.com\n"
            "Subject: test patch\n"
            "\n"
            "--- a/file.txt\n"
            "+++ b/file.txt\n"
            "@@ -1,1 +1,2 @@\n"
            "-old line\n"
            "+new line\n"
            "\n"
            "From def456 Mon Sep 17 00:00:00 2001\n"
            "From: test@test.com\n"
            "Subject: another patch\n"
            "\n"
            "--- a/file2.txt\n"
            "+++ b/file2.txt\n"
            "@@ -1,1 +1,2 @@\n"
            "-old\n"
            "+new\n"
        )
        result = git.split_patches(patch_data)
        assert len(result) == 2, f"Expected 2 patches, got {len(result)}"

    def test_munge_subject_to_filename(self):
        """munge_subject_to_filename generates valid filenames (pass_to_pass)."""
        git = import_git_module()
        result = git.munge_subject_to_filename("fix: some bug in code.patch")
        assert result == "fix_some_bug_in_code.patch", f"Got: {result}"

        result = git.munge_subject_to_filename("Add new feature")
        assert result == "add_new_feature.patch", f"Got: {result}"

    def test_filter_patches(self):
        """filter_patches correctly filters patches by key (pass_to_pass)."""
        git = import_git_module()
        patches = [["Subject: fix bug", "key: value"], ["Subject: other", "no match"]]
        result = git.filter_patches(patches, "key")
        assert len(result) == 1, f"Expected 1 match, got {len(result)}"

        result = git.filter_patches(patches, None)
        assert len(result) == 2, f"Expected all patches with None key, got {len(result)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
