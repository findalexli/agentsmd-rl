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
    """Verify the fix compiles correctly — this is the PRIMARY behavioral test."""

    def test_globwalker_zig_compiles(self):
        """GlobWalker.zig must parse correctly (AST check), or skip if zig unavailable."""
        import shutil
        if not shutil.which("zig"):
            pytest.skip("zig not available in environment")
        parse_r = subprocess.run(
            ["zig", "ast-check", GLOBWALKER_PATH],
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

        # The exact buggy pattern from the gold solution's base
        buggy_pattern = re.compile(r'computeNtFilter\s*\(\s*component_idx\s*\)')
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

        # Must NOT use the old buggy variable
        buggy_pattern = re.compile(r'computeNtFilter\s*\(\s*component_idx\s*\)')
        assert not buggy_pattern.search(context), (
            "Buggy component_idx still used in computeNtFilter"
        )

        # Must USE the active BitSet to derive the index
        assert re.search(r'\bactive\b', context), (
            "active BitSet not found near setNameFilter — fix must use active to derive index"
        )

        # Must call computeNtFilter (with a derived index, not component_idx)
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

        # Conditional (if/else or ternary) must be present
        has_if_else = re.search(r'\bif\s*\(', context) and re.search(r'\belse\b', context)
        has_ternary = re.search(r'\?', context)
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

        # Either null OR empty slice (&[_]u16{}) is valid for skipping filter
        has_null = re.search(r'\bnull\b', context)
        has_empty_slice = re.search(r'&\[\]_u16\{\}', context)
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
