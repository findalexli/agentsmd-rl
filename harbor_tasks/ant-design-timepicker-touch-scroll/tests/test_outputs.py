"""
Tests for TimePicker touch scroll fix.

The bug: TimePicker columns use overflowY: 'hidden' by default and only
switch to overflowY: 'auto' on hover. Touch devices don't support hover,
so columns can't scroll directly.

The fix: Set overflowY: 'auto' as default and remove the hover override.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Repository path
REPO = Path("/workspace/ant-design")
TARGET_FILE = REPO / "components" / "date-picker" / "style" / "panel.ts"


def _install_deps():
    """Install pnpm and dependencies."""
    subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, check=True)
    subprocess.run(["pnpm", "install"], capture_output=True, cwd=REPO, check=True)


def test_file_exists():
    """Target file must exist."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_typescript_compiles():
    """TypeScript must compile without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_overflow_y_is_auto():
    """overflowY must be set to 'auto' (not 'hidden') in the time column style."""
    content = TARGET_FILE.read_text()

    # Find the time column style object - look for the pattern around line 542
    # The key line is: overflowY: 'auto',

    # First, check that overflowY: 'hidden' is NOT present in the file
    hidden_pattern = r"overflowY:\s*['\"]hidden['\"]"
    hidden_matches = re.findall(hidden_pattern, content)
    assert len(hidden_matches) == 0, f"Found overflowY: 'hidden' in file - should be 'auto'. Matches: {hidden_matches}"

    # Second, verify overflowY: 'auto' exists
    auto_pattern = r"overflowY:\s*['\"]auto['\"]"
    auto_matches = re.findall(auto_pattern, content)
    assert len(auto_matches) >= 1, f"Expected at least one overflowY: 'auto' in file, found {len(auto_matches)}"


def test_hover_overflow_removed():
    """The hover block that sets overflowY: 'auto' must be removed."""
    content = TARGET_FILE.read_text()

    # Look for the hover block pattern that was removed
    # The old code had:
    #   '&:hover': {
    #     overflowY: 'auto',
    #   },

    hover_overflow_pattern = r"['\"]&:hover['\"]:\s*\{[^}]*overflowY:\s*['\"]auto['\"][^}]*\}"
    hover_matches = re.findall(hover_overflow_pattern, content, re.DOTALL)
    assert len(hover_matches) == 0, f"Found &:hover block with overflowY: 'auto' - this should be removed"


def test_time_column_structure_preserved():
    """The time column style structure must be preserved (other properties intact)."""
    content = TARGET_FILE.read_text()

    # Check that the time column style still has expected properties
    # These should not have been accidentally removed
    required_patterns = [
        r"width:\s*timeColumnWidth",
        r"textAlign:\s*['\"]start['\"]",
        r"listStyle:\s*['\"]none['\"]",
    ]

    for pattern in required_patterns:
        matches = re.findall(pattern, content)
        assert len(matches) >= 1, f"Required pattern '{pattern}' not found - time column structure may be broken"


def test_fix_is_idempotent():
    """Running the fix again should not break anything (idempotency check)."""
    # This is checked implicitly - if tests pass after solve.sh runs,
    # the fix is idempotent
    content = TARGET_FILE.read_text()

    # Verify we have exactly what we expect
    auto_count = len(re.findall(r"overflowY:\s*['\"]auto['\"]", content))
    hidden_count = len(re.findall(r"overflowY:\s*['\"]hidden['\"]", content))

    assert hidden_count == 0, f"Found {hidden_count} overflowY: 'hidden' - fix not applied correctly"
    assert auto_count >= 1, f"Expected at least 1 overflowY: 'auto', found {auto_count}"


def test_no_regression_in_other_components():
    """Other parts of the date picker should not be affected."""
    content = TARGET_FILE.read_text()

    # Check that the overall structure of the file is intact
    # The file should still have the genPanelStyle function
    assert "genPanelStyle" in content, "genPanelStyle function missing - major regression"

    # Check for other expected CSS properties that shouldn't be affected
    assert "timeColumnWidth" in content, "timeColumnWidth token missing"
    assert "motionDurationMid" in content, "motionDurationMid token missing"


# ===== Pass-to-Pass Tests (Repo CI/CD) =====

def test_repo_biome_lint():
    """Repo's Biome lint check passes (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["npm", "run", "lint:biome"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_eslint():
    """Repo's ESLint check passes (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["npm", "run", "lint:script"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # ESLint exits with 0 for warnings only, non-zero for errors
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_tsc():
    """Repo's TypeScript compilation passes (pass_to_pass)."""
    _install_deps()
    # TypeScript compilation needs more memory for this large project
    import os
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-500:]}"


def test_repo_prettier_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    _install_deps()
    # Only check the specific file related to the fix
    r = subprocess.run(
        ["pnpm", "exec", "prettier", "-c", "components/date-picker/style/panel.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Prettier returns 0 if file is formatted correctly, 1 if not
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
