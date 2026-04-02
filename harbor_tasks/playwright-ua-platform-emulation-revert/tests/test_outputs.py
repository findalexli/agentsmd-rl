"""
Task: playwright-ua-platform-emulation-revert
Repo: playwright @ 346b39c7895a7df03b50b087d503e9f2997fe2e0
PR:   40016

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"

BROWSER_CONTEXT = Path(REPO) / "packages/playwright-core/src/server/browserContext.ts"
CR_PAGE = Path(REPO) / "packages/playwright-core/src/server/chromium/crPage.ts"
FF_BROWSER = Path(REPO) / "packages/playwright-core/src/server/firefox/ffBrowser.ts"
WK_PAGE = Path(REPO) / "packages/playwright-core/src/server/webkit/wkPage.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO, capture_output=True, timeout=180,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n{r.stderr.decode()[-3000:]}\n{r.stdout.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_firefox_no_platform_override():
    """Firefox browser must not call setPlatformOverride when setting user agent."""
    src = FF_BROWSER.read_text()
    assert "setPlatformOverride" not in src, (
        "ffBrowser.ts still calls Browser.setPlatformOverride — "
        "Firefox should not override navigator.platform based on user agent"
    )


# [pr_diff] fail_to_pass
def test_webkit_no_platform_override():
    """WebKit browser must not override platform in updateUserAgent."""
    src = WK_PAGE.read_text()
    # Extract the updateUserAgent method body
    match = re.search(
        r"async updateUserAgent\(\)[^{]*\{(.*?)\n  \}",
        src, re.DOTALL,
    )
    assert match is not None, "Could not find updateUserAgent method in wkPage.ts"
    method_body = match.group(1)
    assert "overridePlatform" not in method_body, (
        "wkPage.ts updateUserAgent still calls Page.overridePlatform — "
        "WebKit should not override navigator.platform based on user agent"
    )


# [pr_diff] fail_to_pass
def test_chromium_no_platform_in_ua_override():
    """Chromium _updateUserAgent must not pass a 'platform' key to setUserAgentOverride."""
    src = CR_PAGE.read_text()
    # Find the _updateUserAgent method and its send() call
    match = re.search(
        r"async _updateUserAgent\(\)[^{]*\{(.*?)\n  \}",
        src, re.DOTALL,
    )
    assert match is not None, "Could not find _updateUserAgent method in crPage.ts"
    method_body = match.group(1)
    # The method should call send('Emulation.setUserAgentOverride', {...})
    # It must NOT include a 'platform' property in that call
    assert "setUserAgentOverride" in method_body, (
        "_updateUserAgent does not call Emulation.setUserAgentOverride"
    )
    # Check that 'platform:' or 'platform :' is NOT a key in the call arguments
    # (but 'userAgentMetadata' should be present)
    lines_in_send = method_body[method_body.index("setUserAgentOverride"):]
    assert not re.search(r"\bplatform\s*[:,]", lines_in_send), (
        "crPage.ts _updateUserAgent still passes 'platform' to "
        "Emulation.setUserAgentOverride — navigatorPlatform override should be removed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_chromium_still_sends_ua_metadata():
    """Chromium _updateUserAgent must still send userAgentMetadata for client hints."""
    src = CR_PAGE.read_text()
    match = re.search(
        r"async _updateUserAgent\(\)[^{]*\{(.*?)\n  \}",
        src, re.DOTALL,
    )
    assert match is not None, "Could not find _updateUserAgent method in crPage.ts"
    method_body = match.group(1)
    assert "userAgentMetadata" in method_body, (
        "crPage.ts _updateUserAgent no longer sends userAgentMetadata — "
        "Chromium still needs UA client hints metadata"
    )
