#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_trim]=0.35
WEIGHTS[behavioral_preserve]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15
WEIGHTS[config_fmt]=0.05

for key in behavioral_trim behavioral_preserve structural antistub config_fmt; do
    RESULTS[$key]=0
done

TARGET="src/multimodal.rs"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (35%): Behavioral - trim instead of error ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Must NOT have TooManyImages error return for exceeding max_images
// The old code had: return Err(MultimodalError::TooManyImages { ... })
if (src.includes('TooManyImages') && src.includes('return Err(MultimodalError::TooManyImages')) {
    console.log('FAIL: still returns TooManyImages error');
    process.exit(1);
}

// Must have a trim function
if (!src.includes('trim_old_images') && !src.includes('trim_images') && !src.includes('remove_old_images')) {
    console.log('FAIL: no trim_old_images function');
    process.exit(1);
}

// Must call the trim function when images exceed limit
if (!src.includes('total_images > max_images') && !src.includes('found_images > max_images')) {
    // Check for alternative condition patterns
    if (!src.includes('> max_images')) {
        console.log('FAIL: no condition checking for excess images');
        process.exit(1);
    }
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_trim]=1; echo "TEST behavioral_trim: PASS"; else echo "TEST behavioral_trim: FAIL"; fi

# ---------- PRIMARY 2 (25%): Preserves text and newest images ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Must strip images from oldest messages first
// Look for iteration that processes messages by index
if (!src.includes('enumerate()') && !src.includes('image_positions')) {
    console.log('FAIL: no ordered processing of messages by position');
    process.exit(1);
}

// Must preserve text content when stripping images
if (!src.includes('parse_image_markers') && !src.includes('cleaned') && !src.includes('[image removed')) {
    console.log('FAIL: no text preservation logic');
    process.exit(1);
}

// Must only strip from user messages
if (!src.includes('role == \"user\"') && !src.includes('role != \"user\"')) {
    console.log('FAIL: no role-based filtering');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_preserve]=1; echo "TEST behavioral_preserve: PASS"; else echo "TEST behavioral_preserve: FAIL"; fi

# ---------- SUPPLEMENTARY (20%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Should have a dedicated trim function
const hasFn = /fn\s+trim_old_images/.test(src) || /fn\s+trim_images/.test(src) || /fn\s+remove_old_images/.test(src);
if (!hasFn) {
    console.log('FAIL: no dedicated trim function');
    process.exit(1);
}

// The function should take messages and max_images as parameters
if (!src.includes('max_images: usize') && !src.includes('max_images')) {
    console.log('FAIL: trim function does not take max_images parameter');
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
    [src.split('\n').length > 100, 'substantial content'],
    [src.includes('prepare_messages_for_provider'), 'main function'],
    [src.includes('MultimodalConfig'), 'config struct'],
    [src.includes('parse_image_markers'), 'image marker parsing'],
    [src.includes('ChatMessage'), 'message type'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "cargo fmt --all -- --check" ----------
# Source: AGENTS.md line 3 @ 3e02e68ec0e26b2c43593c40d660e2298c8cb332
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
w = {'behavioral_trim': ${WEIGHTS[behavioral_trim], 'config_fmt': ${WEIGHTS[config_fmt]}}, 'behavioral_preserve': ${WEIGHTS[behavioral_preserve]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_trim': ${RESULTS[behavioral_trim], 'config_fmt': ${RESULTS[config_fmt]}}, 'behavioral_preserve': ${RESULTS[behavioral_preserve]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
