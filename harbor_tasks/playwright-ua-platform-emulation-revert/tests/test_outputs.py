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
# Gates (pass_to_pass) — lint / compilation checks
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:57 @ 346b39c7
def test_flint_passes():
    """npm run flint must pass (includes tsc + lint + DEPS.list import boundary checks)."""
    r = subprocess.run(
        ["npm", "run", "flint"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"flint failed:\n{r.stderr.decode()[-3000:]}\n{r.stdout.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# Source inspection because: TypeScript code requiring browser engine binaries
# to execute; browsers not installed in verification container.
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_shared_function_not_exported():
    """calculateUserAgentEmulation must no longer be exported from browserContext.ts."""
    src = BROWSER_CONTEXT.read_text()
    # The function should be completely removed or at least not exported
    assert "export function calculateUserAgentEmulation" not in src, (
        "browserContext.ts still exports calculateUserAgentEmulation — "
        "the shared platform-syncing function should be removed"
    )


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
    assert "setUserAgentOverride" in method_body, (
        "_updateUserAgent does not call Emulation.setUserAgentOverride"
    )
    # Must NOT include a 'platform' property in the call arguments
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


# [static] pass_to_pass
def test_chromium_metadata_has_platform_parsing():
    """Chromium must still parse UA string to derive platform metadata for client hints.

    The UA metadata calculation (for sec-ch-ua-* headers) should exist somewhere in
    crPage.ts — either as a local function or inline. It must handle multiple platforms.
    """
    src = CR_PAGE.read_text()
    # The metadata calculation must parse at least Android, iOS/iPhone, macOS, Windows
    # from the user agent string to populate userAgentMetadata.platform
    platforms_found = sum(1 for p in ["Android", "iPhone", "macOS", "Windows", "Linux"]
                         if p in src)
    assert platforms_found >= 4, (
        f"crPage.ts only references {platforms_found}/5 platform strings — "
        "UA metadata calculation must parse multiple platforms from the user agent"
    )


# [pr_diff] fail_to_pass
def test_firefox_no_import_calculate_emulation():
    """Firefox must not import calculateUserAgentEmulation from browserContext."""
    src = FF_BROWSER.read_text()
    assert "calculateUserAgentEmulation" not in src, (
        "ffBrowser.ts still references calculateUserAgentEmulation — "
        "the import and all usages should be removed"
    )


# [pr_diff] fail_to_pass
def test_webkit_no_import_calculate_emulation():
    """WebKit must not import calculateUserAgentEmulation from browserContext."""
    src = WK_PAGE.read_text()
    assert "calculateUserAgentEmulation" not in src, (
        "wkPage.ts still references calculateUserAgentEmulation — "
        "the import and all usages should be removed"
    )
