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
    # The PR adds deepEqual to: routeMeta, links, preloadLinks, styles, and scripts (last one)

    # Find useStore calls with 3 arguments (store, selector, comparator)
    usestore_3arg_pattern = r'useStore\(\s*\n?\s*router\.stores\.\w+\s*,\s*\n?\s*(?:\([^)]*\)|\w+)\s*,\s*\n?\s*(\w+)\s*\n?\s*\)'
    matches = re.findall(usestore_3arg_pattern, content, re.DOTALL)

    # All useStore calls with 3 args should use deepEqual
    for comparator in matches:
        assert comparator == "deepEqual", \
            f"useStore calls must use deepEqual as comparator, found: {comparator}"

    # Verify at least 5 useStore calls have deepEqual (routeMeta, links, preloadLinks, styles, scripts)
    deepequal_count = content.count("deepEqual,") + content.count("deepEqual,")
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


def test_head_utils_route_meta_deepequal():
    """headContentUtils.tsx routeMeta useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # Find the routeMeta useStore section
    pattern = r'const routeMeta = useStore\(\s*\n?\s*router\.stores\.activeMatchesSnapshot[^}]+}\s*,\s*\n?\s*deepEqual\s*\n?\s*\)'
    assert re.search(pattern, content, re.DOTALL), \
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

    # Find preloadLinks useStore with deepEqual
    pattern = r'const preloadLinks = useStore\([^)]+deepEqual\s*\)'
    assert re.search(pattern, content, re.DOTALL), \
        "preloadLinks useStore call must use deepEqual comparator"


def test_head_utils_styles_deepequal():
    """headContentUtils.tsx styles useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # Find styles useStore with deepEqual
    pattern = r'const styles = useStore\([^)]+deepEqual\s*\)'
    assert re.search(pattern, content, re.DOTALL), \
        "styles useStore call must use deepEqual comparator"


def test_head_utils_scripts_deepequal():
    """headContentUtils.tsx scripts useStore must use deepEqual."""
    content = HEAD_UTILS_FILE.read_text()

    # Find the last useStore (scripts) with deepEqual - it's near the end of useTags function
    pattern = r'const scripts = useStore\([^)]+deepEqual\s*\)'
    assert re.search(pattern, content, re.DOTALL), \
        "scripts useStore call must use deepEqual comparator"


def test_no_unused_deepequal():
    """deepEqual should be used in all relevant useStore calls, not just imported."""
    scripts_content = SCRIPTS_FILE.read_text()
    head_utils_content = HEAD_UTILS_FILE.read_text()

    # Count import occurrences vs usage occurrences
    scripts_import_count = len(re.findall(r'import.*deepEqual.*from', scripts_content))
    head_utils_import_count = len(re.findall(r'import.*deepEqual.*from', head_utils_content))

    scripts_usage_count = scripts_content.count("deepEqual,") + scripts_content.count("deepEqual\n")
    head_utils_usage_count = head_utils_content.count("deepEqual,") + head_utils_content.count("deepEqual\n")

    # Should have imports
    assert scripts_import_count >= 1, "Scripts.tsx must import deepEqual"
    assert head_utils_import_count >= 1, "headContentUtils.tsx must import deepEqual"

    # Should have usages (more than just in imports)
    assert scripts_usage_count > scripts_import_count, \
        "Scripts.tsx must actually use deepEqual in useStore calls"
    assert head_utils_usage_count > head_utils_import_count, \
        "headContentUtils.tsx must actually use deepEqual in useStore calls"
