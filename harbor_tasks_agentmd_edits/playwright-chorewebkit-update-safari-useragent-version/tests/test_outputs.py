"""
Task: playwright-chorewebkit-update-safari-useragent-version
Repo: microsoft/playwright @ 3aba395f2d151d2345de3182b8b3e9564507c9e5
PR:   39974

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_version_consistency_across_sources():
    """BROWSER_VERSION in wkBrowser.ts, browsers.json, and device descriptors must all be '26.4'."""
    r = subprocess.run(
        ["python3", "-c", """
import json, re, sys
from pathlib import Path

REPO = "/workspace/playwright"

# 1. Extract BROWSER_VERSION from wkBrowser.ts
ts_src = Path(f"{REPO}/packages/playwright-core/src/server/webkit/wkBrowser.ts").read_text()
m = re.search(r"const BROWSER_VERSION\\s*=\\s*'([^']+)'", ts_src)
assert m, "BROWSER_VERSION not found in wkBrowser.ts"
ts_version = m.group(1)

# 2. Extract browserVersion from browsers.json
bj = json.loads(Path(f"{REPO}/packages/playwright-core/browsers.json").read_text())
webkit = [b for b in bj["browsers"] if b["name"] == "webkit"]
assert len(webkit) == 1, f"Expected 1 webkit entry, got {len(webkit)}"
json_version = webkit[0]["browserVersion"]

# 3. Check all WebKit device descriptors use the same version
dd = json.loads(Path(f"{REPO}/packages/playwright-core/src/server/deviceDescriptorsSource.json").read_text())
webkit_devices = {n: d for n, d in dd.items() if d.get("defaultBrowserType") == "webkit"}
assert len(webkit_devices) > 10, f"Expected >10 webkit devices, got {len(webkit_devices)}"

stale = []
for name, desc in webkit_devices.items():
    ua = desc.get("userAgent", "")
    if "Version/" in ua and f"Version/{ts_version}" not in ua:
        stale.append(name)

# All three sources must agree on 26.4
assert ts_version == "26.4", f"wkBrowser.ts BROWSER_VERSION={ts_version}, expected 26.4"
assert json_version == "26.4", f"browsers.json browserVersion={json_version}, expected 26.4"
assert len(stale) == 0, f"{len(stale)} devices have wrong version: {stale[:5]}"
print("PASS: all sources consistent at 26.4")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Version consistency check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_readme_webkit_badge():
    """README.md WebKit badge must show version 26.4."""
    readme = Path(f"{REPO}/README.md").read_text()
    assert "webkit-26.4" in readme, "README.md badge should show webkit-26.4"
    assert ">26.4<" in readme, (
        "README.md compatibility table should list WebKit 26.4"
    )


# [pr_diff] fail_to_pass
def test_release_notes_webkit_version():
    """Release notes across all languages must list WebKit 26.4."""
    for lang in ("js", "python", "java", "csharp"):
        notes = Path(f"{REPO}/docs/src/release-notes-{lang}.md").read_text()
        assert "WebKit 26.4" in notes, (
            f"release-notes-{lang}.md should mention 'WebKit 26.4'"
        )


# [pr_diff] fail_to_pass
def test_skill_doc_created():
    """Skill doc for WebKit Safari version update must exist with required content."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path

doc = Path("/workspace/playwright/.claude/skills/playwright-dev/webkit-safari-version.md")
assert doc.exists(), "webkit-safari-version.md does not exist"

content = doc.read_text()
assert len(content) > 100, f"Skill doc too short ({len(content)} chars)"

# Must mention BROWSER_VERSION as the source of truth
assert "BROWSER_VERSION" in content, "Skill doc must mention BROWSER_VERSION constant"

# Must reference wkBrowser.ts where the version is declared
assert "wkBrowser" in content, "Skill doc must reference wkBrowser.ts"

# Must explain how to find the latest stable Safari version
lower = content.lower()
assert "safari" in lower, "Skill doc must mention Safari"
assert "stable" in lower or "release" in lower, (
    "Skill doc must explain finding the latest stable Safari version"
)

print("PASS: skill doc has required content")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Skill doc check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skill_index_updated():
    """SKILL.md must link to the webkit-safari-version skill doc."""
    skill_md = Path(f"{REPO}/.claude/skills/playwright-dev/SKILL.md").read_text()
    assert "webkit-safari-version" in skill_md, (
        "SKILL.md must contain a link to webkit-safari-version.md"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax and structure gates
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_wkbrowser_ts_valid_syntax():
    """wkBrowser.ts must have a well-formed BROWSER_VERSION declaration."""
    src = Path(f"{REPO}/packages/playwright-core/src/server/webkit/wkBrowser.ts").read_text()
    assert len(src) > 100, "wkBrowser.ts seems truncated"
    assert re.search(r"const BROWSER_VERSION\s*=\s*'[^']+'\s*;", src), (
        "BROWSER_VERSION declaration is malformed"
    )


# [static] pass_to_pass
def test_browsers_json_valid():
    """browsers.json must be valid JSON with a browsers key."""
    data = json.loads(
        Path(f"{REPO}/packages/playwright-core/browsers.json").read_text()
    )
    assert "browsers" in data, "browsers.json must have a 'browsers' key"


# [static] pass_to_pass
def test_device_descriptors_valid_json():
    """deviceDescriptorsSource.json must be valid JSON with many entries."""
    data = json.loads(
        Path(
            f"{REPO}/packages/playwright-core/src/server/deviceDescriptorsSource.json"
        ).read_text()
    )
    assert len(data) > 50, "deviceDescriptorsSource.json seems truncated"
