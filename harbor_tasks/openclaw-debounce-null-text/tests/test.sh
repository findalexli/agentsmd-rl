#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_combine]=0.35
WEIGHTS[behavioral_enqueue]=0.30
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.15
WEIGHTS[config_boundary]=0.05

for key in behavioral_combine behavioral_enqueue structural antistub config_boundary; do
    RESULTS[$key]=0
done

TARGET="extensions/bluebubbles/src/monitor-debounce.ts"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (35%): combineDebounceEntries guards null text ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

const fnStart = src.indexOf('combineDebounceEntries');
if (fnStart < 0) {
    console.log('FAIL: combineDebounceEntries not found');
    process.exit(1);
}

const fnBody = src.substring(fnStart, src.indexOf('\nfunction ', fnStart + 10) || src.length);

// Must guard against null text before .trim()
const hasGuard = fnBody.includes('typeof') || fnBody.includes('normalizeDebounce') ||
    fnBody.includes('|| \"\"') || fnBody.includes('?? \"\"') ||
    fnBody.includes('String(') || fnBody.includes('normalize');

if (!hasGuard && fnBody.includes('.text.trim()')) {
    console.log('FAIL: .text.trim() without null guard');
    process.exit(1);
}

if (!fnBody.includes('trim()')) {
    console.log('FAIL: no trim call');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_combine]=1; echo "TEST behavioral_combine: PASS"; else echo "TEST behavioral_combine: FAIL"; fi

# ---------- PRIMARY 2 (30%): Enqueue boundary sanitization ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

const hasSanitize = src.includes('sanitize') || src.includes('Sanitize');
const hasNormalize = src.includes('normalize') || src.includes('Normalize');
const hasEnqueueGuard = src.includes('enqueue') && (
    src.includes('typeof') || src.includes('|| \"\"') || src.includes('?? \"\"')
);
const hasWrapperEnqueue = /enqueue:\s*async\s*\(item\)/.test(src);

if (!hasSanitize && !hasNormalize && !hasEnqueueGuard && !hasWrapperEnqueue) {
    console.log('FAIL: no sanitization at enqueue boundary');
    process.exit(1);
}
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_enqueue]=1; echo "TEST behavioral_enqueue: PASS"; else echo "TEST behavioral_enqueue: FAIL"; fi

# ---------- SUPPLEMENTARY (15%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const hasNormFn = /function\s+(normalize|sanitize)\w*/i.test(src);
if (!hasNormFn) {
    if (src.includes('typeof') || src.includes('|| \"\"') || src.includes('?? \"\"')) {
        console.log('PASS');
    } else {
        process.exit(1);
    }
} else {
    console.log('PASS');
}
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural]=1; echo "TEST structural: PASS"; else echo "TEST structural: FAIL"; fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const checks = [
    [src.split('\n').length > 40, 'substantial content'],
    [src.includes('combineDebounceEntries'), 'combine function'],
    [src.includes('BlueBubblesDebouncer'), 'debouncer type'],
    [src.includes('enqueue'), 'enqueue method'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "Extension code must import from plugin-sdk/*" ----------
# Source: CLAUDE.md line 16 @ 756df2e9554da097679e6c4d3c75deff025098b9
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find extensions/bluebubbles/src -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
let fail = false;
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    const lines = content.split('\\n');
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (/^import .* from ['\"]\.\.\/\.\.\/\.\.\/src\//.test(line)) {
            console.log('FAIL: ' + f + ':' + (i+1) + ' imports core internals: ' + line.trim());
            fail = true;
        }
    }
}
if (fail) process.exit(1);
console.log('PASS: no cross-boundary imports');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[config_boundary]=1; echo "TEST config_boundary: PASS"; else echo "TEST config_boundary: FAIL"; fi

SCORE=$(python3 -c "
w = {'behavioral_combine': ${WEIGHTS[behavioral_combine]}, 'config_boundary': ${WEIGHTS[config_boundary]}, 'behavioral_enqueue': ${WEIGHTS[behavioral_enqueue]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_combine': ${RESULTS[behavioral_combine]}, 'config_boundary': ${RESULTS[config_boundary]}, 'behavioral_enqueue': ${RESULTS[behavioral_enqueue]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
