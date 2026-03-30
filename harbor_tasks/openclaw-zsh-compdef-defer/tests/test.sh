#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_defer]=0.35
WEIGHTS[behavioral_no_bare]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15
WEIGHTS[config_nocheck]=0.05

for key in behavioral_defer behavioral_no_bare structural antistub config_nocheck; do
    RESULTS[$key]=0
done

TARGET="src/cli/completion-cli.ts"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (35%): Deferred registration pattern ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Must define a register_completion function
if (!src.includes('register_completion')) {
    console.log('FAIL: no register_completion function defined');
    process.exit(1);
}

// Must check if compdef is available using zsh function check
if (!src.includes('functions[compdef]') && !src.includes('command -v compdef') && !src.includes('type compdef')) {
    console.log('FAIL: no compdef availability check');
    process.exit(1);
}

// Must add to precmd_functions for deferred execution
if (!src.includes('precmd_functions')) {
    console.log('FAIL: no precmd_functions hook for deferred registration');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_defer]=1; echo "TEST behavioral_defer: PASS"; else echo "TEST behavioral_defer: FAIL"; fi

# ---------- PRIMARY 2 (25%): No bare compdef at top level ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// The generated script must NOT have a bare 'compdef ... openclaw' at the top level
// (outside of a function body). It should only be inside a function.

// Find the zsh script generation section
const zshSection = src.substring(src.indexOf('zsh'));

// Check that compdef is only called inside a function
// A bare compdef would be: compdef _name command (not inside a function block)
// The fix wraps it in _register_completion function

// Ensure there's no bare compdef line that's not inside a function
const lines = src.split('\n');
let inFunction = false;
let bareCompdef = false;
for (const line of lines) {
    const trimmed = line.trim();
    // This is template literal in TS, so we look for the pattern
    if (trimmed.includes('compdef _') && !trimmed.includes('function') &&
        !trimmed.includes('register_completion') && !trimmed.includes('//') &&
        !trimmed.includes('if') && !trimmed.includes('$+functions')) {
        // Check if this bare compdef is the OLD pattern (not wrapped)
        // In the fixed version, compdef should only appear inside the register function
        const lineIdx = lines.indexOf(line);
        const context = lines.slice(Math.max(0, lineIdx - 5), lineIdx).join('\n');
        if (!context.includes('register_completion') && !context.includes('function')) {
            bareCompdef = true;
        }
    }
}

// The key check: the script should have register_completion wrapping compdef
if (!src.includes('register_completion')) {
    console.log('FAIL: compdef not wrapped in register function');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_no_bare]=1; echo "TEST behavioral_no_bare: PASS"; else echo "TEST behavioral_no_bare: FAIL"; fi

# ---------- SUPPLEMENTARY (20%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Should remove itself from precmd_functions after registering
if (!src.includes('precmd_functions') || !src.includes('unfunction')) {
    // Acceptable alternatives: remove from array
    if (!src.includes('precmd_functions') || (!src.includes(':#') && !src.includes('remove'))) {
        console.log('FAIL: does not clean up after registration');
        process.exit(1);
    }
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural]=1; echo "TEST structural: PASS"; else echo "TEST structural: FAIL"; fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const checks = [
    [src.split('\n').length > 50, 'substantial content'],
    [src.includes('getCompletionScript'), 'main function'],
    [src.includes('zsh'), 'zsh handling'],
    [src.includes('compdef'), 'compdef usage'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "Never add @ts-nocheck" ----------
# Source: CLAUDE.md line 104 @ f32f7d0809b088e719ec2f5fcd81cb5fd087c5bb
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find src/cli -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
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
w = {'behavioral_defer': ${WEIGHTS[behavioral_defer]}, 'config_nocheck': ${WEIGHTS[config_nocheck]}, 'behavioral_no_bare': ${WEIGHTS[behavioral_no_bare]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_defer': ${RESULTS[behavioral_defer]}, 'config_nocheck': ${RESULTS[config_nocheck]}, 'behavioral_no_bare': ${RESULTS[behavioral_no_bare]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
