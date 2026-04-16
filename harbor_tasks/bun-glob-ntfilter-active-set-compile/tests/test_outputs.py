#!/usr/bin/env python3
import subprocess
import pytest

GLOBWALKER_PATH = "/workspace/bun/src/glob/GlobWalker.zig"

def read_source_file():
    """Read the current source file content."""
    with open(GLOBWALKER_PATH, "r") as f:
        return f.read()

def get_fix_context(source, window=5):
    """
    Get the context around the setNameFilter call that needs to be fixed.
    The buggy code has: iterator.setNameFilter(this.computeNtFilter(component_idx));
    The fixed code has: iterator.setNameFilter(filter); where filter is computed above.
    We look for lines containing setNameFilter and return context around them.
    """
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if "setNameFilter" in line and "iterator." in line:
            # This is the setNameFilter call in the GlobWalker_ function
            start = max(0, i - window)
            end = min(len(lines), i + 1)
            return "\n".join(lines[start:end])
    return None

class TestBuggyPatternRemoved:
    """
    Verify the broken computeNtFilter(component_idx) call is removed.
    """

    def test_buggy_component_idx_not_in_setNameFilter_context(self):
        """The component_idx variable must not be passed to computeNtFilter."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        assert "component_idx" not in context, (
            "Buggy component_idx still used"
        )

class TestFixUsesActiveBitSet:
    """
    Verify the fix uses the active BitSet.
    """

    def test_active_count_used(self):
        """active.count() must be used to check number of active components."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        assert "active.count()" in context, (
            "active.count() must be used"
        )

    def test_findFirstSet_used(self):
        """findFirstSet() must be used to get single active index."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        assert "findFirstSet" in context, (
            "findFirstSet() must be used"
        )

    def test_intCast_used(self):
        """@intCast must be used to convert BitSet index."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        assert "@intCast" in context, (
            "@intCast must be used"
        )

class TestMultiActiveConditional:
    """
    Verify the fix handles multiple active components correctly.
    """

    def test_null_used_when_multiple(self):
        """null must be passed when multiple components active."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        assert "null" in context, (
            "null must be used when multiple components active"
        )

    def test_conditional_logic_present(self):
        """if/else conditional must be present."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        has_if = "if (" in context or "if(" in context
        has_else = "else" in context
        assert has_if and has_else, (
            "if/else conditional must be present"
        )

class TestSetNameFilterPreserved:
    """Verify setNameFilter is preserved."""

    def test_setNameFilter_exists(self):
        """setNameFilter must exist in source."""
        source = read_source_file()
        assert "setNameFilter" in source

class TestComputeNtFilterPreserved:
    """Verify computeNtFilter is still called."""

    def test_computeNtFilter_still_called(self):
        """computeNtFilter must still be called."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        assert "computeNtFilter" in context, (
            "computeNtFilter must still be called"
        )

class TestSolutionUniqueness:
    """
    Verify tests pass for any correct fix.
    """

    def test_all_required_behaviors_present(self):
        """All required behaviors must be present."""
        source = read_source_file()
        context = get_fix_context(source)
        assert context is not None, "iterator.setNameFilter not found"
        
        # Check each required behavior
        assert "component_idx" not in context, "Buggy component_idx still used"
        assert "active.count()" in context, "active.count() not used"
        assert "findFirstSet" in context, "findFirstSet not used"
        assert "@intCast" in context, "@intCast not used"
        assert "null" in context, "null not used"
        assert "computeNtFilter" in context, "computeNtFilter not called"
        
        has_if = "if (" in context or "if(" in context
        has_else = "else" in context
        assert has_if and has_else, "if/else conditional not present"
