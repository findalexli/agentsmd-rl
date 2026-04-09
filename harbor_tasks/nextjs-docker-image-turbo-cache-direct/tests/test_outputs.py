"""
Task: nextjs-docker-image-turbo-cache-direct
Repo: next.js @ 7bce97d6485599cab2964ef58fde8a55d19904d3
PR:   92029

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified JS/MJS files parse without Node.js syntax errors."""
    files = [
        "scripts/docker-image-cache.js",
        "scripts/docker-native-build.js",
        "scripts/turbo-cache.mjs",
    ]
    for f in files:
        fpath = os.path.join(REPO, f)
        if not os.path.exists(fpath):
            continue
        r = subprocess.run(
            ["node", "--check", fpath],
            capture_output=True, timeout=10,
        )
        assert r.returncode == 0, (
            f"{f} has syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_artifact_url_vercel():
    """turbo-cache.mjs artifactUrl() returns correct vercel.com API path."""
    r = subprocess.run(
        ["node", "--input-type=module", "-e", """
import { artifactUrl } from './scripts/turbo-cache.mjs';
const key = 'deadbeef1234';
const url = artifactUrl(key);
console.log(url);
"""],
        cwd=REPO, capture_output=True, timeout=10,
        env={**os.environ, "TURBO_API": "https://vercel.com", "TURBO_TEAM": "", "TURBO_TOKEN": "fake"},
    )
    assert r.returncode == 0, f"Failed to import turbo-cache.mjs:\n{r.stderr.decode()}"
    url = r.stdout.decode().strip()
    assert "/api/v8/artifacts/deadbeef1234" in url, f"Expected vercel.com API path, got: {url}"
    assert "vercel.com" in url, f"Expected vercel.com domain, got: {url}"


# [pr_diff] fail_to_pass
def test_artifact_url_selfhosted():
    """turbo-cache.mjs artifactUrl() returns different path for self-hosted servers."""
    custom_api = "https://cache.example.com"
    r = subprocess.run(
        ["node", "--input-type=module", "-e", f"""
import {{ artifactUrl }} from './scripts/turbo-cache.mjs';
const url = artifactUrl('abc999');
console.log(url);
"""],
        cwd=REPO, capture_output=True, timeout=10,
        env={**os.environ, "TURBO_API": custom_api, "TURBO_TEAM": "", "TURBO_TOKEN": "fake"},
    )
    assert r.returncode == 0, f"Failed to import turbo-cache.mjs:\n{r.stderr.decode()}"
    url = r.stdout.decode().strip()
    # Self-hosted servers use /v8/artifacts/ (no /api/ prefix)
    assert url.startswith(f"{custom_api}/v8/artifacts/abc999"), f"Expected self-hosted path, got: {url}"
    assert "/api/" not in url, f"Self-hosted URL should not have /api/ prefix: {url}"


# [pr_diff] fail_to_pass
def test_artifact_url_team_param():
    """turbo-cache.mjs artifactUrl() appends team parameter for vercel.com."""
    r = subprocess.run(
        ["node", "--input-type=module", "-e", """
import { artifactUrl } from './scripts/turbo-cache.mjs';
const url = artifactUrl('ff00ff');
console.log(url);
"""],
        cwd=REPO, capture_output=True, timeout=10,
        env={**os.environ, "TURBO_API": "https://vercel.com", "TURBO_TEAM": "team_abc123", "TURBO_TOKEN": "fake"},
    )
    assert r.returncode == 0, f"Failed:\n{r.stderr.decode()}"
    url = r.stdout.decode().strip()
    assert "teamId=team_abc123" in url, f"Expected teamId param, got: {url}"
    assert "ff00ff" in url, f"Expected key in URL, got: {url}"


# [pr_diff] fail_to_pass
def test_turbo_cache_exports():
    """turbo-cache.mjs exports all required API functions."""
    r = subprocess.run(
        ["node", "--input-type=module", "-e", """
import * as cache from './scripts/turbo-cache.mjs';
const required = ['exists', 'get', 'getStream', 'put', 'artifactUrl', 'healthCheck'];
const missing = required.filter(fn => typeof cache[fn] !== 'function');
if (missing.length > 0) {
    console.error('Missing exports:', missing.join(', '));
    process.exit(1);
}
console.log('All exports present');
"""],
        cwd=REPO, capture_output=True, timeout=10,
        env={**os.environ, "TURBO_API": "https://vercel.com", "TURBO_TEAM": "", "TURBO_TOKEN": ""},
    )
    assert r.returncode == 0, (
        f"Missing exports in turbo-cache.mjs:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    )


# [pr_diff] fail_to_pass
def test_no_build_docker_script():
    """packages/next-swc/package.json no longer has build-docker-image script."""
    pkg = json.loads(Path(f"{REPO}/packages/next-swc/package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "build-docker-image" not in scripts, (
        "build-docker-image script should be removed from packages/next-swc/package.json"
    )


# [pr_diff] fail_to_pass
def test_native_build_direct_invocation():
    """docker-native-build.js calls docker-image-cache.js directly, not via pnpm turbo."""
    src = Path(f"{REPO}/scripts/docker-native-build.js").read_text()
    # Old code used: execSync(`pnpm -F @next/swc build-docker-image...`)
    assert "pnpm -F @next/swc build-docker-image" not in src, (
        "docker-native-build.js should call docker-image-cache.js directly, "
        "not via pnpm turbo task"
    )
    # New code uses: execFileSync('node', [path.join(__dirname, 'docker-image-cache.js'), ...])
    assert "docker-image-cache.js" in src, (
        "docker-native-build.js should reference docker-image-cache.js"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cache_input_files_exist():
    """All Docker image cache input files exist on disk (pass_to_pass)."""
    files = [
        "scripts/native-builder.Dockerfile",
        "scripts/docker-image-cache.js",
        "scripts/docker-native-build.js",
        "scripts/docker-native-build.sh",
        "rust-toolchain.toml",
    ]
    for f in files:
        fpath = os.path.join(REPO, f)
        assert os.path.exists(fpath), f"Required cache input file missing: {f}"


# [repo_tests] pass_to_pass
def test_docker_image_cache_builtin_modules():
    """docker-image-cache.js only imports built-in Node.js modules (pass_to_pass)."""
    src = Path(f"{REPO}/scripts/docker-image-cache.js").read_text()
    requires = re.findall(r'require\(["\']([^"\']+)["\']\)', src)
    builtins = {
        "child_process", "crypto", "fs", "os", "path",
        "node:util", "node:child_process", "stream", "node:stream",
    }
    for mod in requires:
        assert mod in builtins, (
            f"docker-image-cache.js imports non-built-in module: {mod}"
        )


# [repo_tests] pass_to_pass
def test_docker_native_build_builtin_modules():
    """docker-native-build.js only imports built-in Node.js modules (pass_to_pass)."""
    src = Path(f"{REPO}/scripts/docker-native-build.js").read_text()
    requires = re.findall(r'require\(["\']([^"\']+)["\']\)', src)
    builtins = {
        "child_process", "crypto", "fs", "os", "path",
        "node:util", "node:child_process", "stream", "node:stream",
    }
    for mod in requires:
        assert mod in builtins, (
            f"docker-native-build.js imports non-built-in module: {mod}"
        )


# [repo_tests] pass_to_pass
def test_scripts_have_shebangs():
    """Script files have proper Node.js shebangs (pass_to_pass)."""
    scripts = [
        "scripts/docker-image-cache.js",
        "scripts/docker-native-build.js",
    ]
    for f in scripts:
        src = Path(os.path.join(REPO, f)).read_text()
        assert src.startswith("#!/usr/bin/env node"), (
            f"{f} missing proper shebang line"
        )


# [repo_tests] pass_to_pass
def test_next_swc_package_json_valid():
    """packages/next-swc/package.json is valid JSON with expected fields (pass_to_pass)."""
    pkg = json.loads(Path(f"{REPO}/packages/next-swc/package.json").read_text())
    assert pkg["name"] == "@next/swc", (
        f"Expected @next/swc, got: {pkg.get('name')}"
    )
    assert "scripts" in pkg, "Missing scripts in packages/next-swc/package.json"
    assert "build-native" in pkg["scripts"], (
        "build-native script missing from packages/next-swc/package.json"
    )


# [repo_tests] pass_to_pass
def test_docker_image_cache_has_parseargs():
    """docker-image-cache.js properly imports and uses parseArgs (pass_to_pass)."""
    src = Path(f"{REPO}/scripts/docker-image-cache.js").read_text()
    assert "parseArgs" in src, "docker-image-cache.js missing parseArgs usage"
    assert "force" in src, "docker-image-cache.js missing --force flag handling"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_image_preserved():
    """docker-image-cache.js still has buildImage function (core functionality)."""
    src = Path(f"{REPO}/scripts/docker-image-cache.js").read_text()
    assert "function buildImage()" in src, (
        "buildImage() function must be preserved in docker-image-cache.js"
    )
    # Verify it still does a docker build (not a stub)
    assert "docker build" in src or "docker buildx" in src, (
        "buildImage() must actually build a docker image"
    )


# [pr_diff] fail_to_pass
def test_turbo_jsonc_no_docker_task():
    """packages/next-swc/turbo.jsonc no longer defines build-docker-image task."""
    src = Path(f"{REPO}/packages/next-swc/turbo.jsonc").read_text()
    assert '"build-docker-image"' not in src, (
        "build-docker-image task should be removed from turbo.jsonc"
    )
