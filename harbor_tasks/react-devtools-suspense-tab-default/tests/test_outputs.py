"""
Task: react-devtools-suspense-tab-default
Repo: facebook/react @ 8374c2abf13fa803233025192b8d7e87de70b087
PR:   35768

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = Path("/workspace/react")

INDEX_JS = REPO / "packages/react-devtools-extensions/src/main/index.js"
AGENT_JS = REPO / "packages/react-devtools-shared/src/backend/agent.js"
BRIDGE_JS = REPO / "packages/react-devtools-shared/src/bridge.js"
STORE_JS = REPO / "packages/react-devtools-shared/src/devtools/store.js"
DEVTOOLS_JS = REPO / "packages/react-devtools-shared/src/devtools/views/DevTools.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — required files must exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_required_files_exist():
    """All five modified files must exist in the repo."""
    for f in [INDEX_JS, AGENT_JS, BRIDGE_JS, STORE_JS, DEVTOOLS_JS]:
        assert f.exists(), f"{f} not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes from the PR
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_suspense_panel_created_eagerly():
    """createSuspensePanel() is called directly inside mountReactDevTools, not via event listener."""
    # AST-only because: JavaScript/Flow source cannot be executed in Python test environment
    src = INDEX_JS.read_text()
    lines = src.splitlines()

    mount_idx = next(
        (i for i, l in enumerate(lines) if "function mountReactDevTools" in l), None
    )
    assert mount_idx is not None, "mountReactDevTools function not found in index.js"

    # The function body should directly call createSuspensePanel() (within ~30 lines)
    fn_body = "\n".join(lines[mount_idx : mount_idx + 30])
    assert "createSuspensePanel()" in fn_body, (
        "createSuspensePanel() should be called directly inside mountReactDevTools, "
        "not conditionally via event listener"
    )


# [pr_diff] fail_to_pass
def test_enable_suspense_tab_listener_removed_from_index():
    """The dynamic enableSuspenseTab event listener is removed from index.js."""
    # AST-only because: JavaScript/Flow source cannot be executed in Python test environment
    src = INDEX_JS.read_text()
    assert "store.addListener('enableSuspenseTab'" not in src, (
        "enableSuspenseTab event listener should be removed from index.js"
    )
    assert 'store.addListener("enableSuspenseTab"' not in src, (
        "enableSuspenseTab event listener should be removed from index.js"
    )


# [pr_diff] fail_to_pass
def test_static_tabs_array_in_devtools():
    """DevTools.js uses a static tabs array with suspenseTab instead of conditional logic."""
    # AST-only because: JavaScript/Flow source cannot be executed in Python test environment
    src = DEVTOOLS_JS.read_text()

    assert "useIsSuspenseTabEnabled" not in src, (
        "useIsSuspenseTabEnabled hook should be removed from DevTools.js"
    )
    assert re.search(
        r"const tabs\s*=\s*\[componentsTab,\s*profilerTab,\s*suspenseTab\]", src
    ), "Static tabs array including suspenseTab not found in DevTools.js"


# [pr_diff] fail_to_pass
def test_suspense_tab_rendered_unconditionally():
    """Suspense tab JSX is rendered unconditionally — no {enableSuspenseTab && ...} guard."""
    # AST-only because: JavaScript/Flow source cannot be executed in Python test environment
    src = DEVTOOLS_JS.read_text()
    assert "enableSuspenseTab &&" not in src, (
        "Suspense tab content should be rendered unconditionally; "
        "remove the enableSuspenseTab && conditional wrapper"
    )


# [pr_diff] fail_to_pass
def test_enable_suspense_tab_removed_from_bridge():
    """enableSuspenseTab event type is removed from the BackendEvents type in bridge.js."""
    # AST-only because: JavaScript/Flow source cannot be executed in Python test environment
    src = BRIDGE_JS.read_text()
    assert "enableSuspenseTab:" not in src, (
        "enableSuspenseTab event type should be removed from bridge.js BackendEvents"
    )


# [pr_diff] fail_to_pass
def test_version_check_removed_from_agent():
    """Version-based Suspense tab feature detection is removed from agent.js."""
    # AST-only because: JavaScript/Flow source cannot be executed in Python test environment
    src = AGENT_JS.read_text()
    assert "enableSuspenseTab" not in src, (
        "enableSuspenseTab references should be fully removed from agent.js"
    )


# [pr_diff] fail_to_pass
def test_enable_suspense_tab_removed_from_store():
    """enableSuspenseTab listener, getter, and field are all removed from store.js."""
    # AST-only because: JavaScript/Flow source cannot be executed in Python test environment
    src = STORE_JS.read_text()
    assert "enableSuspenseTab" not in src, (
        "enableSuspenseTab references should be fully removed from store.js"
    )
    assert "_supportsSuspenseTab" not in src, (
        "_supportsSuspenseTab field should be removed from store.js"
    )
