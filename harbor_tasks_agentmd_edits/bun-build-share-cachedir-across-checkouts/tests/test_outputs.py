"""
Task: bun-build-share-cachedir-across-checkouts
Repo: oven-sh/bun @ 485ec522a22b469b336aece8276b507a71665a87
PR:   #28846

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import os
from pathlib import Path

REPO = "/workspace/bun"
BUILD_DIR = Path(REPO) / "scripts/build"


def _run_node_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code via Node with experimental-strip-types."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_source_files_exist():
    """Modified source files must exist and be non-empty."""
    files = [
        BUILD_DIR / "config.ts",
        BUILD_DIR / "download.ts",
        BUILD_DIR / "clean.ts",
        BUILD_DIR / "CLAUDE.md",
        BUILD_DIR / "configure.ts",
    ]
    for f in files:
        assert f.exists(), f"{f} does not exist"
        assert f.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

def test_cachedir_branches_on_ci():
    """resolveConfig() must branch on ci when defaulting cacheDir."""
    # Write JS code to file to avoid escaping issues
    js_code = """
import { readFileSync } from 'fs';

const configText = readFileSync('scripts/build/config.ts', 'utf8');

const hasHomedirImport = configText.includes('homedir');
const hasBunInstallLogic = configText.includes('process.env.BUN_INSTALL');
const hasBuildCache = configText.includes('build-cache');
const hasCiBranch = configText.match(/:\\s*ci\\s*\\?/) !== null || configText.includes('ci\\n        ? resolve(buildDir');

if (!hasHomedirImport) {
    console.log(JSON.stringify({pass: false, error: "Missing homedir import"}));
} else if (!hasBunInstallLogic) {
    console.log(JSON.stringify({pass: false, error: "Missing BUN_INSTALL logic"}));
} else if (!hasBuildCache) {
    console.log(JSON.stringify({pass: false, error: "Missing build-cache path"}));
} else if (!hasCiBranch) {
    console.log(JSON.stringify({pass: false, error: "Missing CI branch in cacheDir"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(js_code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"cacheDir CI branch check failed: {result.get('error', r.stdout)}"


def test_download_pid_unique_temps():
    """downloadWithRetry must use process.pid in temp file paths."""
    js_code = """
import { readFileSync } from 'fs';

const downloadText = readFileSync('scripts/build/download.ts', 'utf8');

const hasPidInTmpPath = downloadText.includes('process.pid') && downloadText.includes('.partial');
const hasFetchPrebuiltPid = downloadText.includes('const suffix =') && downloadText.includes('process.pid');

if (!hasPidInTmpPath) {
    console.log(JSON.stringify({pass: false, error: "Missing process.pid in tmpPath"}));
} else if (!hasFetchPrebuiltPid) {
    console.log(JSON.stringify({pass: false, error: "Missing process.pid in fetchPrebuilt suffix"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(js_code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"PID temp path check failed: {result.get('error', r.stdout)}"


def test_clean_cache_preset():
    """clean.ts must define a 'cache' preset targeting the shared build cache."""
    js_code = """
import { readFileSync } from 'fs';

const cleanText = readFileSync('scripts/build/clean.ts', 'utf8');

const hasSharedCacheDir = cleanText.includes('sharedCacheDir');
const hasBuildCacheInShared = cleanText.includes('sharedCacheDir') && cleanText.includes('build-cache');
const hasCachePreset = cleanText.includes('cache:') && cleanText.includes('() =>');
const cachePresetHasShared = cleanText.match(/cache\\s*:\\s*\\(\\)\\s*=>/) !== null && cleanText.includes('sharedCacheDir');

if (!hasSharedCacheDir) {
    console.log(JSON.stringify({pass: false, error: "Missing sharedCacheDir constant"}));
} else if (!hasBuildCacheInShared) {
    console.log(JSON.stringify({pass: false, error: "sharedCacheDir doesn't reference build-cache"}));
} else if (!hasCachePreset) {
    console.log(JSON.stringify({pass: false, error: "Missing cache preset"}));
} else if (!cachePresetHasShared) {
    console.log(JSON.stringify({pass: false, error: "cache preset doesn't use sharedCacheDir"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(js_code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"Clean cache preset check failed: {result.get('error', r.stdout)}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) - CLAUDE.md documentation
# ---------------------------------------------------------------------------

def test_claudemd_documents_shared_cache():
    """CLAUDE.md Gotchas section must document shared cache behavior."""
    js_code = """
import { readFileSync } from 'fs';

const claudeText = readFileSync('scripts/build/CLAUDE.md', 'utf8');

const gotchasMatch = claudeText.match(/## Gotchas/);
if (!gotchasMatch) {
    console.log(JSON.stringify({pass: false, error: "No Gotchas section found"}));
    process.exit(0);
}

const gotchasStart = gotchasMatch.index;
const nextHeading = claudeText.slice(gotchasStart + 1).match(/\\n## /);
const gotchasEnd = nextHeading ? gotchasStart + 1 + nextHeading.index : claudeText.length;
const gotchas = claudeText.slice(gotchasStart, gotchasEnd);

const hasBuildCache = gotchas.includes('build-cache');
const hasRmRf = gotchas.match(/rm -rf build.*cache|cache.*rm -rf build/i) !== null;
const hasCiDistinction = gotchas.includes('CI') || gotchas.includes('ci');

if (!hasBuildCache) {
    console.log(JSON.stringify({pass: false, error: "Missing build-cache mention in Gotchas"}));
} else if (!hasRmRf) {
    console.log(JSON.stringify({pass: false, error: "Missing rm -rf build/ explanation"}));
} else if (!hasCiDistinction) {
    console.log(JSON.stringify({pass: false, error: "Missing CI vs local distinction"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(js_code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"CLAUDE.md shared cache docs check failed: {result.get('error', r.stdout)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression tests
# ---------------------------------------------------------------------------

def test_cachedir_explicit_override_preserved():
    """Explicit cacheDir override must still work."""
    js_code = """
import { readFileSync } from 'fs';

const configText = readFileSync('scripts/build/config.ts', 'utf8');

const hasExplicitCheck = configText.includes('partial.cacheDir') && configText.includes('undefined');
const hasIsAbsolute = configText.includes('isAbsolute(partial.cacheDir)');

if (!hasExplicitCheck) {
    console.log(JSON.stringify({pass: false, error: "Missing explicit cacheDir override check"}));
} else if (!hasIsAbsolute) {
    console.log(JSON.stringify({pass: false, error: "Missing isAbsolute check for explicit cacheDir"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(js_code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"Explicit cacheDir override check failed: {result.get('error', r.stdout)}"


def test_config_imports_homedir():
    """config.ts must import homedir from node:os."""
    js_code = """
import { readFileSync } from 'fs';

const configText = readFileSync('scripts/build/config.ts', 'utf8');
const hasHomedirImport = configText.includes('homedir') && configText.includes('node:os');

if (!hasHomedirImport) {
    console.log(JSON.stringify({pass: false, error: "Missing homedir import from node:os"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(js_code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"homedir import check failed: {result.get('error', r.stdout)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD gates
# ---------------------------------------------------------------------------

def test_repo_typescript_syntax():
    """Modified TypeScript files have valid syntax (pass_to_pass)."""
    files = [
        "scripts/build/config.ts",
        "scripts/build/download.ts",
        "scripts/build/clean.ts",
        "scripts/build/configure.ts",
    ]
    for f in files:
        r = subprocess.run(
            ["node", "--check", f],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\\n{r.stderr}"


def test_repo_typescript_types_basic():
    """scripts/build TypeScript has no type errors (pass_to_pass)."""
    r = subprocess.run(
        ["tsc", "--noEmit", "--project", "scripts/build/tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript type errors:\\n{r.stderr[-500:]}"


def test_repo_build_script_runnable():
    """Build entry point script is syntactically valid (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--check", "scripts/build.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert "SyntaxError" not in r.stderr, f"Syntax error in build.ts: {r.stderr}"
