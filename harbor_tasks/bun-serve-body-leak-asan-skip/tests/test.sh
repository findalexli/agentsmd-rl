#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/bun

TARGET="test/js/bun/http/serve-body-leak.test.ts"

##############################################################################
# GATE: Target file exists and is non-empty
##############################################################################
# [pr_diff] (gate): serve-body-leak.test.ts must exist
if [ ! -s "$TARGET" ]; then
    echo "GATE FAILED: $TARGET missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass (0.45)
# Evaluate the actual skip conditions with isASAN=true. On the buggy baseline,
# the condition is `skip || (isFlaky && isWindows)` which does NOT skip when
# isASAN=true. A correct fix makes the condition evaluate to true.
##############################################################################

# [pr_diff] (0.45): When isASAN=true, memory leak tests are skipped
# Accepts: todoIf/skipIf with isASAN, describe.skipIf(isASAN), if(!isASAN) block
add_total 0.45
F2P_ASAN_SKIP=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');

// Bind variables: isASAN=true, everything else false/default
const isASAN = true;
const isFlaky = false;
const isWindows = false;
const isLinux = false;
const isMacOS = false;
const isDebug = false;
const isCI = false;
const skip = false;

let skipped = false;

// Check describe.skipIf(condition) — skips entire block
const descSkips = text.match(/describe\.skipIf\(([^)]+)\)/g) || [];
for (const m of descSkips) {
    const cond = m.match(/describe\.skipIf\(([^)]+)\)/)[1];
    try { if (eval(cond)) { skipped = true; break; } } catch(e) {}
}

// Check it.todoIf(condition) and it.skipIf(condition)
const itSkips = text.match(/it\.(todoIf|skipIf)\(([^)]+)\)/g) || [];
for (const m of itSkips) {
    const cond = m.match(/it\.(todoIf|skipIf)\(([^)]+)\)/)[2];
    try { if (eval(cond)) { skipped = true; break; } } catch(e) {}
}

// Check if(!isASAN) or if(isASAN) wrapping patterns
if (/if\s*\(\s*!?\s*isASAN\s*\)/.test(text)) { skipped = true; }

console.log(skipped ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$F2P_ASAN_SKIP" = "PASS" ]; then
    add_score 0.45
    echo "PASS [0.45]: isASAN=true causes memory leak tests to be skipped"
else
    echo "FAIL [0.45]: isASAN=true does not cause tests to be skipped"
fi

##############################################################################
# BEHAVIORAL: Pass-to-pass (0.15)
# When isASAN=false, the tests should still run (condition = false).
##############################################################################

# [pr_diff] (0.15): When isASAN=false (normal build), tests are NOT skipped
add_total 0.15
P2P_NON_ASAN=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');

// Bind: isASAN=false, normal non-flaky non-Windows build
const isASAN = false;
const isFlaky = false;
const isWindows = false;
const isLinux = true;
const isMacOS = false;
const isDebug = false;
const isCI = false;
const skip = false;

let wouldSkip = false;

// Check describe-level skip
const descSkips = text.match(/describe\.skipIf\(([^)]+)\)/g) || [];
for (const m of descSkips) {
    const cond = m.match(/describe\.skipIf\(([^)]+)\)/)[1];
    try { if (eval(cond)) { wouldSkip = true; break; } } catch(e) {}
}

// Check it-level todoIf/skipIf — find conditions near 'should not leak memory' tests
const itSkips = text.match(/it\.(todoIf|skipIf)\(([^)]+)\)/g) || [];
for (const m of itSkips) {
    const cond = m.match(/it\.(todoIf|skipIf)\(([^)]+)\)/)[2];
    try { if (eval(cond)) { wouldSkip = true; break; } } catch(e) {}
}

// if(isASAN) { return } would not trigger with isASAN=false, so fine
// if(!isASAN) { tests } would run tests, so fine

console.log(!wouldSkip ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$P2P_NON_ASAN" = "PASS" ]; then
    add_score 0.15
    echo "PASS [0.15]: tests still run when isASAN=false (normal build)"
else
    echo "FAIL [0.15]: tests incorrectly skipped on non-ASAN build"
fi

##############################################################################
# STRUCTURAL: Import + anti-stub (0.15)
##############################################################################

# [pr_diff] (0.10): isASAN is imported from the harness module
add_total 0.10
ASAN_IMPORT=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');
// Accept: import { ..., isASAN, ... } from 'harness'
// Accept: const { ..., isASAN, ... } = require('harness')
const hasImport = /import\s*\{[^}]*\bisASAN\b[^}]*\}\s*from\s*['\"]harness['\"]/.test(text)
    || /(?:const|let|var)\s*\{[^}]*\bisASAN\b[^}]*\}\s*=\s*require\s*\(\s*['\"]harness['\"]\s*\)/.test(text);
console.log(hasImport ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$ASAN_IMPORT" = "PASS" ]; then
    add_score 0.10
    echo "PASS [0.10]: isASAN imported from harness"
else
    echo "FAIL [0.10]: isASAN not imported from harness"
fi

# [pr_diff] (0.05): File retains substantial test logic (anti-stub)
add_total 0.05
FILE_LINES=$(wc -l < "$TARGET")
if [ "$FILE_LINES" -gt 140 ]; then
    add_score 0.05
    echo "PASS [0.05]: anti-stub — file has $FILE_LINES lines"
else
    echo "FAIL [0.05]: file suspiciously small ($FILE_LINES lines)"
fi

##############################################################################
# REGRESSION: Existing behavior preserved (0.10)
##############################################################################

# [pr_diff] (0.05): All 7 original test case names are preserved
add_total 0.05
TESTS_PRESERVED=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');
const expected = [
    'should not leak memory when ignoring the body',
    'should not leak memory when buffering the body',
    'should not leak memory when streaming the body',
    'should not leak memory when using Bun.file()',
    'should not leak memory when converting the body to JSON',
    'should not leak memory when getting the text of the body',
    'should not leak memory when streaming the body and echoing it back',
];
const found = expected.filter(t => text.includes(t)).length;
console.log(found >= 6 ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$TESTS_PRESERVED" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: original test case names preserved"
else
    echo "FAIL [0.05]: original test case names missing"
fi

# [pr_diff] (0.05): Existing isFlaky && isWindows skip condition still present
add_total 0.05
OTHER_SKIPS=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');
console.log(/isFlaky\s*&&\s*isWindows/.test(text) ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$OTHER_SKIPS" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: existing isFlaky && isWindows skip preserved"
else
    echo "FAIL [0.05]: existing skip conditions altered or removed"
fi

##############################################################################
# CONFIG-DERIVED: Agent config rules (0.10)
##############################################################################

# [agent_config] (0.05): "Do not write flaky tests" — CLAUDE.md:102
# Skip condition uses deterministic build flag, not timing heuristics
add_total 0.05
NO_FLAKY=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');
// Extract all todoIf/skipIf conditions
const re = /it\.(todoIf|skipIf)\(([^)]+)\)/g;
const conditions = [];
let m;
while ((m = re.exec(text)) !== null) conditions.push(m[2]);
// Check none use non-deterministic patterns
const hasBad = conditions.some(c =>
    /setTimeout|Math\.random|Date\.now|performance\.now/.test(c)
);
console.log(!hasBad ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$NO_FLAKY" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: skip condition uses deterministic detection (CLAUDE.md:102)"
else
    echo "FAIL [0.05]: skip condition uses non-deterministic approach"
fi

# [agent_config] (0.05): "Follow existing code style" — CLAUDE.md:228
# Uses standard skip mechanisms, not process.exit or early return
add_total 0.05
STYLE_OK=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');
// Acceptable: todoIf, skipIf, describe.skipIf, or if-block with isASAN
const usesStandard = /(todoIf|skipIf)\([^)]*isASAN/.test(text)
    || /if\s*\(\s*!?\s*isASAN\s*\)/.test(text)
    || /describe\.skipIf\([^)]*isASAN/.test(text);
// Reject: process.exit to skip
const hasBad = /process\.exit\s*\(/.test(text) && /isASAN/.test(text);
console.log(usesStandard && !hasBad ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$STYLE_OK" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: uses standard skip pattern (CLAUDE.md:228)"
else
    echo "FAIL [0.05]: non-standard skip mechanism used"
fi

##############################################################################
# STYLE RUBRIC: Documentation (0.05)
##############################################################################

# [pr_diff] (0.05): Comment near skip condition explains ASAN rationale
add_total 0.05
ASAN_COMMENT=$(node -e "
const fs = require('fs');
const text = fs.readFileSync(process.argv[1], 'utf8');
// Comment mentioning ASAN + a reason (RSS, memory, timeout, quarantine, overhead)
const hasComment = /\/\/.*(?:ASAN|asan|AddressSanitizer).*(?:RSS|memory|timeout|quarantine|overhead|inflate|slow)/i.test(text)
    || /\/\/.*(?:RSS|memory|timeout|quarantine|overhead|inflate|slow).*(?:ASAN|asan|AddressSanitizer)/i.test(text)
    || /\/\*[\s\S]{0,200}?(?:ASAN|AddressSanitizer)[\s\S]{0,200}?(?:RSS|memory|timeout)[\s\S]*?\*\//i.test(text);
console.log(hasComment ? 'PASS' : 'FAIL');
" "$TARGET" 2>/dev/null)
if [ "$ASAN_COMMENT" = "PASS" ]; then
    add_score 0.05
    echo "PASS [0.05]: comment explains ASAN skip rationale"
else
    echo "FAIL [0.05]: missing comment explaining why ASAN is skipped"
fi

##############################################################################
# Final scoring
##############################################################################

FINAL=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "Total: $FINAL / $TOTAL"
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
behavioral = 0.0
regression = 0.0
config = 0.0
style = 0.0

# Behavioral (F2P + P2P)
behavioral += 0.45 if '$F2P_ASAN_SKIP' == 'PASS' else 0
behavioral += 0.15 if '$P2P_NON_ASAN' == 'PASS' else 0

# Structural (import + anti-stub) counted toward regression bucket
regression += 0.10 if '$ASAN_IMPORT' == 'PASS' else 0
regression += 0.05 if int('$FILE_LINES') > 140 else 0
regression += 0.05 if '$TESTS_PRESERVED' == 'PASS' else 0
regression += 0.05 if '$OTHER_SKIPS' == 'PASS' else 0

# Config
config += 0.05 if '$NO_FLAKY' == 'PASS' else 0
config += 0.05 if '$STYLE_OK' == 'PASS' else 0

# Style
style += 0.05 if '$ASAN_COMMENT' == 'PASS' else 0

score = round(behavioral + regression + config + style, 4)
data = {
    'reward': score,
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': round(style, 4),
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
