"""
Tests for Cascader menu item ellipsis fix (ant-design/ant-design#57540)

This PR fixes the Cascader menu item ellipsis styles for long option labels.
The ellipsis styles were incorrectly applied to the parent node (`&-item`)
instead of the actual text container (`&-content`), preventing proper
truncation in flex layouts.

The fix:
1. Removes `...textEllipsis` from `&-item`
2. Adds `maxWidth: 400` to `&-item`
3. Adds `minWidth: 0` and `...textEllipsis` to `&-content`
"""

import os
import subprocess
import sys

REPO_DIR = "/workspace/ant-design"
COLUMNS_STYLE_FILE = os.path.join(REPO_DIR, "components/cascader/style/columns.ts")


def read_columns_style_file():
    """Read the Cascader columns style file."""
    with open(COLUMNS_STYLE_FILE, 'r') as f:
        return f.read()


def test_cascader_columns_file_exists():
    """Verify the columns.ts style file exists."""
    assert os.path.exists(COLUMNS_STYLE_FILE), f"File not found: {COLUMNS_STYLE_FILE}"


def test_text_ellipsis_moved_to_content():
    """
    Fail-to-pass test: The textEllipsis should be in &-content, not &-item.

    This test fails on the base commit where textEllipsis was incorrectly
    applied to the parent &-item element, and passes when it's moved to
    &-content where it belongs.
    """
    content = read_columns_style_file()

    # Find the &-item block and check it does NOT contain textEllipsis
    # We need to check that textEllipsis is not directly in &-item but is in &-content

    # Look for the &-content block with textEllipsis
    lines = content.split('\n')
    in_item_block = False
    in_content_block = False
    item_has_ellipsis = False
    content_has_ellipsis = False
    item_brace_depth = 0
    content_brace_depth = 0

    for line in lines:
        stripped = line.strip()

        # Track &-item block
        if "'&-item':" in stripped or '"&-item":' in stripped:
            in_item_block = True
            item_brace_depth = stripped.count('{') - stripped.count('}')
            continue

        # Track &-content block (nested inside &-item)
        if "'&-content':" in stripped or '"&-content":' in stripped:
            in_content_block = True
            content_brace_depth = stripped.count('{') - stripped.count('}')
            continue

        if in_content_block:
            # Track content block first (nested takes precedence)
            content_brace_depth += stripped.count('{') - stripped.count('}')
            if content_brace_depth >= 0 and 'textEllipsis' in stripped:
                content_has_ellipsis = True
            if content_brace_depth < 0:
                in_content_block = False
        elif in_item_block:
            # Only check item block if we're not in content block
            item_brace_depth += stripped.count('{') - stripped.count('}')
            if item_brace_depth >= 0 and 'textEllipsis' in stripped:
                item_has_ellipsis = True
            if item_brace_depth < 0:
                in_item_block = False

    # The fix: textEllipsis should be in &-content, NOT in &-item
    assert content_has_ellipsis, "FAIL: textEllipsis should be in &-content block"
    assert not item_has_ellipsis, "FAIL: textEllipsis should NOT be in &-item block (it should be in &-content)"


def test_content_has_min_width_zero():
    """
    Fail-to-pass test: &-content should have minWidth: 0 for flexbox ellipsis to work.

    In flex layouts, text ellipsis requires the flex item to have min-width: 0
    to properly calculate overflow and show ellipsis.
    """
    content = read_columns_style_file()

    lines = content.split('\n')
    in_content_block = False
    brace_depth = 0
    has_min_width_zero = False

    for line in lines:
        stripped = line.strip()

        if "'&-content':" in stripped or '"&-content":' in stripped:
            in_content_block = True
            brace_depth = stripped.count('{') - stripped.count('}')
            continue

        if in_content_block:
            brace_depth += stripped.count('{') - stripped.count('}')

            if brace_depth >= 0 and 'minWidth' in stripped and '0' in stripped:
                has_min_width_zero = True

            if brace_depth < 0:
                in_content_block = False

    assert has_min_width_zero, "FAIL: &-content should have minWidth: 0 for ellipsis to work in flex layout"


def test_item_has_max_width():
    """
    Pass-to-pass test: &-item should have maxWidth constraint.

    The fix adds maxWidth: 400 to the &-item to constrain the flex container.
    """
    content = read_columns_style_file()

    lines = content.split('\n')
    in_item_block = False
    brace_depth = 0
    has_max_width = False

    for line in lines:
        stripped = line.strip()

        if "'&-item':" in stripped or '"&-item":' in stripped:
            in_item_block = True
            brace_depth = stripped.count('{') - stripped.count('}')
            continue

        if in_item_block:
            brace_depth += stripped.count('{') - stripped.count('}')

            if brace_depth >= 0 and 'maxWidth' in stripped:
                has_max_width = True

            if brace_depth < 0:
                in_item_block = False

    assert has_max_width, "FAIL: &-item should have maxWidth constraint"


def test_typescript_compiles():
    """
    Verify the TypeScript file is syntactically valid.
    """
    result = subprocess.run(
        ['npx', 'tsc', '--noEmit', '--skipLibCheck', COLUMNS_STYLE_FILE],
        cwd=REPO_DIR,
        capture_output=True,
        timeout=120
    )

    # If tsc is not available, try a simpler syntax check
    if result.returncode != 0 and b"not found" in result.stderr:
        # Fallback: just verify the file has balanced braces
        content = read_columns_style_file()
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, "FAIL: Unbalanced braces in TypeScript file"
    elif result.returncode != 0:
        # Allow certain known type errors but not syntax errors
        stderr = result.stderr.decode()
        # If it mentions syntax or parsing error, that's a real failure
        if "syntax" in stderr.lower() or "parse" in stderr.lower() or "unexpected" in stderr.lower():
            assert False, f"TypeScript syntax error: {stderr[:500]}"


def test_style_structure_valid():
    """
    Verify the style file has the expected structure with proper CSS properties.
    """
    content = read_columns_style_file()

    # Check for key structure elements
    assert "GenerateStyle" in content, "File should import/use GenerateStyle type"
    assert "CascaderToken" in content, "File should reference CascaderToken"
    assert "getColumnsStyle" in content, "File should export getColumnsStyle function"


def test_repo_typescript_check():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR, env=env
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


def test_repo_biome_lint():
    """Repo's Biome lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:biome"],
        capture_output=True, text=True, timeout=120, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stderr[-500:]}"


def test_repo_eslint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:script"],
        capture_output=True, text=True, timeout=180, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_cascader_tests():
    """Repo's Cascader component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=cascader", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader tests failed:\n{r.stderr[-500:]}"


def calculate_reward():
    """Calculate the final reward based on test results."""
    tests = [
        test_cascader_columns_file_exists,
        test_text_ellipsis_moved_to_content,
        test_content_has_min_width_zero,
        test_item_has_max_width,
        test_typescript_compiles,
        test_style_structure_valid,
        test_repo_typescript_check,
        test_repo_biome_lint,
        test_repo_eslint,
        test_repo_cascader_tests,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL: {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"ERROR: {test.__name__}: {e}")

    total = passed + failed
    reward = passed / total if total > 0 else 0

    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    print(f"REWARD: {reward:.2f}")
    print(f"{'='*50}")

    return reward


if __name__ == "__main__":
    reward = calculate_reward()
    sys.exit(0 if reward >= 0.8 else 1)
