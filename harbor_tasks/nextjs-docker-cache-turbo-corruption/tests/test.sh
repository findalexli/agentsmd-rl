#!/usr/bin/env bash
# Verifier for nextjs-docker-cache-turbo-corruption
#
# Bug: Turborepo remote cache corrupts/truncates large Docker image tar files (~2.8GB).
# Fix: Bypass turbo for docker image caching; use direct cache API with content-hash keys.
#
# Weight allocation:
#   TEST 1 [pr_diff] (0.15): F2P behavioral — turbo-cache.mjs exports 5 callable cache functions
#   TEST 2 [pr_diff] (0.15): F2P behavioral — artifactUrl Vercel URL format
#   TEST 3 [pr_diff] (0.15): F2P behavioral — artifactUrl self-hosted URL format
#   TEST 4 [pr_diff] (0.20): F2P behavioral — docker-image-cache.js computes deterministic hex cache key
#   TEST 5 [pr_diff] (0.10): F2P — docker-image-cache.js uses direct cache, not turbo tar flow
#   TEST 6 [pr_diff] (0.10): F2P — docker-native-build.js no longer invokes turbo build-docker-image task
#   TEST 7 [pr_diff] (0.05): F2P — build-docker-image task removed from package.json and turbo.jsonc
#   TEST 8 [pr_diff] (0.05): P2P — buildImage function and --force flag preserved
#   TEST 9 [structural] (0.05): Anti-stub — turbo-cache.mjs functions have real bodies
#   TOTAL                = 1.00
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

REPO="/workspace/next.js"
CACHE_JS="$REPO/scripts/docker-image-cache.js"
CACHE_MJS="$REPO/scripts/turbo-cache.mjs"
NATIVE_JS="$REPO/scripts/docker-native-build.js"
PKG_JSON="$REPO/packages/next-swc/package.json"
TURBO_JSONC="$REPO/packages/next-swc/turbo.jsonc"

###############################################################################
# GATE: Key source file exists and has valid syntax
###############################################################################
if [ ! -f "$CACHE_JS" ]; then
    echo "GATE FAILED: scripts/docker-image-cache.js missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
node --check "$CACHE_JS" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: docker-image-cache.js has syntax errors"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
if [ -f "$CACHE_MJS" ]; then
    node --input-type=module --check < "$CACHE_MJS" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAILED: turbo-cache.mjs has syntax errors"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
fi
if [ -f "$NATIVE_JS" ]; then
    node --check "$NATIVE_JS" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAILED: docker-native-build.js has syntax errors"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
fi
echo "GATE: All JS files pass syntax check — PASS"

SCORE="0.0"

###############################################################################
# TEST 1 [pr_diff] (0.15): F2P behavioral — turbo-cache.mjs exports 5 callable
# cache client functions: artifactUrl, exists, get, getStream, put.
# Base commit: turbo-cache.mjs does not exist → fails on buggy code.
# Accepts any export style (named, default object, etc.) as long as they're functions.
###############################################################################
echo ""
echo "TEST 1: [pr_diff] (0.15) F2P — turbo-cache.mjs exports working cache client"
if [ -f "$CACHE_MJS" ]; then
    T1=$(node --input-type=module -e "
import { artifactUrl, exists, get, getStream, put } from '$CACHE_MJS';
const fns = { artifactUrl, exists, get, getStream, put };
for (const [name, fn] of Object.entries(fns)) {
    if (typeof fn !== 'function') {
        console.log('FAIL:' + name + '_not_function');
        process.exit(0);
    }
}
// Verify artifactUrl is not a stub — must return a string containing the hash
const url = artifactUrl('testhash999');
if (typeof url !== 'string' || !url.includes('testhash999')) {
    console.log('FAIL:artifactUrl_stub');
    process.exit(0);
}
console.log('OK');
" 2>&1)
    if echo "$T1" | grep -q "^OK"; then
        echo "  PASS: All 5 exports are callable functions, artifactUrl returns URL with hash"
        SCORE=$(python3 -c "print(round($SCORE + 0.15, 4))")
    else
        echo "  FAIL: $T1"
    fi
else
    echo "  FAIL: scripts/turbo-cache.mjs does not exist"
fi

###############################################################################
# TEST 2 [pr_diff] (0.15): F2P behavioral — artifactUrl Vercel URL format
# Vercel API uses /api/v8/artifacts/{hash} with teamId query param.
# Base commit: function doesn't exist → fails on buggy code.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] (0.15) F2P — artifactUrl correct for Vercel"
if [ -f "$CACHE_MJS" ]; then
    T2=$(TURBO_API="https://vercel.com" TURBO_TEAM="myteam" node --input-type=module -e "
import { artifactUrl } from '$CACHE_MJS';
const url = artifactUrl('abc123');
// Vercel URL must: include /api/ prefix, include /v8/artifacts/, include hash, include team
const checks = [
    [url.includes('/api/'), 'missing /api/ prefix'],
    [url.includes('/v8/artifacts/'), 'missing /v8/artifacts/'],
    [url.includes('abc123'), 'missing hash in URL'],
    [url.includes('myteam'), 'missing team in URL'],
];
const failed = checks.filter(([ok]) => !ok);
if (failed.length === 0) {
    console.log('OK');
} else {
    console.log('FAIL:' + failed.map(([,m]) => m).join(',') + ':' + url);
}
" 2>&1)
    if echo "$T2" | grep -q "^OK"; then
        echo "  PASS: Vercel URL format correct"
        SCORE=$(python3 -c "print(round($SCORE + 0.15, 4))")
    else
        echo "  FAIL: $T2"
    fi
else
    echo "  FAIL: scripts/turbo-cache.mjs does not exist"
fi

###############################################################################
# TEST 3 [pr_diff] (0.15): F2P behavioral — artifactUrl self-hosted URL format
# Self-hosted cache uses /v8/artifacts/{hash} (no /api/ prefix), slug query param.
# Base commit: function doesn't exist → fails on buggy code.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] (0.15) F2P — artifactUrl correct for self-hosted"
if [ -f "$CACHE_MJS" ]; then
    T3=$(TURBO_API="https://cache.example.com" TURBO_TEAM="team2" node --input-type=module -e "
import { artifactUrl } from '$CACHE_MJS';
const url = artifactUrl('def456');
// Self-hosted URL must: include /v8/artifacts/, include hash, include team, NOT have /api/ prefix
const checks = [
    [url.includes('/v8/artifacts/'), 'missing /v8/artifacts/'],
    [url.includes('def456'), 'missing hash in URL'],
    [url.includes('team2'), 'missing team in URL'],
    [!url.includes('/api/'), 'should not have /api/ prefix for self-hosted'],
];
const failed = checks.filter(([ok]) => !ok);
if (failed.length === 0) {
    console.log('OK');
} else {
    console.log('FAIL:' + failed.map(([,m]) => m).join(',') + ':' + url);
}
" 2>&1)
    if echo "$T3" | grep -q "^OK"; then
        echo "  PASS: Self-hosted URL format correct"
        SCORE=$(python3 -c "print(round($SCORE + 0.15, 4))")
    else
        echo "  FAIL: $T3"
    fi
else
    echo "  FAIL: scripts/turbo-cache.mjs does not exist"
fi

###############################################################################
# TEST 4 [pr_diff] (0.20): F2P behavioral — docker-image-cache.js computes a
# deterministic hex hash from repo file contents as cache key.
# Base commit: no cache key computation (relied entirely on turbo).
# We extract the hash function via AST and actually CALL it to verify behavior.
# (AST extraction justified: script runs main() on require, can't import directly)
###############################################################################
echo ""
echo "TEST 4: [pr_diff] (0.20) F2P — Cache key is a deterministic hex hash from file contents"
T4=$(node -e "
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');
const src = fs.readFileSync('$CACHE_JS', 'utf8');

// Must use crypto hash — the whole point is content-addressed caching
if (!src.includes('createHash')) {
    console.log('FAIL:no_createHash');
    process.exit(0);
}
if (!src.includes(\"digest('hex')\") && !src.includes('digest(\"hex\")')) {
    console.log('FAIL:no_hex_digest');
    process.exit(0);
}

// Find function whose body contains createHash + digest (the cache key function)
const funcPattern = /(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{/g;
let match, hashFunc = null;
while ((match = funcPattern.exec(src)) !== null) {
    const startBrace = src.indexOf('{', match.index + match[0].length - 1);
    let depth = 0, endIdx = startBrace;
    for (let i = startBrace; i < src.length; i++) {
        if (src[i] === '{') depth++;
        if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
    }
    const body = src.slice(match.index, endIdx);
    if (body.includes('createHash') && body.includes('digest')) {
        hashFunc = { name: match[1], src: body };
        break;
    }
}

if (!hashFunc) {
    // Check for arrow function pattern: const X = (...) => { ...createHash... }
    const arrowPattern = /(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=])\s*=>\s*\{/g;
    while ((match = arrowPattern.exec(src)) !== null) {
        const startBrace = src.indexOf('{', match.index + match[0].length - 1);
        let depth = 0, endIdx = startBrace;
        for (let i = startBrace; i < src.length; i++) {
            if (src[i] === '{') depth++;
            if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
        }
        const body = src.slice(match.index, endIdx);
        if (body.includes('createHash') && body.includes('digest')) {
            // Convert to callable form
            hashFunc = { name: match[1], src: 'function ' + match[1] + '() ' + src.slice(startBrace, endIdx) };
            break;
        }
    }
}

if (!hashFunc) {
    // Hash computation exists in file but not in extractable function
    // Give partial credit — the key behavioral signal (createHash + hex digest) is present
    console.log('PARTIAL:hash_present_not_extractable');
    process.exit(0);
}

try {
    const fn = new Function('require', '__dirname', 'path', 'fs', 'crypto', 'REPO_ROOT',
        hashFunc.src + '; return ' + hashFunc.name + ';'
    );
    const REPO_ROOT = '$REPO';
    const computeKey = fn(require, path.dirname('$CACHE_JS'), path, fs, crypto, REPO_ROOT);

    const key1 = computeKey();
    const key2 = computeKey();

    if (typeof key1 !== 'string') {
        console.log('FAIL:not_string:' + typeof key1);
    } else if (!/^[0-9a-f]{8,}\$/.test(key1)) {
        console.log('FAIL:not_hex:' + key1.substring(0, 40));
    } else if (key1 !== key2) {
        console.log('FAIL:not_deterministic:' + key1 + '!=' + key2);
    } else {
        console.log('OK:' + key1.substring(0, 16));
    }
} catch(e) {
    // Function exists but needs dependencies we can't provide — partial credit
    console.log('PARTIAL:' + e.message.substring(0, 100));
}
" 2>&1)

if echo "$T4" | grep -q "^OK:"; then
    echo "  PASS: Cache key is deterministic hex hash"
    SCORE=$(python3 -c "print(round($SCORE + 0.20, 4))")
elif echo "$T4" | grep -q "^PARTIAL"; then
    echo "  PARTIAL: Hash logic present but couldn't fully verify: $T4"
    SCORE=$(python3 -c "print(round($SCORE + 0.10, 4))")
else
    echo "  FAIL: $T4"
fi

###############################################################################
# TEST 5 [pr_diff] (0.10): F2P — docker-image-cache.js uses direct cache, not turbo
# Base commit: saves tar to target/docker-image.tar for turbo, has --load flag.
# After fix: uses direct cache API (imports turbo-cache or implements HTTP client),
# no longer saves tar for turbo to manage.
# Accepts: import turbo-cache, OR inline HTTP/fetch calls, OR any direct cache approach.
###############################################################################
echo ""
echo "TEST 5: [pr_diff] (0.10) F2P — docker-image-cache.js bypasses turbo caching"
T5=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$CACHE_JS', 'utf8');

// The fix MUST eliminate the turbo tar-based flow.
// Old pattern: saves to 'target/docker-image.tar' for turbo to cache as output.
const hasTarFlow = src.includes('docker-image.tar') && src.includes('docker save');

// The fix should use direct cache: either import turbo-cache module or use fetch/http
const usesDirectCache = src.includes('turbo-cache') ||
    src.includes('turboCache') ||
    src.includes('fetch(') ||
    src.includes('http.request') ||
    src.includes('https.request') ||
    src.includes('artifactUrl');

// The --load flag should be gone (it was for loading turbo-restored tar)
const hasLoadFlag = /['\"]load['\"]\s*:\s*\{\s*type/.test(src);

if (!hasTarFlow && usesDirectCache && !hasLoadFlag) {
    console.log('OK');
} else if (!hasTarFlow && !hasLoadFlag) {
    // Tar flow gone and load flag gone, but can't detect direct cache method
    console.log('PARTIAL:no_tar_no_load');
} else {
    const reasons = [];
    if (hasTarFlow) reasons.push('still_has_tar_flow');
    if (hasLoadFlag) reasons.push('still_has_load_flag');
    if (!usesDirectCache) reasons.push('no_direct_cache_detected');
    console.log('FAIL:' + reasons.join(','));
}
" 2>&1)

if echo "$T5" | grep -q "^OK"; then
    echo "  PASS: Uses direct cache API, no turbo tar flow, no --load"
    SCORE=$(python3 -c "print(round($SCORE + 0.10, 4))")
elif echo "$T5" | grep -q "^PARTIAL"; then
    echo "  PARTIAL: $T5"
    SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
else
    echo "  FAIL: $T5"
fi

###############################################################################
# TEST 6 [pr_diff] (0.10): F2P — docker-native-build.js no longer uses turbo task
# Base commit: calls `pnpm -F @next/swc build-docker-image` (the turbo path).
# After fix: calls docker-image-cache.js directly (or equivalent).
###############################################################################
echo ""
echo "TEST 6: [pr_diff] (0.10) F2P — docker-native-build.js bypasses turbo for docker image"
if [ -f "$NATIVE_JS" ]; then
    T6=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$NATIVE_JS', 'utf8');

// Strip comments to avoid false positives from explanatory comments
const noComments = src.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Must NOT invoke the turbo build-docker-image task in actual code
const hasTurboTask = noComments.includes('build-docker-image');

// Should reference docker-image-cache directly (any form: path string, require, import)
const hasDirect = noComments.includes('docker-image-cache') ||
    noComments.includes('docker_image_cache') ||
    noComments.includes('dockerImageCache');

if (!hasTurboTask && hasDirect) {
    console.log('OK');
} else if (!hasTurboTask) {
    // Turbo task gone, but direct reference not found — might use different approach
    console.log('PARTIAL:no_turbo_no_direct');
} else {
    console.log('FAIL:still_has_turbo_task');
}
" 2>&1)
    if echo "$T6" | grep -q "^OK"; then
        echo "  PASS: Calls docker-image-cache.js directly, no turbo task"
        SCORE=$(python3 -c "print(round($SCORE + 0.10, 4))")
    elif echo "$T6" | grep -q "^PARTIAL"; then
        echo "  PARTIAL: Turbo task removed but direct call not detected: $T6"
        SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
    else
        echo "  FAIL: $T6"
    fi
else
    echo "  FAIL: docker-native-build.js not found"
fi

###############################################################################
# TEST 7 [pr_diff] (0.05): F2P — build-docker-image turbo task removed from config
# Base commit: package.json has "build-docker-image" script, turbo.jsonc has the task.
# After fix: both references removed.
###############################################################################
echo ""
echo "TEST 7: [pr_diff] (0.05) F2P — build-docker-image removed from turbo config"
T7_PASS=0
T7_TOTAL=0
if [ -f "$PKG_JSON" ]; then
    T7_TOTAL=$((T7_TOTAL + 1))
    if ! grep -q "build-docker-image" "$PKG_JSON"; then
        echo "  PASS: build-docker-image removed from package.json"
        T7_PASS=$((T7_PASS + 1))
    else
        echo "  FAIL: build-docker-image still in package.json"
    fi
fi
if [ -f "$TURBO_JSONC" ]; then
    T7_TOTAL=$((T7_TOTAL + 1))
    if ! grep -q "build-docker-image" "$TURBO_JSONC"; then
        echo "  PASS: build-docker-image removed from turbo.jsonc"
        T7_PASS=$((T7_PASS + 1))
    else
        echo "  FAIL: build-docker-image still in turbo.jsonc"
    fi
fi
if [ $T7_TOTAL -gt 0 ] && [ $T7_PASS -eq $T7_TOTAL ]; then
    SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
fi

###############################################################################
# TEST 8 [pr_diff] (0.05): P2P — buildImage function and --force flag preserved
# These existed before the fix and must still work. Accepts multiple function styles.
###############################################################################
echo ""
echo "TEST 8: [pr_diff] (0.05) P2P — buildImage and --force preserved"
T8=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('$CACHE_JS', 'utf8');

// buildImage: accept function declaration, async function, arrow function, method
const hasBuildImage = /(?:function\s+buildImage|const\s+buildImage\s*=|let\s+buildImage\s*=|async\s+function\s+buildImage|buildImage\s*\()/.test(src);

// --force flag: accept parseArgs option, manual argv check, minimist, etc.
const hasForce = src.includes('force');

if (hasBuildImage && hasForce) {
    console.log('OK');
} else {
    const missing = [];
    if (!hasBuildImage) missing.push('buildImage');
    if (!hasForce) missing.push('force');
    console.log('FAIL:missing_' + missing.join('_'));
}
" 2>&1)

if echo "$T8" | grep -q "^OK"; then
    echo "  PASS: buildImage function and --force flag present"
    SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
else
    echo "  FAIL: $T8"
fi

###############################################################################
# TEST 9 [structural] (0.05): Anti-stub — turbo-cache.mjs has real implementations
# Checks that exported functions have non-trivial bodies (>3 statements),
# not just empty functions or single-line returns.
###############################################################################
echo ""
echo "TEST 9: [structural] (0.05) Anti-stub — turbo-cache.mjs is a real implementation"
if [ -f "$CACHE_MJS" ]; then
    T9=$(node --input-type=module -e "
import { artifactUrl, exists, get, put } from '$CACHE_MJS';
import fs from 'fs';

// Read source to check function bodies are non-trivial
const src = fs.readFileSync('$CACHE_MJS', 'utf8');

// Count total non-empty, non-comment lines
const lines = src.split('\n').filter(l => l.trim() && !l.trim().startsWith('//'));

// Must have at least 40 meaningful lines (a real HTTP cache client needs this)
if (lines.length < 40) {
    console.log('FAIL:only_' + lines.length + '_meaningful_lines');
    process.exit(0);
}

// Verify exists/get/put reference HTTP or fetch (they talk to a cache server)
const hasHttpLogic = src.includes('fetch') || src.includes('http') ||
    src.includes('request') || src.includes('axios') || src.includes('got(');
if (!hasHttpLogic) {
    console.log('FAIL:no_http_logic');
    process.exit(0);
}

console.log('OK:' + lines.length + '_lines');
" 2>&1)
    if echo "$T9" | grep -q "^OK:"; then
        echo "  PASS: $T9"
        SCORE=$(python3 -c "print(round($SCORE + 0.05, 4))")
    else
        echo "  FAIL: $T9"
    fi
else
    echo "  FAIL: turbo-cache.mjs does not exist"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "=============================="
echo "FINAL SCORE: $SCORE"
echo "=============================="
echo "$SCORE" > "$REWARD_FILE"

# Optional LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
