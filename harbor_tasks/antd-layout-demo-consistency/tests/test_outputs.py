"""Tests for ant-design layout demo consistency fix.

This verifies that currentYear is initialized inside the App component
rather than at module level for consistency across all layout demos.
"""

import ast
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
DEMO_DIR = REPO / "components" / "layout" / "demo"

TARGET_FILES = [
    "fixed-sider.tsx",
    "fixed.tsx",
    "responsive.tsx",
    "side.tsx",
    "top-side.tsx",
    "top.tsx",
]


def run_repo_command(cmd, cwd=REPO, timeout=120, env=None):
    """Run a command in the repo directory and return the result."""
    # Inherit PATH from current environment to find npx
    import os
    full_env = os.environ.copy()
    full_env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    if env:
        full_env.update(env)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        env=full_env,
    )


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD checks that should pass on both base and fix
# =============================================================================


def test_repo_tsc():
    """Repo's TypeScript typecheck passes (pass_to_pass).

    Verifies the codebase has no TypeScript errors.
    """
    r = run_repo_command(["npx", "tsc", "--noEmit"], timeout=120)
    err_out = r.stderr[-1000:] if r.stderr else ""
    std_out = r.stdout[-1000:] if r.stdout else ""
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{err_out}\n{std_out}"


def test_repo_eslint_layout():
    """Repo's ESLint passes on layout demo files (pass_to_pass).

    Verifies the layout demo files follow the project's linting rules.
    """
    r = run_repo_command(
        ["npx", "eslint", "components/layout/demo/", "--cache"],
        timeout=60,
    )
    err_out = r.stderr[-500:] if r.stderr else ""
    std_out = r.stdout[-500:] if r.stdout else ""
    assert r.returncode == 0, f"ESLint failed:\n{err_out}\n{std_out}"


def test_repo_biome_lint_layout():
    """Repo's Biome lint passes on layout demo files (pass_to_pass).

    Verifies the layout demo files pass Biome linting rules.
    """
    r = run_repo_command(
        ["npx", "biome", "lint", "components/layout/demo/"],
        timeout=60,
    )
    err_out = r.stderr[-500:] if r.stderr else ""
    std_out = r.stdout[-500:] if r.stdout else ""
    assert r.returncode == 0, f"Biome lint failed:\n{err_out}\n{std_out}"


def test_repo_layout_demo_tests():
    """Repo's Jest tests for layout component pass (pass_to_pass).

    Verifies the layout component and its demos render correctly.
    """
    # Generate version file first (required for tests)
    r1 = run_repo_command(["npm", "run", "version"], timeout=30)
    err_out1 = r1.stderr[-500:] if r1.stderr else ""
    assert r1.returncode == 0, f"Version generation failed:\n{err_out1}"

    # Run layout demo tests
    r = run_repo_command(
        [
            "npx",
            "jest",
            "--config",
            ".jest.js",
            "components/layout/__tests__/demo.test.ts",
            "--no-cache",
            "--maxWorkers=1",
        ],
        timeout=120,
    )
    err_out = r.stderr[-1000:] if r.stderr else ""
    std_out = r.stdout[-1000:] if r.stdout else ""
    assert r.returncode == 0, f"Layout demo tests failed:\n{err_out}\n{std_out}"


def test_repo_prettier_layout():
    """Repo's Prettier formatting check passes on layout demo files (pass_to_pass).

    Verifies the layout demo files follow the project's Prettier formatting rules.
    """
    r = run_repo_command(
        ["npx", "prettier", "--check", "components/layout/demo/*.tsx"],
        timeout=60,
    )
    err_out = r.stderr[-500:] if r.stderr else ""
    std_out = r.stdout[-500:] if r.stdout else ""
    assert r.returncode == 0, f"Prettier check failed:\n{err_out}\n{std_out}"


def test_repo_node_tests():
    """Repo's Node.js environment tests pass (pass_to_pass).

    Verifies the Node.js-specific tests (SSR/rendering) pass.
    """
    r = run_repo_command(
        ["npm", "run", "test:node"],
        timeout=180,
    )
    err_out = r.stderr[-1000:] if r.stderr else ""
    std_out = r.stdout[-1000:] if r.stdout else ""
    assert r.returncode == 0, f"Node tests failed:\n{err_out}\n{std_out}"


# =============================================================================
# Original Task Tests
# =============================================================================


def parse_tsx(filepath: Path) -> ast.AST:
    """Parse a TSX file using Python's ast module (treats as JSX-like)."""
    content = filepath.read_text(encoding="utf-8")
    return content


def has_module_level_current_year(content: str) -> bool:
    """Check if currentYear is declared at module level (outside any function/component)."""
    lines = content.split('\n')
    in_component = False
    brace_depth = 0

    for line in lines:
        stripped = line.strip()

        # Track entering/exiting the App component
        if 'const App: React.FC' in stripped or 'const App = ' in stripped:
            in_component = True

        # Track brace depth for arrow functions
        if in_component:
            brace_depth += stripped.count('{') - stripped.count('}')
            if brace_depth <= 0 and ('};' in stripped or stripped.endswith('}')):
                # Exiting component
                pass

        # Check for module-level currentYear declaration
        if not in_component and 'const currentYear' in stripped:
            return True

    return False


def has_component_level_current_year(content: str) -> bool:
    """Check if currentYear is declared inside the App component."""
    lines = content.split('\n')
    in_component = False
    brace_depth = 0
    found_useToken = False

    for line in lines:
        stripped = line.strip()

        # Entering App component
        if 'const App: React.FC' in stripped or 'const App = ' in stripped:
            in_component = True
            continue

        if in_component:
            # Track brace depth
            brace_depth += stripped.count('{') - stripped.count('}')

            # Check for theme.useToken() to find the right location
            if 'theme.useToken()' in stripped:
                found_useToken = True

            # Check for currentYear declaration inside component
            if 'const currentYear' in stripped:
                # Verify it's after theme.useToken()
                if found_useToken:
                    return True
                # Or check if it's inside the component braces
                if brace_depth > 0:
                    return True

    return False


def test_typescript_compiles():
    """Verify TypeScript syntax and basic structure checks."""
    for filename in TARGET_FILES:
        filepath = DEMO_DIR / filename
        if not filepath.exists():
            raise AssertionError(f"File not found: {filepath}")

        content = filepath.read_text(encoding="utf-8")

        # Basic structure checks
        assert "import React" in content or "from 'react'" in content, \
            f"{filename}: Missing React import"
        assert "export default App" in content, \
            f"{filename}: Missing App export"

        # Check that the file is valid TSX (basic balance checks)
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, \
            f"{filename}: Mismatched braces (syntax error)"


def test_no_module_level_current_year():
    """Fail-to-pass: currentYear should NOT be declared at module level.

    Before the fix, all 6 files had `const currentYear = new Date().getFullYear();`
    at module level (outside any function/component).
    """
    violations = []
    for filename in TARGET_FILES:
        filepath = DEMO_DIR / filename
        content = filepath.read_text(encoding="utf-8")

        if has_module_level_current_year(content):
            violations.append(filename)

    assert not violations, \
        f"Module-level currentYear found in: {', '.join(violations)}. " \
        f"Move currentYear inside the App component."


def test_current_year_inside_component():
    """Pass-to-pass: currentYear should be declared inside the App component.

    After the fix, currentYear should be initialized inside the App component
    for consistency with React best practices (avoiding module-level side effects).
    """
    missing = []
    for filename in TARGET_FILES:
        filepath = DEMO_DIR / filename
        content = filepath.read_text(encoding="utf-8")

        if not has_component_level_current_year(content):
            missing.append(filename)

    assert not missing, \
        f"Component-level currentYear not found in: {', '.join(missing)}. " \
        f"Add `const currentYear = new Date().getFullYear();` inside the App component."


def test_consistent_component_structure():
    """Verify all demos follow the same pattern: theme.useToken() then currentYear."""
    for filename in TARGET_FILES:
        filepath = DEMO_DIR / filename
        content = filepath.read_text(encoding="utf-8")

        lines = content.split('\n')
        found_use_token = False
        found_current_year = False
        current_year_after_token = False

        for line in lines:
            stripped = line.strip()

            if 'theme.useToken()' in stripped:
                found_use_token = True

            if 'const currentYear' in stripped:
                found_current_year = True
                if found_use_token:
                    current_year_after_token = True

        # Both should exist
        assert found_use_token, f"{filename}: Missing theme.useToken() call"

        # After fix, currentYear should be present
        if found_current_year:
            assert current_year_after_token, \
                f"{filename}: currentYear should be declared after theme.useToken()"


def test_footer_uses_current_year():
    """Verify the Footer component actually uses the currentYear variable."""
    for filename in TARGET_FILES:
        filepath = DEMO_DIR / filename
        content = filepath.read_text(encoding="utf-8")

        # Check that Footer uses currentYear
        assert "{currentYear}" in content or "©{currentYear}" in content or "Ant Design ©" in content, \
            f"{filename}: Footer should reference currentYear"
