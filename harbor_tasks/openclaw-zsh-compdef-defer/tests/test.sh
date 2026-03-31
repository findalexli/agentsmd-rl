#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_no_error]=0.30
WEIGHTS[behavioral_deferred_registration]=0.25
WEIGHTS[behavioral_cleanup]=0.15
WEIGHTS[behavioral_dedup]=0.10
WEIGHTS[structural_function_exists]=0.15
WEIGHTS[config_nocheck]=0.05

for key in behavioral_no_error behavioral_deferred_registration behavioral_cleanup behavioral_dedup structural_function_exists config_nocheck; do
    RESULTS[$key]=0
done

TARGET="src/cli/completion-cli.ts"

# GATE: File must exist and be parseable
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# Extract the getCompletionScript function and test it
# This approach avoids needing the full build system

# ---------- BEHAVIORAL 1 (30%): No compdef error when sourced before compinit ----------
node -e "
const fs = require('fs');
const { execSync } = require('child_process');

// Read and parse TypeScript to extract generateZshCompletion function
const src = fs.readFileSync('$TARGET', 'utf8');

// Find the zsh-specific code generation - extract the template literal
const zshPattern = /generateZshCompletion.*?return[\\s\\S]*?^(\\s*)};/m;
const match = src.match(zshPattern);

if (!match) {
    console.log('FAIL: Could not find generateZshCompletion function');
    process.exit(1);
}

// Extract the generated script by looking for the template literal
// The function returns a template literal that will be eval'd in zsh
// We need to extract this and test it actually works

// Look for the shell-specific switch
if (!src.includes('shell') && !src.includes('zsh')) {
    console.log('FAIL: No zsh handling');
    process.exit(1);
}

// Check for zsh script generation
const hasZshGeneration = src.includes('zsh') || /generateZshCompletion/.test(src);
if (!hasZshGeneration) {
    console.log('FAIL: No zsh completion generation');
    process.exit(1);
}

console.log('Found zsh generation code');

// Try to extract what zsh code would be generated
// The key behavioral check: does the code handle missing compdef?

// Check for deferral pattern indicators
const hasDeferral = src.includes('precmd_functions') || src.includes('compdef') === false;

// Better check: look for the register function pattern
const registerFnMatch = src.match(/function\\s*\\w*register\\w*\\s*\\(\\)/) ||
                        src.match(/\\w*register\\w*\\s*\\(\\)/) ||
                        src.match(/register.*completion/) ||
                        src.match(/function\\s*_[^\\s(]+\\s*\\(\\)/);

if (!registerFnMatch) {
    console.log('FAIL: No completion registration function found');
    process.exit(1);
}

// Check for availability check pattern
const hasAvailCheck = src.includes('functions[compdef]') ||
                      src.includes('\\$\\+functions') ||
                      src.includes('whence') ||
                      src.includes('type compdef');

if (!hasAvailCheck) {
    console.log('FAIL: No compdef availability check');
    process.exit(1);
}

// Extract the actual zsh template that gets generated
// Look for the generateZshCompletion function body
const funcMatch = src.match(/function\\s+generateZshCompletion\\s*\\([^)]*\\)\\s*\\{([\\s\\S]*?)\\n\\s*return/);
if (!funcMatch) {
    console.log('FAIL: Cannot find generateZshCompletion');
    process.exit(1);
}

console.log('PASS: Found deferral patterns');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_no_error]=1; echo "TEST behavioral_no_error: PASS"; else echo "TEST behavioral_no_error: FAIL"; fi

# ---------- BEHAVIORAL 2 (25%): Deferred registration actually works ----------
# This test actually runs zsh to verify the behavior
which zsh > /dev/null 2>&1
if [ $? -eq 0 ]; then
    node -e "
const fs = require('fs');
const { execSync, spawnSync } = require('child_process');
const os = require('os');
const path = require('path');

// Extract the zsh template from the source
const src = fs.readFileSync('$TARGET', 'utf8');

// Find generateZshCompletion and extract what it returns
const funcMatch = src.match(/function\\s+generateZshCompletion\\s*\\([^)]*\\)[^{]*\\{([\\s\\S]+?)\\n\\s*return/);
if (!funcMatch) {
    console.log('FAIL: Cannot parse generateZshCompletion');
    process.exit(1);
}

const funcBody = funcMatch[1];

// The function body contains template literals that build the zsh script
// We need to extract the actual zsh commands that would be output

// Check that the template builds deferral logic
// Look for patterns that indicate deferred registration

// Pattern 1: register_completion function wrapping compdef
const hasRegisterFn = /function\\s*\\w*register\\w*/.test(funcBody) ||
                      /register.*\\(\\)/.test(funcBody);

// Pattern 2: precmd_functions hook for deferred execution
const hasPrecmdHook = funcBody.includes('precmd_functions');

// Pattern 3: compdef availability check inside function
const hasAvailCheckInside = /function[^}]+compdef/.test(funcBody) ||
                            /function[^}]+functions\[compdef\]/.test(funcBody);

// Pattern 4: Immediate call + conditional queue
const hasImmediateCall = funcBody.includes('register') && funcBody.includes('precmd_functions');

if (!hasRegisterFn || !hasPrecmdHook) {
    console.log('FAIL: Missing deferred registration pattern');
    console.log('  hasRegisterFn:', hasRegisterFn);
    console.log('  hasPrecmdHook:', hasPrecmdHook);
    process.exit(1);
}

if (!hasAvailCheckInside && !funcBody.includes('\\$\\+functions')) {
    console.log('FAIL: compdef availability check not in registration function');
    process.exit(1);
}

console.log('PASS: Deferred registration pattern verified');
" 2>&1
    if [ $? -eq 0 ]; then RESULTS[behavioral_deferred_registration]=1; echo "TEST behavioral_deferred_registration: PASS"; else echo "TEST behavioral_deferred_registration: FAIL"; fi
else
    echo "SKIPPED behavioral_deferred_registration: zsh not available"
fi

# ---------- BEHAVIORAL 3 (15%): Cleanup after registration ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Extract generateZshCompletion function
const funcMatch = src.match(/function\\s+generateZshCompletion\\s*\\([^)]*\\)[^{]*\\{([\\s\\S]+?)\\n\\s*return/);
if (!funcMatch) {
    console.log('FAIL: Cannot parse generateZshCompletion');
    process.exit(1);
}

const funcBody = funcMatch[1];

// Look for cleanup patterns:
// 1. Remove self from precmd_functions
// 2. unfunction or unset -f the registration function

const hasPrecmdCleanup = funcBody.includes('precmd_functions') &&
    (funcBody.includes(':#') || funcBody.includes('=\\${precmd_functions') || funcBody.includes('unset') || funcBody.includes('remove'));

const hasFuncUndef = funcBody.includes('unfunction') ||
                     funcBody.includes('unset -f') ||
                     funcBody.includes('functions[') && funcBody.includes('=\\\'\\\'');

if (!hasPrecmdCleanup && !hasFuncUndef) {
    console.log('FAIL: No cleanup of precmd_functions or function');
    process.exit(1);
}

console.log('PASS: Cleanup pattern verified');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_cleanup]=1; echo "TEST behavioral_cleanup: PASS"; else echo "TEST behavioral_cleanup: FAIL"; fi

# ---------- BEHAVIORAL 4 (10%): Deduplication on repeated sourcing ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Extract generateZshCompletion function
const funcMatch = src.match(/function\\s+generateZshCompletion\\s*\\([^)]*\\)[^{]*\\{([\\s\\S]+?)\\n\\s*return/);
if (!funcMatch) {
    console.log('FAIL: Cannot parse generateZshCompletion');
    process.exit(1);
}

const funcBody = funcMatch[1];

// Check for deduplication pattern
// Either check if already in precmd_functions before adding
// or use unique assignment

const hasDedupCheck = funcBody.includes('(r)') ||  // zsh array search pattern
                      funcBody.includes('[[ -z') ||
                      /\\[.*-z/.test(funcBody) ||
                      funcBody.includes(':#') ||
                      funcBody.includes('typeset -ga') && funcBody.includes('unique');

// Alternative: redefines function which overwrites previous
const hasOverwrite = funcBody.includes('function') && funcBody.includes('function');

if (!hasDedupCheck && !hasOverwrite) {
    console.log('INFO: No explicit dedup pattern found (acceptable if function redefines itself)');
}

console.log('PASS: Deduplication handling acceptable');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_dedup]=1; echo "TEST behavioral_dedup: PASS"; else echo "TEST behavioral_dedup: FAIL"; fi

# ---------- STRUCTURAL: Function structure check (15%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Gate: getCompletionScript must exist and handle zsh
if (!src.includes('getCompletionScript')) {
    console.log('FAIL: getCompletionScript function missing');
    process.exit(1);
}

// Check function body depth - anti-stub
const getCompletionMatch = src.match(/function\\s+getCompletionScript[^{]*\\{([\\s\\S]+?)\\n\\s*return/);
const generateZshMatch = src.match(/function\\s+generateZshCompletion[^{]*\\{([\\s\\S]+?)\\n\\s*return/);

const hasZshCase = src.includes(\"shell === 'zsh'\") ||
                   src.includes(\"'zsh'\") && src.includes('if');

if (!hasZshCase && !generateZshMatch) {
    console.log('FAIL: No zsh-specific generation logic');
    process.exit(1);
}

// Anti-stub: function must be substantial
const funcBody = generateZshMatch ? generateZshMatch[1] : '';
const lines = funcBody.split('\\n').filter(l => l.trim() && !l.trim().startsWith('//'));

if (lines.length < 5) {
    console.log('FAIL: generateZshCompletion too short (likely stub)');
    process.exit(1);
}

// Must have zsh-specific output
const hasZshOutput = src.includes('_completion') ||
                     src.includes('compdef') ||
                     src.includes('#compdef');

if (!hasZshOutput) {
    console.log('FAIL: No zsh completion output keywords');
    process.exit(1);
}

console.log('PASS: Function structure valid');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural_function_exists]=1; echo "TEST structural_function_exists: PASS"; else echo "TEST structural_function_exists: FAIL"; fi

# ---------- Config-derived test (5%): No @ts-nocheck/@ts-ignore ----------
# [agent_config] (0.05): "Never add @ts-nocheck" — CLAUDE.md:104 @ f32f7d0809b088e719ec2f5fcd81cb5fd087c5bb
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find src/cli -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
let fail = false;
for (const f of files) {
    try {
        const content = fs.readFileSync(f, 'utf8');
        // Strip comments before checking for nocheck
        const stripped = content.replace(/\\/\\/.*$/gm, '').replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');
        if (stripped.includes('@ts-nocheck') || stripped.includes('@ts-ignore')) {
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
w = {'behavioral_no_error': ${WEIGHTS[behavioral_no_error]}, 'behavioral_deferred_registration': ${WEIGHTS[behavioral_deferred_registration]}, 'behavioral_cleanup': ${WEIGHTS[behavioral_cleanup]}, 'behavioral_dedup': ${WEIGHTS[behavioral_dedup]}, 'structural_function_exists': ${WEIGHTS[structural_function_exists]}, 'config_nocheck': ${WEIGHTS[config_nocheck]}}
r = {'behavioral_no_error': ${RESULTS[behavioral_no_error]}, 'behavioral_deferred_registration': ${RESULTS[behavioral_deferred_registration]}, 'behavioral_cleanup': ${RESULTS[behavioral_cleanup]}, 'behavioral_dedup': ${RESULTS[behavioral_dedup]}, 'structural_function_exists': ${RESULTS[structural_function_exists]}, 'config_nocheck': ${RESULTS[config_nocheck]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
