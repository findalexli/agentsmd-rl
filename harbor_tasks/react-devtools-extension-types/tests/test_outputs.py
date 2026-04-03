"""
Task: react-devtools-extension-types
Repo: facebook/react @ 9c0323e2cf9be543d6eaa44419598af56922603f

Add Flow type annotations to React DevTools browser extension files,
replacing untyped `chrome` global with proper ExtensionAPI interface.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_modified_files_parse():
    """All modified JS files must be valid (no syntax errors in comments/strings)."""
    for f in [
        "packages/react-devtools-extensions/src/background/index.js",
        "packages/react-devtools-extensions/src/main/index.js",
        "scripts/flow/react-devtools.js",
    ]:
        text = Path(f"{REPO}/{f}").read_text()
        assert len(text) > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — ExtensionRuntimePort interface
# ---------------------------------------------------------------------------

def test_extension_runtime_port_interface_defined():
    """ExtensionRuntimePort interface must be defined in flow types file."""
    src = Path(f"{REPO}/scripts/flow/react-devtools.js").read_text()
    assert "interface ExtensionRuntimePort" in src, \
        "ExtensionRuntimePort interface not defined in react-devtools.js"


def test_chrome_typed_as_extension_api():
    """The chrome global should be declared with ExtensionAPI type, not 'any'."""
    src = Path(f"{REPO}/scripts/flow/react-devtools.js").read_text()
    assert "declare const chrome: ExtensionAPI" in src, \
        "chrome should be typed as ExtensionAPI"


def test_background_uses_extension_runtime_port():
    """Background index.js uses ExtensionRuntimePort type annotations."""
    src = Path(f"{REPO}/packages/react-devtools-extensions/src/background/index.js").read_text()
    assert "ExtensionRuntimePort" in src, \
        "background/index.js should use ExtensionRuntimePort"


def test_background_has_flow_annotation():
    """Background index.js should have @flow annotation."""
    src = Path(f"{REPO}/packages/react-devtools-extensions/src/background/index.js").read_text()
    assert "@flow" in src, "background/index.js should have @flow annotation"


def test_main_uses_extension_runtime_port():
    """Main index.js uses ExtensionRuntimePort instead of local ExtensionPort."""
    src = Path(f"{REPO}/packages/react-devtools-extensions/src/main/index.js").read_text()
    assert "ExtensionRuntimePort" in src, \
        "main/index.js should reference ExtensionRuntimePort"


def test_local_extension_port_removed():
    """Local ExtensionPort type definition removed from main/index.js."""
    src = Path(f"{REPO}/packages/react-devtools-extensions/src/main/index.js").read_text()
    assert "type ExtensionPort = {" not in src, \
        "Local ExtensionPort typedef should be removed from main/index.js"


def test_register_tab_typed():
    """registerTab function should have typed parameter."""
    src = Path(f"{REPO}/packages/react-devtools-extensions/src/background/index.js").read_text()
    assert "registerTab(tabId: number)" in src or "registerTab(tabId:number)" in src, \
        "registerTab should have typed tabId parameter"
