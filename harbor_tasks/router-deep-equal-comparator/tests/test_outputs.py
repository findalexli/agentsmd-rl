"""
Tests for router deepEqual comparator fix.

This test suite verifies that the useStore hooks in Scripts.tsx and
headContentUtils.tsx use deepEqual as a comparator to prevent unnecessary re-renders.
"""

import subprocess
import sys
import re
from pathlib import Path

REPO_ROOT = Path("/workspace/router")
SCRIPTS_FILE = REPO_ROOT / "packages" / "react-router" / "src" / "Scripts.tsx"
HEAD_UTILS_FILE = REPO_ROOT / "packages" / "react-router" / "src" / "headContentUtils.tsx"


def test_scripts_imports_deep_equal():
    """Scripts.tsx must import deepEqual from @tanstack/router-core."""
    content = SCRIPTS_FILE.read_text()

    # Check for deepEqual import
    import_pattern = r'import\s+{[^}]*deepEqual[^}]*}\s+from\s+[\'"]@tanstack/router-core[\'"]'
    assert re.search(import_pattern, content), \
        "Scripts.tsx must import deepEqual from @tanstack/router-core"


def test_scripts_use_store_has_deepequal_comparator():
    """Scripts.tsx useStore calls must have deepEqual as the comparator."""
    content = SCRIPTS_FILE.read_text()

    # Find all useStore calls and verify they have deepEqual as comparator
    usestore_pattern = r'useStore\(\s*\n?\s*router\.stores\.\w+\s*,\s*\n?\s*\w+\s*,\s*\n?\s*(\w+)\s*\n?\s*\)'
    matches = re.findall(usestore_pattern, content)

    # All useStore calls should have deepEqual as the third argument
    for comparator in matches:
        assert comparator == "deepEqual", \
            f"useStore calls must use deepEqual as comparator, found: {comparator}"


def test_head_utils_imports_deep_equal():
    """headContentUtils.tsx must import deepEqual from @tanstack/router-core."""
    content = HEAD_UTILS_FILE.read_text()

    # Check for deepEqual import
    import_pattern = r'import\s+{[^}]*deepEqual[^}]*}\s+from\s+[\'"]@tanstack/router-core[\'"]'
    assert re.search(import_pattern, content), \
        "headContentUtils.tsx must import deepEqual from @tanstack/router-core"


def test_head_utils_use_store_comparators():
    """headContentUtils.tsx useStore calls must use deepEqual as comparator."""
    content = HEAD_UTILS_FILE.read_text()

    # Count useStore calls that should have deepEqual
    # The PR adds deepEqual to: routeMeta, links, preloadLinks, styles, and headScripts

    # Find useStore calls with 3 arguments (store, selector, comparator)
    usestore_3arg_pattern = r'useStore\(\s*\n?\s*router\.stores\.\w+\s*,\s*\n?\s*(?:\([^)]*\)|\w+)\s*,\s*\n?\s*(\w+)\s*\n?\s*\)'
    matches = re.findall(usestore_3arg_pattern, content, re.DOTALL)

    # All useStore calls with 3 args should use deepEqual
    for comparator in matches:
        assert comparator == "deepEqual", \
            f"useStore calls must use deepEqual as comparator, found: {comparator}"

    # Verify at least 5 useStore calls have deepEqual (routeMeta, links, preloadLinks, styles, headScripts)
    deepequal_count = content.count("deepEqual,")
    assert deepequal_count >= 5, \
        f"Expected at least 5 useStore calls with deepEqual, found evidence of {deepequal_count}"


def test_build_succeeds():
    """The package must build successfully after changes."""
    result = subprocess.run(
        ["pnpm", "build"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_unit_tests_pass():
    """Unit tests for react-router package must pass."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"Unit tests failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_scripts_deepequal_in_get_asset_scripts():
    """Scripts.tsx getAssetScripts useStore call must have deepEqual."""
    content = SCRIPTS_FILE.read_text()

    # Check for the specific pattern: getAssetScripts useStore with deepEqual
    pattern = r'getAssetScripts\s*,\s*\n?\s*deepEqual'
    assert re.search(pattern, content), \
        "getAssetScripts useStore call must have deepEqual comparator"


def test_scripts_deepequal_in_get_scripts():
    """Scripts.tsx getScripts useStore call must have deepEqual."""
    content = SCRIPTS_FILE.read_text()

    # Check for the specific pattern: getScripts useStore with deepEqual
    pattern = r'getScripts\s*,\s*\n?\s*deepEqual'
    assert re.search(pattern, content), \
        "getScripts useStore call must have deepEqual comparator"


def _check_variable_has_deepequal(content, var_name):
    """Helper to check that a variable's useStore call has deepEqual."""
    # Find the position of the variable declaration
    var_pos = content.find(f"const {var_name}")
    if var_pos == -1:
        raise AssertionError(f"Variable {var_name} not found")

    # Look for useStore after this variable declaration
    usestore_pos = content.find("useStore", var_pos)
    if usestore_pos == -1:
        raise AssertionError(f"useStore not found after {var_name} declaration")

    # Find the end of this useStore call (closing paren followed by )
    # Look for the pattern where deepEqual appears in the 3rd argument position
    section = content[var_pos:usestore_pos + 2000]

    # Check that deepEqual appears after the useStore call starts
    assert "deepEqual" in section, \
        f"{var_name} useStore call must have deepEqual comparator"


def test_head_utils_route_meta_deepequal():
    """headContentUtils.tsx routeMeta useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # Find the useTags function
    usetags_pos = content.find("export const useTags")
    assert usetags_pos != -1, "useTags function not found"

    # Find routeMeta useStore within useTags (not the helper function)
    route_meta_pos = content.find("const routeMeta = useStore", usetags_pos)
    assert route_meta_pos != -1, "routeMeta useStore not found in useTags"

    # Check that deepEqual appears in this useStore call
    # Find the closing paren of this useStore call
    section = content[route_meta_pos:route_meta_pos + 400]
    assert "deepEqual" in section, \
        "routeMeta useStore call must use deepEqual comparator"


def test_head_utils_links_deepequal():
    """headContentUtils.tsx links useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # The links useStore ends with deepEqual before the closing paren
    # Check that the links useStore has deepEqual
    links_section = content[content.find("const links = useStore"):content.find("const links = useStore") + 2000]
    assert "deepEqual," in links_section or "deepEqual\n" in links_section, \
        "links useStore call must use deepEqual comparator"


def test_head_utils_preload_links_deepequal():
    """headContentUtils.tsx preloadLinks useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # Find preloadLinks useStore after useTags function
    usetags_pos = content.find("export const useTags")
    preload_pos = content.find("const preloadLinks = useStore", usetags_pos)
    assert preload_pos != -1, "preloadLinks useStore not found in useTags"

    # Check deepEqual in this section - need larger section for preloadLinks
    section = content[preload_pos:preload_pos + 1200]
    assert "deepEqual" in section, \
        "preloadLinks useStore call must use deepEqual comparator"


def test_head_utils_styles_deepequal():
    """headContentUtils.tsx styles useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # Find styles useStore after useTags function
    usetags_pos = content.find("export const useTags")
    styles_pos = content.find("const styles = useStore", usetags_pos)
    assert styles_pos != -1, "styles useStore not found in useTags"

    # Check deepEqual in this section
    section = content[styles_pos:styles_pos + 500]
    assert "deepEqual" in section, \
        "styles useStore call must use deepEqual comparator"


def test_head_utils_scripts_deepequal():
    """headContentUtils.tsx headScripts useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # Find headScripts useStore after useTags function (variable is headScripts, not scripts)
    usetags_pos = content.find("export const useTags")
    scripts_pos = content.find("const headScripts", usetags_pos)
    assert scripts_pos != -1, "headScripts useStore not found in useTags"

    # Check deepEqual in this section
    section = content[scripts_pos:scripts_pos + 500]
    assert "deepEqual" in section, \
        "headScripts useStore call must use deepEqual comparator"


def test_no_unused_deepequal():
    """deepEqual should be used in all relevant useStore calls, not just imported."""
    scripts_content = SCRIPTS_FILE.read_text()
    head_utils_content = HEAD_UTILS_FILE.read_text()

    # Count import occurrences vs usage occurrences
    scripts_import_count = len(re.findall(r'import.*deepEqual.*from', scripts_content))
    head_utils_import_count = len(re.findall(r'import.*deepEqual.*from', head_utils_content))

    scripts_usage_count = scripts_content.count("deepEqual,")
    head_utils_usage_count = head_utils_content.count("deepEqual,")

    # Should have imports
    assert scripts_import_count >= 1, "Scripts.tsx must import deepEqual"
    assert head_utils_import_count >= 1, "headContentUtils.tsx must import deepEqual"

    # Should have usages (more than just in imports)
    assert scripts_usage_count > scripts_import_count, \
        "Scripts.tsx must actually use deepEqual in useStore calls"
    assert head_utils_usage_count > head_utils_import_count, \
        "headContentUtils.tsx must actually use deepEqual in useStore calls"


def test_repo_types_check():
    """Repo's TypeScript type check for react-router passes (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"Type check failed:\nstdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-500:]}"


def test_repo_scripts_unit_tests():
    """Repo's unit tests for Scripts.tsx pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "tests/Scripts.test.tsx"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"Scripts unit tests failed:\nstdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-500:]}"
