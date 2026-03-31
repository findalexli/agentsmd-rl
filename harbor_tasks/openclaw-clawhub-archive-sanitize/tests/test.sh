#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_package]=0.35
WEIGHTS[behavioral_skill]=0.35
WEIGHTS[upstream_tests]=0.15
WEIGHTS[antistub]=0.10
WEIGHTS[config_nocheck]=0.05

for key in behavioral_package behavioral_skill upstream_tests antistub config_nocheck; do
    RESULTS[$key]=0
done

TARGET="src/infra/clawhub.ts"
TEST_FILE="src/infra/clawhub.test.ts"

# ---------- GATE: Target file must exist ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- GATE: Code must compile ----------
if command -v npx 2>/dev/null && [ -f "package.json" ]; then
    npx tsc --noEmit "$TARGET" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAIL: $TARGET does not compile"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
fi

# ---------- PRIMARY 1 (35%): Package archive path is sanitized ----------
# [pr_diff] Fail-to-pass: scoped package names create flat filenames
node -e "
const fs = require('fs');
const path = require('path');
const os = require('os');

// Read the source
const src = fs.readFileSync('$TARGET', 'utf8');

// Extract the function using regex - but strip comments first
const srcNoComments = src.replace(/\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Find downloadClawHubPackageArchive function body
const fnMatch = srcNoComments.match(/function\s+downloadClawHubPackageArchive\s*\([^)]*\)\s*\{([\s\S]*?)\n\}/);
if (!fnMatch) {
    console.log('FAIL: downloadClawHubPackageArchive function not found');
    process.exit(1);
}

const fnBody = fnMatch[1];

// Extract params handling - look for archive path construction
const archivePathMatch = fnBody.match(/archivePath\s*=\s*([^;]+);/);
if (!archivePathMatch) {
    console.log('FAIL: archive path construction not found');
    process.exit(1);
}

const archivePathExpr = archivePathMatch[1];

// Check 1: params.name should NOT be used directly in the path (without sanitization)
// The bug is: path.join(tmpDir, '\${params.name}.zip') - this fails for scoped names
if (archivePathExpr.includes('\${params.name}.zip') || archivePathExpr.includes('params.name + \".zip\"')) {
    console.log('FAIL: params.name used directly in archive path (no sanitization)');
    process.exit(1);
}

// Check 2: params.name must be transformed somehow before use
// Valid transforms: safeDirName(), replace(), replaceAll(), split().join(), regex replace
const hasSanitization =
    /safeDirName\s*\(\s*[^)]*params\.name/.test(archivePathExpr) ||
    /params\.name\s*\.\s*(replace|replaceAll)\s*\(/.test(archivePathExpr) ||
    /params\.name\s*\.\s*split\s*\([^)]+\)\s*\.\s*join\s*\(/.test(archivePathExpr);

if (!hasSanitization) {
    console.log('FAIL: params.name not sanitized before use in path');
    process.exit(1);
}

console.log('PASS: Package archive path is sanitized');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_package]=1; echo "TEST behavioral_package: PASS"; else echo "TEST behavioral_package: FAIL"; fi

# ---------- PRIMARY 2 (35%): Skill archive path is sanitized ----------
# [pr_diff] Fail-to-pass: skill slugs with slashes create flat filenames
node -e "
const fs = require('fs');
const path = require('path');

// Read the source and strip comments
const src = fs.readFileSync('$TARGET', 'utf8');
const srcNoComments = src.replace(/\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Find downloadClawHubSkillArchive function body
const fnMatch = srcNoComments.match(/function\s+downloadClawHubSkillArchive\s*\([^)]*\)\s*\{([\s\S]*?)\n\}/);
if (!fnMatch) {
    console.log('FAIL: downloadClawHubSkillArchive function not found');
    process.exit(1);
}

const fnBody = fnMatch[1];

// Extract params handling
const archivePathMatch = fnBody.match(/archivePath\s*=\s*([^;]+);/);
if (!archivePathMatch) {
    console.log('FAIL: archive path construction not found');
    process.exit(1);
}

const archivePathExpr = archivePathMatch[1];

// Check 1: params.slug should NOT be used directly
if (archivePathExpr.includes('\${params.slug}.zip') || archivePathExpr.includes('params.slug + \".zip\"')) {
    console.log('FAIL: params.slug used directly in archive path (no sanitization)');
    process.exit(1);
}

// Check 2: params.slug must be transformed
const hasSanitization =
    /safeDirName\s*\(\s*[^)]*params\.slug/.test(archivePathExpr) ||
    /params\.slug\s*\.\s*(replace|replaceAll)\s*\(/.test(archivePathExpr) ||
    /params\.slug\s*\.\s*split\s*\([^)]+\)\s*\.\s*join\s*\(/.test(archivePathExpr);

if (!hasSanitization) {
    console.log('FAIL: params.slug not sanitized before use in path');
    process.exit(1);
}

console.log('PASS: Skill archive path is sanitized');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_skill]=1; echo "TEST behavioral_skill: PASS"; else echo "TEST behavioral_skill: FAIL"; fi

# ---------- PASS-TO-PASS: Upstream test suite (15%) ----------
# [pr_diff] Verify fix doesn't break existing functionality
if [ -f "$TEST_FILE" ]; then
    # Check if the test file has the fail-to-pass tests from the PR
    if grep -q "scoped package archives to a safe temp file name" "$TEST_FILE" 2>/dev/null && \
       grep -q "skill archives to a safe temp file name" "$TEST_FILE" 2>/dev/null; then
        # Try to run the tests if vitest is available
        if [ -f "package.json" ] && grep -q "vitest" "package.json" 2>/dev/null; then
            npm test -- --run src/infra/clawhub.test.ts 2>/dev/null
            if [ $? -eq 0 ]; then
                RESULTS[upstream_tests]=1
                echo "TEST upstream_tests: PASS"
            else
                echo "TEST upstream_tests: FAIL (tests failed)"
            fi
        else
            # Can't run tests, but tests exist - give partial credit
            RESULTS[upstream_tests]=0.5
            echo "TEST upstream_tests: PARTIAL (tests exist but cannot run)"
        fi
    else
        echo "TEST upstream_tests: FAIL (fail-to-pass tests not added)"
    fi
else
    echo "TEST upstream_tests: FAIL (test file not found)"
fi

# ---------- Anti-stub (10%) ----------
# Verify the implementation is substantial and not just keyword stuffing
node -e "
const fs = require('fs');

// Read source and strip all comments
let src = fs.readFileSync('$TARGET', 'utf8');

// Remove single-line comments
src = src.replace(/\/\/[^\n]*/g, '');
// Remove multi-line comments
src = src.replace(/\/\*[\s\S]*?\*\//g, '');
// Remove string literals (to avoid counting keywords in strings)
src = src.replace(/'[^']*'/g, \"\").replace(/'[^']*'/g, \"\");
src = src.replace(\`\"[^\"]*\"\`, \"\").replace(\`\"[^\"]*\"\`, \"\");
src = src.replace(\`/\`[^\`]*\`/\`, \"\");

const checks = [
    // Must have actual function implementations (more than just signatures)
    [src.includes('async function downloadClawHubPackageArchive') || src.includes('function downloadClawHubPackageArchive'), 'package function defined'],
    [src.includes('async function downloadClawHubSkillArchive') || src.includes('function downloadClawHubSkillArchive'), 'skill function defined'],

    // Must actually call path.join or equivalent (not just mention it in comments)
    [/(path\.)?join\s*\(/.test(src), 'path.join called'],

    // Must write to file (not just mention fs.writeFile)
    [/fs\.writeFile\s*\(/.test(src), 'fs.writeFile called'],

    // Must have the actual archive path assignment
    [/archivePath\s*=/.test(src), 'archivePath assigned'],

    // Function bodies should be substantial (not just throw/pass)
    [src.split('\n').filter(l => l.trim() && !l.trim().startsWith('import') && !l.trim().startsWith('export')).length > 20, 'substantial code'],
];

const failures = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (failures.length > 0) {
    console.log('FAIL: ' + failures.join(', '));
    process.exit(1);
}
console.log('PASS: Implementation is substantial');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi

# ---------- Config-derived test (5%): No @ts-nocheck or @ts-ignore ----------
# [agent_config] "Never add @ts-nocheck" - root CLAUDE.md @ 7a16a481983e62bc3394c7c5f90d320b6be82f0e
node -e "
const fs = require('fs');
const {execSync} = require('child_process');

// Check all TypeScript files in src/infra (excluding test files)
let files = [];
try {
    const output = execSync('find src/infra -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null', {encoding: 'utf8'});
    files = output.trim().split('\n').filter(Boolean);
} catch(e) {}

let fail = false;
for (const f of files) {
    try {
        const content = fs.readFileSync(f, 'utf8');
        // Check directives - these can only appear at start of file, not in comments elsewhere
        if (content.match(/^\s*\/\*\s*@ts-nocheck/) || content.match(/^\s*\/\/\s*@ts-nocheck/) ||
            content.match(/^\s*\/\*\s*@ts-ignore/) || content.match(/^\s*\/\/\s*@ts-ignore/)) {
            console.log('FAIL: ' + f + ' contains @ts-nocheck or @ts-ignore directive');
            fail = true;
        }
    } catch(e) {}
}
if (fail) process.exit(1);
console.log('PASS: no @ts-nocheck/@ts-ignore directives found');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[config_nocheck]=1; echo "TEST config_nocheck: PASS"; else echo "TEST config_nocheck: FAIL"; fi

# Calculate final score
SCORE=$(python3 -c "
w = {
    'behavioral_package': ${WEIGHTS[behavioral_package]},
    'behavioral_skill': ${WEIGHTS[behavioral_skill]},
    'upstream_tests': ${WEIGHTS[upstream_tests]},
    'antistub': ${WEIGHTS[antistub]},
    'config_nocheck': ${WEIGHTS[config_nocheck]}
}
r = {
    'behavioral_package': ${RESULTS[behavioral_package]},
    'behavioral_skill': ${RESULTS[behavioral_skill]},
    'upstream_tests': ${RESULTS[upstream_tests]},
    'antistub': ${RESULTS[antistub]},
    'config_nocheck': ${RESULTS[config_nocheck]}
}
score = sum(w[k] * r[k] for k in w)
print(f'{score:.2f}')
")

echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# Optional: Write detailed breakdown
echo "{\"reward\": $SCORE, \"behavioral_package\": ${RESULTS[behavioral_package]}, \"behavioral_skill\": ${RESULTS[behavioral_skill]}, \"upstream_tests\": ${RESULTS[upstream_tests]}, \"antistub\": ${RESULTS[antistub]}, \"config_nocheck\": ${RESULTS[config_nocheck]}}" > "${REWARD_FILE%.txt}.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
