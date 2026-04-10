"""Test file for pass-to-pass and fail-to-pass tests."""

import subprocess
import sys
import os

# Docker-internal path where the repo lives inside the container
REPO = "/workspace/gradio"


def test_repo_format_check():
    """Repo's code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_vitest_core():
    """Repo's core unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "js/core/src/init.test.ts", "--config", ".config/vitest.config.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Core unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_client_build():
    """Repo's client package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_vitest_i18n():
    """Repo's i18n unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "js/core/src/i18n.test.ts", "--config", ".config/vitest.config.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"i18n unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# Fail-to-pass tests (from PR diff - these should fail on base commit and pass after fix)

def test_tabs_selective_visibility():
    """Tabs node only makes selected tab's children visible, not all tabs (fail_to_pass)."""
    init_file = os.path.join(REPO, "js/core/src/init.svelte.ts")
    with open(init_file, "r") as f:
        content = f.read()

    has_is_target_param = "is_target_node" in content
    has_tabs_selected_check = 'node.type === "tabs"' in content
    has_selected_id_logic = "selectedId" in content or "selected ??" in content

    assert has_is_target_param, "Fix missing: is_target_node parameter not found in make_visible_if_not_rendered"
    assert has_tabs_selected_check, "Fix missing: Tabs type check not found"
    assert has_selected_id_logic, "Fix missing: Selected tab ID logic not found"

    tabs_section_start = content.find('if (node.type === "tabs")')
    if tabs_section_start != -1:
        tabs_section = content[tabs_section_start:tabs_section_start + 800]
        assert 'child.type === "tabitem"' in tabs_section, "Fix missing: Tabs should check child.type === 'tabitem'"
        assert ("child.props.props.id === selectedId" in tabs_section or
                "child.id === selectedId" in tabs_section), "Fix missing: Tabs should only recurse into selected tab's children"


def test_closed_accordion_lazy_load():
    """Closed accordion does not eagerly load its children (fail_to_pass)."""
    init_file = os.path.join(REPO, "js/core/src/init.svelte.ts")
    with open(init_file, "r") as f:
        content = f.read()

    has_accordion_check = 'node.type === "accordion"' in content
    has_open_false_check = "open === false" in content
    has_is_target_check = "is_target_node" in content

    assert has_accordion_check, "Fix missing: Accordion type check not found"
    assert has_open_false_check, "Fix missing: open === false check not found"
    assert has_is_target_check, "Fix missing: is_target_node check not found"

    accordion_section_start = content.find('if (node.type === "accordion")')
    if accordion_section_start != -1:
        accordion_section = content[accordion_section_start:accordion_section_start + 600]
        assert "open === false" in accordion_section and "is_target_node" in accordion_section, "Fix missing: Should skip recursion into closed accordion when not target node"


def test_tab_initial_tabs_fallback():
    """Tabs without selected prop fall back to initial_tabs[0] (fail_to_pass)."""
    init_file = os.path.join(REPO, "js/core/src/init.svelte.ts")
    with open(init_file, "r") as f:
        content = f.read()

    has_fallback_logic = "??" in content and "initial_tabs" in content
    assert has_fallback_logic, "Fix missing: Fallback to initial_tabs[0] not found"

    tabs_section_start = content.find('if (node.type === "tabs")')
    if tabs_section_start != -1:
        tabs_section = content[tabs_section_start:tabs_section_start + 800]
        assert "??" in tabs_section and "initial_tabs" in tabs_section, "Fix missing: Tabs should fall back to initial_tabs[0] when selected is not set"


def test_open_accordion_children_visible():
    """Open accordion children are still made visible (regression - pass_to_pass)."""
    init_file = os.path.join(REPO, "js/core/src/init.svelte.ts")
    with open(init_file, "r") as f:
        content = f.read()

    accordion_section_start = content.find('if (node.type === "accordion")')
    if accordion_section_start != -1:
        accordion_section = content[accordion_section_start:accordion_section_start + 600]
        has_else_block = "else" in accordion_section
        has_children_recursion = "node.children.forEach" in accordion_section
        assert has_else_block, "Fix missing: Should have else block for open accordion handling"
        assert has_children_recursion, "Fix missing: Should recurse into open accordion children"


def test_not_stub():
    """Modified functions have real logic, not stubs (pass_to_pass)."""
    init_file = os.path.join(REPO, "js/core/src/init.svelte.ts")
    with open(init_file, "r") as f:
        content = f.read()

    func_start = content.find("function make_visible_if_not_rendered")
    if func_start != -1:
        brace_start = content.find("{", func_start)
        func_body = content[brace_start:brace_start + 2000]
        assert "pass" not in func_body or "bypass" in func_body, "Function should not be a stub with 'pass' statement"
        has_real_logic = ("if" in func_body and ("forEach" in func_body or "recurse" in func_body.lower()))
        assert has_real_logic, "Function should have real implementation logic"


if __name__ == "__main__":
    test_name = sys.argv[1] if len(sys.argv) > 1 else None
    if test_name:
        globals()[test_name]()
    else:
        test_repo_format_check()
        test_repo_vitest_core()
        test_repo_client_build()
        test_repo_vitest_i18n()
        print("All pass-to-pass tests passed!")
