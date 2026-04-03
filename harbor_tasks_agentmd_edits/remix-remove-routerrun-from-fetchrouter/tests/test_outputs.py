"""
Task: remix-remove-routerrun-from-fetchrouter
Repo: remix-run/remix @ 783fa46240191001e0ee2084297b5c81d78b3545
PR:   11071

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"

ROUTER_TS = f"{REPO}/packages/fetch-router/src/lib/router.ts"
ROUTER_TEST_TS = f"{REPO}/packages/fetch-router/src/lib/router.test.ts"
FETCH_ROUTER_README = f"{REPO}/packages/fetch-router/README.md"
BOOKSTORE_README = f"{REPO}/demos/bookstore/README.md"
CHANGE_FILE = f"{REPO}/packages/fetch-router/.changes/minor.router-run.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must be non-empty with balanced braces."""
    for path in [ROUTER_TS, ROUTER_TEST_TS]:
        src = Path(path).read_text()
        assert len(src.strip()) > 0, f"{path} is empty"
        assert src.count("{") == src.count("}"), f"{path} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — router.run removed from code
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_router_run_method_removed_from_interface():
    """The Router interface must NOT declare a run() method."""
    src = Path(ROUTER_TS).read_text()
    # Match "run<" or "run(" in the interface portion (before createRouter)
    interface_match = re.search(
        r"export\s+interface\s+Router\s*\{([\s\S]*?)\n\}", src
    )
    assert interface_match, "Router interface not found"
    interface_body = interface_match.group(1)
    assert "run" not in interface_body.split("fetch")[1].split("route")[0] if "route" in interface_body else True, \
        "Router interface still declares run()"
    # More direct: no "run<result>" or "run(" signatures
    assert not re.search(r"\brun\s*[<(]", interface_body), \
        "Router interface still has run() method signature"


# [pr_diff] fail_to_pass
def test_router_run_implementation_removed():
    """The createRouter function must NOT contain a run() implementation."""
    src = Path(ROUTER_TS).read_text()
    # Look for the run implementation in the returned object
    assert "async run" not in src, \
        "router.ts still contains async run implementation"
    assert "router.run()" not in src, \
        "router.ts still references router.run()"


# [pr_diff] fail_to_pass
def test_router_run_tests_removed():
    """The test file must NOT contain a describe('router.run()') block."""
    src = Path(ROUTER_TEST_TS).read_text()
    assert "router.run" not in src.lower(), \
        "router.test.ts still contains router.run tests"


# [pr_diff] fail_to_pass
def test_change_file_deleted():
    """The unreleased change file for router.run must be removed."""
    assert not Path(CHANGE_FILE).exists(), \
        "packages/fetch-router/.changes/minor.router-run.md should be deleted"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — router.fetch still works
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_router_fetch_still_in_interface():
    """The Router interface must still declare fetch()."""
    src = Path(ROUTER_TS).read_text()
    assert re.search(r"\bfetch\s*\(", src), \
        "Router interface must still have fetch() method"


# [static] pass_to_pass
def test_router_map_still_in_interface():
    """The Router interface must still declare map()."""
    src = Path(ROUTER_TS).read_text()
    assert re.search(r"\bmap\s*[<(]", src), \
        "Router interface must still have map() method"


# [static] pass_to_pass
def test_createStorageKey_import_removed_from_tests():
    """The test file should not import createStorageKey (only used by run tests)."""
    src = Path(ROUTER_TEST_TS).read_text()
    assert "createStorageKey" not in src, \
        "router.test.ts still imports createStorageKey which was only used by run() tests"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — README still has other content
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_fetch_router_readme_still_has_content():
    """fetch-router README must still document router.fetch and other features."""
    content = Path(FETCH_ROUTER_README).read_text()
    assert "router.fetch" in content, "README must still document router.fetch"
    assert "## Features" in content, "README must still have Features section"
    assert "## Usage" in content, "README must still have Usage section"
    assert "### Testing" in content, "README must still have Testing section"
