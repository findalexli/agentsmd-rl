"""
Task: react-devtools-prerendering-pageshow
Repo: facebook/react @ 4b568a8dbb4cb84b0067f353b9c0bec1ddb61d8e
PR:   facebook/react#35958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
PROXY = Path(REPO) / "packages/react-devtools-extensions/src/contentScripts/proxy.js"
FLOW_DOM = Path(REPO) / "flow-typed/environments/dom.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_proxy_js_syntax_valid():
    """proxy.js must be valid JavaScript (node --check)."""
    assert PROXY.exists(), f"proxy.js not found at {PROXY}"
    r = subprocess.run(
        ["node", "--check", str(PROXY)],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Syntax error in proxy.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_handle_pageshow_function_defined():
    """A handlePageShow function must be defined to guard against prerendering."""
    content = PROXY.read_text()
    assert re.search(r'\bfunction\s+handlePageShow\s*\(', content), (
        "handlePageShow function not found in proxy.js — "
        "the fix requires extracting prerendering logic into a dedicated handler"
    )


# [pr_diff] fail_to_pass
def test_prerendering_checked_before_injection():
    """handlePageShow must guard with if (document.prerendering) before injecting."""
    content = PROXY.read_text()
    # The fix requires a conditional check, not just referencing the property
    assert re.search(r'if\s*\(\s*document\.prerendering\s*\)', content), (
        "No 'if (document.prerendering)' guard found in proxy.js — "
        "the fix must check document.prerendering before calling injectProxy"
    )


# [pr_diff] fail_to_pass
def test_prerenderingchange_listener_registered():
    """When prerendering, a prerenderingchange listener must defer injection."""
    content = PROXY.read_text()
    assert "prerenderingchange" in content, (
        "prerenderingchange not referenced in proxy.js"
    )
    # Must be used as an addEventListener event name (not just in a comment)
    assert re.search(r"addEventListener\s*\(\s*['\"]prerenderingchange['\"]", content), (
        "prerenderingchange not used as an addEventListener event — "
        "the fix must register a listener to defer injection until prerendering ends"
    )


# [pr_diff] fail_to_pass
def test_pageshow_listener_uses_handle_pageshow():
    """The pageshow event listener must call handlePageShow, not injectProxy directly."""
    content = PROXY.read_text()
    # New handler is handlePageShow
    assert (
        "addEventListener('pageshow', handlePageShow)" in content
        or 'addEventListener("pageshow", handlePageShow)' in content
    ), "pageshow listener not updated to use handlePageShow"
    # Old direct call to injectProxy must be gone
    assert (
        "addEventListener('pageshow', injectProxy)" not in content
        and 'addEventListener("pageshow", injectProxy)' not in content
    ), "pageshow listener still calls injectProxy directly — must use handlePageShow"


# [pr_diff] fail_to_pass
def test_inject_proxy_signature_updated():
    """injectProxy must not destructure {target} from its argument."""
    content = PROXY.read_text()
    # Old signature: function injectProxy({target}: {target: any})
    assert not re.search(r'function\s+injectProxy\s*\(\s*\{', content), (
        "injectProxy still uses old {target} parameter destructuring — "
        "the fix removes this unused parameter"
    )
    # New signature: function injectProxy()
    assert re.search(r'function\s+injectProxy\s*\(\s*\)', content), (
        "injectProxy() with no parameters not found — "
        "the fix changes the signature to take no arguments"
    )


# [pr_diff] fail_to_pass
def test_flow_prerendering_type_defined():
    """flow-typed/environments/dom.js must declare prerendering on Document."""
    assert FLOW_DOM.exists(), f"dom.js not found at {FLOW_DOM}"
    content = FLOW_DOM.read_text()
    # The fix adds: prerendering: boolean;
    assert re.search(r'\bprerendering\s*:', content), (
        "prerendering property not declared in flow-typed/environments/dom.js — "
        "the fix adds a Flow type definition for document.prerendering"
    )
