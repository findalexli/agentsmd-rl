"""
Task: react-devtools-suspense-breadcrumbs
Repo: facebook/react @ 95ffd6cd9c794842e5c8ab36150296afab1ae70c
PR:   35700

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/react"
BREADCRUMBS_JS = f"{REPO}/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.js"
BREADCRUMBS_CSS = f"{REPO}/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.css"
SUSPENSE_TAB_CSS = f"{REPO}/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.css"
SUSPENSE_TAB_JS = f"{REPO}/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """All modified files must be present in the repo."""
    # AST-only because: CSS/JS files cannot be executed in Python
    for path in [BREADCRUMBS_JS, BREADCRUMBS_CSS, SUSPENSE_TAB_CSS, SUSPENSE_TAB_JS]:
        assert Path(path).exists(), f"Missing file: {path}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_container_css_class():
    """SuspenseBreadcrumbsContainer CSS class added for flex overflow containment."""
    # AST-only because: CSS/JS files cannot be executed in Python
    css = Path(BREADCRUMBS_CSS).read_text()
    assert "SuspenseBreadcrumbsContainer" in css, (
        "SuspenseBreadcrumbsContainer class missing from SuspenseBreadcrumbs.css"
    )


# [pr_diff] fail_to_pass
def test_menu_css_classes():
    """CSS classes for overflow menu button and modal dropdown defined."""
    # AST-only because: CSS/JS files cannot be executed in Python
    css = Path(BREADCRUMBS_CSS).read_text()
    assert "SuspenseBreadcrumbsMenuButton" in css, (
        "SuspenseBreadcrumbsMenuButton class missing from SuspenseBreadcrumbs.css"
    )
    assert "SuspenseBreadcrumbsModal" in css, (
        "SuspenseBreadcrumbsModal class missing from SuspenseBreadcrumbs.css"
    )


# [pr_diff] fail_to_pass
def test_overflow_components_added():
    """FlatList, Menu, and Dropdown sub-components implemented in SuspenseBreadcrumbs.js."""
    # AST-only because: CSS/JS files cannot be executed in Python
    js = Path(BREADCRUMBS_JS).read_text()
    assert "function SuspenseBreadcrumbsFlatList" in js, (
        "SuspenseBreadcrumbsFlatList component missing from SuspenseBreadcrumbs.js"
    )
    assert "function SuspenseBreadcrumbsMenu" in js, (
        "SuspenseBreadcrumbsMenu component missing from SuspenseBreadcrumbs.js"
    )
    assert "function SuspenseBreadcrumbsDropdown" in js, (
        "SuspenseBreadcrumbsDropdown component missing from SuspenseBreadcrumbs.js"
    )


# [pr_diff] fail_to_pass
def test_overflow_detection_hook():
    """useIsOverflowing hook imported and applied for overflow detection."""
    # AST-only because: CSS/JS files cannot be executed in Python
    js = Path(BREADCRUMBS_JS).read_text()
    assert "useIsOverflowing" in js, (
        "useIsOverflowing hook not present in SuspenseBreadcrumbs.js"
    )


# [pr_diff] fail_to_pass
def test_resize_observer_used():
    """ResizeObserver used to measure breadcrumb container width dynamically."""
    # AST-only because: CSS/JS files cannot be executed in Python
    js = Path(BREADCRUMBS_JS).read_text()
    assert "ResizeObserver" in js, (
        "ResizeObserver missing from SuspenseBreadcrumbs.js"
    )


# [pr_diff] fail_to_pass
def test_conditional_overflow_rendering():
    """Component conditionally renders menu or flat list based on overflow state."""
    # AST-only because: CSS/JS files cannot be executed in Python
    js = Path(BREADCRUMBS_JS).read_text()
    assert "isOverflowing" in js, (
        "isOverflowing variable missing from SuspenseBreadcrumbs.js"
    )
    # Must be used in a conditional (ternary) to switch between views
    assert ("isOverflowing ?" in js or "isOverflowing?" in js), (
        "isOverflowing must be used in a ternary conditional to switch rendering modes"
    )


# [pr_diff] fail_to_pass
def test_overflow_x_scrollbar_removed():
    """overflow-x: auto removed from SuspenseTab.css — no more horizontal scrollbar."""
    # AST-only because: CSS/JS files cannot be executed in Python
    css = Path(SUSPENSE_TAB_CSS).read_text()
    assert "overflow-x: auto" not in css, (
        "overflow-x: auto still present in SuspenseTab.css; horizontal scrollbar not removed"
    )


# [pr_diff] fail_to_pass
def test_wrapper_div_removed():
    """Wrapper div with SuspenseBreadcrumbs className removed from SuspenseTab.js."""
    # AST-only because: CSS/JS files cannot be executed in Python
    js = Path(SUSPENSE_TAB_JS).read_text()
    assert "className={styles.SuspenseBreadcrumbs}" not in js, (
        "Old wrapper div with className={styles.SuspenseBreadcrumbs} still present in SuspenseTab.js"
    )


# [pr_diff] fail_to_pass
def test_reach_ui_menu_import():
    """Menu components imported from reach-ui/menu-button for accessible dropdown."""
    # AST-only because: CSS/JS files cannot be executed in Python
    js = Path(BREADCRUMBS_JS).read_text()
    assert "from '../Components/reach-ui/menu-button'" in js, (
        "reach-ui menu-button import missing from SuspenseBreadcrumbs.js"
    )
