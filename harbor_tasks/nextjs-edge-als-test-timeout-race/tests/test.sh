#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
REPO="/workspace/next.js"
TEST_DIR="$REPO/test/e2e/edge-async-local-storage"
TEST_FILE="$TEST_DIR/index.test.ts"

mkdir -p /logs/verifier

add_score() {
    local weight="$1"
    local name="$2"
    SCORE=$(python3 -c "print(round($SCORE + $weight, 4))")
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    echo "PASS ($weight): $name"
}

add_fail() {
    local weight="$1"
    local name="$2"
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    echo "FAIL ($weight): $name"
}

# Helper: find fixture file at common locations
find_fixture() {
    local name="$1"
    for ext in js ts jsx tsx mjs; do
        local p="$TEST_DIR/pages/api/$name.$ext"
        [ -f "$p" ] && echo "$p" && return 0
    done
    for ext in js ts mjs; do
        local p="$TEST_DIR/app/api/$name/route.$ext"
        [ -f "$p" ] && echo "$p" && return 0
    done
    return 1
}

# ============================================================
# GATE: Test file must exist
# ============================================================
if [ ! -f "$TEST_FILE" ]; then
    echo "GATE FAIL: Test file does not exist"
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: Test file exists"

# ============================================================
# FAIL-TO-PASS BEHAVIORAL: Fixture files work correctly (0.55)
# These actually execute the fixture handler and verify output.
# ============================================================

# [pr_diff] (0.30): Single fixture is a working edge API route
# Runs the handler with a mock request and checks it returns {id: <req-id>}
SINGLE_FIX=$(find_fixture "single")
if [ -n "$SINGLE_FIX" ]; then
    node -e "
const vm = require('vm');
const fs = require('fs');
const { AsyncLocalStorage } = require('async_hooks');

let code = fs.readFileSync('$SINGLE_FIX', 'utf8');
// Transform ESM exports to sandbox-compatible assignments
code = code.replace(/^export\s+default\s+/m, '__exports.default = ');
code = code.replace(/^export\s+(const|let|var|function|async\s+function|class)\s+/gm, '\$1 ');
code = code.replace(/^import\s+.*$/gm, '');

const __exports = {};
const sandbox = {
    AsyncLocalStorage,
    Response: globalThis.Response,
    fetch: async () => ({ text: async () => '', ok: true }),
    console, __exports, setTimeout, clearTimeout, Promise,
    require: require,
};

try { vm.runInNewContext(code, sandbox, { timeout: 5000 }); }
catch(e) { console.error('Eval failed:', e.message); process.exit(1); }

const handler = __exports.default;
if (typeof handler !== 'function') {
    console.error('No default export function'); process.exit(1);
}

const mockReq = { headers: { get: (n) => n === 'req-id' ? 'test-42' : null } };
handler(mockReq).then(async (resp) => {
    const json = await resp.json();
    if (json.id !== 'test-42') {
        console.error('Expected id=test-42, got', JSON.stringify(json));
        process.exit(1);
    }
    console.log('Single fixture OK:', JSON.stringify(json));
}).catch((e) => { console.error('Handler error:', e.message); process.exit(1); });
" 2>&1
    if [ $? -eq 0 ]; then
        add_score 0.30 "Single fixture returns correct response"
    else
        add_fail 0.30 "Single fixture does not return correct response"
    fi
else
    add_fail 0.30 "No single fixture file found"
fi

# [pr_diff] (0.25): Multiple fixture with nested ALS returns {id, nestedId}
MULTI_FIX=$(find_fixture "multiple")
if [ -n "$MULTI_FIX" ]; then
    node -e "
const vm = require('vm');
const fs = require('fs');
const { AsyncLocalStorage } = require('async_hooks');

let code = fs.readFileSync('$MULTI_FIX', 'utf8');
code = code.replace(/^export\s+default\s+/m, '__exports.default = ');
code = code.replace(/^export\s+(const|let|var|function|async\s+function|class)\s+/gm, '\$1 ');
code = code.replace(/^import\s+.*$/gm, '');

const __exports = {};
const sandbox = {
    AsyncLocalStorage,
    Response: globalThis.Response,
    fetch: async () => ({ text: async () => '', ok: true }),
    console, __exports, setTimeout, clearTimeout, Promise,
    require: require,
};

try { vm.runInNewContext(code, sandbox, { timeout: 5000 }); }
catch(e) { console.error('Eval failed:', e.message); process.exit(1); }

const handler = __exports.default;
if (typeof handler !== 'function') {
    console.error('No default export function'); process.exit(1);
}

const mockReq = { headers: { get: (n) => n === 'req-id' ? 'test-99' : null } };
handler(mockReq).then(async (resp) => {
    const json = await resp.json();
    if (json.id !== 'test-99') {
        console.error('Expected id=test-99, got', JSON.stringify(json));
        process.exit(1);
    }
    if (!json.nestedId || !String(json.nestedId).includes('nested')) {
        console.error('Expected nestedId containing nested, got', JSON.stringify(json));
        process.exit(1);
    }
    console.log('Multiple fixture OK:', JSON.stringify(json));
}).catch((e) => { console.error('Handler error:', e.message); process.exit(1); });
" 2>&1
    if [ $? -eq 0 ]; then
        add_score 0.25 "Multiple fixture returns correct nested response"
    else
        add_fail 0.25 "Multiple fixture does not return correct response"
    fi
else
    add_fail 0.25 "No multiple fixture file found"
fi

# ============================================================
# FAIL-TO-PASS STRUCTURAL (0.20)
# ============================================================

# [pr_diff] (0.15): No per-test instance creation (the core race condition bug)
# Buggy code calls createNext inside it.each body. Any correct fix moves setup
# outside test bodies (nextTestSetup, manual beforeAll, factory, etc.)
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');

// If no createNext at all, fix uses alternative (nextTestSetup etc.) — PASS
if (!code.includes('createNext')) process.exit(0);

// createNext exists: verify it is NOT inside an it/test callback.
// Walk lines with brace-depth tracking to detect test body scope.
const lines = code.split('\\n');
let inTestBody = false;
let braceDepth = 0;
let testEntryDepth = -1;

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!inTestBody && /\\b(it|test)\\s*[.(]/.test(line)) {
        inTestBody = true;
        testEntryDepth = braceDepth;
    }
    for (const ch of line) {
        if (ch === '{') braceDepth++;
        if (ch === '}') braceDepth--;
    }
    if (inTestBody && braceDepth <= testEntryDepth) {
        inTestBody = false;
    }
    if (inTestBody && line.includes('createNext')) {
        console.error('createNext inside test body at line ' + (i+1));
        process.exit(1);
    }
}
console.log('createNext not called per-test');
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.15 "No per-test instance creation (race condition fixed)"
else
    add_fail 0.15 "Still has per-test instance creation"
fi

# [pr_diff] (0.05): No inline route code as template strings in test file
# Buggy code had multi-line backtick strings containing full route handlers
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
// Reject template literals that contain route handler signatures
const tmpl = /\x60[^\x60]{50,}\x60/s;
const matches = code.match(/\x60([^\x60]*)\x60/gs) || [];
for (const m of matches) {
    if (/export\s+(default|const\s+config)/.test(m) || /function\s+handler/.test(m)) {
        console.error('Inline route code found in template string');
        process.exit(1);
    }
}
console.log('No inline route code');
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.05 "No inline route code in test file"
else
    add_fail 0.05 "Still has inline route code in test file"
fi

# ============================================================
# PASS-TO-PASS REGRESSION (0.10)
# ============================================================

# [pr_diff] (0.05): Test still uses fetchViaHTTP from next-test-utils
if grep -q 'fetchViaHTTP' "$TEST_FILE"; then
    add_score 0.05 "Still uses fetchViaHTTP"
else
    add_fail 0.05 "Lost fetchViaHTTP usage"
fi

# [pr_diff] (0.05): Test sends concurrent requests with req-id headers
if grep -q 'req-id' "$TEST_FILE" && grep -q 'Promise.all' "$TEST_FILE"; then
    add_score 0.05 "Concurrent requests with req-id preserved"
else
    add_fail 0.05 "Lost concurrent request pattern"
fi

# ============================================================
# CONFIG-DERIVED (0.10)
# ============================================================

# [agent_config] (0.05): "Prefer real fixture directories over inline files" — AGENTS.md:207-217 @ 9f181bd
# Accepts __dirname, path.join, path.resolve, import.meta.url, or absence of inline files: {}
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
if (/__dirname|import\\.meta|path\\.(join|resolve)/.test(code)) process.exit(0);
if (!/files\s*:\s*\{/.test(code)) process.exit(0);
process.exit(1);
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.05 "Uses fixture directory reference (per AGENTS.md)"
else
    add_fail 0.05 "Uses inline files object instead of fixture directory"
fi

# [agent_config] (0.05): No deprecated check() function — AGENTS.md:194-206 @ 9f181bd
if ! grep -qE '\bcheck\s*\(' "$TEST_FILE"; then
    add_score 0.05 "No deprecated check() function"
else
    add_fail 0.05 "Uses deprecated check() function"
fi

# ============================================================
# ANTI-STUB (0.05)
# ============================================================

# [pr_diff] (0.05): Test file has real test structure — not a hollow stub
node -e "
const fs = require('fs');
const code = fs.readFileSync('$TEST_FILE', 'utf8');
const meaningful = code.split('\\n').filter(l => l.trim() && !l.trim().startsWith('//')).length;
const hasDescribe = /\\bdescribe\\s*\\(/.test(code);
const hasIt = /\\b(it|test)\\s*[.(]/.test(code);
const hasFetchOrExpect = /fetchViaHTTP|\\bexpect\\s*\\(/.test(code);
if (meaningful >= 15 && hasDescribe && hasIt && hasFetchOrExpect) {
    console.log('Real test structure:', meaningful, 'meaningful lines');
    process.exit(0);
}
console.error('Stub detected');
process.exit(1);
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.05 "Test file has real test structure"
else
    add_fail 0.05 "Test file appears to be a stub"
fi

# ============================================================
# Final score
# ============================================================
echo ""
echo "=== Score: $SCORE / $TOTAL ==="
echo "$SCORE" > /logs/verifier/reward.txt

# Optional LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
