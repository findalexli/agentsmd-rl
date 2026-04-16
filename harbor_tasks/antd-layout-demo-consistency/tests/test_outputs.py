"""Tests for ant-design layout demo consistency fix.

This verifies that currentYear is initialized inside the App component
rather than at module level for consistency across all layout demos.
"""

import re
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
# Fail-to-Pass Tests: Must fail on buggy code, pass on fixed code
# =============================================================================


def _get_current_year_declarations(content: str):
    """
    Find all declarations that look like `currentYear = new Date().getFullYear()`
    and determine whether each is at module level or inside a component.

    Returns a list of tuples: (line_number, is_inside_component)
    """
    lines = content.split('\n')
    declarations = []

    in_component = False
    brace_depth = 0
    component_start_line = -1
    seen_arrow_brace = False

    # Pattern to match currentYear declaration
    year_pattern = re.compile(r'const\s+currentYear\s*=\s*new\s+Date\(\)\.getFullYear\(\)')

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect App component start
        if 'const App' in stripped and ('React.FC' in stripped or '= ()' in stripped or '= () =>' in stripped):
            in_component = True
            component_start_line = i
            brace_depth = 0
            seen_arrow_brace = False
            # Check if => { is on this same line
            if '=>' in stripped and '{' in stripped:
                seen_arrow_brace = True
                brace_depth = 1
            continue

        if in_component:
            # If we haven't found the arrow brace yet, look for it
            if not seen_arrow_brace:
                if '=>' in stripped:
                    # The next { after => is the function body
                    idx = stripped.find('=>')
                    after_arrow = stripped[idx+2:]
                    if '{' in after_arrow:
                        seen_arrow_brace = True
                        brace_depth = 1
                        # Count any remaining braces on this line
                        brace_depth += after_arrow.count('{') - after_arrow.count('}')
                    elif stripped.startswith('}'):
                        # } on next line is still part of destructuring, skip
                        continue
            else:
                # Track brace depth
                brace_depth += stripped.count('{') - stripped.count('}')

            # Check for currentYear declaration
            if year_pattern.search(stripped):
                # If seen_arrow_brace and brace_depth > 0, we're inside the function body
                if seen_arrow_brace and brace_depth > 0:
                    declarations.append((i, True))
                else:
                    declarations.append((i, False))

            # Exit component when we've closed all braces and we're past the start
            if seen_arrow_brace and brace_depth <= 0 and i > component_start_line:
                if '};' in stripped or stripped == '}' or stripped.endswith('}'):
                    in_component = False
        else:
            # Module level - check for currentYear
            if year_pattern.search(stripped):
                declarations.append((i, False))

    return declarations


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

        decls = _get_current_year_declarations(content)
        module_level = [d for d in decls if not d[1]]

        if module_level:
            violations.append(f"{filename} (lines: {[d[0]+1 for d in module_level]})")

    assert not violations, \
        f"Module-level currentYear declarations found in: {', '.join(violations)}. " \
        f"Move currentYear inside the App component."


def test_current_year_inside_component():
    """Fail-to-pass: currentYear should be declared inside the App component.

    After the fix, currentYear should be initialized inside the App component
    for consistency with React best practices.
    """
    missing = []
    for filename in TARGET_FILES:
        filepath = DEMO_DIR / filename
        content = filepath.read_text(encoding="utf-8")

        decls = _get_current_year_declarations(content)
        inside_component = [d for d in decls if d[1]]

        if not inside_component:
            missing.append(filename)

    assert not missing, \
        f"Component-level currentYear not found in: {', '.join(missing)}. " \
        f"Add `const currentYear = new Date().getFullYear();` inside the App component."


def test_footer_uses_current_year():
    """Verify the Footer component actually uses the currentYear variable."""
    for filename in TARGET_FILES:
        filepath = DEMO_DIR / filename
        content = filepath.read_text(encoding="utf-8")

        # Check that Footer uses currentYear in JSX
        assert "{currentYear}" in content, \
            f"{filename}: Footer should reference currentYear in JSX (e.g., as {{currentYear}})"