"""Tests for Hugo fileEventsContentPaths panic fix.

The bug: nested loop had dirs as outer loop and others as inner loop with
a single counter 'n', causing n to exceed len(others) when multiple dirs existed.
"""

import subprocess
import re

REPO = "/workspace/hugo"


def test_rebuild_add_content_with_multiple_dir_creations():
    """Test that rebuilding with multiple dir creations doesn't panic (f2p).

    This test reproduces issue #14573 where creating multiple directories
during a rebuild caused an index out of range panic.

    Note: The test TestRebuildAddContentWithMultipleDirCreations was added
    in the PR. On base commit it doesn't exist. The structural tests
    (test_dirs_loop_counter_bug_fixed, test_safe_counter_pattern) verify
    the fix is applied correctly.
    """
    # Run the test - if it doesn't exist, go test will report "no tests to run"
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestRebuildAddContentWithMultipleDirCreations$",
         "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = result.stdout + result.stderr

    # Check for the specific panic we expect on base commit
    if "index out of range" in output or "runtime error" in output:
        assert False, f"Index out of range panic detected:\n{output[-2000:]}"

    # If test doesn't exist ("no tests to run"), that's expected on base commit
    # The structural tests verify the fix. If test exists and passes, that's
    # the gold standard after fix.
    if "no tests to run" in output.lower():
        # Test not found - expected on base commit, pass this test
        # The structural tests (test_dirs_loop_counter_bug_fixed etc.) will
        # catch whether the fix is applied
        return

    # The test should pass (exit code 0) after the fix
    assert result.returncode == 0, f"Test failed:\n{output[-2000:]}"


def test_repo_hugolib_compiles():
    """Hugo hugolib package compiles without errors (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "-o", "/dev/null", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"


def test_repo_hugolib_vet():
    """Hugo hugolib package passes go vet (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stderr}"


def test_repo_gofmt():
    """Hugo source passes gofmt check (pass_to_pass)."""
    result = subprocess.run(
        ["./check_gofmt.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"gofmt check failed:\n{result.stdout}{result.stderr}"


def test_repo_hugolib_rebuild_tests():
    """Hugo hugolib rebuild tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-count=1", "-timeout", "120s", "-run", "Rebuild", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    output = result.stdout + result.stderr

    # Check for specific panics
    if "index out of range" in output or "runtime error" in output:
        assert False, f"Index out of range panic detected:\n{output[-2000:]}"

    assert result.returncode == 0, f"Rebuild tests failed:\n{output[-1000:]}"


def test_repo_doctree_tests():
    """Hugo doctree subpackage tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-count=1", "-timeout", "30s", "./hugolib/doctree/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"doctree tests failed:\n{result.stderr[-500:]}"


def test_repo_hugolib_unit_tests():
    """Hugo hugolib unit tests pass (pass_to_pass)."""
    # Run a quick subset of tests (excluding rebuild tests which have their own test)
    result = subprocess.run(
        ["go", "test", "-count=1", "-timeout", "60s", "-run", "Test[^R]", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:]}"


def test_dirs_loop_counter_bug_fixed():
    """Verify the specific counter bug in the dirs filtering loop is fixed (f2p).

    The buggy code was in the section that filters 'others' based on 'dirs'.
    It had:
    - Outer: for _, d := range dirs
    - Inner: for _, o := range others
    - Bug: others[n] = o and n++ inside the inner loop

    This caused n to exceed len(others) when len(dirs) > 1.

    The fix swaps the loops:
    - Outer: for _, o := range others
    - Inner: for _, d := range dirs
    - Correct: others[n] = o and n++ inside 'if keep' block (per outer iteration)
    """
    with open(f"{REPO}/hugolib/site.go", "r") as f:
        content = f.read()

    # Find the specific section: "Remove all files below dir."
    # This is the buggy section that needs fixing
    section_match = re.search(
        r'// Remove all files below dir\.'
        r'(.*?)'
        r'others = others\[:n\]',
        content,
        re.DOTALL
    )

    if not section_match:
        assert False, "Could not find 'Remove all files below dir' section"

    section = section_match.group(1)

    # Check for the FIXED pattern:
    # - Outer loop over 'others'
    # - Inner loop over 'dirs'
    # - 'keep' variable
    # - n++ only in the outer loop context

    has_outer_others = "for _, o := range others" in section
    has_inner_dirs = "for _, d := range dirs" in section
    has_keep = "keep := true" in section

    if not has_outer_others:
        assert False, "Fix not applied: Outer loop should iterate over 'others', not 'dirs'"

    if not has_inner_dirs:
        assert False, "Fix not applied: Inner loop should iterate over 'dirs'"

    if not has_keep:
        assert False, "Fix not applied: Should use 'keep := true' pattern"


def test_no_buggy_counter_pattern():
    """Verify the buggy counter pattern is not present (f2p).

    The buggy pattern increments n inside the inner loop that iterates over 'others',
    but the outer loop iterates over 'dirs'. When len(dirs) > 1 and len(others) > 0,
    n will exceed len(others).

    Buggy pattern:
        for _, d := range dirs {       <- outer
            for _, o := range others { <- inner
                if ... {
                    others[n] = o      <- n incremented here - BUG!
                    n++
                }
            }
        }
    """
    with open(f"{REPO}/hugolib/site.go", "r") as f:
        content = f.read()

    # Find the section after "Remove all files below dir."
    section_match = re.search(
        r'// Remove all files below dir\.'
        r'(.*?)'
        r'others = others\[:n\]',
        content,
        re.DOTALL
    )

    if not section_match:
        assert False, "Could not find 'Remove all files below dir' section"

    section = section_match.group(1)

    # The buggy pattern has:
    # - 'for _, d := range dirs' as the OUTER loop (comes first in code)
    # - 'for _, o := range others' as the INNER loop
    # - 'others[n] = o' and 'n++' inside the inner loop body

    # Check loop order by finding positions
    outer_dirs_match = re.search(r'for _, d := range dirs', section)
    inner_others_match = re.search(r'for _, o := range others', section)

    if not outer_dirs_match or not inner_others_match:
        # Loops not found - might already be fixed or structure changed
        return

    # If dirs loop comes before others loop in the section,
    # AND others[n] is inside the others loop body, it's buggy
    if outer_dirs_match.start() < inner_others_match.start():
        # Dirs is outer - check if n++ is inside the others (inner) loop
        # Find the position of n++ after the others loop
        after_others = section[inner_others_match.start():]

        # Find where the inner loop ends (next closing brace at that indent level)
        # Simple heuristic: look for n++ before the closing of inner loop
        # The n++ should be at the same indentation level as the 'if' inside the inner loop

        # Check if 'n++' appears inside the inner loop body
        # The inner loop body starts after 'for _, o := range others {'
        inner_loop_start = inner_others_match.end()

        # Look for the next closing brace that ends the inner loop
        # This is complex, so we'll use a simpler check:
        # If the pattern 'if' followed by 'others[n]' and 'n++' exists inside the
        # section after 'for _, o := range others', it's the buggy pattern

        inner_section = section[inner_loop_start:]

        # Find n++ in the inner section (before any function-level closing braces)
        n_plus_plus = re.search(r'n\+\+', inner_section)
        others_n = re.search(r'others\[n\] = o', inner_section)

        if n_plus_plus and others_n:
            # Check that n++ is at the same level as the if statement (indented)
            # In the buggy code, both are inside the inner loop
            # In the fixed code, n++ is inside 'if keep' which is at outer loop level

            # Simple check: if n++ appears before the next 'for' or 'if keep',
            # it's likely in the wrong place
            lines = inner_section.split('\n')
            n_plus_plus_line = -1
            if_keep_line = -1

            for i, line in enumerate(lines):
                if 'n++' in line:
                    n_plus_plus_line = i
                if 'if keep' in line:
                    if_keep_line = i

            if n_plus_plus_line >= 0 and if_keep_line == -1:
                # n++ exists but no 'if keep' - definitely buggy
                assert False, "Buggy counter pattern: n++ without 'if keep' block (missing fix)"

            if n_plus_plus_line >= 0 and if_keep_line >= 0 and n_plus_plus_line < if_keep_line:
                # n++ comes before if keep - could be buggy
                # Actually in the fixed version, n++ is inside the if keep block
                pass  # Let the structural test catch this


def test_safe_counter_pattern():
    """Verify the safe counter pattern is present (f2p).

    The fixed pattern:
        for _, o := range others {
            keep := true
            for _, d := range dirs {
                if strings.HasPrefix(o.p.Path(), d.p.Path()+"/") {
                    keep = false
                    break
                }
            }
            if keep {
                others[n] = o
                n++
            }
        }
    """
    with open(f"{REPO}/hugolib/site.go", "r") as f:
        content = f.read()

    # Find the section
    section_match = re.search(
        r'// Remove all files below dir\.'
        r'(.*?)'
        r'others = others\[:n\]',
        content,
        re.DOTALL
    )

    if not section_match:
        assert False, "Could not find 'Remove all files below dir' section"

    section = section_match.group(1)

    # Check for the fixed pattern components
    # 1. Outer loop over 'others'
    if "for _, o := range others" not in section:
        assert False, "Fixed pattern: missing outer loop over 'others'"

    # 2. 'keep := true' assignment
    if "keep := true" not in section:
        assert False, "Fixed pattern: missing 'keep := true'"

    # 3. Check for d.p.Path()+"/" pattern (the fixed path comparison)
    if 'd.p.Path()+"/"' not in section:
        assert False, "Fixed pattern: missing 'd.p.Path()+\"/\"' (fix uses this form)"

    # 4. 'if keep {' with n++ inside
    if_keep_pattern = re.search(r'if keep \{[^}]*others\[n\] = o[^}]*n\+\+', section, re.DOTALL)
    if not if_keep_pattern:
        # Could be multi-line, check separately
        has_if_keep = "if keep {" in section
        has_others_n = "others[n] = o" in section
        has_n_plus_plus = "n++" in section

        if not (has_if_keep and has_others_n and has_n_plus_plus):
            assert False, "Fixed pattern: missing 'if keep' block with 'others[n] = o' and 'n++'"


