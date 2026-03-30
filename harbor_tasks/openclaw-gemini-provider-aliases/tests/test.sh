#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_alias]=0.30
WEIGHTS[behavioral_prefix]=0.30
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15
WEIGHTS[config_boundary]=0.05

for key in behavioral_alias behavioral_prefix structural antistub config_boundary; do
    RESULTS[$key]=0
done

TARGET_INDEX="extensions/google/index.ts"
TARGET_MODELS="extensions/google/provider-models.ts"

if [ ! -f "$TARGET_INDEX" ] || [ ! -f "$TARGET_MODELS" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (30%): Provider alias resolution ----------
node -e "
const fs = require('fs');
const index = fs.readFileSync('$TARGET_INDEX', 'utf8');

// Must NOT hardcode providerId: 'google'
if (/providerId:\s*['\"]google['\"]/.test(index)) {
    console.log('FAIL: still hardcodes providerId: \"google\"');
    process.exit(1);
}

// Must use runtime provider from context
if (!index.includes('ctx.provider')) {
    console.log('FAIL: does not use ctx.provider');
    process.exit(1);
}

// Must have templateProviderId for cross-provider fallback
if (!index.includes('templateProviderId')) {
    console.log('FAIL: missing templateProviderId');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_alias]=1; echo "TEST behavioral_alias: PASS"; else echo "TEST behavioral_alias: FAIL"; fi

# ---------- PRIMARY 2 (30%): Flash-lite prefix ordering ----------
node -e "
const fs = require('fs');
const models = fs.readFileSync('$TARGET_MODELS', 'utf8');

const fnStart = models.indexOf('resolveGoogle31ForwardCompatModel');
if (fnStart < 0) { console.log('FAIL: function not found'); process.exit(1); }
const fnBody = models.substring(fnStart);

// flash-lite must be defined as a constant
if (!models.includes('GEMINI_3_1_FLASH_LITE_PREFIX') && !models.includes('flash-lite')) {
    console.log('FAIL: no flash-lite prefix handling');
    process.exit(1);
}

// In the if-else chain, flash-lite must come before flash
const liteBranch = fnBody.indexOf('flash-lite') || fnBody.indexOf('FLASH_LITE');
const flashBranch = fnBody.indexOf('FLASH_PREFIX');
if (liteBranch < 0) {
    console.log('FAIL: no flash-lite branch');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_prefix]=1; echo "TEST behavioral_prefix: PASS"; else echo "TEST behavioral_prefix: FAIL"; fi

# ---------- SUPPLEMENTARY (20%): Structural ----------
node -e "
const fs = require('fs');
const models = fs.readFileSync('$TARGET_MODELS', 'utf8');

if (!/templateProviderId\??:\s*string/.test(models)) {
    console.log('FAIL: no templateProviderId parameter');
    process.exit(1);
}

if (!models.includes('cloneFirstGoogleTemplateModel') && !models.includes('templateProviderIds')) {
    if (!models.includes('for') && !models.includes('forEach')) {
        console.log('FAIL: no multi-provider lookup');
        process.exit(1);
    }
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural]=1; echo "TEST structural: PASS"; else echo "TEST structural: FAIL"; fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const m = fs.readFileSync('$TARGET_MODELS', 'utf8');
const checks = [
    [m.split('\n').length > 30, 'substantial'],
    [m.includes('resolveGoogle31ForwardCompatModel'), 'resolver'],
    [m.includes('GEMINI_3_1'), 'constants'],
    [m.includes('cloneFirstTemplateModel') || m.includes('cloneFirstGoogleTemplateModel'), 'cloning'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "Extension code must import from plugin-sdk/*" ----------
# Source: CLAUDE.md line 16 @ 6be14ab388eb74cd100e43bf975aad78146ac220
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find extensions/google/src -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
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
w = {'behavioral_alias': ${WEIGHTS[behavioral_alias]}, 'config_boundary': ${WEIGHTS[config_boundary]}, 'behavioral_prefix': ${WEIGHTS[behavioral_prefix]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_alias': ${RESULTS[behavioral_alias]}, 'config_boundary': ${RESULTS[config_boundary]}, 'behavioral_prefix': ${RESULTS[behavioral_prefix]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
