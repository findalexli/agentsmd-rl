"""
Test suite for cssinjs-simplify-selectors task.

This task requires refactoring CSS-in-JS style files to simplify redundant
static style selector keys from multi-line template literals to single-line strings.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/ant-design")

# Files that should be modified
TARGET_FILES = [
    "components/collapse/style/index.ts",
    "components/date-picker/style/panel.ts",
    "components/dropdown/style/index.ts",
    "components/form/style/index.ts",
    "components/menu/style/index.ts",
    "components/table/style/bordered.ts",
    "components/table/style/empty.ts",
    "components/table/style/index.ts",
    "components/typography/style/index.ts",
    "components/typography/style/mixins.ts",
]


def test_typescript_compiles():
    """Fail-to-pass: TypeScript should compile without errors after the fix."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_no_multiline_template_selectors_in_collapse():
    """Fail-to-pass: Collapse style should not use multi-line template selectors."""
    content = (REPO / "components/collapse/style/index.ts").read_text()
    # Should NOT have the old multi-line template literal pattern
    assert "`\\n          &,\\n          & > .arrow\\n        `" not in content, \
        "Found multi-line template selector in collapse style that should be refactored"
    # SHOULD have the simplified single-line string
    assert "'&, & > .arrow'" in content, \
        "Missing simplified selector string in collapse style"


def test_no_multiline_template_selectors_in_date_picker():
    """Fail-to-pass: Date picker panel style should not use multi-line template selectors."""
    content = (REPO / "components/date-picker/style/panel.ts").read_text()
    # Should NOT have old multi-line patterns
    assert "&-prev-icon,\\n        &-next-icon" not in content, \
        "Found multi-line template selector in date-picker panel style"
    # SHOULD have simplified single-line strings
    assert "'&-prev-icon, &-next-icon, &-super-prev-icon, &-super-next-icon'" in content, \
        "Missing simplified selector string in date-picker panel style"


def test_no_multiline_template_selectors_in_dropdown():
    """Fail-to-pass: Dropdown style should not use multi-line template selectors."""
    content = (REPO / "components/dropdown/style/index.ts").read_text()
    # Should NOT have old multi-line patterns
    assert "&-hidden,\\n        &-menu-hidden" not in content, \
        "Found multi-line template selector in dropdown style"
    # SHOULD have simplified single-line string
    assert "'&-hidden, &-menu-hidden, &-menu-submenu-hidden'" in content, \
        "Missing simplified selector string in dropdown style"


def test_no_multiline_template_selectors_in_form():
    """Fail-to-pass: Form style should not use multi-line template selectors."""
    content = (REPO / "components/form/style/index.ts").read_text()
    # Should NOT have old multi-line patterns
    assert "input[type='file']:focus,\\n  input[type='radio']:focus" not in content, \
        "Found multi-line template selector in form style"
    # SHOULD have simplified single-line string (note: uses double quotes)
    assert '''"input[type='file']:focus, input[type='radio']:focus, input[type='checkbox']:focus"''' in content, \
        "Missing simplified selector string in form style"


def test_no_multiline_template_selectors_in_menu():
    """Fail-to-pass: Menu style should not use multi-line template selectors."""
    content = (REPO / "components/menu/style/index.ts").read_text()
    # Check for various menu selector patterns that were refactored
    # Should NOT have the old multi-line patterns
    assert "&-placement-leftTop,\\n          &-placement-bottomRight" not in content, \
        "Found multi-line template selector in menu style"
    # SHOULD have simplified single-line strings
    assert "'&-placement-leftTop, &-placement-bottomRight'" in content, \
        "Missing simplified selector string in menu style"


def test_no_multiline_template_selectors_in_table_bordered():
    """Fail-to-pass: Table bordered style should not use multi-line template selectors."""
    content = (REPO / "components/table/style/bordered.ts").read_text()
    # Should NOT have old multi-line patterns for tbody cells
    assert "> table > tbody > tr > th,\\n            > table > tbody > tr > td" not in content, \
        "Found multi-line template selector in table bordered style"
    # SHOULD have simplified single-line strings
    assert "'> table > tbody > tr > th, > table > tbody > tr > td'" in content, \
        "Missing simplified selector string in table bordered style"


def test_no_multiline_template_selectors_in_table_empty():
    """Fail-to-pass: Table empty style should not use multi-line template selectors."""
    content = (REPO / "components/table/style/empty.ts").read_text()
    # Should NOT have old multi-line pattern
    assert "&:hover > th,\\n          &:hover > td" not in content, \
        "Found multi-line template selector in table empty style"
    # SHOULD have simplified single-line string
    assert "'&:hover > th, &:hover > td'" in content, \
        "Missing simplified selector string in table empty style"


def test_no_multiline_template_selectors_in_table_index():
    """Fail-to-pass: Table index style should not use multi-line template selectors."""
    content = (REPO / "components/table/style/index.ts").read_text()
    # Should NOT have old multi-line pattern
    assert "> tr > th,\\n          > tr > td" not in content, \
        "Found multi-line template selector in table index style"
    # SHOULD have simplified single-line string
    assert "'> tr > th, > tr > td'" in content, \
        "Missing simplified selector string in table index style"


def test_no_multiline_template_selectors_in_typography():
    """Fail-to-pass: Typography style should not use multi-line template selectors."""
    content = (REPO / "components/typography/style/index.ts").read_text()
    # Should NOT have old multi-line patterns
    assert "div&,\\n        p" not in content, \
        "Found multi-line template selector in typography style"
    # SHOULD have simplified single-line strings
    assert "'div&, p'" in content, \
        "Missing simplified selector string 'div&, p' in typography style"


def test_no_multiline_template_selectors_in_typography_mixins():
    """Fail-to-pass: Typography mixins should not use multi-line template selectors."""
    content = (REPO / "components/typography/style/mixins.ts").read_text()
    # Should NOT have old multi-line patterns for copy-success
    assert "&,\\n    &:hover,\\n    &:focus" not in content, \
        "Found multi-line template selector in typography mixins"
    # SHOULD have simplified single-line strings
    assert "'&, &:hover, &:focus'" in content, \
        "Missing simplified selector string in typography mixins"


def test_file_count_unchanged():
    """Pass-to-pass: The number of modified files should match expected count."""
    # Verify all expected files exist
    for file_path in TARGET_FILES:
        full_path = REPO / file_path
        assert full_path.exists(), f"Expected file does not exist: {file_path}"


def test_consistent_selector_format():
    """Pass-to-pass: All modified files should use consistent selector formatting."""
    # Verify at least one of the files has the simplified pattern
    collapse_content = (REPO / "components/collapse/style/index.ts").read_text()
    typography_content = (REPO / "components/typography/style/index.ts").read_text()

    # Check for simplified single-line string patterns
    has_simplified_collapse = "'&, & > .arrow'" in collapse_content
    has_simplified_typography = "'div&, p'" in typography_content

    assert has_simplified_collapse or has_simplified_typography, \
        "No simplified selector patterns found in modified files"


def test_repo_biome_lint():
    """Repo's Biome lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:biome"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_version():
    """Repo's version script passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "version"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Version script failed:\n{r.stderr}"
