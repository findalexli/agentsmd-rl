#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_no_constant]=0.35
WEIGHTS[behavioral_uses_config]=0.30
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.15
WEIGHTS[config_fmt]=0.05

for key in behavioral_no_constant behavioral_uses_config structural antistub config_fmt; do
    RESULTS[$key]=0
done

TARGET="src/channels/mod.rs"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (35%): Hardcoded constant removed ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

if (src.includes('const MAX_CHANNEL_HISTORY') || src.includes('MAX_CHANNEL_HISTORY')) {
    console.log('FAIL: MAX_CHANNEL_HISTORY still present');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_no_constant]=1; echo "TEST behavioral_no_constant: PASS"; else echo "TEST behavioral_no_constant: FAIL"; fi

# ---------- PRIMARY 2 (30%): Uses config value ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

if (!src.includes('max_history_messages')) {
    console.log('FAIL: max_history_messages not referenced');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_uses_config]=1; echo "TEST behavioral_uses_config: PASS"; else echo "TEST behavioral_uses_config: FAIL"; fi

# ---------- SUPPLEMENTARY (15%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

if (src.includes('Maximum history messages to keep per sender')) {
    console.log('FAIL: old comment still present');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural]=1; echo "TEST structural: PASS"; else echo "TEST structural: FAIL"; fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const checks = [
    [src.split('\n').length > 50, 'substantial'],
    [src.includes('ConversationHistoryMap'), 'history map'],
    [src.includes('ChatMessage'), 'message type'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "cargo fmt --all -- --check" ----------
# Source: AGENTS.md line 3 @ 5b6d0585dd635a719f47c97f761dbaae817f6daa
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
w = {'behavioral_no_constant': ${WEIGHTS[behavioral_no_constant], 'config_fmt': ${WEIGHTS[config_fmt]}}, 'behavioral_uses_config': ${WEIGHTS[behavioral_uses_config]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_no_constant': ${RESULTS[behavioral_no_constant], 'config_fmt': ${RESULTS[config_fmt]}}, 'behavioral_uses_config': ${RESULTS[behavioral_uses_config]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
