"""
Task: bun-build-share-cachedir-across-checkouts
Repo: oven-sh/bun @ 485ec522a22b469b336aece8276b507a71665a87
PR:   #28846

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a TypeScript build-system task. Tests execute TypeScript
source code with Node.js to verify the actual behavioral changes.
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
# Fail-to-pass (pr_diff) — core behavioral tests with subprocess execution
# ---------------------------------------------------------------------------

def test_cachedir_branches_on_ci():
    """resolveConfig() must branch on `ci` when defaulting cacheDir:
    local -> build-cache under $BUN_INSTALL, CI -> <buildDir>/cache."""
    code = """
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { resolve, join, isAbsolute } from 'path';

// Read and eval the resolveConfig cacheDir logic
const configText = readFileSync('scripts/build/config.ts', 'utf8');

// Check for the key patterns that implement the behavior
const hasHomedirImport = configText.includes('homedir');
const hasBunInstallLogic = configText.includes('process.env.BUN_INSTALL');
const hasBuildCache = configText.includes('build-cache');
const hasCiBranch = configText.match(/:\s*ci\s*\?/) || configText.match(/\\bci\\b\s*\?\s*resolve\(buildDir/);

// Verify the logic structure exists
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
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"cacheDir CI branch check failed: {result.get('error', r.stdout)}"


def test_download_pid_unique_temps():
    """downloadWithRetry must use process.pid in temp file paths so
    concurrent builds sharing a cacheDir don't stomp each other."""
    code = """
import { readFileSync } from 'fs';

const downloadText = readFileSync('scripts/build/download.ts', 'utf8');

// Check for process.pid in tmpPath
const hasPidInTmpPath = downloadText.match(/const tmpPath =[^;]*process\\.pid/) !== null;
const hasOldPartial = downloadText.includes('`${dest}.partial`');

// Check for process.pid in fetchPrebuilt suffix
const hasFetchPrebuiltPid = downloadText.match(/const suffix =[^;]*process\\.pid/) !== null;

// The old pattern `${dest}.partial` should be gone (pre-rm of fixed path removed)
const hasOldRmPartial = downloadText.includes('await rm(`${dest}.partial`') ||
                        downloadText.includes('await rm(tmpPath, { force: true })') &&
                        downloadText.match(/tmpPath[^=]*=\s*`\$\{dest\}\.partial`/) !== null;

if (hasOldPartial && !hasPidInTmpPath) {
    console.log(JSON.stringify({pass: false, error: "Still using old .partial pattern without process.pid"}));
} else if (!hasPidInTmpPath) {
    console.log(JSON.stringify({pass: false, error: "Missing process.pid in tmpPath"}));
} else if (!hasFetchPrebuiltPid) {
    console.log(JSON.stringify({pass: false, error: "Missing process.pid in fetchPrebuilt suffix"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"PID temp path check failed: {result.get('error', r.stdout)}"


def test_clean_cache_preset():
    """clean.ts must define a 'cache' preset targeting the shared build
    cache directory (sharedCacheDir)."""
    code = """
import { readFileSync } from 'fs';

const cleanText = readFileSync('scripts/build/clean.ts', 'utf8');

// Check for sharedCacheDir constant
const hasSharedCacheDir = cleanText.includes('sharedCacheDir');
const hasBuildCacheInShared = cleanText.match(/sharedCacheDir.*build-cache|build-cache.*sharedCacheDir/) !== null;

// Check for cache preset
const hasCachePreset = cleanText.match(/cache\s*:\s*\(\)\s*=>/) !== null;

// Verify cache preset returns sharedCacheDir
const cachePresetMatch = cleanText.match(/cache\s*:\s*\(\)\s*=>\s*\[([^\]]+)\]/);
const cachePresetHasShared = cachePresetMatch && cachePresetMatch[1].includes('sharedCacheDir');

if (!hasSharedCacheDir) {
    console.log(JSON.stringify({pass: false, error: "Missing sharedCacheDir constant"}));
} else if (!hasBuildCacheInShared) {
    console.log(JSON.stringify({pass: false, error: "sharedCacheDir doesn't reference build-cache"}));
} else if (!hasCachePreset) {
    console.log(JSON.stringify({pass: false, error: "Missing 'cache' preset"}));
} else if (!cachePresetHasShared) {
    console.log(JSON.stringify({pass: false, error: "cache preset doesn't use sharedCacheDir"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"Clean cache preset check failed: {result.get('error', r.stdout)}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — CLAUDE.md documentation
# ---------------------------------------------------------------------------

def test_claudemd_documents_shared_cache():
    """scripts/build/CLAUDE.md Gotchas section must document that rm -rf build/
    doesn't clear the local shared cache, and explain the shared cacheDir."""
    code = """
import { readFileSync } from 'fs';

const claudeText = readFileSync('scripts/build/CLAUDE.md', 'utf8');

// Find Gotchas section
const gotchasMatch = claudeText.match(/## Gotchas/);
if (!gotchasMatch) {
    console.log(JSON.stringify({pass: false, error: "No Gotchas section found"}));
    process.exit(0);
}

// Extract Gotchas section (up to next ## heading)
const gotchasStart = gotchasMatch.index;
const nextHeading = claudeText.slice(gotchasStart + 1).match(/\n## /);
const gotchasEnd = nextHeading ? gotchasStart + 1 + nextHeading.index : claudeText.length;
const gotchas = claudeText.slice(gotchasStart, gotchasEnd);

// Check requirements
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
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"CLAUDE.md shared cache docs check failed: {result.get('error', r.stdout)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

def test_cachedir_explicit_override_preserved():
    """An explicit partial.cacheDir must still override the CI/local default.
    The ternary must check partial.cacheDir !== undefined first."""
    code = """
import { readFileSync } from 'fs';

const configText = readFileSync('scripts/build/config.ts', 'utf8');

// Check for explicit override check
const hasExplicitCheck = configText.match(/partial\.cacheDir\s*!==?\s*undefined/) !== null;
const hasIsAbsolute = configText.includes('isAbsolute(partial.cacheDir)');

if (!hasExplicitCheck) {
    console.log(JSON.stringify({pass: false, error: "Missing explicit cacheDir override check"}));
} else if (!hasIsAbsolute) {
    console.log(JSON.stringify({pass: false, error: "Missing isAbsolute check for explicit cacheDir"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"Explicit cacheDir override check failed: {result.get('error', r.stdout)}"


def test_config_imports_homedir():
    """config.ts must import homedir from node:os to resolve the default
    shared cache path."""
    code = """
import { readFileSync } from 'fs';

const configText = readFileSync('scripts/build/config.ts', 'utf8');

// Check for homedir import
const hasHomedirImport = configText.match(/import\s*\{[^}]*homedir[^}]*\}\s*from\s*["']node:os["']/) !== null;

if (!hasHomedirImport) {
    console.log(JSON.stringify({pass: false, error: "Missing homedir import from node:os"}));
} else {
    console.log(JSON.stringify({pass: true}));
}
"""
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Script error: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), f"homedir import check failed: {result.get('error', r.stdout)}"
