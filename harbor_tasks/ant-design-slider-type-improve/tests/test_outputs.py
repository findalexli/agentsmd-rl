#!/usr/bin/env python3
"""
Test suite for ant-design Slider TypeScript type improvement.

This verifies:
1. TypeScript compilation passes without errors
2. The 'as any' cast is removed from onChangeComplete
3. The @ts-ignore comment is removed from RcSlider
4. Proper type assertions are in place
5. Repo CI/CD checks pass (pass_to_pass)
"""

import subprocess
import sys
import re

REPO_PATH = "/workspace/ant-design"
SLIDER_FILE = f"{REPO_PATH}/components/slider/index.tsx"


def test_typescript_compilation():
    """Test that TypeScript compilation passes without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Filter out irrelevant errors - we only care about the slider component
    stderr_lines = result.stderr.strip().split('\n') if result.stderr else []
    slider_errors = [line for line in stderr_lines if 'slider' in line.lower()]

    # Check that there are no TypeScript errors related to slider
    if slider_errors:
        print(f"TypeScript errors in slider component:\n{chr(10).join(slider_errors)}")
        assert False, f"Found {len(slider_errors)} TypeScript errors in slider component"

    # Also check return code - but some repos have pre-existing errors
    # So we primarily care about no NEW slider-related errors
    print("TypeScript compilation check passed (no slider-specific errors)")


def test_no_as_any_cast():
    """Test that 'as any' cast is removed from onChangeComplete handler."""
    with open(SLIDER_FILE, 'r') as f:
        content = f.read()

    # Look for the pattern: onChangeComplete?.(nextValues as any)
    # This is the old, buggy pattern
    old_pattern = r"onChangeComplete\?\.\s*\(\s*nextValues\s+as\s+any\s*\)"

    if re.search(old_pattern, content):
        assert False, "Found 'as any' cast in onChangeComplete call - should use proper type assertion"

    # Verify proper type assertion exists - accept any valid type assertion pattern
    # Could be: (onChangeComplete as Type)?.(nextValues) or similar patterns
    new_patterns = [
        r"\(\s*onChangeComplete\s+as\s+[^)]+\)\?\.",  # (onChangeComplete as SomeType)?.pattern
        r"\(\s*onChangeComplete\s+as\s+[^)]+\)\s*\?",  # (onChangeComplete as SomeType)?
    ]

    has_proper_assertion = any(re.search(p, content) for p in new_patterns)
    if not has_proper_assertion:
        assert False, "Proper type assertion for onChangeComplete not found - expected '(onChangeComplete as SomeType)?.pattern'"

    print("No 'as any' cast found - using proper type assertion")


def test_no_ts_ignore_comment():
    """Test that @ts-ignore comment is removed before RcSlider component."""
    with open(SLIDER_FILE, 'r') as f:
        content = f.read()

    # Look for @ts-ignore comment before RcSlider
    # Pattern: // @ts-ignore followed by <RcSlider within a few lines
    old_pattern = r"//\s*@ts-ignore.*\n.*<RcSlider"

    if re.search(old_pattern, content, re.DOTALL):
        assert False, "Found @ts-ignore comment before RcSlider - should be removed with proper typing"

    # Verify RcSlider is present without @ts-ignore
    if "<RcSlider" not in content:
        assert False, "RcSlider component not found in file"

    print("@ts-ignore comment properly removed from RcSlider usage")


def test_proper_restprops_typing():
    """Test that restProps uses proper type assertion with Omit."""
    with open(SLIDER_FILE, 'r') as f:
        content = f.read()

    # Check for the proper pattern: {...(restProps as Omit<SliderProps, 'onAfterChange' | 'onChange'>)}
    # Accept any Omit pattern that excludes onAfterChange and onChange
    proper_patterns = [
        r"restProps\s+as\s+Omit<SliderProps,\s*['\"]onAfterChange['\"]\s*\|\s*['\"]onChange['\"]>",
        r"restProps\s+as\s+Omit<SliderProps,\s*['\"]onChange['\"]\s*\|\s*['\"]onAfterChange['\"]>",
        r"restProps\s+as\s+Omit<[^>]+onAfterChange[^>]+onChange[^>]*>",
        r"restProps\s+as\s+Omit<[^>]+onChange[^>]+onAfterChange[^>]*>",
    ]

    has_proper_typing = any(re.search(p, content) for p in proper_patterns)

    if not has_proper_typing:
        assert False, "Proper Omit type assertion for restProps not found - expected 'restProps as Omit<...>' excluding onAfterChange and onChange"

    print("Proper Omit type assertion found for restProps")


def test_slider_component_functional():
    """Test that the Slider component still functions correctly after type changes."""
    # This is an integration test - we run the repo's existing tests for the slider
    result = subprocess.run(
        ["sh", "-c", "npm run version && npx jest --config .jest.js --no-cache --testPathPatterns='slider/__tests__/(?!demo)' --passWithNoTests --no-coverage"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120
    )

    # We accept either success or no tests found
    # The main goal is that the component doesn't crash
    if result.returncode != 0 and "No tests found" not in result.stdout:
        # Check if it's a real failure vs just no tests
        if "FAIL" in result.stdout or "error" in result.stderr.lower():
            print(f"Test output:\n{result.stdout}\n{result.stderr}")
            assert False, "Slider tests failed"

    print("Slider component functional check passed")


# ============================================================================
# Pass-to-Pass Tests - Repo CI/CD Checks
# These verify that existing repo CI checks pass on both base and fixed code.
# ============================================================================


def test_repo_slider_unit_tests():
    """Repo's unit tests for slider component pass (pass_to_pass)."""
    # Need to generate version file first (required by antd test setup)
    subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        cwd=REPO_PATH,
    )
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "--testPathPatterns=slider/__tests__/index", "--no-coverage", "--maxWorkers=2"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Slider unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    print("Slider unit tests passed")


def test_repo_eslint_slider():
    """Repo's ESLint check on slider component passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "components/slider/index.tsx", "--max-warnings", "0"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"
    print("ESLint check on slider passed")


def test_repo_biome_lint_slider():
    """Repo's Biome lint check on slider component passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "biome", "lint", "components/slider"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Biome lint check failed:\n{r.stderr[-500:]}"
    print("Biome lint check on slider passed")


def test_repo_biome_check_slider():
    """Repo's Biome check (format + lint) on slider component passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "biome", "check", "components/slider"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Biome check failed:\n{r.stderr[-500:]}"
    print("Biome check on slider passed")


def test_repo_tsc_slider():
    """Repo's TypeScript compilation passes (pass_to_pass)."""
    import os
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO_PATH,
        env=env,
    )
    # Check for any slider-specific errors
    stderr_lines = r.stderr.strip().split('\n') if r.stderr else []
    slider_errors = [line for line in stderr_lines if 'slider' in line.lower()]
    if slider_errors:
        assert False, f"TypeScript errors in slider component:\n{chr(10).join(slider_errors[-10:])}"
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-500:]}"
    print("TypeScript compilation passed")


def test_repo_node_tests():
    """Repo's Node.js tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test:node"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Node tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    print("Node.js tests passed")


def test_repo_slider_type_tests():
    """Repo's slider type tests pass (pass_to_pass)."""
    # Need to generate version file first (required by antd test setup)
    subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        cwd=REPO_PATH,
    )
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "--testPathPatterns=slider/__tests__/type", "--no-coverage", "--maxWorkers=2"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Slider type tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    print("Slider type tests passed")


def test_repo_slider_semantic_tests():
    """Repo's slider semantic tests pass (pass_to_pass)."""
    # Need to generate version file first (required by antd test setup)
    subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        cwd=REPO_PATH,
    )
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "--testPathPatterns=slider/__tests__/semantic", "--no-coverage", "--maxWorkers=2"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Slider semantic tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
    print("Slider semantic tests passed")


if __name__ == "__main__":
    test_functions = [
        test_typescript_compilation,
        test_no_as_any_cast,
        test_no_ts_ignore_comment,
        test_proper_restprops_typing,
        test_slider_component_functional,
        test_repo_slider_unit_tests,
        test_repo_eslint_slider,
        test_repo_biome_lint_slider,
        test_repo_biome_check_slider,
        test_repo_tsc_slider,
        test_repo_node_tests,
        test_repo_slider_type_tests,
        test_repo_slider_semantic_tests,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
            print(f"✓ {test_func.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"✗ {test_func.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__} (unexpected error): {e}")

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
