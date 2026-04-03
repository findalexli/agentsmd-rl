"""
Task: react-devtools-prerendering-pageshow
Repo: facebook/react @ 4b568a8dbb4cb84b0067f353b9c0bec1ddb61d8e
PR:   facebook/react#35958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
PROXY = Path(REPO) / "packages/react-devtools-extensions/src/contentScripts/proxy.js"
FLOW_DOM = Path(REPO) / "flow-typed/environments/dom.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_proxy_js_exists_and_nontrivial():
    """proxy.js must exist and contain core extension functions."""
    # AST-only because: proxy.js uses Flow type annotations (@flow), node --check rejects Flow syntax
    assert PROXY.exists(), f"proxy.js not found at {PROXY}"
    content = PROXY.read_text()
    assert "function injectProxy" in content, "injectProxy function missing from proxy.js"
    assert "connectPort" in content, "connectPort function missing from proxy.js"
    assert len(content) > 500, "proxy.js is suspiciously small — likely truncated or stubbed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_handle_pageshow_function_defined():
    """A handlePageShow function must be defined to guard against prerendering."""
    # AST-only because: browser extension content script requires window/document/chrome APIs
    content = PROXY.read_text()
    assert re.search(r'\bfunction\s+handlePageShow\s*\(', content), (
        "handlePageShow function not found in proxy.js — "
        "the fix requires a dedicated handler that checks prerendering state"
    )


# [pr_diff] fail_to_pass
def test_prerendering_checked_before_injection():
    """handlePageShow must check document.prerendering before calling injectProxy."""
    # AST-only because: browser extension content script requires window/document/chrome APIs
    content = PROXY.read_text()
    assert re.search(r'if\s*\(\s*document\.prerendering\s*\)', content), (
        "No 'if (document.prerendering)' guard found in proxy.js — "
        "the fix must check the prerendering state before injecting the proxy"
    )


# [pr_diff] fail_to_pass
def test_prerenderingchange_listener_defers_injection():
    """When prerendering, a prerenderingchange listener must defer proxy injection."""
    # AST-only because: browser extension content script requires window/document/chrome APIs
    content = PROXY.read_text()
    assert re.search(
        r"addEventListener\s*\(\s*['\"]prerenderingchange['\"]", content
    ), (
        "No addEventListener('prerenderingchange', ...) found — "
        "the fix must listen for prerenderingchange to defer injection until prerendering ends"
    )
    # The listener should use {once: true} to avoid duplicate injections
    # Find the prerenderingchange addEventListener call and check for once: true nearby
    match = re.search(
        r"addEventListener\s*\(\s*['\"]prerenderingchange['\"][^)]*\{[^}]*once\s*:\s*true[^}]*\}",
        content,
    )
    assert match, (
        "prerenderingchange listener should use {once: true} to prevent duplicate injection"
    )


# [pr_diff] fail_to_pass
def test_pageshow_listener_uses_handle_pageshow():
    """The pageshow event listener must call handlePageShow, not injectProxy directly."""
    # AST-only because: browser extension content script requires window/document/chrome APIs
    content = PROXY.read_text()
    # New: pageshow → handlePageShow
    assert re.search(
        r"""addEventListener\s*\(\s*['"]pageshow['"]\s*,\s*handlePageShow\s*\)""",
        content,
    ), "pageshow listener not updated to use handlePageShow"
    # Old direct call must be gone
    assert not re.search(
        r"""addEventListener\s*\(\s*['"]pageshow['"]\s*,\s*injectProxy\s*\)""",
        content,
    ), "pageshow listener still calls injectProxy directly — must use handlePageShow"


# [pr_diff] fail_to_pass
def test_inject_proxy_no_target_parameter():
    """injectProxy must not destructure {target} — signature updated to no parameters."""
    # AST-only because: browser extension content script requires window/document/chrome APIs
    content = PROXY.read_text()
    assert not re.search(r'function\s+injectProxy\s*\(\s*\{', content), (
        "injectProxy still uses old {target} parameter destructuring — "
        "the fix removes this unused parameter"
    )
    assert re.search(r'function\s+injectProxy\s*\(\s*\)', content), (
        "injectProxy() with empty parameter list not found — "
        "the fix changes the signature to take no arguments"
    )


# [pr_diff] fail_to_pass
def test_flow_prerendering_type_declared():
    """flow-typed/environments/dom.js must declare prerendering: boolean on Document."""
    # AST-only because: Flow type definition file, not executable JavaScript
    assert FLOW_DOM.exists(), f"Flow DOM type definitions not found at {FLOW_DOM}"
    content = FLOW_DOM.read_text()
    assert re.search(r'\bprerendering\s*:\s*boolean\b', content), (
        "prerendering: boolean not found in flow-typed/environments/dom.js — "
        "the fix adds the Flow type for document.prerendering"
    )
