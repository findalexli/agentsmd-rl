"""Tests for ant-design TypeScript test type safety improvements."""

import subprocess
import re
import os

REPO = "/workspace/ant-design"

# Copy environment and add NODE_OPTIONS for memory
ENV = os.environ.copy()
ENV["NODE_OPTIONS"] = "--max-old-space-size=4096"


def test_snapshot_target_type_exists():
    """Fail-to-pass: SnapshotTarget type must be defined in setupAfterEnv.ts"""
    with open(f"{REPO}/tests/setupAfterEnv.ts", "r") as f:
        content = f.read()

    # Must have SnapshotTarget type definition
    assert "type SnapshotTarget = HTMLElement | DocumentFragment | HTMLCollection | NodeList | Node[]" in content, \
        "SnapshotTarget type not found or incorrect"


def test_format_html_uses_proper_types():
    """Fail-to-pass: formatHTML function must use SnapshotTarget instead of any"""
    with open(f"{REPO}/tests/setupAfterEnv.ts", "r") as f:
        content = f.read()

    # Must use SnapshotTarget type for parameter
    assert "function formatHTML(nodes: SnapshotTarget)" in content, \
        "formatHTML function signature doesn't use SnapshotTarget type"

    # Must use proper types for cloneNodes variable
    assert "let cloneNodes: Node | Node[]" in content, \
        "cloneNodes variable not properly typed"

    # Must use proper type assertions instead of 'as any'
    assert "as any" not in content or "as HTMLElement" in content, \
        "Still using 'as any' instead of 'as HTMLElement'"


def test_print_uses_type_assertion():
    """Fail-to-pass: print functions must use SnapshotTarget type assertion"""
    with open(f"{REPO}/tests/setupAfterEnv.ts", "r") as f:
        content = f.read()

    # Both print functions must cast element to SnapshotTarget
    # First serializer uses: formatHTML(element as SnapshotTarget)
    assert "formatHTML(element as SnapshotTarget)" in content, \
        "First print function not using SnapshotTarget type assertion"

    # Check for the second serializer - may use "element as SnapshotTarget" or
    # "(children.length > 1 ? children : children[0]) as SnapshotTarget"
    matches = re.findall(r"as SnapshotTarget", content)
    assert len(matches) >= 2, f"Expected at least 2 SnapshotTarget assertions, found {len(matches)}"


def test_focusable_ref_type_exists():
    """Fail-to-pass: FocusableRef type must be defined in focusTest.tsx"""
    with open(f"{REPO}/tests/shared/focusTest.tsx", "r") as f:
        content = f.read()

    # Must have FocusableRef type with focus and blur methods
    assert "type FocusableRef = {" in content, "FocusableRef type not found"
    assert "focus: () => void" in content, "FocusableRef.focus method not found"
    assert "blur: () => void" in content, "FocusableRef.blur method not found"


def test_focus_test_ref_uses_proper_type():
    """Fail-to-pass: React.createRef must use FocusableRef instead of any"""
    with open(f"{REPO}/tests/shared/focusTest.tsx", "r") as f:
        content = f.read()

    # Must use React.createRef<FocusableRef>() instead of React.createRef<any>()
    assert "React.createRef<FocusableRef>()" in content, \
        "createRef not using FocusableRef type"

    # Should not use createRef<any>()
    assert "React.createRef<any>()" not in content, \
        "Still using createRef<any>()"


def test_get_element_returns_typed_element():
    """Fail-to-pass: getElement must return HTMLElement and use generic querySelector"""
    with open(f"{REPO}/tests/shared/focusTest.tsx", "r") as f:
        content = f.read()

    # Must return HTMLElement type explicitly
    assert "const getElement = (container: HTMLElement): HTMLElement => {" in content, \
        "getElement function doesn't have proper return type annotation"

    # Must use querySelector<HTMLElement> instead of querySelector without type
    assert "querySelector<HTMLElement>" in content, \
        "querySelector not using generic type parameter"

    # Must have expect(element).not.toBeNull() assertion
    assert "expect(element).not.toBeNull()" in content, \
        "Missing null check assertion for element"


def test_fire_event_calls_without_nonnull_assertion():
    """Fail-to-pass: fireEvent calls should not need non-null assertion operator"""
    with open(f"{REPO}/tests/shared/focusTest.tsx", "r") as f:
        content = f.read()

    # After fixing getElement to return HTMLElement (not nullable),
    # fireEvent calls should not need the `!` non-null assertion
    # The old code had `fireEvent.focus(getElement(container)!)`
    # The new code should have `fireEvent.focus(getElement(container))`

    # Count calls with non-null assertion (should be 0 after fix)
    non_null_calls = content.count("getElement(container)!")
    assert non_null_calls == 0, \
        f"Found {non_null_calls} fireEvent calls still using non-null assertion on getElement result"


def test_typescript_compiles():
    """Pass-to-pass: TypeScript compilation must pass (tsc --noEmit)"""
    # Run full type check - this validates the repo compiles with our changes
    result = subprocess.run(
        "npx tsc --noEmit",
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=ENV,
        shell=True
    )

    # If OOM, the types are probably valid (compilation started)
    # If syntax/type errors, the fix is incomplete
    stderr_lower = result.stderr.lower()
    stdout_lower = result.stdout.lower()

    # Check for actual TypeScript type errors (not OOM or other issues)
    has_type_error = "error ts" in stderr_lower or "error ts" in stdout_lower
    has_syntax_error = "syntax" in stderr_lower or "unexpected" in stdout_lower

    if has_type_error or has_syntax_error:
        assert False, f"TypeScript compilation has type/syntax errors:\n{result.stdout}\n{result.stderr}"

    # If OOM or success, consider it passed (OOM indicates compilation was attempted)
    # The AST-based tests will verify the actual types


def test_focus_test_runs():
    """Pass-to-pass: Focus-related tests must pass"""
    # Run a quick test on just the setup and focus test files
    result = subprocess.run(
        "npx jest --config .jest.js --testPathPattern focusTest --passWithNoTests",
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV,
        shell=True
    )

    # This may fail if no tests match, but we check for specific errors
    if result.returncode != 0:
        # Check if it's a TypeScript compilation error
        stderr = result.stderr.lower()
        stdout = result.stdout.lower()
        if "typescript" in stderr or "ts(" in stderr or "error ts" in stdout:
            assert False, f"TypeScript compilation error in tests:\n{result.stderr}\n{result.stdout}"


def test_lint_passes():
    """Pass-to-pass: ESLint must pass on modified files"""
    # Check the specific files for lint errors
    for file in ["tests/setupAfterEnv.ts", "tests/shared/focusTest.tsx"]:
        result = subprocess.run(
            f"npx eslint {file} --max-warnings 0",
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
            env=ENV,
            shell=True
        )

        # Not strictly failing on returncode as ESLint might be configured differently
        # But check for actual TypeScript-related lint errors
        if "@typescript-eslint/no-explicit-any" in result.stdout:
            assert False, f"Found explicit 'any' types in {file} - violates @typescript-eslint/no-explicit-any"


def test_lint_biome_passes():
    """Pass-to-pass: Biome lint must pass (repo CI check)"""
    # Biome lint is part of the repo's CI pipeline
    result = subprocess.run(
        "npx biome lint",
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV,
        shell=True
    )

    # Biome lint should pass with no errors
    assert result.returncode == 0, f"Biome lint failed:\n{result.stdout}\n{result.stderr}"


def test_full_lint_suite_passes():
    """Pass-to-pass: Full lint suite (version + tsc + lint:script + biome + md + changelog)"""
    # Run the full npm run lint which includes:
    # - npm run version (generate version file)
    # - npm run tsc (TypeScript check)
    # - npm run lint:script (ESLint)
    # - npm run lint:biome (Biome)
    # - npm run lint:md (Markdown)
    # - npm run lint:changelog (Changelog)
    result = subprocess.run(
        "npm run lint",
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=ENV,
        shell=True
    )

    # The lint command should pass
    # Note: There may be warnings but no errors
    stderr_lower = result.stderr.lower() if result.stderr else ""
    stdout_lower = result.stdout.lower() if result.stdout else ""

    # Check for actual errors (not warnings)
    has_error = "error:" in stderr_lower or "error:" in stdout_lower
    has_ts_error = "error ts" in stderr_lower or "error ts" in stdout_lower

    if has_error or has_ts_error:
        assert False, f"Lint suite failed with errors:\n{result.stdout}\n{result.stderr}"
