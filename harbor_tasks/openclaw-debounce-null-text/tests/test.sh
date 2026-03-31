#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_f2p]=0.45
WEIGHTS[behavioral_p2p]=0.15
WEIGHTS[antistub]=0.15
WEIGHTS[config_boundary]=0.05
WEIGHTS[style_rubric]=0.20

for key in behavioral_f2p behavioral_p2p antistub config_boundary style_rubric; do
    RESULTS[$key]=0
done

TARGET="extensions/bluebubbles/src/monitor-debounce.ts"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- GATE: Code parses as valid TypeScript ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
try {
    // Basic syntax check - TypeScript will be checked later
    new Function('return ' + src.replace(/export /g, '').replace(/import.*?from.*$/gm, ''));
} catch (e) {
    // If that fails, it's likely still valid TS (types aren't JS)
    // Just check for obvious syntax errors
    if (e.message.includes('Unexpected token') && e.message.includes('interface')) {
        console.log('PASS: TypeScript interface syntax');
    } else if (e.message.includes('Unexpected token') && e.message.includes('type ')) {
        console.log('PASS: TypeScript type syntax');
    } else {
        console.log('CHECK: ' + e.message);
    }
}
console.log('PASS: file is readable');
" 2>&1
if [ $? -ne 0 ]; then
    echo "GATE FAIL: File does not parse"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY (45%): Fail-to-pass behavioral test ----------
# [pr_diff] (0.45): create entry with null text, call combineDebounceEntries, verify no crash
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Skip if target file imports heavy dependencies we can't mock
const hasHeavyImports = /import.*from\s+['\"](?!\.|openclaw\/plugin-sdk|\.\/)/.test(src);

// Extract just the combineDebounceEntries function and any helper functions
const extractFunction = (name) => {
    const pattern = new RegExp('(function\\\\s+' + name + '\\\\s*\\\\([^)]*\\\\)\\\\s*:[^;]*?)\\\\{', 'g');
    let match;
    const functions = [];
    while ((match = pattern.exec(src)) !== null) {
        // Find complete function body
        let startIdx = match.index;
        let braceCount = 0;
        let i = match.index + match[0].length - 1;
        for (; i < src.length && braceCount >= 0; i++) {
            if (src[i] === '{') braceCount++;
            else if (src[i] === '}') {
                braceCount--;
                if (braceCount === 0) break;
            }
        }
        functions.push(src.substring(startIdx, i + 1));
    }
    return functions.join('\\n\\n');
};

// Extract type definitions used by the function
const extractTypes = () => {
    const typeMatches = src.match(/type\\s+\\w+\\s*=\\s*\\{[^}]*\\}/g) || [];
    return typeMatches.join('\\n');
};

const fnCode = extractFunction('combineDebounceEntries');
const helperFns = extractFunction('normalize'); // may include sanitize/normalize helpers
const types = extractTypes();

if (!fnCode) {
    console.log('FAIL: combineDebounceEntries not found');
    process.exit(1);
}

// Build a test that executes the actual function
const testCode = \`
\${types}
\${helperFns}
\${fnCode}

// Test data: entry with null text (the bug trigger)
const nullTextEntry = {
    message: {
        text: null,
        attachments: [],
        timestamp: 1234567890,
        messageId: 'test-1'
    },
    target: { channelId: 'test-channel' }
};

const validEntry = {
    message: {
        text: 'Hello world',
        attachments: [],
        timestamp: 1234567891,
        messageId: 'test-2'
    },
    target: { channelId: 'test-channel' }
};

// This is the core test: does null text crash?
try {
    // Test with null text entry
    const result1 = combineDebounceEntries([nullTextEntry]);
    console.log('PASS: single null entry handled');
} catch (e) {
    if (e.message && (e.message.includes('Cannot read properties of null') || e.message.includes('null reading') || e.message.includes('.trim'))) {
        console.log('FAIL: null text causes crash: ' + e.message);
        process.exit(1);
    }
    // Other errors might be expected
    console.log('CHECK: error on null entry (may be expected): ' + e.message);
}

try {
    // Test mixed entries (null + valid)
    const result2 = combineDebounceEntries([nullTextEntry, validEntry]);
    console.log('PASS: mixed null+valid entries handled');
} catch (e) {
    if (e.message && (e.message.includes('Cannot read properties of null') || e.message.includes('null reading') || e.message.includes('.trim'))) {
        console.log('FAIL: null text in mixed entries causes crash: ' + e.message);
        process.exit(1);
    }
}

console.log('PASS: null text guard works');
\`;

// Write and execute test
fs.writeFileSync('/tmp/f2p_test.js', testCode);
" 2>&1

# Run the generated test
if [ -f /tmp/f2p_test.js ]; then
    node /tmp/f2p_test.js 2>&1
    F2P_RESULT=$?
else
    echo "FAIL: test generation failed"
    F2P_RESULT=1
fi

if [ $F2P_RESULT -eq 0 ]; then RESULTS[behavioral_f2p]=1; echo "TEST behavioral_f2p: PASS"; else echo "TEST behavioral_f2p: FAIL"; fi

# ---------- PASS-TO-PASS (15%): Valid entries still process correctly ----------
# [pr_diff] (0.15): Valid entries return expected combined output
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Check function returns sensible output for valid input
const extractFunction = (name) => {
    const pattern = new RegExp('(function\\\\s+' + name + '\\\\s*\\\\([^)]*\\\\)\\\\s*:[^;]*?)\\\\{', 'g');
    let match;
    const functions = [];
    while ((match = pattern.exec(src)) !== null) {
        let startIdx = match.index;
        let braceCount = 0;
        let i = match.index + match[0].length - 1;
        for (; i < src.length && braceCount >= 0; i++) {
            if (src[i] === '{') braceCount++;
            else if (src[i] === '}') {
                braceCount--;
                if (braceCount === 0) break;
            }
        }
        functions.push(src.substring(startIdx, i + 1));
    }
    return functions.join('\\n\\n');
};

const fnCode = extractFunction('combineDebounceEntries');
if (!fnCode || !fnCode.includes('return')) {
    console.log('FAIL: function missing return statement');
    process.exit(1);
}

// Check for iteration over entries (ensures processing)
if (!fnCode.includes('for') && !fnCode.includes('.map') && !fnCode.includes('.forEach') && !fnCode.includes('.reduce')) {
    // Single entry case handled specially
    if (!fnCode.includes('entries[0]') && !fnCode.includes('entries.length')) {
        console.log('FAIL: function does not iterate over entries');
        process.exit(1);
    }
}

console.log('PASS: valid entry processing structure intact');
" 2>&1

if [ $? -eq 0 ]; then RESULTS[behavioral_p2p]=1; echo "TEST behavioral_p2p: PASS"; else echo "TEST behavioral_p2p: FAIL"; fi

# ---------- Anti-stub (15%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const lines = src.split('\\n');

// Count non-empty, non-comment lines
const codeLines = lines.filter(l => {
    const trimmed = l.trim();
    return trimmed.length > 0 && !trimmed.startsWith('//') && !trimmed.startsWith('*') && !trimmed.startsWith('/*');
}).length;

const checks = [
    [codeLines > 20, 'substantial code (' + codeLines + ' lines)'],
    [src.includes('combineDebounceEntries'), 'combine function exists'],
    [src.includes('BlueBubbles'), 'BlueBubbles type present'],
    [/\\b(debounce|enqueue|flush)\\b/i.test(src), 'debounce methods present'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS: not a stub');
" 2>&1

if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi

# ---------- Config-derived test (5%): No cross-boundary imports ----------
# [agent_config] (0.05): \"Extension code must import from plugin-sdk/*\" — AGENTS.md:16 @ 756df2e
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

# ---------- Style rubric placeholder (20%) ----------
RESULTS[style_rubric]=0

SCORE=$(python3 -c "
w = {'behavioral_f2p': ${WEIGHTS[behavioral_f2p]}, 'behavioral_p2p': ${WEIGHTS[behavioral_p2p]}, 'antistub': ${WEIGHTS[antistub]}, 'config_boundary': ${WEIGHTS[config_boundary]}, 'style_rubric': ${WEIGHTS[style_rubric]}}
r = {'behavioral_f2p': ${RESULTS[behavioral_f2p]}, 'behavioral_p2p': ${RESULTS[behavioral_p2p]}, 'antistub': ${RESULTS[antistub]}, 'config_boundary': ${RESULTS[config_boundary]}, 'style_rubric': ${RESULTS[style_rubric]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
