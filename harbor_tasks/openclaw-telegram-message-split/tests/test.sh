#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_word_boundary]=0.35
WEIGHTS[behavioral_hard_split]=0.15
WEIGHTS[behavioral_format]=0.15
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.15
WEIGHTS[config_boundary]=0.05

for key in behavioral_word_boundary behavioral_hard_split behavioral_format structural antistub config_boundary; do
    RESULTS[$key]=0
done

TARGET="extensions/telegram/src/format.ts"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (35%): No more proportional estimate ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

if (src.includes('proportionalLimit') || src.includes('Math.floor((currentTextLength * htmlLimit)')) {
    console.log('BEHAVIORAL_WORD_BOUNDARY FAIL: still uses proportional estimate');
    process.exit(1);
}

// Must check actual rendered HTML length for candidates
if (!src.includes('renderTelegramChunkHtml') || !src.includes('sliceMarkdownIR')) {
    console.log('BEHAVIORAL_WORD_BOUNDARY FAIL: missing HTML rendering or slicing');
    process.exit(1);
}

// Must iterate to find fitting prefix
const hasSearch = src.includes('candidateLength') || src.includes('candidate') ||
    /for\s*\(let\s+\w+\s*=.*;\s*\w+\s*>=\s*1/.test(src) ||
    src.includes('binary');
if (!hasSearch) {
    console.log('BEHAVIORAL_WORD_BOUNDARY FAIL: no search for largest fitting prefix');
    process.exit(1);
}

console.log('BEHAVIORAL_WORD_BOUNDARY PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_word_boundary]=1; echo "TEST behavioral_word_boundary: PASS"; else echo "TEST behavioral_word_boundary: FAIL"; fi

# ---------- PRIMARY 2 (15%): Hard split fallback ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
if (src.includes('sliceMarkdownIR') && src.includes('splitMarkdownIRPreserveWhitespace')) {
    console.log('PASS');
} else {
    console.log('FAIL: no hard-split fallback');
    process.exit(1);
}
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_hard_split]=1; echo "TEST behavioral_hard_split: PASS"; else echo "TEST behavioral_hard_split: FAIL"; fi

# ---------- PRIMARY 3 (15%): Format preservation ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
if (src.includes('renderTelegramChunkHtml') && src.includes('MarkdownIR')) {
    console.log('PASS');
} else {
    process.exit(1);
}
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_format]=1; echo "TEST behavioral_format: PASS"; else echo "TEST behavioral_format: FAIL"; fi

# ---------- SUPPLEMENTARY (15%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const fnMatch = src.match(/function\s+splitTelegramChunkByHtmlLimit\s*\([^)]+\)/);
if (fnMatch && fnMatch[0].includes('renderedHtmlLength')) {
    console.log('STRUCTURAL FAIL: still takes renderedHtmlLength parameter');
    process.exit(1);
}
console.log('STRUCTURAL PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[structural]=1; echo "TEST structural: PASS"; else echo "TEST structural: FAIL"; fi

# ---------- Anti-stub (20%) ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const checks = [
    [src.split('\n').length > 200, 'substantial content'],
    [src.includes('splitTelegramChunkByHtmlLimit'), 'split function exists'],
    [src.includes('renderTelegramChunkHtml'), 'HTML rendering function'],
    [src.includes('htmlLimit'), 'HTML limit parameter'],
];
const failures = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (failures.length > 0) { console.log('FAIL: ' + failures.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi

# ---------- Final ----------

# ---------- Config-derived test (0.05): "Extension code must import from plugin-sdk/*" ----------
# Source: CLAUDE.md line 16 @ 865160e57292bfc32082fa885efe1a48e64bb06c
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
w = {'behavioral_word_boundary': ${WEIGHTS[behavioral_word_boundary]}, 'config_boundary': ${WEIGHTS[config_boundary]}, 'behavioral_hard_split': ${WEIGHTS[behavioral_hard_split]}, 'behavioral_format': ${WEIGHTS[behavioral_format]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_word_boundary': ${RESULTS[behavioral_word_boundary]}, 'config_boundary': ${RESULTS[config_boundary]}, 'behavioral_hard_split': ${RESULTS[behavioral_hard_split]}, 'behavioral_format': ${RESULTS[behavioral_format]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
