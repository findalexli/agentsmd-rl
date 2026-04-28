#!/usr/bin/env python3
"""
Behavioral tests for the GlobWalker.zig fix.
These tests verify compilation, the removal of the buggy pattern, and observable
behavior without asserting on gold-specific literals.
"""
import re
import subprocess
import pytest

GLOBWALKER_PATH = "/workspace/bun/src/glob/GlobWalker.zig"


def get_setNameFilter_context(window=15):
    """Extract the setNameFilter call and surrounding context in the Windows block."""
    with open(GLOBWALKER_PATH, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "setNameFilter" in line and "iterator." in line:
            start = max(0, i - window)
            end = min(len(lines), i + 1)
            return i, "".join(lines[start:end])

    return None, None


class TestCompilation:
    """Verify the fix compiles correctly — PRIMARY behavioral test."""

    def test_globwalker_zig_compiles(self):
        """GlobWalker.zig must pass zig ast-check (syntax + basic semantic check)."""
        import shutil
        if not shutil.which("zig"):
            pytest.skip("zig not available in environment")
        parse_r = subprocess.run(
            ["bash", "-lc", "zig ast-check src/glob/GlobWalker.zig"],
            capture_output=True, text=True, timeout=30, cwd="/workspace/bun",
        )
        assert parse_r.returncode == 0, (
            f"zig ast-check failed:\nstdout: {parse_r.stdout}\nstderr: {parse_r.stderr}"
        )


class TestBuggyPatternRemoved:
    """Verify the broken pattern is no longer present."""

    def test_buggy_component_idx_removed_from_computeNtFilter(self):
        """
        The buggy computeNtFilter(component_idx) call must be removed.
        This is the root cause of the compilation failure.
        """
        _, context = get_setNameFilter_context()
        assert context is not None, "iterator.setNameFilter not found in Windows block"

        buggy_pattern = re.compile(r"computeNtFilter\s*\(\s*component_idx\s*\)")
        assert not buggy_pattern.search(context), (
            "Buggy computeNtFilter(component_idx) still present"
        )


class TestFixDerivesIndexFromActiveBitSet:
    """Verify the fix derives the pattern index from the active BitSet."""

    def test_active_bitset_used_near_setNameFilter(self):
        """
        The fix must use the 'active' BitSet (not the old component_idx variable)
        to derive the index for computeNtFilter.
        """
        _, context = get_setNameFilter_context()
        assert context is not None, "iterator.setNameFilter not found in Windows block"

        buggy_pattern = re.compile(r"computeNtFilter\s*\(\s*component_idx\s*\)")
        assert not buggy_pattern.search(context), (
            "Buggy component_idx still used in computeNtFilter"
        )

        assert re.search(r"\bactive\b", context), (
            "active BitSet not found near setNameFilter — fix must use active to derive index"
        )

        assert "computeNtFilter" in context, (
            "computeNtFilter must still be called near setNameFilter"
        )


class TestMultiActiveCaseHandled:
    """Verify the fix handles the multi-active component case."""

    def test_conditional_logic_present_near_setNameFilter(self):
        """
        The fix must have conditional logic (if/else or ternary) to handle
        the case when multiple pattern components are active.
        """
        _, context = get_setNameFilter_context()
        assert context is not None, "iterator.setNameFilter not found in Windows block"

        has_if_else = re.search(r"\bif\s*\(", context) and re.search(r"\belse\b", context)
        has_ternary = re.search(r"\?", context)
        assert has_if_else or has_ternary, (
            "No conditional logic (if/else or ternary) found near setNameFilter"
        )

    def test_multi_active_branch_is_sane(self):
        """
        When multiple components are active (count != 1), the else-branch
        must pass either null OR an empty slice to setNameFilter — both are
        valid ways to disable the kernel filter.
        """
        _, context = get_setNameFilter_context()
        assert context is not None, "iterator.setNameFilter not found in Windows block"

        has_null = re.search(r"\bnull\b", context)
        has_empty_slice = re.search(r"&\[\]_u16\{\}", context)
        assert has_null or has_empty_slice, (
            "Multi-active branch must pass null or empty slice &[_]u16{} to setNameFilter"
        )


class TestPassToPass:
    """Pass-to-pass tests — these verify structural elements preserved by the fix."""

    def test_setNameFilter_exists(self):
        """setNameFilter must exist in source (pass-to-pass)."""
        with open(GLOBWALKER_PATH, "r") as f:
            source = f.read()
        assert "setNameFilter" in source

    def test_computeNtFilter_still_called(self):
        """computeNtFilter must still be called near setNameFilter (pass-to-pass)."""
        _, context = get_setNameFilter_context()
        assert context is not None, "iterator.setNameFilter not found in Windows block"
        assert "computeNtFilter" in context, "computeNtFilter must still be called"

    def test_computeNtFilter_function_preserved(self):
        """computeNtFilter function definition must still exist with u32 parameter."""
        with open(GLOBWALKER_PATH, "r") as f:
            source = f.read()
        assert re.search(r"fn\s+computeNtFilter\s*\([^)]*u32[^)]*\)", source), (
            "computeNtFilter function with u32 parameter not found"
        )

    def test_source_file_exists_balanced_braces(self):
        """GlobWalker.zig file exists and has roughly balanced braces."""
        with open(GLOBWALKER_PATH, "r") as f:
            source = f.read()
        open_count = source.count("{")
        close_count = source.count("}")
        assert open_count > 0, "File has no opening braces"
        assert abs(open_count - close_count) <= 5, (
            f"Brace imbalance: {open_count} open vs {close_count} close"
        )

    def test_no_std_usage_near_fix(self):
        """No std.* API usage near the setNameFilter fix site."""
        _, context = get_setNameFilter_context(window=20)
        assert context is not None, "iterator.setNameFilter not found in Windows block"
        # std.* on its own line or as a parameter (not in import paths like builtin.os)
        assert not re.search(r"\bstd\.\w", context), (
            "std.* API usage found near setNameFilter — use bun.* APIs instead"
        )

    def test_no_inline_import_near_fix(self):
        """No inline @import() near the setNameFilter fix site."""
        _, context = get_setNameFilter_context(window=20)
        assert context is not None, "iterator.setNameFilter not found in Windows block"
        assert "@import(" not in context, (
            "Inline @import() found near setNameFilter — imports must be at file bottom"
        )
