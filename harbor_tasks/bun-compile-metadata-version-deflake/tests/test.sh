#!/usr/bin/env bash
set +e

EARNED=0
TOTAL_WEIGHT=0

add() {
    # $1 = weight, $2 = earned (1 or 0)
    TOTAL_WEIGHT=$(python3 -c "print($TOTAL_WEIGHT + $1)")
    if [ "$2" -eq 1 ]; then
        EARNED=$(python3 -c "print($EARNED + $1)")
    fi
}

cd /workspace/bun

TEST_FILE="test/bundler/compile-windows-metadata.test.ts"
ORIG_FILE=$(git show HEAD:"$TEST_FILE" 2>/dev/null)

##############################################################################
# GATE: File exists, is substantive, and is valid JS/TS syntax
##############################################################################
# [pr_diff] (gate): Test file must exist, not be a stub, and parse as valid syntax
if [ ! -s "$TEST_FILE" ]; then
    echo "GATE FAILED: $TEST_FILE missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

LINE_COUNT=$(wc -l < "$TEST_FILE")
if [ "$LINE_COUNT" -lt 280 ]; then
    echo "GATE FAILED: File too short ($LINE_COUNT lines). Original is ~360 lines; a valid fix changes ~40 lines."
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# Syntax gate: file must parse as valid JavaScript/TypeScript
# (strips type annotations that trip up basic parsers)
SYNTAX_OK=$(node -e "
const fs = require('fs');
let text = fs.readFileSync('$TEST_FILE', 'utf8');
// Strip TS-only syntax so acorn/node can parse structure
// Remove import type, type annotations after colons, angle bracket generics
// We just need to verify it's not syntactic garbage
try {
    // Use a simple heuristic: balanced braces
    let depth = 0;
    for (const ch of text) {
        if (ch === '{') depth++;
        else if (ch === '}') depth--;
        if (depth < 0) throw new Error('unbalanced');
    }
    if (depth !== 0) throw new Error('unbalanced');
    process.stdout.write('PASS');
} catch(e) {
    process.stdout.write('FAIL');
}
" 2>/dev/null)

if [ "$SYNTAX_OK" != "PASS" ]; then
    echo "GATE FAILED: File has unbalanced braces (likely broken syntax)"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

GATE_PASSED=1
echo "GATE PASSED: File exists, substantive ($LINE_COUNT lines), balanced syntax"

##############################################################################
# FAIL-TO-PASS: Core bug fix (0.60)
# These are structural checks because the bun test harness is not available.
# Each check verifies the behavioral intent through code analysis.
##############################################################################

# [pr_diff] (0.25): FAIL-TO-PASS — The buggy baseline has a for-loop over
# invalidVersions containing Bun.spawn. The fix must remove this pattern.
# We verify: (a) the ORIGINAL file has the bug, (b) the MODIFIED file does not.
BASELINE_HAS_BUG=$(echo "$ORIG_FILE" | node -e "
const text = require('fs').readFileSync('/dev/stdin', 'utf8');
// Original must have the loop-over-versions pattern
const hasLoop = /for\s*\([^)]*\)\s*\{[\s\S]*?Bun\.spawn/s.test(text) ||
                /(?:const|let|var)\s+invalidVersions\s*=\s*\[/.test(text);
process.stdout.write(hasLoop ? 'YES' : 'NO');
" 2>/dev/null)

FIX_REMOVES_BUG=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
const hasLoop = /for\s*\([^)]*\)\s*\{[\s\S]*?Bun\.spawn/s.test(text);
const hasVersionArray = /(?:const|let|var)\s+invalidVersions\s*=\s*\[/.test(text);
const hasWhileLoop = /while\s*\([^)]*\)\s*\{[\s\S]*?Bun\.spawn/s.test(text);
process.stdout.write(!hasLoop && !hasVersionArray && !hasWhileLoop ? 'YES' : 'NO');
" 2>/dev/null)

if [ "$BASELINE_HAS_BUG" = "YES" ] && [ "$FIX_REMOVES_BUG" = "YES" ]; then
    echo "PASS [pr_diff] (0.25): Fail-to-pass — buggy loop removed"
    add 0.25 1
else
    echo "FAIL [pr_diff] (0.25): Fail-to-pass — baseline_has_bug=$BASELINE_HAS_BUG, fix_removes=$FIX_REMOVES_BUG"
    add 0.25 0
fi

# [pr_diff] (0.20): Each invalid version gets its own test case via ANY mechanism:
# test.each, describe.each, forEach/map generating tests, individual test()/it() calls,
# or describe() sub-blocks. Accepts any valid approach that isolates versions.
PARAMETERIZED=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
const versions = ['not.a.version', '1.2.3.4.5', '1.-2.3.4', '65536.0.0.0'];

// Count how many versions appear inside SEPARATE test/it/describe registrations.
// We look for each version appearing in its own test(...), it(...), or describe(...) block.
let separateCount = 0;

// Method 1: test.each / it.each / describe.each with version data
const eachMatch = text.match(/(?:test|it|describe)\.each\s*\((\[[\s\S]*?\])\)/);
if (eachMatch) {
    const matched = versions.filter(v => eachMatch[1].includes(v)).length;
    if (matched >= 3) separateCount = Math.max(separateCount, matched);
}
// template literal .each
const eachTpl = text.match(/(?:test|it|describe)\.each\x60([\s\S]*?)\x60/);
if (eachTpl) {
    const matched = versions.filter(v => eachTpl[1].includes(v)).length;
    if (matched >= 3) separateCount = Math.max(separateCount, matched);
}

// Method 2: forEach/map generating test registrations
if (/\.(?:forEach|map)\s*\([\s\S]*?(?:test|it|describe)\s*\(/.test(text)) {
    const matched = versions.filter(v => text.includes(v)).length;
    if (matched >= 3) separateCount = Math.max(separateCount, matched);
}

// Method 3: Individual test()/it()/describe() calls each referencing a version
// (in the name string or body)
let individual = 0;
for (const v of versions) {
    const escaped = v.replace(/[.*+?^\${}()|[\\]\\\\]/g, '\\\\$&');
    // Check: version appears in a test/it/describe call argument
    const pat = new RegExp('(?:test|it|describe)\\\\s*\\\\([^)]*' + escaped, 's');
    if (pat.test(text)) individual++;
}
if (individual >= 3) separateCount = Math.max(separateCount, individual);

process.stdout.write(separateCount >= 3 ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$PARAMETERIZED" = "PASS" ]; then
    echo "PASS [pr_diff] (0.20): Versions parameterized into individual test cases"
    add 0.20 1
else
    echo "FAIL [pr_diff] (0.20): Versions not split into individual test cases"
    add 0.20 0
fi

# [pr_diff] (0.10): All 5 invalid version strings must still be tested.
ALL_VERSIONS=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
const required = ['not.a.version', '1.2.3.4.5', '1.-2.3.4', '65536.0.0.0'];
const found = required.filter(v => text.includes(v)).length;
// Empty string: check various representations
const hasEmpty = /version['\"]?\s*[:,]\s*['\"]['\"]/.test(text) ||
                 /['\"]['\"]/.test(text) && /empty|invalid.*version/i.test(text) ||
                 text.includes('\"\"');
const total = found + (hasEmpty ? 1 : 0);
process.stdout.write(total >= 5 ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$ALL_VERSIONS" = "PASS" ]; then
    echo "PASS [pr_diff] (0.10): All 5 invalid versions present"
    add 0.10 1
else
    echo "FAIL [pr_diff] (0.10): Some invalid versions missing"
    add 0.10 0
fi

# [pr_diff] (0.05): Non-zero exit code assertion preserved.
# Accepts any assertion that verifies exitCode is non-zero:
# .not.toBe(0), .toBeGreaterThan(0), .toBeTruthy(), .toEqual(1),
# !== 0, > 0, etc.
EXIT_CHECK=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
const patterns = [
    /expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.not\s*\.toBe\s*\(\s*0\s*\)/,
    /expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.toBeGreaterThan\s*\(\s*0\s*\)/,
    /expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.not\s*\.toEqual\s*\(\s*0\s*\)/,
    /expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.not\s*\.toStrictEqual\s*\(\s*0\s*\)/,
    /expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.toBeTruthy/,
    /expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.toEqual\s*\(\s*[1-9]/,
    /expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.toBe\s*\(\s*[1-9]/,
    /assert.*[Ee]xit[Cc]ode\s*[!>]/,
    /[Ee]xit[Cc]ode\s*!==?\s*0/,
    /[Ee]xit[Cc]ode\s*>\s*0/,
];
const hasCheck = patterns.some(p => p.test(text));
process.stdout.write(hasCheck ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$EXIT_CHECK" = "PASS" ]; then
    echo "PASS [pr_diff] (0.05): Non-zero exit code assertion preserved"
    add 0.05 1
else
    echo "FAIL [pr_diff] (0.05): Exit code assertion missing"
    add 0.05 0
fi

##############################################################################
# PASS-TO-PASS: Regression (0.15)
##############################################################################

# [pr_diff] (0.05): Valid version parsing tests must be untouched.
VALID_TESTS=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
const hasValidVersions = text.includes('1.0.0.0') && text.includes('0.0.0.0');
process.stdout.write(hasValidVersions ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$VALID_TESTS" = "PASS" ]; then
    echo "PASS [pr_diff] (0.05): Valid version parse tests intact"
    add 0.05 1
else
    echo "FAIL [pr_diff] (0.05): Valid version tests damaged"
    add 0.05 0
fi

# [pr_diff] (0.05): Describe block structure preserved.
# Accept any reasonable variant of the describe block names.
STRUCTURE=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
// Must have a describe block related to Windows/compile/metadata
const hasMainDescribe = /describe\s*[\.(].*(?:Windows|compile|metadata)/i.test(text);
// Must have a describe block related to CLI flags
const hasCLIDescribe = /describe\s*[\.(].*(?:CLI|flags)/i.test(text);
process.stdout.write(hasMainDescribe && hasCLIDescribe ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$STRUCTURE" = "PASS" ]; then
    echo "PASS [pr_diff] (0.05): Describe structure preserved"
    add 0.05 1
else
    echo "FAIL [pr_diff] (0.05): Describe structure damaged"
    add 0.05 0
fi

# [pr_diff] (0.05): Other test blocks not modified (metadata flags tests exist).
OTHER_TESTS=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
// Accept variations: 'all metadata flags via CLI', 'all metadata flags', etc.
const hasAll = /(?:all|every)\s+metadata\s+flags/i.test(text);
const hasPartial = /partial\s+metadata\s+flags/i.test(text);
process.stdout.write(hasAll && hasPartial ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$OTHER_TESTS" = "PASS" ]; then
    echo "PASS [pr_diff] (0.05): Other test blocks preserved"
    add 0.05 1
else
    echo "FAIL [pr_diff] (0.05): Other test blocks damaged"
    add 0.05 0
fi

##############################################################################
# CONFIG-DERIVED (0.10)
##############################################################################

# [agent_config] (0.05): "Prefer concurrent tests" — test/AGENTS.md:20
# The parent describe uses .concurrent — verify it's preserved.
CONCURRENT=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
// describe.concurrent or describe.skipIf(...).concurrent must be present
const hasConcurrent = /describe(?:\.\w+\s*\([^)]*\))*\s*\.concurrent\s*\(/.test(text) ||
                      /describe\s*\.concurrent/.test(text);
process.stdout.write(hasConcurrent ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$CONCURRENT" = "PASS" ]; then
    echo "PASS [agent_config] (0.05): Concurrent test pattern preserved — test/AGENTS.md:20"
    add 0.05 1
else
    echo "FAIL [agent_config] (0.05): Concurrent test pattern broken"
    add 0.05 0
fi

# [agent_config] (0.05): "Do not write flaky tests" — test/AGENTS.md:20
# Anti-regression: no setTimeout or sleep calls added.
NO_FLAKY=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');
const hasSleep = /(?:setTimeout|sleep)\s*\(/.test(text);
process.stdout.write(!hasSleep ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$NO_FLAKY" = "PASS" ]; then
    echo "PASS [agent_config] (0.05): No flaky setTimeout/sleep added — test/AGENTS.md:20"
    add 0.05 1
else
    echo "FAIL [agent_config] (0.05): Flaky setTimeout/sleep pattern detected"
    add 0.05 0
fi

##############################################################################
# ANTI-GAMING: Substantive test bodies (0.05)
# Gated behind GATE_PASSED
##############################################################################

# [pr_diff] (0.05): Each invalid-version test must have a substantive body:
# - Bun.spawn invocation
# - await .exited
# - expect assertion
# A stub with empty test bodies or just keywords will fail this.
if [ "$GATE_PASSED" -eq 1 ]; then
    INTEGRITY=$(node -e "
const text = require('fs').readFileSync('$TEST_FILE', 'utf8');

// Count test blocks that contain ALL three: Bun.spawn, await...exited, expect
// This catches stubs that have keywords but not in the right test bodies.
// We split by test/it registrations and check each body.
const testBodies = text.match(/(?:test|it)\s*\([^,]*,\s*(?:async\s*)?\(?[^)]*\)?\s*(?:=>)?\s*\{[\s\S]*?\n\s*\}\s*[,\)]/g) || [];

let substantiveCount = 0;
for (const body of testBodies) {
    const hasSpawn = /Bun\.spawn\s*\(/.test(body);
    const hasExited = /\.exited/.test(body);
    const hasExpect = /expect\s*\(/.test(body);
    if (hasSpawn && hasExited && hasExpect) substantiveCount++;
}

// Must have at least 4 substantive test bodies (covering the invalid versions)
process.stdout.write(substantiveCount >= 4 ? 'PASS' : 'FAIL');
" 2>/dev/null)

    if [ "$INTEGRITY" = "PASS" ]; then
        echo "PASS [pr_diff] (0.05): >= 4 test bodies have Bun.spawn + await exited + expect"
        add 0.05 1
    else
        echo "FAIL [pr_diff] (0.05): Fewer than 4 substantive test bodies found"
        add 0.05 0
    fi
else
    echo "SKIP [pr_diff] (0.05): Gate failed, skipping integrity check"
    add 0.05 0
fi

##############################################################################
# FINAL SCORING
##############################################################################

REWARD=$(python3 -c "
t = $TOTAL_WEIGHT
e = $EARNED
print(round(e / t, 4) if t > 0 else 0.0)
")

echo ""
echo "TOTAL SCORE: $EARNED / $TOTAL_WEIGHT"
echo "REWARD: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Breakdown (approximate bucket assignment)
python3 -c "
import json
e = $EARNED
behavioral = min(e, 0.60)
regression = min(max(e - 0.60, 0), 0.15)
config = min(max(e - 0.75, 0), 0.10)
reward = round(e / $TOTAL_WEIGHT, 4) if $TOTAL_WEIGHT > 0 else 0.0
print(json.dumps({'reward': reward, 'behavioral': round(behavioral,4), 'regression': round(regression,4), 'config': round(config,4), 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
