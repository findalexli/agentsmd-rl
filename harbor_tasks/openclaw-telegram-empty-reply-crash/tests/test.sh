#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[behavioral_paths]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15
WEIGHTS[config_boundary]=0.05

for key in behavioral behavioral_paths structural antistub config_boundary; do
    RESULTS[$key]=0
done

TARGET="extensions/telegram/src/bot/delivery.replies.ts"

# ---------- GATE ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: file exists"

# ---------- PRIMARY 1 (35%): Behavioral - whitespace filtering ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Must have logic that filters or guards against whitespace-only text
const hasTrimCheck = src.includes('.trim()') && (
    src.includes('.length > 0') || src.includes('.length !== 0') ||
    src.includes('.length >= 1') || src.includes('!== \"\"')
);
const hasFilterCall = src.includes('filter') && src.includes('trim');

if (!hasTrimCheck && !hasFilterCall) {
    console.log('BEHAVIORAL FAIL: no whitespace filtering logic found');
    process.exit(1);
}

console.log('BEHAVIORAL PASS: whitespace filter logic present');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): All three delivery paths covered ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

let pathsFixed = 0;

// Path 1: deliverTextReply - should filter chunks before sending
const idx1 = src.indexOf('deliverTextReply');
const idx2 = src.indexOf('sendPendingFollowUpText');
const idx3 = src.indexOf('sendTelegramVoiceFallbackText');

if (idx1 >= 0 && idx2 >= 0) {
    const section1 = src.substring(idx1, idx2);
    if (section1.includes('filter') || (section1.includes('trim') && section1.includes('length'))) {
        pathsFixed++;
    }
}

if (idx2 >= 0 && idx3 >= 0) {
    const section2 = src.substring(idx2, idx3);
    if (section2.includes('filter') || (section2.includes('trim') && section2.includes('length'))) {
        pathsFixed++;
    }
}

if (idx3 >= 0) {
    const section3 = src.substring(idx3);
    if (section3.includes('filter') || (section3.includes('trim') && section3.includes('length'))) {
        pathsFixed++;
    }
}

if (pathsFixed < 3) {
    console.log('BEHAVIORAL_PATHS FAIL: only ' + pathsFixed + '/3 delivery paths have filtering');
    process.exit(1);
}

console.log('BEHAVIORAL_PATHS PASS: all 3 delivery paths have empty filtering');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[behavioral_paths]=1
    echo "TEST behavioral_paths: PASS"
else
    echo "TEST behavioral_paths: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Should have a dedicated filter function or at least consistent filtering
const hasFunction = /function\s+\w*[Ff]ilter\w*[Ee]mpty\w*/.test(src) ||
                    /function\s+\w*[Ff]ilter\w*[Tt]ext\w*/.test(src);
const hasArrow = /const\s+\w*[Ff]ilter\w*\s*=/.test(src);

if (!hasFunction && !hasArrow) {
    const filterCount = (src.match(/\.filter\s*\(/g) || []).length;
    if (filterCount < 2) {
        console.log('STRUCTURAL FAIL: no reusable filter pattern');
        process.exit(1);
    }
}

console.log('STRUCTURAL PASS');
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const lines = src.split('\n').length;

const checks = [
    [lines > 80, 'file has substantial content (' + lines + ' lines)'],
    [src.includes('sendChunkedTelegramReplyText') || src.includes('sendTelegramText'), 'send function present'],
    [src.includes('DeliveryProgress') || src.includes('progress'), 'delivery progress tracking present'],
    [src.includes('trim'), 'trim logic present'],
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

# ---------- Config-derived test (0.05): "Extension code must import from plugin-sdk/*" ----------
# Source: CLAUDE.md line 16 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find extensions/telegram/src -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
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
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral_paths': ${WEIGHTS[behavioral_paths]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'behavioral_paths': ${RESULTS[behavioral_paths]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
for key in behavioral behavioral_paths structural antistub config_boundary; do
    echo "  $key (${WEIGHTS[$key]}): ${RESULTS[$key]}"
done
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
