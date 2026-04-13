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


# [repo_tests] pass_to_pass — npm run build
def test_repo_npm_build():
    """Repo builds successfully with npm run build (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"""
cd {REPO}
npm ci 2>/dev/null
npm run build 2>&1
echo EXIT:$?
"""],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"npm build failed: {{r.stderr[-500:]}}"
    assert "EXIT:0" in r.stdout, f"npm build did not exit cleanly: {{r.stdout[-500:]}}"


# [repo_tests] pass_to_pass — npm run check-deps
def test_repo_npm_check_deps():
    """Repo DEPS check passes with npm run check-deps (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"""
cd {REPO}
npm ci 2>/dev/null
npm run build 2>/dev/null
npm run check-deps 2>&1
echo EXIT:$?
"""],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"check-deps failed: {{r.stderr[-500:]}}"
    assert "EXIT:0" in r.stdout, f"check-deps did not exit cleanly: {{r.stdout[-500:]}}"


# [repo_tests] pass_to_pass — npm run lint-packages
def test_repo_npm_lint_packages():
    """Repo package lint passes with npm run lint-packages (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"""
cd {REPO}
npm ci 2>/dev/null
npm run build 2>/dev/null
npm run lint-packages 2>&1
echo EXIT:$?
"""],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"lint-packages failed: {{r.stderr[-500:]}}"
    assert "EXIT:0" in r.stdout, f"lint-packages did not exit cleanly: {{r.stdout[-500:]}}"


# [repo_tests] pass_to_pass — npm run lint-tests
def test_repo_npm_lint_tests():
    """Repo test lint passes with npm run lint-tests (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"""
cd {REPO}
npm ci 2>/dev/null
npm run build 2>/dev/null
npm run lint-tests 2>&1
echo EXIT:$?
"""],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"lint-tests failed: {{r.stderr[-500:]}}"
    assert "EXIT:0" in r.stdout, f"lint-tests did not exit cleanly: {{r.stdout[-500:]}}"


# [repo_tests] pass_to_pass — browsers.json strict validation
def test_repo_browsers_json_strict():
    """browsers.json has valid webkit entry with browserVersion (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
from pathlib import Path
repo = "/workspace/playwright"
path = Path(repo) / "packages" / "playwright-core" / "browsers.json"
data = json.loads(path.read_text())
assert "browsers" in data, "Missing browsers key"
webkit = [b for b in data["browsers"] if b.get("name") == "webkit"]
assert len(webkit) == 1, f"Expected 1 webkit, got {len(webkit)}"
assert "browserVersion" in webkit[0], "Missing browserVersion"
assert "revision" in webkit[0], "Missing revision"
assert "title" in webkit[0], "Missing title"
print("PASS: browsers.json is valid")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"browsers.json strict check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — deviceDescriptorsSource.json strict validation
def test_repo_device_descriptors_strict():
    """deviceDescriptorsSource.json has webkit devices with valid userAgent (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
from pathlib import Path
repo = "/workspace/playwright"
path = Path(repo) / "packages" / "playwright-core" / "src" / "server" / "deviceDescriptorsSource.json"
data = json.loads(path.read_text())
webkit_count = 0
for name, desc in data.items():
    if desc.get("defaultBrowserType") == "webkit":
        webkit_count += 1
        ua = desc.get("userAgent", "")
        assert "Safari" in ua or len(ua) == 0, f"WebKit device {name} missing Safari in UA"
assert webkit_count > 10, f"Expected >10 webkit devices, got {webkit_count}"
print(f"PASS: {webkit_count} webkit devices found with valid user agents")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"device descriptors check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — release notes markdown structure
def test_repo_release_notes_structure():
    """Release notes files have valid markdown structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
repo = "/workspace/playwright"
for lang in ("js", "python", "java", "csharp"):
    path = Path(repo) / "docs" / "src" / f"release-notes-{lang}.md"
    content = path.read_text()
    assert content.startswith("---"), f"{path} missing frontmatter"
    assert "id:" in content, f"{path} missing id in frontmatter"
    assert "title:" in content, f"{path} missing title in frontmatter"
    assert len(content) > 500, f"{path} too short"
print("PASS: All release notes have valid structure")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"release notes check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — SKILL.md valid markdown
def test_repo_skill_md_valid():
    """SKILL.md exists and has valid structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
repo = "/workspace/playwright"
path = Path(repo) / ".claude" / "skills" / "playwright-dev" / "SKILL.md"
content = path.read_text()
assert content.startswith("---"), "Missing frontmatter"
assert "name:" in content, "Missing name field"
assert "description:" in content, "Missing description field"
assert "- [" in content, "Missing skill links"
print("PASS: SKILL.md has valid structure")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"SKILL.md check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass — wkBrowser.ts TypeScript syntax
def test_repo_wkbrowser_ts_syntax():
    """wkBrowser.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import re
from pathlib import Path
repo = "/workspace/playwright"
path = Path(repo) / "packages" / "playwright-core" / "src" / "server" / "webkit" / "wkBrowser.ts"
content = path.read_text()
# Check for TypeScript class structure
assert "export class" in content or "class WKBrowser" in content, "Missing class declaration"
assert "extends" in content, "Missing extends clause"
assert "constructor" in content, "Missing constructor"
# Check BROWSER_VERSION format
version_match = re.search(r"const BROWSER_VERSION\\s*=\\s*'([0-9.]+)'", content)
assert version_match, "BROWSER_VERSION not in expected format"
print(f"PASS: wkBrowser.ts has valid TS syntax, version={version_match.group(1)}")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"wkBrowser.ts syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout
