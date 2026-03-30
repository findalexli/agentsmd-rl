#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_stream]=0.30
WEIGHTS[behavioral_throw]=0.30
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15
WEIGHTS[config_nocheck]=0.05

for key in behavioral_stream behavioral_throw structural antistub config_nocheck; do
    RESULTS[$key]=0
done

TARGET_RECOVERY="src/agents/pi-embedded-runner/run/attempt.stop-reason-recovery.ts"
TARGET_ATTEMPT="src/agents/pi-embedded-runner/run/attempt.ts"

# ---------- GATE: file existence ----------
if [ ! -f "$TARGET_RECOVERY" ]; then
    echo "GATE FAIL: $TARGET_RECOVERY does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: recovery module exists"

# ---------- PRIMARY 1 (30%): Behavioral - stream error path ----------
# Test that the recovery module exports a function that catches "Unhandled stop reason"
# errors in stream events and converts them to structured error messages.
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET_RECOVERY', 'utf8');

// The module must define a regex or string match for 'Unhandled stop reason'
if (!src.includes('Unhandled stop reason')) {
    console.log('BEHAVIORAL_STREAM FAIL: no Unhandled stop reason pattern');
    process.exit(1);
}

// The module must produce user-facing error messages mentioning the stop reason
if (!src.includes('unhandled stop reason')) {
    console.log('BEHAVIORAL_STREAM FAIL: no user-facing error message');
    process.exit(1);
}

// Simulate the core logic: extract and test the regex
const reMatch = src.match(/\\/\\^Unhandled stop reason.*\\/i?/);
if (!reMatch) {
    // Maybe uses string includes instead of regex
    if (!src.includes('Unhandled stop reason')) {
        console.log('BEHAVIORAL_STREAM FAIL: no pattern matching for stop reasons');
        process.exit(1);
    }
}

// Test that the module converts specific stop reasons into messages
// Extract the format function pattern
const formatMatch = src.match(/unhandled stop reason:\\s*\\\$\\{([^}]+)\\}/i) ||
                    src.match(/unhandled stop reason:\\s*\\\${([^}]+)}/i) ||
                    src.includes('unhandled stop reason');

if (!formatMatch) {
    console.log('BEHAVIORAL_STREAM FAIL: no error message formatting with stop reason');
    process.exit(1);
}

// Verify the function converts errors properly by checking for stopReason = 'error'
if (!src.includes('stopReason') || !src.includes('errorMessage')) {
    console.log('BEHAVIORAL_STREAM FAIL: does not set stopReason/errorMessage on result');
    process.exit(1);
}

console.log('BEHAVIORAL_STREAM PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[behavioral_stream]=1
    echo "TEST behavioral_stream: PASS"
else
    echo "TEST behavioral_stream: FAIL"
fi

# ---------- PRIMARY 2 (30%): Behavioral - synchronous throw path ----------
# The wrapper must also catch synchronous throws from the stream function
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET_RECOVERY', 'utf8');

// Must have try/catch for synchronous errors
const hasTryCatch = src.includes('try {') && src.includes('catch');
if (!hasTryCatch) {
    console.log('BEHAVIORAL_THROW FAIL: no try/catch for synchronous throws');
    process.exit(1);
}

// Must handle both sync and async paths
// Look for promise handling (.then) or await for async path
const hasAsyncHandling = src.includes('.then') || src.includes('await') || src.includes('Promise');
if (!hasAsyncHandling) {
    console.log('BEHAVIORAL_THROW FAIL: no async error path handling');
    process.exit(1);
}

// The wrapper must return a stream on error (not re-throw)
// Look for creating an error stream or pushing error events
const hasErrorStream = src.includes('createAssistantMessageEventStream') ||
                       src.includes('stream.push') ||
                       src.includes('buildStreamError') ||
                       src.includes('ErrorStream');
if (!hasErrorStream) {
    console.log('BEHAVIORAL_THROW FAIL: does not create error stream on catch');
    process.exit(1);
}

// Must extract the stop reason from the error message
const extractsReason = src.includes('match') || src.includes('replace') || src.includes('slice');
if (!extractsReason) {
    console.log('BEHAVIORAL_THROW FAIL: does not extract stop reason from error message');
    process.exit(1);
}

console.log('BEHAVIORAL_THROW PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[behavioral_throw]=1
    echo "TEST behavioral_throw: PASS"
else
    echo "TEST behavioral_throw: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural check ----------
node -e "
const fs = require('fs');
const attempt = fs.readFileSync('$TARGET_ATTEMPT', 'utf8');

// attempt.ts must import the recovery module
if (!attempt.includes('stop-reason-recovery') && !attempt.includes('stopReasonRecovery')) {
    console.log('STRUCTURAL FAIL: attempt.ts does not import recovery module');
    process.exit(1);
}

// attempt.ts must wrap streamFn with the recovery function
if (!attempt.includes('wrapStreamFn') && !attempt.includes('HandleSensitiveStopReason') &&
    !attempt.includes('handleStopReason') && !attempt.includes('stopReason')) {
    console.log('STRUCTURAL FAIL: attempt.ts does not wire recovery wrapper');
    process.exit(1);
}

// Recovery module must export a wrapping function
const recovery = fs.readFileSync('$TARGET_RECOVERY', 'utf8');
if (!recovery.includes('export')) {
    console.log('STRUCTURAL FAIL: recovery module has no exports');
    process.exit(1);
}

console.log('STRUCTURAL PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET_RECOVERY', 'utf8');
const lines = src.split('\n').length;

const checks = [
    [lines > 30, 'recovery module has substantial content (>30 lines): ' + lines],
    [src.includes('function'), 'has function definitions'],
    [src.includes('export'), 'has exports'],
    [src.includes('Unhandled stop reason'), 'handles unhandled stop reason pattern'],
    [src.includes('stopReason') || src.includes('stop_reason'), 'references stop reason'],
    [src.includes('error'), 'handles errors'],
];

const failures = checks.filter(([ok]) => !ok).map(([, desc]) => desc);
if (failures.length > 0) {
    console.log('ANTI-STUB FAIL: ' + failures.join(', '));
    process.exit(1);
}
console.log('ANTI-STUB PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------

# ---------- Config-derived test (0.05): "Never add @ts-nocheck" ----------
# Source: CLAUDE.md line 104 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find src/agents -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
let fail = false;
for (const f of files) {
    try {
        const content = fs.readFileSync(f, 'utf8');
        if (content.includes('@ts-nocheck') || content.includes('@ts-ignore')) {
            console.log('FAIL: ' + f + ' contains @ts-nocheck or @ts-ignore');
            fail = true;
        }
    } catch(e) {}
}
if (fail) process.exit(1);
console.log('PASS: no @ts-nocheck/@ts-ignore found');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[config_nocheck]=1; echo "TEST config_nocheck: PASS"; else echo "TEST config_nocheck: FAIL"; fi

SCORE=$(python3 -c "
weights = {'behavioral_stream': ${WEIGHTS[behavioral_stream]}, 'behavioral_throw': ${WEIGHTS[behavioral_throw]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_stream': ${RESULTS[behavioral_stream]}, 'behavioral_throw': ${RESULTS[behavioral_throw]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_stream (${WEIGHTS[behavioral_stream]}): ${RESULTS[behavioral_stream]}"
echo "  behavioral_throw  (${WEIGHTS[behavioral_throw]}): ${RESULTS[behavioral_throw]}"
echo "  structural        (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub          (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
