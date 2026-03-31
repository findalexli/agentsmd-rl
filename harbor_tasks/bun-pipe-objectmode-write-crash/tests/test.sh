#!/usr/bin/env bash
set +e

REPO="/workspace/bun"
TARGET="$REPO/src/js/internal/streams/readable.ts"
REWARD=0

# --- Install Node.js for behavioral testing ---
if ! command -v node &>/dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz 2>/dev/null \
        | tar -xJ -C /usr/local --strip-components=1 2>/dev/null
fi
HAS_NODE=0
command -v node &>/dev/null && HAS_NODE=1

# --- Helpers ---
pass() { REWARD=$(python3 -c "print($REWARD + $1)"); echo "PASS ($1): $2"; }
fail() { echo "FAIL ($1): $2"; }

# =============================================================================
# GATE: File exists and Readable.prototype.pipe is present
# =============================================================================
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: target file not found"
    echo "0.0" > "/logs/verifier/reward.txt"
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > "/logs/verifier/reward.json"
    exit 0
fi
if ! python3 -c "
import sys
c = open('$TARGET').read()
if 'Readable.prototype.pipe' not in c:
    sys.exit(1)
# Basic brace balance
if abs(c.count('{') - c.count('}')) > 5:
    sys.exit(1)
"; then
    echo "GATE FAIL: structural integrity"
    echo "0.0" > "/logs/verifier/reward.txt"
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > "/logs/verifier/reward.json"
    exit 0
fi
echo "GATE PASS"

# =============================================================================
# FAIL-TO-PASS BEHAVIORAL (0.35): Write error is caught (not thrown to caller)
# Extract ondata function, strip $debug, execute with mock dest that throws
# =============================================================================
# [pr_diff] (0.35): dest.write() errors in ondata must be caught, not thrown
F2P_CATCH=0
if [ "$HAS_NODE" = "1" ]; then
    cat > /tmp/test_catch.js << 'JSEOF'
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

// Extract ondata function using balanced brace matching (not regex)
const ondataIdx = content.indexOf('function ondata');
if (ondataIdx === -1) { console.error('No ondata function found'); process.exit(1); }
const openBrace = content.indexOf('{', ondataIdx);
if (openBrace === -1) process.exit(1);
let depth = 1, i = openBrace + 1;
while (depth > 0 && i < content.length) {
    if (content[i] === '{') depth++;
    else if (content[i] === '}') depth--;
    i++;
}
let funcSrc = content.substring(ondataIdx, i);

// Strip Bun-specific $debug lines (macros that don't exist in Node)
funcSrc = funcSrc.split('\n').filter(l => !l.includes('$debug')).join('\n');

// Mock dest that throws on write (simulating object→byte mode mismatch)
let destroyed = false;
let destroyErr = null;
let emittedErrors = [];

const dest = {
    write(chunk) { throw new TypeError('ERR_INVALID_ARG_TYPE: expected string or Buffer'); },
    destroy(err) { destroyed = true; destroyErr = err; },
    emit(event, ...args) { if (event === 'error') emittedErrors.push(args[0]); }
};
let paused = false;
function pause() { paused = true; }

// Evaluate the extracted ondata function
try { eval(funcSrc); } catch(e) {
    console.error('Failed to eval ondata:', e.message);
    process.exit(1);
}

// Test: call ondata with an object chunk (triggers the TypeError)
let threwUncaught = false;
try {
    ondata({ hello: 'world' });
} catch(e) {
    threwUncaught = true;
}

if (threwUncaught) {
    console.error('FAIL: write error escaped ondata (not caught)');
    process.exit(1);
}

// Error must have been forwarded to dest somehow (destroy OR error event)
if (!destroyed && emittedErrors.length === 0) {
    console.error('FAIL: error not forwarded to dest');
    process.exit(1);
}

console.log('PASS: write error caught and forwarded');
JSEOF
    node /tmp/test_catch.js "$TARGET" 2>/dev/null && F2P_CATCH=1
fi
if [ "$F2P_CATCH" = "1" ]; then pass 0.35 "[pr_diff] F2P: write error caught and forwarded to dest"; else fail 0.35 "[pr_diff] F2P: write error caught and forwarded to dest"; fi

# =============================================================================
# FAIL-TO-PASS BEHAVIORAL (0.15): Error is specifically propagated (not swallowed)
# The caught error object must reach dest.destroy() or dest.emit('error')
# =============================================================================
# [pr_diff] (0.15): caught error object is the same TypeError that write() threw
F2P_PROPAGATE=0
if [ "$HAS_NODE" = "1" ]; then
    cat > /tmp/test_propagate.js << 'JSEOF'
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

const ondataIdx = content.indexOf('function ondata');
if (ondataIdx === -1) process.exit(1);
const openBrace = content.indexOf('{', ondataIdx);
let depth = 1, i = openBrace + 1;
while (depth > 0 && i < content.length) {
    if (content[i] === '{') depth++;
    else if (content[i] === '}') depth--;
    i++;
}
let funcSrc = content.substring(ondataIdx, i);
funcSrc = funcSrc.split('\n').filter(l => !l.includes('$debug')).join('\n');

// Track exact error object
const writeError = new TypeError('ERR_INVALID_ARG_TYPE');
let destroyErr = null;
let emittedErr = null;

const dest = {
    write(chunk) { throw writeError; },
    destroy(err) { destroyErr = err; },
    emit(event, ...args) { if (event === 'error') emittedErr = args[0]; }
};
function pause() {}

eval(funcSrc);
try { ondata({ x: 1 }); } catch(e) { process.exit(1); }

// The SAME error object should have been forwarded (not swallowed or replaced)
const forwarded = destroyErr || emittedErr;
if (forwarded !== writeError) {
    console.error('FAIL: error was swallowed or replaced');
    process.exit(1);
}
console.log('PASS: exact error object propagated');
JSEOF
    node /tmp/test_propagate.js "$TARGET" 2>/dev/null && F2P_PROPAGATE=1
fi
if [ "$F2P_PROPAGATE" = "1" ]; then pass 0.15 "[pr_diff] F2P: exact error object propagated to dest"; else fail 0.15 "[pr_diff] F2P: exact error object propagated to dest"; fi

# =============================================================================
# PASS-TO-PASS BEHAVIORAL (0.10): Normal writes still work after the fix
# =============================================================================
# [pr_diff] (0.10): non-throwing dest.write() still passes data through
P2P_NORMAL=0
if [ "$HAS_NODE" = "1" ]; then
    cat > /tmp/test_normal.js << 'JSEOF'
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

const ondataIdx = content.indexOf('function ondata');
if (ondataIdx === -1) process.exit(1);
const openBrace = content.indexOf('{', ondataIdx);
let depth = 1, i = openBrace + 1;
while (depth > 0 && i < content.length) {
    if (content[i] === '{') depth++;
    else if (content[i] === '}') depth--;
    i++;
}
let funcSrc = content.substring(ondataIdx, i);
funcSrc = funcSrc.split('\n').filter(l => !l.includes('$debug')).join('\n');

let written = null;
let destroyed = false;
const dest = {
    write(chunk) { written = chunk; return true; },
    destroy(err) { destroyed = true; },
    emit() {}
};
let paused = false;
function pause() { paused = true; }

eval(funcSrc);
ondata(Buffer.from('hello'));

if (written === null) { console.error('FAIL: write not called'); process.exit(1); }
if (destroyed) { console.error('FAIL: dest destroyed on valid write'); process.exit(1); }
if (paused) { console.error('FAIL: paused on true return'); process.exit(1); }
console.log('PASS: normal write works');
JSEOF
    node /tmp/test_normal.js "$TARGET" 2>/dev/null && P2P_NORMAL=1
fi
if [ "$P2P_NORMAL" = "1" ]; then pass 0.10 "[pr_diff] P2P: normal writes still work"; else fail 0.10 "[pr_diff] P2P: normal writes still work"; fi

# =============================================================================
# PASS-TO-PASS BEHAVIORAL (0.10): Backpressure still triggers pause
# =============================================================================
# [pr_diff] (0.10): dest.write() returning false still causes pause()
P2P_BACKPRESSURE=0
if [ "$HAS_NODE" = "1" ]; then
    cat > /tmp/test_backpressure.js << 'JSEOF'
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

const ondataIdx = content.indexOf('function ondata');
if (ondataIdx === -1) process.exit(1);
const openBrace = content.indexOf('{', ondataIdx);
let depth = 1, i = openBrace + 1;
while (depth > 0 && i < content.length) {
    if (content[i] === '{') depth++;
    else if (content[i] === '}') depth--;
    i++;
}
let funcSrc = content.substring(ondataIdx, i);
funcSrc = funcSrc.split('\n').filter(l => !l.includes('$debug')).join('\n');

let destroyed = false;
const dest = {
    write(chunk) { return false; },  // buffer full
    destroy(err) { destroyed = true; },
    emit() {}
};
let paused = false;
function pause() { paused = true; }

eval(funcSrc);
ondata(Buffer.from('data'));

if (!paused) { console.error('FAIL: pause not called on false write return'); process.exit(1); }
if (destroyed) { console.error('FAIL: dest destroyed on non-throwing write'); process.exit(1); }
console.log('PASS: backpressure pause works');
JSEOF
    node /tmp/test_backpressure.js "$TARGET" 2>/dev/null && P2P_BACKPRESSURE=1
fi
if [ "$P2P_BACKPRESSURE" = "1" ]; then pass 0.10 "[pr_diff] P2P: backpressure pause still works"; else fail 0.10 "[pr_diff] P2P: backpressure pause still works"; fi

# =============================================================================
# PASS-TO-PASS STRUCTURAL (0.05): Core event wiring preserved in pipe()
# =============================================================================
# [repo_tests] (0.05): pipe() still sets up data/drain/end listeners and returns dest
P2P_EVENTS=0
python3 -c "
import sys
c = open('$TARGET').read()
# These are fundamental to pipe() — must exist somewhere in the pipe method
required = ['on(', 'data', 'drain', 'end', 'return dest']
missing = [r for r in required if r not in c]
if missing:
    print(f'Missing: {missing}')
    sys.exit(1)
" 2>/dev/null && P2P_EVENTS=1
if [ "$P2P_EVENTS" = "1" ]; then pass 0.05 "[repo_tests] P2P: core event wiring preserved"; else fail 0.05 "[repo_tests] P2P: core event wiring preserved"; fi

# =============================================================================
# ANTI-STUB (0.05): ondata function has real logic, not empty/trivial
# =============================================================================
# [pr_diff] (0.05): ondata body is non-trivial (>= 4 meaningful statements)
ANTI_STUB=0
if [ "$HAS_NODE" = "1" ]; then
    cat > /tmp/test_stub.js << 'JSEOF'
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

const ondataIdx = content.indexOf('function ondata');
if (ondataIdx === -1) process.exit(1);
const openBrace = content.indexOf('{', ondataIdx);
let depth = 1, i = openBrace + 1;
while (depth > 0 && i < content.length) {
    if (content[i] === '{') depth++;
    else if (content[i] === '}') depth--;
    i++;
}
const body = content.substring(openBrace + 1, i - 1);

// Count meaningful lines (not empty, not just comments, not just braces)
const meaningful = body.split('\n').filter(l => {
    const t = l.trim();
    return t && !t.startsWith('//') && !t.startsWith('*') && t !== '{' && t !== '}';
}).length;

if (meaningful < 4) {
    console.error('FAIL: ondata body too trivial (' + meaningful + ' lines)');
    process.exit(1);
}

// Must reference dest.write somewhere
if (!body.includes('dest.write') && !body.includes('write(chunk)')) {
    console.error('FAIL: no write call in ondata');
    process.exit(1);
}
console.log('PASS: ondata is non-trivial (' + meaningful + ' lines)');
JSEOF
    node /tmp/test_stub.js "$TARGET" 2>/dev/null && ANTI_STUB=1
fi
if [ "$ANTI_STUB" = "1" ]; then pass 0.05 "[pr_diff] anti-stub: ondata is non-trivial"; else fail 0.05 "[pr_diff] anti-stub: ondata is non-trivial"; fi

# =============================================================================
# CONFIG (0.10): Use .$call/.$apply, not .call/.apply
# =============================================================================
# [agent_config] (0.10): "Use .$call and .$apply, never .call or .apply" — src/js/CLAUDE.md:45-52 @ 2d4c2be
CONFIG_CALL=0
python3 -c "
import subprocess, sys, re
# Check git diff for prohibited .call()/.apply() usage
for diff_cmd in [['git','diff','HEAD'], ['git','diff','--cached'], ['git','diff','HEAD~1']]:
    result = subprocess.run(diff_cmd, capture_output=True, text=True, cwd='$REPO')
    if result.stdout.strip():
        added = [l[1:] for l in result.stdout.split('\n') if l.startswith('+') and not l.startswith('+++')]
        for line in added:
            s = line.strip()
            if s.startswith('//') or s.startswith('*'):
                continue
            # Match .call( or .apply( but NOT .$call( or .$apply(
            if re.search(r'(?<!\\\$)\.call\(', line) and '.\$call(' not in line:
                sys.exit(1)
            if re.search(r'(?<!\\\$)\.apply\(', line) and '.\$apply(' not in line:
                sys.exit(1)
        break
" 2>/dev/null && CONFIG_CALL=1
if [ "$CONFIG_CALL" = "1" ]; then pass 0.10 "[agent_config] no .call/.apply in new code — src/js/CLAUDE.md:45-52 @ 2d4c2be"; else fail 0.10 "[agent_config] no .call/.apply in new code"; fi

# =============================================================================
# RESULTS
# =============================================================================

echo ""
echo "=== Test Results ==="
FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $REWARD)):.4f}')")
echo "$FINAL" > "/logs/verifier/reward.txt"

BEHAVIORAL=$(python3 -c "print($F2P_CATCH * 0.35 + $F2P_PROPAGATE * 0.15 + $P2P_NORMAL * 0.10 + $P2P_BACKPRESSURE * 0.10)")
REGRESSION=$(python3 -c "print($P2P_EVENTS * 0.05)")
CONFIG=$(python3 -c "print($CONFIG_CALL * 0.10)")
STUB=$(python3 -c "print($ANTI_STUB * 0.05)")

echo "{\"reward\": $FINAL, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > "/logs/verifier/reward.json"

echo "Final reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
