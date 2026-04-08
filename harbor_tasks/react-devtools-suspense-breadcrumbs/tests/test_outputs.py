"""
Task: react-devtools-suspense-breadcrumbs
Repo: facebook/react @ 95ffd6cd9c794842e5c8ab36150296afab1ae70c
PR:   35700

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
DEVTOOLS = REPO + "/packages/react-devtools-shared/src/devtools/views/SuspenseTab"
BREADCRUMBS_JS = DEVTOOLS + "/SuspenseBreadcrumbs.js"
BREADCRUMBS_CSS = DEVTOOLS + "/SuspenseBreadcrumbs.css"
SUSPENSE_TAB_CSS = DEVTOOLS + "/SuspenseTab.css"
SUSPENSE_TAB_JS = DEVTOOLS + "/SuspenseTab.js"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_files_exist():
    """All modified files must be present in the repo."""
    for path in [BREADCRUMBS_JS, BREADCRUMBS_CSS, SUSPENSE_TAB_CSS, SUSPENSE_TAB_JS]:
        assert Path(path).exists(), f"Missing file: {path}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js execution
# ---------------------------------------------------------------------------

def test_breadcrumbs_css_overflow_handling():
    """SuspenseBreadcrumbsContainer CSS class with flex layout, MenuButton and Modal classes added."""
    r = _run_node(
        'import { readFileSync } from "fs";\n'
        'const css = readFileSync("' + BREADCRUMBS_CSS + '", "utf8");\n'
        '\n'
        '// Container class must exist with flex layout\n'
        'const containerMatch = css.match(/\\.SuspenseBreadcrumbsContainer\\s*\\{([^}]+)\\}/);\n'
        'if (!containerMatch) { console.error("FAIL: .SuspenseBreadcrumbsContainer not found"); process.exit(1); }\n'
        'const body = containerMatch[1];\n'
        'if (!/display:\\s*flex/.test(body)) { console.error("FAIL: Container missing display: flex"); process.exit(1); }\n'
        '\n'
        '// MenuButton and Modal classes must exist\n'
        'if (!css.includes(".SuspenseBreadcrumbsMenuButton")) { console.error("FAIL: MenuButton class missing"); process.exit(1); }\n'
        'if (!css.includes(".SuspenseBreadcrumbsModal")) { console.error("FAIL: Modal class missing"); process.exit(1); }\n'
        '\n'
        'console.log("PASS");\n'
    )
    assert r.returncode == 0, f"CSS validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_overflow_components_implemented():
    """FlatList, Menu, and Dropdown component functions declared in SuspenseBreadcrumbs.js."""
    r = _run_node(
        'import { readFileSync } from "fs";\n'
        'const js = readFileSync("' + BREADCRUMBS_JS + '", "utf8");\n'
        '\n'
        'const required = ["SuspenseBreadcrumbsFlatList", "SuspenseBreadcrumbsMenu", "SuspenseBreadcrumbsDropdown"];\n'
        'for (const fn of required) {\n'
        '    const re = new RegExp("function\\\\s+" + fn + "\\\\b");\n'
        '    if (!re.test(js)) { console.error("FAIL: function " + fn + " not found"); process.exit(1); }\n'
        '}\n'
        '\n'
        'console.log("PASS");\n'
    )
    assert r.returncode == 0, f"Component validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_overflow_detection_logic():
    """useIsOverflowing hook, ResizeObserver, and conditional ternary rendering implemented."""
    r = _run_node(
        'import { readFileSync } from "fs";\n'
        'const js = readFileSync("' + BREADCRUMBS_JS + '", "utf8");\n'
        '\n'
        'if (!js.includes("useIsOverflowing")) { console.error("FAIL: useIsOverflowing not found"); process.exit(1); }\n'
        'if (!js.includes("ResizeObserver")) { console.error("FAIL: ResizeObserver not found"); process.exit(1); }\n'
        'if (!js.includes("isOverflowing")) { console.error("FAIL: isOverflowing variable not found"); process.exit(1); }\n'
        'if (!js.includes("isOverflowing ?") && !js.includes("isOverflowing?")) {\n'
        '    console.error("FAIL: isOverflowing not in ternary conditional"); process.exit(1);\n'
        '}\n'
        '\n'
        'console.log("PASS");\n'
    )
    assert r.returncode == 0, f"Overflow detection validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_horizontal_scrollbar_removed():
    """overflow-x: auto and .SuspenseBreadcrumbs class removed from SuspenseTab.css."""
    r = _run_node(
        'import { readFileSync } from "fs";\n'
        'const css = readFileSync("' + SUSPENSE_TAB_CSS + '", "utf8");\n'
        '\n'
        '// overflow-x: auto must be gone\n'
        'if (/overflow-x:\\s*auto/.test(css)) {\n'
        '    console.error("FAIL: overflow-x: auto still present in SuspenseTab.css");\n'
        '    process.exit(1);\n'
        '}\n'
        '\n'
        '// .SuspenseBreadcrumbs standalone class must be removed (not matching longer names)\n'
        'if (/\\.SuspenseBreadcrumbs(?![A-Za-z])\\s*\\{/.test(css)) {\n'
        '    console.error("FAIL: .SuspenseBreadcrumbs class still defined in SuspenseTab.css");\n'
        '    process.exit(1);\n'
        '}\n'
        '\n'
        'console.log("PASS");\n'
    )
    assert r.returncode == 0, f"SuspenseTab.css validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_wrapper_div_removed():
    """Wrapper div with styles.SuspenseBreadcrumbs className removed from SuspenseTab.js."""
    r = _run_node(
        'import { readFileSync } from "fs";\n'
        'const js = readFileSync("' + SUSPENSE_TAB_JS + '", "utf8");\n'
        '\n'
        'if (js.includes("className={styles.SuspenseBreadcrumbs}")) {\n'
        '    console.error("FAIL: className={styles.SuspenseBreadcrumbs} still in SuspenseTab.js");\n'
        '    process.exit(1);\n'
        '}\n'
        '\n'
        '// SuspenseBreadcrumbs component should still be referenced\n'
        'if (!js.includes("SuspenseBreadcrumbs")) {\n'
        '    console.error("FAIL: SuspenseBreadcrumbs no longer referenced in SuspenseTab.js");\n'
        '    process.exit(1);\n'
        '}\n'
        '\n'
        'console.log("PASS");\n'
    )
    assert r.returncode == 0, f"SuspenseTab.js validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_reach_ui_menu_import():
    """Menu, MenuList, MenuButton, MenuItem imported from reach-ui/menu-button."""
    r = _run_node(
        'import { readFileSync } from "fs";\n'
        'const js = readFileSync("' + BREADCRUMBS_JS + '", "utf8");\n'
        '\n'
        "const importMatch = js.match(/import\\s*\\{([^}]+)\\}\\s*from\\s*['\"]\\.\\.\\/Components\\/reach-ui\\/menu-button['\"]/);\n"
        'if (!importMatch) {\n'
        '    console.error("FAIL: reach-ui/menu-button import not found");\n'
        '    process.exit(1);\n'
        '}\n'
        'const imports = importMatch[1];\n'
        'for (const name of ["Menu", "MenuList", "MenuButton", "MenuItem"]) {\n'
        '    if (!imports.includes(name)) {\n'
        '        console.error("FAIL: " + name + " not imported from reach-ui/menu-button");\n'
        '        process.exit(1);\n'
        '    }\n'
        '}\n'
        '\n'
        'console.log("PASS");\n'
    )
    assert r.returncode == 0, f"Import validation failed: {r.stderr}"
    assert "PASS" in r.stdout
