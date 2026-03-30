#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_signature]=0.30
WEIGHTS[behavioral_repair]=0.30
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15
WEIGHTS[config_fmt]=0.05

for key in behavioral_signature behavioral_repair structural antistub config_fmt; do
    RESULTS[$key]=0
done

TARGET="src/onboard/wizard.rs"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (30%): setup_channels accepts existing config ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// setup_channels must accept an Option<ChannelsConfig> parameter
const fnSig = src.match(/fn\s+setup_channels\s*\(([^)]*)\)/);
if (!fnSig) {
    console.log('FAIL: setup_channels function not found');
    process.exit(1);
}

const params = fnSig[1];
if (!params.includes('Option') && !params.includes('existing') && !params.includes('ChannelsConfig')) {
    console.log('FAIL: setup_channels does not accept existing config parameter');
    process.exit(1);
}

// Must use unwrap_or_default or similar pattern
if (!src.includes('unwrap_or_default') && !src.includes('unwrap_or(') && !src.includes('match existing')) {
    console.log('FAIL: no unwrap_or_default for existing config');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_signature]=1; echo "TEST behavioral_signature: PASS"; else echo "TEST behavioral_signature: FAIL"; fi

# ---------- PRIMARY 2 (30%): Repair wizard passes existing config ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// run_channels_repair_wizard must pass existing config to setup_channels
const repairFn = src.substring(src.indexOf('run_channels_repair_wizard'));
if (!repairFn) {
    console.log('FAIL: run_channels_repair_wizard not found');
    process.exit(1);
}

// Must pass Some(config.channels_config) or equivalent
if (!repairFn.includes('Some(') || !repairFn.includes('channels_config')) {
    console.log('FAIL: repair wizard does not pass existing config');
    process.exit(1);
}

// run_wizard should pass None (fresh setup)
const wizardFn = src.substring(src.indexOf('pub async fn run_wizard'));
const wizardSetupCall = wizardFn.substring(0, wizardFn.indexOf('setup_tunnel') || wizardFn.length);
if (!wizardSetupCall.includes('None') && !wizardSetupCall.includes('setup_channels(None)')) {
    // Check for implicit None
    if (wizardSetupCall.includes('setup_channels()')) {
        console.log('FAIL: run_wizard calls setup_channels() without None');
        process.exit(1);
    }
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_repair]=1; echo "TEST behavioral_repair: PASS"; else echo "TEST behavioral_repair: FAIL"; fi

# ---------- SUPPLEMENTARY (20%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Should preserve existing values in channel prompts (e.g. default for token input)
const hasExistingPrePopulation = src.includes('has_existing') || src.includes('keep existing') ||
    src.includes('Enter to keep') || src.includes('existing_tg') || src.includes('tg_users_default');

if (!hasExistingPrePopulation) {
    console.log('WARN: no pre-population of existing values in prompts');
}

// The function signature change is the key structural requirement
const fnSig = src.match(/fn\s+setup_channels\s*\(([^)]*)\)/);
if (fnSig && fnSig[1].includes('Option')) {
    console.log('PASS');
} else {
    console.log('FAIL: setup_channels signature not updated');
    process.exit(1);
}
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural]=1; echo "TEST structural: PASS"; else echo "TEST structural: FAIL"; fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const checks = [
    [src.split('\n').length > 500, 'substantial content'],
    [src.includes('setup_channels'), 'setup function'],
    [src.includes('ChannelsConfig'), 'config type'],
    [src.includes('run_wizard'), 'wizard function'],
    [src.includes('telegram') || src.includes('Telegram'), 'telegram handling'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "cargo fmt --all -- --check" ----------
# Source: AGENTS.md line 3 @ ce6dd7ca3740473e6414c3eee3d8172e15d79758
python3 -c "
import subprocess, sys, os
os.chdir('/workspace/zeroclaw')
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'], capture_output=True, text=True)
changed_rs = [f for f in result.stdout.strip().split(chr(10)) if f.endswith('.rs')]
if not changed_rs:
    result2 = subprocess.run(['find', 'src', '-name', '*.rs', '-newer', 'Cargo.toml'], capture_output=True, text=True)
    changed_rs = [f for f in result2.stdout.strip().split(chr(10)) if f]
warns = 0
for f in changed_rs[:20]:
    try:
        with open(f) as fh:
            for i, line in enumerate(fh, 1):
                if line.rstrip() != line.rstrip(chr(10)).rstrip():
                    warns += 1
    except: pass
if warns > 5:
    print(f'WARN: {warns} trailing whitespace issues')
print('PASS')
"
if [ $? -eq 0 ]; then RESULTS[config_fmt]=1; echo "TEST config_fmt: PASS"; else echo "TEST config_fmt: FAIL"; fi

SCORE=$(python3 -c "
w = {'behavioral_signature': ${WEIGHTS[behavioral_signature], 'config_fmt': ${WEIGHTS[config_fmt]}}, 'behavioral_repair': ${WEIGHTS[behavioral_repair]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_signature': ${RESULTS[behavioral_signature], 'config_fmt': ${RESULTS[config_fmt]}}, 'behavioral_repair': ${RESULTS[behavioral_repair]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
