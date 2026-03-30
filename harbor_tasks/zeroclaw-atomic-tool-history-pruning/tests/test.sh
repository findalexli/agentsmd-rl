#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_emergency]=0.25
WEIGHTS[behavioral_collapse]=0.20
WEIGHTS[behavioral_budget]=0.20
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.15
WEIGHTS[config_fmt]=0.05

for key in behavioral_emergency behavioral_collapse behavioral_budget structural antistub config_fmt; do
    RESULTS[$key]=0
done

TARGET_HISTORY="src/agent/history.rs"
TARGET_PRUNER="src/agent/history_pruner.rs"

if [ ! -f "$TARGET_HISTORY" ] || [ ! -f "$TARGET_PRUNER" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (25%): emergency_history_trim handles tool groups ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET_HISTORY', 'utf8');

const fnStart = src.indexOf('emergency_history_trim');
if (fnStart < 0) {
    console.log('FAIL: emergency_history_trim not found');
    process.exit(1);
}

const fnBody = src.substring(fnStart, src.indexOf('\npub', fnStart + 10) || src.length);

// Must handle assistant messages specially - count tool messages
if (!fnBody.includes('\"assistant\"') || !fnBody.includes('\"tool\"')) {
    console.log('FAIL: does not check for assistant/tool roles');
    process.exit(1);
}

// Must count consecutive tool messages
if (!fnBody.includes('tool_count') && !fnBody.includes('tool_group') && !fnBody.includes('consecutive')) {
    // Check for any loop that counts following tool messages
    if (!fnBody.includes('while') || !fnBody.includes('tool')) {
        console.log('FAIL: does not count consecutive tool messages');
        process.exit(1);
    }
}

// Must remove the group atomically
if (!fnBody.includes('0..=tool_count') && !fnBody.includes('0..tool_count') &&
    !fnBody.includes('remove(i)')) {
    console.log('FAIL: does not remove tool group atomically');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_emergency]=1; echo "TEST behavioral_emergency: PASS"; else echo "TEST behavioral_emergency: FAIL"; fi

# ---------- PRIMARY 2 (20%): Phase 1 collapse handles multi-tool groups ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET_PRUNER', 'utf8');

// Phase 1 must handle multiple consecutive tool messages after an assistant
if (!src.includes('tool_count') && !src.includes('consecutive tool') && !src.includes('tool_group')) {
    console.log('FAIL: no multi-tool group handling in collapse phase');
    process.exit(1);
}

// Summary should mention tool call count
if (!src.includes('tool call(s)') && !src.includes('tool calls') && !src.includes('Tool exchange')) {
    console.log('FAIL: no multi-tool summary format');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_collapse]=1; echo "TEST behavioral_collapse: PASS"; else echo "TEST behavioral_collapse: FAIL"; fi

# ---------- PRIMARY 3 (20%): Phase 2 budget enforcement is atomic ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET_PRUNER', 'utf8');

// Phase 2 must also handle atomic dropping of tool groups
// Look for the budget enforcement section
const phase2 = src.substring(src.indexOf('budget') || src.indexOf('max_tokens'));

if (!phase2.includes('\"assistant\"') || !phase2.includes('\"tool\"')) {
    console.log('FAIL: budget phase does not check roles');
    process.exit(1);
}

// Must drop atomically
if (!phase2.includes('tool_count') && !phase2.includes('atomic') && !phase2.includes('group')) {
    // Check for any pattern that removes multiple messages together
    const hasAtomicDrop = phase2.includes('0..=') || phase2.includes('for _') ||
        (phase2.includes('remove') && phase2.includes('while'));
    if (!hasAtomicDrop) {
        console.log('FAIL: no atomic dropping in budget phase');
        process.exit(1);
    }
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_budget]=1; echo "TEST behavioral_budget: PASS"; else echo "TEST behavioral_budget: FAIL"; fi

# ---------- SUPPLEMENTARY (15%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET_PRUNER', 'utf8');

// The old code had: if messages[i].role == 'assistant' && messages[i + 1].role == 'tool'
// This pattern should be replaced with multi-tool handling
if (src.includes('messages[i + 1].role == \"tool\"') && !src.includes('tool_count')) {
    console.log('FAIL: still uses single-pair pattern without tool_count');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural]=1; echo "TEST structural: PASS"; else echo "TEST structural: FAIL"; fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const h = fs.readFileSync('$TARGET_HISTORY', 'utf8');
const p = fs.readFileSync('$TARGET_PRUNER', 'utf8');
const checks = [
    [h.split('\n').length > 30, 'history.rs substantial'],
    [p.split('\n').length > 50, 'history_pruner.rs substantial'],
    [h.includes('emergency_history_trim'), 'emergency trim function'],
    [p.includes('prune_history'), 'prune function'],
    [p.includes('HistoryPrunerConfig'), 'config struct'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "cargo fmt --all -- --check" ----------
# Source: AGENTS.md line 3 @ 753d4fc65f32b45797e7aba52db6c8eb3a24ad89
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
w = {'behavioral_emergency': ${WEIGHTS[behavioral_emergency], 'config_fmt': ${WEIGHTS[config_fmt]}}, 'behavioral_collapse': ${WEIGHTS[behavioral_collapse]}, 'behavioral_budget': ${WEIGHTS[behavioral_budget]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_emergency': ${RESULTS[behavioral_emergency], 'config_fmt': ${RESULTS[config_fmt]}}, 'behavioral_collapse': ${RESULTS[behavioral_collapse]}, 'behavioral_budget': ${RESULTS[behavioral_budget]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
