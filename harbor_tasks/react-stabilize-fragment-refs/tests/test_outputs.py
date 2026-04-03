"""
Task: react-stabilize-fragment-refs
Repo: facebook/react @ e6f1c33acf81d9865863ab149d24726f43a56db0
PR:   35642

Graduate `unstable_reactFragments` → `reactFragments` in DOM bindings,
React Native Fabric config, and the corresponding test file.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = Path("/workspace/react")
DOM_CONFIG = REPO / "packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"
FABRIC_CONFIG = REPO / "packages/react-native-renderer/src/ReactFiberConfigFabric.js"
TEST_FILE = REPO / "packages/react-dom/src/__tests__/ReactDOMFragmentRefs-test.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — required files exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """All three modified files must be present in the workspace."""
    for f in [DOM_CONFIG, FABRIC_CONFIG, TEST_FILE]:
        assert f.exists(), f"Required file missing: {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — DOM bindings stabilization
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dom_config_type_uses_stable_name():
    """InstanceWithFragmentHandles type in ReactFiberConfigDOM.js uses reactFragments (no unstable_ prefix)."""
    src = DOM_CONFIG.read_text()
    assert "unstable_reactFragments?" not in src, \
        "ReactFiberConfigDOM.js still uses 'unstable_reactFragments?' in type definition"
    assert "reactFragments?" in src, \
        "ReactFiberConfigDOM.js does not have 'reactFragments?' in type definition"


# [pr_diff] fail_to_pass
def test_dom_config_add_uses_stable_name():
    """addFragmentHandleToInstance in DOM config accesses instance.reactFragments (not unstable_)."""
    src = DOM_CONFIG.read_text()
    assert "instance.unstable_reactFragments" not in src, \
        "ReactFiberConfigDOM.js still references 'instance.unstable_reactFragments'"
    assert "instance.reactFragments" in src, \
        "ReactFiberConfigDOM.js does not reference 'instance.reactFragments'"


# [pr_diff] fail_to_pass
def test_dom_config_delete_uses_stable_name():
    """deleteChildFromFragmentInstance in DOM config calls instance.reactFragments.delete."""
    src = DOM_CONFIG.read_text()
    assert "instance.reactFragments.delete" in src, \
        "ReactFiberConfigDOM.js does not contain 'instance.reactFragments.delete'"
    assert "instance.unstable_reactFragments.delete" not in src, \
        "ReactFiberConfigDOM.js still calls 'instance.unstable_reactFragments.delete'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Fabric (React Native) stabilization
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fabric_config_type_uses_stable_name():
    """PublicInstanceWithFragmentHandles type in ReactFiberConfigFabric.js uses reactFragments."""
    src = FABRIC_CONFIG.read_text()
    assert "unstable_reactFragments?" not in src, \
        "ReactFiberConfigFabric.js still uses 'unstable_reactFragments?' in type definition"
    assert "reactFragments?" in src, \
        "ReactFiberConfigFabric.js does not have 'reactFragments?' in type definition"


# [pr_diff] fail_to_pass
def test_fabric_config_functions_use_stable_name():
    """addFragmentHandleToInstance and deleteChildFromFragmentInstance in Fabric use reactFragments."""
    src = FABRIC_CONFIG.read_text()
    assert "instance.unstable_reactFragments" not in src, \
        "ReactFiberConfigFabric.js still references 'instance.unstable_reactFragments'"
    # publicInstance.reactFragments is used in Fabric's delete function
    assert ("instance.reactFragments" in src or "publicInstance.reactFragments" in src), \
        "ReactFiberConfigFabric.js does not reference reactFragments on instance"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — test file stabilization
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_test_file_uses_stable_name():
    """ReactDOMFragmentRefs-test.js assertions reference childA.reactFragments (not unstable_)."""
    src = TEST_FILE.read_text()
    assert "unstable_reactFragments" not in src, \
        "ReactDOMFragmentRefs-test.js still references 'unstable_reactFragments'"
    assert "reactFragments" in src, \
        "ReactDOMFragmentRefs-test.js does not reference 'reactFragments'"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — completeness / anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_unstable_refs_in_modified_files():
    """No occurrences of unstable_reactFragments remain in any of the three modified files."""
    offenders = []
    for path in [DOM_CONFIG, FABRIC_CONFIG, TEST_FILE]:
        src = path.read_text()
        count = src.count("unstable_reactFragments")
        if count > 0:
            offenders.append(f"{path.name}: {count} occurrence(s)")
    assert not offenders, \
        "Remaining 'unstable_reactFragments' references:\n" + "\n".join(offenders)


# [static] pass_to_pass
def test_coverage_nontrivial():
    """Both DOM and Fabric configs have multiple reactFragments references (rename is complete, not partial)."""
    dom_src = DOM_CONFIG.read_text()
    fabric_src = FABRIC_CONFIG.read_text()
    dom_count = dom_src.count("reactFragments")
    fabric_count = fabric_src.count("reactFragments")
    assert dom_count >= 4, \
        f"ReactFiberConfigDOM.js has only {dom_count} 'reactFragments' reference(s); expected >= 4"
    assert fabric_count >= 4, \
        f"ReactFiberConfigFabric.js has only {fabric_count} 'reactFragments' reference(s); expected >= 4"
