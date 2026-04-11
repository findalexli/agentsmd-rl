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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — git repo integrity check
def test_repo_git_checkout_valid():
    """Repo is a valid git checkout with expected commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Git check failed: {r.stderr}"
    commit = r.stdout.strip()
    # Base commit is 3aba395f2d151d2345de3182b8b3e9564507c9e5
    assert len(commit) == 40, f"Unexpected commit format: {commit}"


# [repo_tests] pass_to_pass — browsers.json schema validation
def test_repo_browsers_json_schema():
    """browsers.json has required schema with webkit entry (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import json
import sys
with open("{REPO}/packages/playwright-core/browsers.json") as f:
    data = json.load(f)
assert "browsers" in data, "Missing 'browsers' key"
browsers = data["browsers"]
webkit = [b for b in browsers if b.get("name") == "webkit"]
assert len(webkit) == 1, f"Expected 1 webkit browser, got {{len(webkit)}}"
assert "revision" in webkit[0], "Missing revision in webkit entry"
assert "browserVersion" in webkit[0], "Missing browserVersion in webkit entry"
print("PASS: browsers.json schema valid")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Schema check failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — package.json integrity
def test_repo_package_json_valid():
    """Root package.json is valid JSON with expected structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import json
with open("{REPO}/package.json") as f:
    data = json.load(f)
assert data.get("name") == "playwright-internal", "Unexpected package name"
assert "workspaces" in data, "Missing workspaces"
assert "scripts" in data, "Missing scripts"
assert "lint" in data["scripts"], "Missing lint script"
print("PASS: package.json valid")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"package.json check failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — docs directory structure
def test_repo_docs_structure():
    """Docs directory has expected release notes structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
repo = "{REPO}"
for lang in ("js", "python", "java", "csharp"):
    path = Path(repo) / "docs" / "src" / f"release-notes-{{lang}}.md"
    assert path.exists(), f"Missing release notes: {{path}}"
    content = path.read_text()
    assert len(content) > 100, f"Release notes too short: {{path}}"
print("PASS: All release notes files present")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Docs check failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — skill directory structure
def test_repo_skill_directory():
    """Skill docs directory exists with SKILL.md (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
from pathlib import Path
repo = "{REPO}"
skill_dir = Path(repo) / ".claude" / "skills" / "playwright-dev"
assert skill_dir.exists(), f"Skill directory missing: {{skill_dir}}"
skill_md = skill_dir / "SKILL.md"
assert skill_md.exists(), f"SKILL.md missing: {{skill_md}}"
print("PASS: Skill directory structure valid")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Skill dir check failed: {{r.stderr}}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — wkBrowser.ts structure
def test_repo_wkbrowser_structure():
    """wkBrowser.ts has expected structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import re
from pathlib import Path
repo = "{REPO}"
path = Path(repo) / "packages" / "playwright-core" / "src" / "server" / "webkit" / "wkBrowser.ts"
assert path.exists(), f"wkBrowser.ts missing: {{path}}"
content = path.read_text()
assert "BROWSER_VERSION" in content, "Missing BROWSER_VERSION constant"
assert "DEFAULT_USER_AGENT" in content, "Missing DEFAULT_USER_AGENT"
assert "webkit" in content.lower(), "Missing webkit references"
print("PASS: wkBrowser.ts structure valid")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"wkBrowser.ts check failed: {{r.stderr}}"
    assert "PASS" in r.stdout
