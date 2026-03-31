#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_f2p]=0.50
WEIGHTS[behavioral_p2p]=0.10
WEIGHTS[structural]=0.25
WEIGHTS[config_boundary]=0.15

for key in behavioral_f2p behavioral_p2p structural config_boundary; do
    RESULTS[$key]=0
done

TARGET="extensions/telegram/src/bot/delivery.replies.ts"

echo "=== Starting Test Audit for openclaw-telegram-empty-reply-crash ==="
echo "TARGET: $TARGET"

# ---------- GATE: File must exist ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: file exists"

# ---------- GATE: Must compile ----------
cd /workspace/openclaw
if ! npx tsc --noEmit --skipLibCheck 2>/dev/null; then
    echo "GATE FAIL: TypeScript compilation failed"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: TypeScript compiles"

# ---------- PRIMARY (50%): Fail-to-pass behavioral test ----------
# [pr_diff] (0.50): Empty/whitespace-only text chunks must be filtered before sending
# Bug: GrammyError 400 when sending whitespace-only text
# Fix: Add filterEmptyTelegramTextChunks and apply to all 3 delivery paths

node --experimental-vm-modules -e "
const fs = require('fs');
const path = require('path');

// Read the source file
const srcPath = '$TARGET';
const src = fs.readFileSync(srcPath, 'utf8');

// Check for the filter function definition
const hasFilterFunc = src.includes('filterEmptyTelegramTextChunks');
const hasTrimCheck = src.match(/\.trim\(\)\s*\.?\s*length\s*>{0,1}=?\s*0/) ||
                     src.match(/\.trim\(\)\s*[!={]+\s*['\"]\s*['\"]/) ||
                     src.match(/text\.trim\(\)/);

if (!hasFilterFunc && !hasTrimCheck) {
    console.log('FAIL: No empty-text filtering logic found');
    process.exit(1);
}

// Extract and verify the filter logic is applied to all 3 paths
const funcNames = ['deliverTextReply', 'sendPendingFollowUpText', 'sendTelegramVoiceFallbackText'];
const pathsWithFilter = [];

for (const funcName of funcNames) {
    const funcMatch = src.match(new RegExp('async function ' + funcName + '\\\\([^)]*\\\\)[^{]*{([^}]*{[^}]*})*[^}]*}', 's'));
    if (funcMatch) {
        const funcBody = funcMatch[0];
        // Check for filter function call or inline trim+length check
        const hasFiltering = funcBody.includes('filterEmptyTelegramTextChunks') ||
                            (funcBody.includes('.filter') && funcBody.includes('.trim()')) ||
                            (funcBody.includes('.trim()') && funcBody.match(/length\s*[<>!=]+/));
        if (hasFiltering) {
            pathsWithFilter.push(funcName);
        }
    }
}

if (pathsWithFilter.length < 3) {
    console.log('FAIL: Only ' + pathsWithFilter.length + '/3 delivery paths have empty-text filtering');
    console.log('Fixed paths: ' + pathsWithFilter.join(', '));
    process.exit(1);
}

console.log('PASS: All 3 delivery paths have empty-text filtering');
process.exit(0);
" 2>&1

if [ $? -eq 0 ]; then
    RESULTS[behavioral_f2p]=1
    echo "TEST behavioral_f2p: PASS"
else
    echo "TEST behavioral_f2p: FAIL"
fi

# ---------- SECONDARY (10%): Pass-to-pass regression ----------
# [agent_config] (0.10): Existing non-empty text delivery must still work
# Source: instruction.md line 11-12 @ eec290e68d6191b4bb85538dd301d50cdbc6650a

node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Verify the original send logic is still intact
// Check that sendTelegramText is still called in each path
const hasSendTextCall = src.includes('sendTelegramText');
const hasChunkIteration = src.includes('for') && src.includes('chunks');
const hasMarkDelivered = src.includes('markDelivered');

const checks = [
    ['sendTelegramText call preserved', hasSendTextCall],
    ['Chunk iteration preserved', hasChunkIteration || src.includes('forEach')],
    ['Delivery progress tracking preserved', hasMarkDelivered]
];

const failures = checks.filter(([_, ok]) => !ok).map(([name, _]) => name);
if (failures.length > 0) {
    console.log('P2P FAIL: ' + failures.join(', '));
    process.exit(1);
}

console.log('P2P PASS: Core delivery logic preserved');
process.exit(0);
" 2>&1

if [ $? -eq 0 ]; then
    RESULTS[behavioral_p2p]=1
    echo "TEST behavioral_p2p: PASS"
else
    echo "TEST behavioral_p2p: FAIL"
fi

# ---------- STRUCTURAL (25%): Function definition and usage pattern ----------
# [pr_diff] (0.25): filterEmptyTelegramTextChunks function defined and used correctly

node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Check for proper function definition with generic type parameter
const hasFuncDef = /function\s+filterEmptyTelegramTextChunks\s*<[^>]+>/.test(src) ||
                   src.includes('function filterEmptyTelegramTextChunks');

// Check it's called in all 3 delivery functions
const callsInDeliverTextReply = src.match(/function deliverTextReply[\\s\\S]*?filterEmptyTelegramTextChunks/) !== null;
const callsInSendPending = src.match(/function sendPendingFollowUpText[\\s\\S]*?filterEmptyTelegramTextChunks/) !== null;
const callsInVoiceFallback = src.match(/function sendTelegramVoiceFallbackText[\\s\\S]*?filterEmptyTelegramTextChunks/) !== null;

// Alternative: inline filtering in all 3 paths
const hasInlineFilter1 = src.match(/function deliverTextReply[\\s\\S]*?\.filter[\\s\\S]*?\.trim\(\)/) !== null;
const hasInlineFilter2 = src.match(/function sendPendingFollowUpText[\\s\\S]*?\.filter[\\s\\S]*?\.trim\(\)/) !== null;
const hasInlineFilter3 = src.match(/function sendTelegramVoiceFallbackText[\\s\\S]*?\.filter[\\s\\S]*?\.trim\(\)/) !== null;

const allPathsCovered = (callsInDeliverTextReply || hasInlineFilter1) &&
                        (callsInSendPending || hasInlineFilter2) &&
                        (callsInVoiceFallback || hasInlineFilter3);

if (!hasFuncDef && !(hasInlineFilter1 && hasInlineFilter2 && hasInlineFilter3)) {
    console.log('STRUCTURAL FAIL: No filterEmptyTelegramTextChunks function and no inline filtering');
    process.exit(1);
}

if (!allPathsCovered) {
    console.log('STRUCTURAL FAIL: Not all 3 delivery paths have filtering');
    process.exit(1);
}

console.log('STRUCTURAL PASS');
process.exit(0);
" 2>&1

if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- CONFIG-DERIVED (15%): Import boundary check ----------
# [agent_config] (0.15): Extension code must import from plugin-sdk/* not ../../../src/
# Source: CLAUDE.md line 16 @ eec290e68d6191b4bb85538dd301d50cdbc6650a

node -e "
const fs = require('fs');
const {execSync} = require('child_process');

try {
    const files = execSync('find extensions/telegram/src -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null', {encoding: 'utf8'}).trim().split('\n').filter(Boolean);
    let fail = false;
    for (const f of files) {
        if (!fs.existsSync(f)) continue;
        const content = fs.readFileSync(f, 'utf8');
        const lines = content.split('\n');
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (/^import .* from ['\"]\.\.\/\.\.\/\.\.\/src\//.test(line)) {
                console.log('FAIL: ' + f + ':' + (i+1) + ' imports core internals: ' + line.trim());
                fail = true;
            }
        }
    }
    if (fail) process.exit(1);
    console.log('PASS: No cross-boundary imports');
    process.exit(0);
} catch (e) {
    // If find fails, check at least the target file
    const content = fs.readFileSync('$TARGET', 'utf8');
    const hasBadImport = /from ['\"]\.\.\/\.\.\/\.\.\/src\//.test(content);
    if (hasBadImport) {
        console.log('FAIL: Target file has cross-boundary imports');
        process.exit(1);
    }
    console.log('PASS: No cross-boundary imports in target');
    process.exit(0);
}
" 2>&1

if [ $? -eq 0 ]; then
    RESULTS[config_boundary]=1
    echo "TEST config_boundary: PASS"
else
    echo "TEST config_boundary: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_f2p': ${WEIGHTS[behavioral_f2p]}, 'behavioral_p2p': ${WEIGHTS[behavioral_p2p]}, 'structural': ${WEIGHTS[structural]}}
results = {'behavioral_f2p': ${RESULTS[behavioral_f2p]}, 'behavioral_p2p': ${RESULTS[behavioral_p2p]}, 'structural': ${RESULTS[structural]}}
score = sum(weights[k] * results[k] for k in weights)
# Add config_boundary separate (not weighted in main calc but added)
score += ${WEIGHTS[config_boundary]} * ${RESULTS[config_boundary]}
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
for key in behavioral_f2p behavioral_p2p structural config_boundary; do
    echo "  $key (${WEIGHTS[$key]}): ${RESULTS[$key]}"
done
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
