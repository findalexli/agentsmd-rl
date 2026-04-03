"""
Task: playwright-chorewebkit-update-safari-useragent-version
Repo: microsoft/playwright @ 3aba395f2d151d2345de3182b8b3e9564507c9e5
PR:   39974

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_wkbrowser_version_constant():
    """BROWSER_VERSION in wkBrowser.ts must be '26.4'."""
    src = Path(f"{REPO}/packages/playwright-core/src/server/webkit/wkBrowser.ts").read_text()
    match = re.search(r"const BROWSER_VERSION\s*=\s*'([^']+)'", src)
    assert match is not None, "Could not find BROWSER_VERSION constant in wkBrowser.ts"
    assert match.group(1) == "26.4", (
        f"BROWSER_VERSION should be '26.4', got '{match.group(1)}'"
    )


# [pr_diff] fail_to_pass
def test_browsers_json_webkit_version():
    """browsers.json must declare WebKit browserVersion as '26.4'."""
    data = json.loads(
        Path(f"{REPO}/packages/playwright-core/browsers.json").read_text()
    )
    webkit_entries = [
        b for b in data.get("browsers", []) if b.get("name") == "webkit"
    ]
    assert len(webkit_entries) == 1, "Expected exactly one 'webkit' entry in browsers.json"
    version = webkit_entries[0].get("browserVersion", "")
    assert version == "26.4", (
        f"WebKit browserVersion in browsers.json should be '26.4', got '{version}'"
    )


# [pr_diff] fail_to_pass
def test_device_descriptors_version():
    """Device descriptor user-agent strings must contain Version/26.4."""
    data = json.loads(
        Path(
            f"{REPO}/packages/playwright-core/src/server/deviceDescriptorsSource.json"
        ).read_text()
    )
    # Check a representative sample of WebKit devices
    webkit_devices = {
        name: desc
        for name, desc in data.items()
        if desc.get("defaultBrowserType") == "webkit"
    }
    assert len(webkit_devices) > 10, "Expected many WebKit device descriptors"

    stale = []
    for name, desc in webkit_devices.items():
        ua = desc.get("userAgent", "")
        if "Version/26.0" in ua:
            stale.append(name)
        elif "Version/26.4" not in ua:
            # Devices that don't have any Version/ string are fine (non-Safari UA)
            if "Version/" in ua:
                stale.append(name)

    assert len(stale) == 0, (
        f"{len(stale)} WebKit device(s) still have old version: {stale[:5]}"
    )


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass
def test_release_notes_webkit_version():
    """Release notes must list WebKit 26.4."""
    for lang in ("js", "python", "java", "csharp"):
        notes = Path(f"{REPO}/docs/src/release-notes-{lang}.md").read_text()
        assert "WebKit 26.4" in notes, (
            f"release-notes-{lang}.md should mention 'WebKit 26.4'"
        )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — skill doc creation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax gate
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_wkbrowser_ts_valid_syntax():
    """wkBrowser.ts must be valid TypeScript (no unterminated strings)."""
    src = Path(f"{REPO}/packages/playwright-core/src/server/webkit/wkBrowser.ts").read_text()
    # Basic checks: file is non-empty and BROWSER_VERSION line is well-formed
    assert len(src) > 100, "wkBrowser.ts seems truncated"
    assert re.search(r"const BROWSER_VERSION\s*=\s*'[^']+'\s*;", src), (
        "BROWSER_VERSION declaration is malformed"
    )


# [static] pass_to_pass
def test_browsers_json_valid():
    """browsers.json must be valid JSON."""
    data = json.loads(
        Path(f"{REPO}/packages/playwright-core/browsers.json").read_text()
    )
    assert "browsers" in data, "browsers.json must have a 'browsers' key"


# [static] pass_to_pass
def test_device_descriptors_valid_json():
    """deviceDescriptorsSource.json must be valid JSON."""
    data = json.loads(
        Path(
            f"{REPO}/packages/playwright-core/src/server/deviceDescriptorsSource.json"
        ).read_text()
    )
    assert len(data) > 50, "deviceDescriptorsSource.json seems truncated"
