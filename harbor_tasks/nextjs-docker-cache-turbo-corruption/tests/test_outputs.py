"""
Task: nextjs-docker-cache-turbo-corruption
Repo: vercel/next.js @ 7bce97d6485599cab2964ef58fde8a55d19904d3
PR:   91799

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CACHE_JS = f"{REPO}/scripts/docker-image-cache.js"
CACHE_MJS = f"{REPO}/scripts/turbo-cache.mjs"
NATIVE_JS = f"{REPO}/scripts/docker-native-build.js"
PKG_JSON = f"{REPO}/packages/next-swc/package.json"
TURBO_JSONC = f"{REPO}/packages/next-swc/turbo.jsonc"


def _node(code: str, *, input_type: str | None = None, env: dict | None = None,
          timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a Node.js snippet and return the result."""
    import os
    run_env = {**os.environ, **(env or {})}
    cmd = ["node"]
    if input_type:
        cmd += [f"--input-type={input_type}"]
    cmd += ["-e", code]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          cwd=REPO, env=run_env)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files must parse without errors."""
    for path, flag in [(CACHE_JS, []), (NATIVE_JS, [])]:
        if Path(path).exists():
            r = subprocess.run(["node", "--check", path], capture_output=True, text=True, timeout=10)
            assert r.returncode == 0, f"{path} has syntax errors: {r.stderr}"
    if Path(CACHE_MJS).exists():
        r = subprocess.run(["node", "--input-type=module", "--check"],
                           input=Path(CACHE_MJS).read_text(), capture_output=True, text=True, timeout=10)
        assert r.returncode == 0, f"{CACHE_MJS} has syntax errors: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_turbo_cache_exports():
    """turbo-cache.mjs exports 5 callable cache functions: artifactUrl, exists, get, getStream, put."""
    assert Path(CACHE_MJS).exists(), "scripts/turbo-cache.mjs does not exist"
    r = _node("""
import { artifactUrl, exists, get, getStream, put } from './scripts/turbo-cache.mjs';
const fns = { artifactUrl, exists, get, getStream, put };
for (const [name, fn] of Object.entries(fns)) {
    if (typeof fn !== 'function') {
        console.log('FAIL:' + name + '_not_function');
        process.exit(1);
    }
}
// Verify artifactUrl is callable and returns a URL string containing the key
const url = artifactUrl('testhash999');
if (typeof url !== 'string' || !url.includes('testhash999')) {
    console.log('FAIL:artifactUrl_stub');
    process.exit(1);
}
console.log('OK');
""", input_type="module")
    assert r.returncode == 0, f"turbo-cache.mjs exports check failed: {r.stdout}{r.stderr}"
    assert "OK" in r.stdout, f"Unexpected output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_artifact_url_vercel_format():
    """artifactUrl returns Vercel-style URL: /api/v8/artifacts/{hash}?teamId=..."""
    assert Path(CACHE_MJS).exists(), "scripts/turbo-cache.mjs does not exist"
    # Test with multiple keys to verify parameterization
    for key, team in [("abc123", "myteam"), ("ff00dd", "other-team")]:
        r = _node(f"""
import {{ artifactUrl }} from './scripts/turbo-cache.mjs';
const url = artifactUrl('{key}');
const checks = [
    [url.includes('/api/'), 'missing /api/ prefix'],
    [url.includes('/v8/artifacts/'), 'missing /v8/artifacts/'],
    [url.includes('{key}'), 'missing hash in URL'],
    [url.includes('teamId={team}'), 'missing teamId= query param (got url=' + url + ')'],
];
const failed = checks.filter(([ok]) => !ok);
if (failed.length > 0) {{
    console.error('FAIL:' + failed.map(([,m]) => m).join(',') + ' url=' + url);
    process.exit(1);
}}
console.log('OK');
""", input_type="module", env={"TURBO_API": "https://vercel.com", "TURBO_TEAM": team})
        assert r.returncode == 0, f"Vercel URL format wrong for key={key}, team={team}: {r.stdout}{r.stderr}"


# [pr_diff] fail_to_pass
def test_artifact_url_self_hosted_format():
    """artifactUrl returns self-hosted URL: /v8/artifacts/{hash}?slug=... (no /api/ prefix)."""
    assert Path(CACHE_MJS).exists(), "scripts/turbo-cache.mjs does not exist"
    for key, team, api in [("def456", "team2", "https://cache.example.com"),
                           ("aaa111", "squad", "https://turbo.corp.dev")]:
        r = _node(f"""
import {{ artifactUrl }} from './scripts/turbo-cache.mjs';
const url = artifactUrl('{key}');
const checks = [
    [url.includes('/v8/artifacts/'), 'missing /v8/artifacts/'],
    [url.includes('{key}'), 'missing hash in URL'],
    [url.includes('slug={team}'), 'missing slug= query param (got url=' + url + ')'],
    [!url.includes('/api/'), 'should not have /api/ prefix for self-hosted'],
];
const failed = checks.filter(([ok]) => !ok);
if (failed.length > 0) {{
    console.error('FAIL:' + failed.map(([,m]) => m).join(',') + ' url=' + url);
    process.exit(1);
}}
console.log('OK');
""", input_type="module", env={"TURBO_API": api, "TURBO_TEAM": team})
        assert r.returncode == 0, f"Self-hosted URL format wrong for api={api}: {r.stdout}{r.stderr}"


# [pr_diff] fail_to_pass
def test_cache_key_deterministic_hex():
    """docker-image-cache.js computes a deterministic hex cache key from file contents."""
    src = Path(CACHE_JS).read_text()

    # Must use crypto hash — the whole point is content-addressed caching
    assert "createHash" in src, "No createHash call found — cache key must use crypto hash"
    assert "digest" in src and "hex" in src, "No hex digest found"

    # Extract and call the hash function to verify it's deterministic.
    # The function may use destructured imports (e.g. createHash from crypto),
    # so we extract all top-level require destructurings and inject them.
    r = _node("""
const fs = require('fs');
const crypto = require('crypto');
const { createHash } = crypto;
const path = require('path');
const os = require('os');
const src = fs.readFileSync('./scripts/docker-image-cache.js', 'utf8');

// Find function whose body contains createHash/hash + digest
const funcPattern = /(?:async\\s+)?function\\s+(\\w+)\\s*\\([^)]*\\)\\s*\\{/g;
let match, hashFunc = null;
while ((match = funcPattern.exec(src)) !== null) {
    const startBrace = src.indexOf('{', match.index + match[0].length - 1);
    let depth = 0, endIdx = startBrace;
    for (let i = startBrace; i < src.length; i++) {
        if (src[i] === '{') depth++;
        if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
    }
    const body = src.slice(match.index, endIdx);
    if ((body.includes('createHash') || body.includes('crypto.createHash')) && body.includes('digest')) {
        hashFunc = { name: match[1], src: body };
        break;
    }
}
if (!hashFunc) {
    // Try arrow function pattern
    const arrowPattern = /(?:const|let|var)\\s+(\\w+)\\s*=\\s*(?:\\([^)]*\\)|[^=])\\s*=>\\s*\\{/g;
    while ((match = arrowPattern.exec(src)) !== null) {
        const startBrace = src.indexOf('{', match.index + match[0].length - 1);
        let depth = 0, endIdx = startBrace;
        for (let i = startBrace; i < src.length; i++) {
            if (src[i] === '{') depth++;
            if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
        }
        const body = src.slice(match.index, endIdx);
        if ((body.includes('createHash') || body.includes('crypto.createHash')) && body.includes('digest')) {
            hashFunc = { name: match[1], src: 'function ' + match[1] + '() ' + src.slice(startBrace, endIdx) };
            break;
        }
    }
}
if (!hashFunc) { console.error('Could not extract hash function'); process.exit(1); }

// Also extract CACHE_INPUTS or any array of file paths used by the hash function
const REPO_ROOT = process.cwd();
let CACHE_INPUTS;
const inputsMatch = src.match(/CACHE_INPUTS\\s*=\\s*\\[([\\s\\S]*?)\\]/);
if (inputsMatch) {
    // Evaluate the array in context where path and REPO_ROOT are available
    try {
        CACHE_INPUTS = eval('[' + inputsMatch[1] + ']');
    } catch(e) {
        // Fallback: just provide the known files
        CACHE_INPUTS = [
            path.join(REPO_ROOT, 'scripts/native-builder.Dockerfile'),
            path.join(REPO_ROOT, 'scripts/docker-image-cache.js'),
            path.join(REPO_ROOT, 'scripts/docker-native-build.js'),
            path.join(REPO_ROOT, 'scripts/docker-native-build.sh'),
            path.join(REPO_ROOT, 'rust-toolchain.toml'),
        ];
    }
}

try {
    // Execute the extracted function with all required bindings in scope
    const evalSrc = hashFunc.src + '; return ' + hashFunc.name + '();';
    const key1 = new Function(
        'require', '__dirname', 'path', 'fs', 'crypto', 'createHash', 'os',
        'REPO_ROOT', 'CACHE_INPUTS', evalSrc
    )(require, __dirname, path, fs, crypto, createHash, os, REPO_ROOT, CACHE_INPUTS);
    const key2 = new Function(
        'require', '__dirname', 'path', 'fs', 'crypto', 'createHash', 'os',
        'REPO_ROOT', 'CACHE_INPUTS', evalSrc
    )(require, __dirname, path, fs, crypto, createHash, os, REPO_ROOT, CACHE_INPUTS);
    if (typeof key1 !== 'string') { console.error('not_string:' + typeof key1); process.exit(1); }
    if (!/^[0-9a-f]{8,}$/.test(key1)) { console.error('not_hex:' + key1.substring(0, 40)); process.exit(1); }
    if (key1 !== key2) { console.error('not_deterministic'); process.exit(1); }
    console.log('OK:' + key1.substring(0, 16));
} catch(e) {
    console.error('extract_error:' + e.message.substring(0, 200));
    process.exit(1);
}
""")
    assert r.returncode == 0, f"Cache key not deterministic hex: {r.stderr}"
    assert r.stdout.strip().startswith("OK:"), f"Unexpected output: {r.stdout}"
    key_before = r.stdout.strip().split(":", 1)[1]

    # Verify content-sensitivity: mutating a cache input file must change the key
    r2 = _node("""
const fs = require('fs');
const crypto = require('crypto');
const { createHash } = crypto;
const path = require('path');
const os = require('os');

// Temporarily append a byte to rust-toolchain.toml to change file contents
const sentinel = path.join(process.cwd(), 'rust-toolchain.toml');
const original = fs.readFileSync(sentinel);
fs.appendFileSync(sentinel, '\\n# test-mutation');

const src = fs.readFileSync('./scripts/docker-image-cache.js', 'utf8');
const REPO_ROOT = process.cwd();

// Re-extract the hash function (same logic as above)
const funcPattern = /(?:async\\s+)?function\\s+(\\w+)\\s*\\([^)]*\\)\\s*\\{/g;
let match, hashFunc = null;
while ((match = funcPattern.exec(src)) !== null) {
    const startBrace = src.indexOf('{', match.index + match[0].length - 1);
    let depth = 0, endIdx = startBrace;
    for (let i = startBrace; i < src.length; i++) {
        if (src[i] === '{') depth++;
        if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
    }
    const body = src.slice(match.index, endIdx);
    if ((body.includes('createHash') || body.includes('crypto.createHash')) && body.includes('digest')) {
        hashFunc = { name: match[1], src: body };
        break;
    }
}
if (!hashFunc) { fs.writeFileSync(sentinel, original); console.error('no_hash_func'); process.exit(1); }

let CACHE_INPUTS;
const inputsMatch = src.match(/CACHE_INPUTS\\s*=\\s*\\[([\\s\\S]*?)\\]/);
if (inputsMatch) {
    try { CACHE_INPUTS = eval('[' + inputsMatch[1] + ']'); } catch(e) {
        CACHE_INPUTS = [
            path.join(REPO_ROOT, 'scripts/native-builder.Dockerfile'),
            path.join(REPO_ROOT, 'scripts/docker-image-cache.js'),
            path.join(REPO_ROOT, 'scripts/docker-native-build.js'),
            path.join(REPO_ROOT, 'scripts/docker-native-build.sh'),
            path.join(REPO_ROOT, 'rust-toolchain.toml'),
        ];
    }
}

try {
    const evalSrc = hashFunc.src + '; return ' + hashFunc.name + '();';
    const mutatedKey = new Function(
        'require', '__dirname', 'path', 'fs', 'crypto', 'createHash', 'os',
        'REPO_ROOT', 'CACHE_INPUTS', evalSrc
    )(require, __dirname, path, fs, crypto, createHash, os, REPO_ROOT, CACHE_INPUTS);
    console.log('MUTATED:' + mutatedKey.substring(0, 16));
} catch(e) {
    console.error('extract_error:' + e.message.substring(0, 200));
    process.exit(1);
} finally {
    fs.writeFileSync(sentinel, original);
}
""")
    assert r2.returncode == 0, f"Cache key mutation test failed: {r2.stderr}"
    mutated_line = [l for l in r2.stdout.strip().split("\n") if l.startswith("MUTATED:")]
    assert mutated_line, f"No MUTATED output: {r2.stdout}"
    key_after = mutated_line[0].split(":", 1)[1]
    assert key_before != key_after, \
        "Cache key did not change after mutating input file — key is not content-addressed"


# [pr_diff] fail_to_pass
def test_direct_cache_no_turbo_tar():
    """docker-image-cache.js uses direct cache API, not turbo tar flow."""
    src = Path(CACHE_JS).read_text()

    # Old pattern: saves to 'target/docker-image.tar' for turbo to cache
    has_tar_flow = "docker-image.tar" in src and "docker save" in src
    assert not has_tar_flow, "Still uses turbo tar-based caching flow (docker-image.tar + docker save)"

    # Must use direct cache: import turbo-cache module or use fetch/http
    uses_direct = any(s in src for s in [
        "turbo-cache", "turboCache", "fetch(", "http.request",
        "https.request", "artifactUrl"
    ])
    assert uses_direct, "No direct cache API usage detected (expected turbo-cache import or fetch calls)"

    # The --load flag should be gone (was for loading turbo-restored tar)
    has_load_flag = bool(re.search(r"""['"]load['"]\s*:\s*\{\s*type""", src))
    assert not has_load_flag, "--load flag still present (was for turbo tar loading)"


# [pr_diff] fail_to_pass
def test_native_build_bypasses_turbo():
    """docker-native-build.js calls docker-image-cache.js directly instead of turbo task."""
    assert Path(NATIVE_JS).exists(), "docker-native-build.js not found"
    src = Path(NATIVE_JS).read_text()
    # Strip comments to avoid false positives
    no_comments = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    no_comments = re.sub(r"/\*[\s\S]*?\*/", "", no_comments)

    assert "build-docker-image" not in no_comments, \
        "docker-native-build.js still invokes the turbo build-docker-image task"
    assert "docker-image-cache" in no_comments or "dockerImageCache" in no_comments, \
        "docker-native-build.js doesn't reference docker-image-cache.js directly"


# [pr_diff] fail_to_pass
def test_turbo_task_removed_from_config():
    """build-docker-image task removed from package.json and turbo.jsonc."""
    assert Path(PKG_JSON).exists(), "packages/next-swc/package.json not found (must edit, not delete)"
    pkg = Path(PKG_JSON).read_text()
    assert "build-docker-image" not in pkg, \
        "build-docker-image still in packages/next-swc/package.json"
    assert Path(TURBO_JSONC).exists(), "packages/next-swc/turbo.jsonc not found (must edit, not delete)"
    turbo = Path(TURBO_JSONC).read_text()
    assert "build-docker-image" not in turbo, \
        "build-docker-image still in packages/next-swc/turbo.jsonc"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_build_image_and_force_preserved():
    """buildImage function and --force flag are preserved in docker-image-cache.js."""
    src = Path(CACHE_JS).read_text()
    has_build = bool(re.search(
        r"(?:function\s+buildImage|const\s+buildImage\s*=|let\s+buildImage\s*=|"
        r"async\s+function\s+buildImage|buildImage\s*\()", src
    ))
    assert has_build, "buildImage function not found in docker-image-cache.js"
    assert "force" in src, "--force flag not found in docker-image-cache.js"


# ---------------------------------------------------------------------------
# Anti-stub (static) — turbo-cache.mjs is a real implementation
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_no_hardcoded_secret_values():
    """TURBO_TOKEN must be read from process.env only — no hardcoded literals or string fallbacks."""
    for filepath in [CACHE_MJS, CACHE_JS]:
        if not Path(filepath).exists():
            continue
        src = Path(filepath).read_text()
        # Strip single-line and block comments
        no_comments = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
        no_comments = re.sub(r"/\*[\s\S]*?\*/", "", no_comments)
        # No literal string assigned directly to TURBO_TOKEN variable
        assert not re.search(r'TURBO_TOKEN\s*=\s*["\'][^"\']{3,}["\']', no_comments), \
            f"{filepath}: TURBO_TOKEN assigned a hardcoded string literal"
        # No string fallback via || (e.g. TURBO_TOKEN || 'placeholder')
        assert not re.search(r'TURBO_TOKEN\s*\|\|\s*["\']', no_comments), \
            f"{filepath}: TURBO_TOKEN has a string fallback (inventing placeholder credentials)"
        # No nullish-coalescing string fallback (e.g. TURBO_TOKEN ?? 'placeholder')
        assert not re.search(r'TURBO_TOKEN\s*\?\?\s*["\']', no_comments), \
            f"{filepath}: TURBO_TOKEN has a nullish-coalescing string fallback"


# [static] fail_to_pass
def test_turbo_cache_not_stub():
    """turbo-cache.mjs has real HTTP implementation (not a stub)."""
    assert Path(CACHE_MJS).exists(), "scripts/turbo-cache.mjs does not exist"
    src = Path(CACHE_MJS).read_text()
    lines = [l for l in src.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 40, f"Only {len(lines)} meaningful lines — too short for a real cache client"
    has_http = any(s in src for s in ["fetch", "http", "request", "axios", "got("])
    assert has_http, "No HTTP logic found in turbo-cache.mjs"
