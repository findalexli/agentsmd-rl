#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0

add() { SCORE=$(python3 -c "print($SCORE + $1)"); }
total() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

TARGET="src/js/builtins/ProcessObjectInternals.ts"
cd /workspace/bun

##############################################################################
# GATE: Source file must exist
##############################################################################
if [ ! -s "$TARGET" ]; then
    echo "GATE FAILED: $TARGET missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# Helper: extract _final function for behavioral testing
# Bun internal TS uses JSC intrinsics ($isPromise, .$call, etc.) and
# internal require() paths. We can't run the WHOLE file, but we CAN
# extract _final and run it in Node.js with polyfilled Bun globals.
##############################################################################
cat > /tmp/extract_final.js << 'EXTRACT_EOF'
const fs = require('fs');
const source = fs.readFileSync(process.argv[2], 'utf8');

// Find stream._final (or stream["_final"])
let idx = source.indexOf('._final');
if (idx < 0) idx = source.indexOf('["_final"]');
if (idx < 0) {
    console.log(JSON.stringify({ found: false }));
    process.exit(0);
}

// Find the opening 'function' keyword and param
const fnMatch = source.substring(idx).match(/_final['"]*\]?\s*=\s*(?:async\s+)?function\s*\((\w+)\)/);
if (!fnMatch) {
    console.log(JSON.stringify({ found: false }));
    process.exit(0);
}

const cbName = fnMatch[1];

// Find opening brace of function body
const fnStartInSlice = source.indexOf('{', idx + fnMatch.index);
if (fnStartInSlice < 0) {
    console.log(JSON.stringify({ found: false }));
    process.exit(0);
}

// Count braces to find matching close
let depth = 1;
let pos = fnStartInSlice + 1;
while (depth > 0 && pos < source.length) {
    if (source[pos] === '{') depth++;
    else if (source[pos] === '}') depth--;
    pos++;
}
const body = source.substring(fnStartInSlice + 1, pos - 1);
const isAsync = /async\s+function/.test(source.substring(idx, fnStartInSlice));

// Also extract any const/let/var declarations between getStdioWriteStream and _final
// to capture closure variables like kFastPath
const funcStartIdx = source.lastIndexOf('getStdioWriteStream', idx);
const preambleRegion = funcStartIdx >= 0 ? source.substring(funcStartIdx, idx) : '';
const constDecls = [];
const declRegex = /(?:const|let|var)\s+(\w+)\s*=\s*([^;]+);/g;
let dm;
while ((dm = declRegex.exec(preambleRegion)) !== null) {
    constDecls.push({ name: dm[1], init: dm[2].trim() });
}

console.log(JSON.stringify({ found: true, cbName, body, isAsync, constDecls }));
EXTRACT_EOF

node /tmp/extract_final.js "$TARGET" > /tmp/extract_result.json 2>/dev/null
FINAL_FOUND=$(python3 -c "import json; d=json.load(open('/tmp/extract_result.json')); print('yes' if d.get('found') else 'no')" 2>/dev/null || echo "no")

##############################################################################
# BEHAVIORAL F2P 1 (0.30): _final sync flush → cb(null) called
# The core bug: without _final, .end() fires callback before flush completes.
# A correct _final must call sink.flush() and then cb(null) on sync success.
##############################################################################
# [pr_diff] (0.30): _final calls flush synchronously and invokes cb(null)
total 0.30
if [ "$FINAL_FOUND" = "yes" ]; then
cat > /tmp/test_sync_flush.js << 'TESTEOF'
const data = JSON.parse(require('fs').readFileSync('/tmp/extract_result.json','utf8'));
const { cbName, body, constDecls } = data;

// Polyfill Bun globals
globalThis.$isPromise = (x) => x != null && typeof x === 'object' && typeof x.then === 'function';
globalThis.$isCallable = (x) => typeof x === 'function';
globalThis.$isObject = (x) => x != null && typeof x === 'object';

// Mock sink with synchronous flush
let flushCalled = false;
const syncSink = {
    flush() { flushCalled = true; return undefined; },
    write() { return true; },
    close() {},
    ref() {}, unref() {}
};

// Proxy this: any property (including Symbols) returns syncSink
// This makes _final work regardless of HOW it accesses the sink
const thisObj = new Proxy({}, {
    get(t, p) {
        if (p === 'constructor') return Object;
        if (p === Symbol.toPrimitive || p === Symbol.toStringTag) return undefined;
        return syncSink;
    }
});

// Build closure variables from preamble
let closureSetup = '';
for (const d of constDecls) {
    // Mock require() calls to return objects with symbol-like values
    if (d.init.includes('require(')) {
        closureSetup += `var ${d.name} = Symbol('${d.name}');\n`;
    } else {
        closureSetup += `var ${d.name} = undefined;\n`;
    }
}

let cbResult = 'NOT_CALLED';
try {
    const fullBody = closureSetup + body;
    const fn = eval('(function(' + cbName + ') {' + fullBody + '})');
    fn.call(thisObj, (err) => {
        cbResult = err === null ? 'SUCCESS' : (err === undefined ? 'SUCCESS_UNDEF' : 'ERROR');
    });
} catch(e) {
    cbResult = 'EXEC_ERROR: ' + e.message;
}

// Allow microtasks to settle
setTimeout(() => {
    if (flushCalled && (cbResult === 'SUCCESS' || cbResult === 'SUCCESS_UNDEF')) {
        console.log('PASS');
    } else {
        console.log('FAIL: flush=' + flushCalled + ' cb=' + cbResult);
    }
}, 200);
TESTEOF
RESULT=$(timeout 10 node /tmp/test_sync_flush.js 2>/dev/null | head -1)
else
    RESULT="FAIL: no _final found"
fi

if [ "$RESULT" = "PASS" ]; then
    add 0.30
    echo "PASS [0.30]: _final calls sync flush and cb(null)"
else
    echo "FAIL [0.30]: sync flush behavioral test: $RESULT"
fi

##############################################################################
# BEHAVIORAL F2P 2 (0.20): _final async flush → cb(null) after Promise resolves
# If flush() returns a Promise (data still in pipe buffer), _final must wait
# for resolution before calling cb. Without this, async data is truncated.
##############################################################################
# [pr_diff] (0.20): _final handles async flush (Promise case) correctly
total 0.20
if [ "$FINAL_FOUND" = "yes" ]; then
cat > /tmp/test_async_flush.js << 'TESTEOF'
const data = JSON.parse(require('fs').readFileSync('/tmp/extract_result.json','utf8'));
const { cbName, body, constDecls } = data;

globalThis.$isPromise = (x) => x != null && typeof x === 'object' && typeof x.then === 'function';
globalThis.$isCallable = (x) => typeof x === 'function';
globalThis.$isObject = (x) => x != null && typeof x === 'object';

// Mock sink with ASYNC flush (returns Promise)
let flushCalled = false;
let resolveFlush;
const flushPromise = new Promise((resolve) => { resolveFlush = resolve; });
const asyncSink = {
    flush() { flushCalled = true; return flushPromise; },
    write() { return true; },
    close() {}, ref() {}, unref() {}
};

const thisObj = new Proxy({}, {
    get(t, p) {
        if (p === 'constructor') return Object;
        if (p === Symbol.toPrimitive || p === Symbol.toStringTag) return undefined;
        return asyncSink;
    }
});

let closureSetup = '';
for (const d of constDecls) {
    if (d.init.includes('require(')) {
        closureSetup += `var ${d.name} = Symbol('${d.name}');\n`;
    } else {
        closureSetup += `var ${d.name} = undefined;\n`;
    }
}

let cbResult = 'NOT_CALLED';
let cbCalledBeforeResolve = false;
try {
    const fullBody = closureSetup + body;
    const fn = eval('(function(' + cbName + ') {' + fullBody + '})');
    fn.call(thisObj, (err) => {
        cbResult = err === null ? 'SUCCESS' : (err === undefined ? 'SUCCESS_UNDEF' : 'ERROR');
    });
} catch(e) {
    cbResult = 'EXEC_ERROR: ' + e.message;
}

// Check cb was NOT called yet (flush Promise hasn't resolved)
setTimeout(() => {
    if (cbResult !== 'NOT_CALLED') {
        cbCalledBeforeResolve = true;
    }
    // Now resolve the flush Promise
    resolveFlush();

    // Give microtasks time to run
    setTimeout(() => {
        if (!cbCalledBeforeResolve && (cbResult === 'SUCCESS' || cbResult === 'SUCCESS_UNDEF')) {
            console.log('PASS');
        } else if (cbCalledBeforeResolve) {
            console.log('FAIL: cb called before flush Promise resolved');
        } else {
            console.log('FAIL: cb=' + cbResult);
        }
    }, 200);
}, 50);
TESTEOF
RESULT=$(timeout 10 node /tmp/test_async_flush.js 2>/dev/null | head -1)
else
    RESULT="FAIL: no _final found"
fi

if [ "$RESULT" = "PASS" ]; then
    add 0.20
    echo "PASS [0.20]: _final waits for async flush before calling cb"
else
    echo "FAIL [0.20]: async flush behavioral test: $RESULT"
fi

##############################################################################
# BEHAVIORAL F2P 3 (0.15): _final error in flush → cb(err)
# If flush() throws, _final must propagate the error via cb(err), not crash.
##############################################################################
# [pr_diff] (0.15): _final propagates flush errors to callback
total 0.15
if [ "$FINAL_FOUND" = "yes" ]; then
cat > /tmp/test_error_flush.js << 'TESTEOF'
const data = JSON.parse(require('fs').readFileSync('/tmp/extract_result.json','utf8'));
const { cbName, body, constDecls } = data;

globalThis.$isPromise = (x) => x != null && typeof x === 'object' && typeof x.then === 'function';
globalThis.$isCallable = (x) => typeof x === 'function';
globalThis.$isObject = (x) => x != null && typeof x === 'object';

// Mock sink that throws on flush
const errorSink = {
    flush() { throw new Error('pipe broken'); },
    write() { return true; },
    close() {}, ref() {}, unref() {}
};

const thisObj = new Proxy({}, {
    get(t, p) {
        if (p === 'constructor') return Object;
        if (p === Symbol.toPrimitive || p === Symbol.toStringTag) return undefined;
        return errorSink;
    }
});

let closureSetup = '';
for (const d of constDecls) {
    if (d.init.includes('require(')) {
        closureSetup += `var ${d.name} = Symbol('${d.name}');\n`;
    } else {
        closureSetup += `var ${d.name} = undefined;\n`;
    }
}

let cbResult = 'NOT_CALLED';
let cbError = null;
let uncaughtError = false;

process.on('uncaughtException', () => { uncaughtError = true; });

try {
    const fullBody = closureSetup + body;
    const fn = eval('(function(' + cbName + ') {' + fullBody + '})');
    fn.call(thisObj, (err) => {
        if (err && err.message === 'pipe broken') {
            cbResult = 'ERROR_CAUGHT';
            cbError = err;
        } else if (err) {
            cbResult = 'WRONG_ERROR';
        } else {
            cbResult = 'NO_ERROR';
        }
    });
} catch(e) {
    cbResult = 'UNCAUGHT: ' + e.message;
}

setTimeout(() => {
    if (cbResult === 'ERROR_CAUGHT' && !uncaughtError) {
        console.log('PASS');
    } else {
        console.log('FAIL: cb=' + cbResult + ' uncaught=' + uncaughtError);
    }
}, 200);
TESTEOF
RESULT=$(timeout 10 node /tmp/test_error_flush.js 2>/dev/null | head -1)
else
    RESULT="FAIL: no _final found"
fi

if [ "$RESULT" = "PASS" ]; then
    add 0.15
    echo "PASS [0.15]: _final catches flush error and calls cb(err)"
else
    echo "FAIL [0.15]: error handling behavioral test: $RESULT"
fi

##############################################################################
# REGRESSION (0.10): Existing stream setup must not be broken
# _destroy, _isStdio, destroySoon are core parts of the existing stream —
# a correct fix adds _final without removing these.
##############################################################################
# [pr_diff] (0.10): Existing _destroy, _isStdio, and destroySoon preserved
total 0.10
REGRESSION=$(python3 -c "
code = open('$TARGET').read()
has_destroy = '_destroy' in code
has_isStdio = '_isStdio' in code
has_destroySoon = 'destroySoon' in code
print('PASS' if has_destroy and has_isStdio and has_destroySoon else 'FAIL')
")
if [ "$REGRESSION" = "PASS" ]; then
    add 0.10
    echo "PASS [0.10]: Existing _destroy, _isStdio, destroySoon preserved"
else
    echo "FAIL [0.10]: Existing stream setup was broken"
fi

##############################################################################
# STRUCTURAL: Anti-stub (0.10)
# _final must have substantive logic, not empty body or comments-only
##############################################################################
# [pr_diff] (0.10): _final has real executable logic (anti-stub)
total 0.10
if [ "$FINAL_FOUND" = "yes" ]; then
ANTI_STUB=$(python3 -c "
import json, re
data = json.load(open('/tmp/extract_result.json'))
body = data.get('body', '')
lines = body.strip().split('\n')
real_lines = []
for l in lines:
    stripped = l.strip()
    if stripped and not stripped.startswith('//') and not stripped.startswith('*') and not stripped.startswith('/*'):
        real_lines.append(stripped)
has_calls = any('(' in l and ')' in l for l in real_lines)
print('PASS' if len(real_lines) >= 5 and has_calls else 'FAIL')
")
else
    ANTI_STUB="FAIL"
fi

if [ "$ANTI_STUB" = "PASS" ]; then
    add 0.10
    echo "PASS [0.10]: Anti-stub — _final has substantive logic"
else
    echo "FAIL [0.10]: _final appears to be a stub"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.15 total)
##############################################################################

# [agent_config] (0.05): No .call()/.apply() — must use .$call/.$apply
# per src/js/CLAUDE.md:56 "CRITICAL: Use .$call and .$apply, never .call or .apply"
total 0.05
if [ "$FINAL_FOUND" = "yes" ]; then
CALL_CHECK=$(python3 -c "
import json, re
data = json.load(open('/tmp/extract_result.json'))
body = data.get('body', '')
lines = body.split('\n')
code_lines = [l for l in lines if not l.strip().startswith('//')]
code = '\n'.join(code_lines)
bad_call = bool(re.search(r'(?<!\\\$)\.call\s*\(', code))
bad_apply = bool(re.search(r'(?<!\\\$)\.apply\s*\(', code))
print('FAIL' if bad_call or bad_apply else 'PASS')
")
else
    CALL_CHECK="PASS"  # No _final means other checks fail, this is not the blocker
fi

if [ "$CALL_CHECK" = "PASS" ]; then
    add 0.05
    echo "PASS [0.05]: No .call/.apply in _final — src/js/CLAUDE.md:56"
else
    echo "FAIL [0.05]: Uses .call/.apply instead of .\$call/.\$apply"
fi

# [agent_config] (0.05): require() must use string literals only
# per src/js/CLAUDE.md:103 "String literal require() only"
total 0.05
REQUIRE_CHECK=$(python3 -c "
import re
code = open('$TARGET').read()
requires = re.findall(r'require\s*\(([^)]+)\)', code)
all_literal = all(r.strip().startswith('\"') or r.strip().startswith(\"'\") for r in requires)
print('PASS' if all_literal and len(requires) > 0 else 'FAIL')
")
if [ "$REQUIRE_CHECK" = "PASS" ]; then
    add 0.05
    echo "PASS [0.05]: All require() use string literals — src/js/CLAUDE.md:103"
else
    echo "FAIL [0.05]: Non-literal require() found"
fi

# [agent_config] (0.05): Use JSC intrinsics ($-prefixed) for type checks
# per src/js/CLAUDE.md:105 "Use JSC intrinsics for performance"
total 0.05
if [ "$FINAL_FOUND" = "yes" ]; then
INTRINSIC_CHECK=$(python3 -c "
import json
data = json.load(open('/tmp/extract_result.json'))
body = data.get('body', '')
lines = body.split('\n')
code_lines = [l for l in lines if not l.strip().startswith('//')]
code = '\n'.join(code_lines)
has_instanceof_promise = 'instanceof Promise' in code
print('FAIL' if has_instanceof_promise else 'PASS')
")
else
    INTRINSIC_CHECK="PASS"
fi

if [ "$INTRINSIC_CHECK" = "PASS" ]; then
    add 0.05
    echo "PASS [0.05]: Uses JSC intrinsics, not userland APIs — src/js/CLAUDE.md:105"
else
    echo "FAIL [0.05]: Uses instanceof Promise instead of \$isPromise"
fi

##############################################################################
# Final score
##############################################################################

REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Total: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Compute category breakdowns
BEHAVIORAL=$(python3 -c "print(round(min($SCORE, 0.65), 4))")
REGRESSION_SCORE=$(python3 -c "s=$SCORE; print(round(max(min(s - 0.65, 0.10), 0.0), 4))")
STRUCT=$(python3 -c "s=$SCORE; print(round(max(min(s - 0.75, 0.10), 0.0), 4))")
CONFIG=$(python3 -c "s=$SCORE; print(round(max(min(s - 0.85, 0.15), 0.0), 4))")

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION_SCORE, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
