#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_package]=0.30
WEIGHTS[behavioral_skill]=0.30
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15
WEIGHTS[config_nocheck]=0.05

for key in behavioral_package behavioral_skill structural antistub config_nocheck; do
    RESULTS[$key]=0
done

TARGET="src/infra/clawhub.ts"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (30%): Package archive path sanitized ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Find downloadClawHubPackageArchive function
const fnStart = src.indexOf('downloadClawHubPackageArchive');
if (fnStart < 0) {
    console.log('FAIL: downloadClawHubPackageArchive not found');
    process.exit(1);
}

const fnBody = src.substring(fnStart, src.indexOf('export', fnStart + 10) || src.length);

// The archive path must NOT use raw params.name directly
// It should use safeDirName or equivalent sanitization
if (fnBody.includes('\`\${params.name}.zip\`') && !fnBody.includes('safeDirName')) {
    console.log('FAIL: still uses raw params.name in archive path');
    process.exit(1);
}

// Must use safeDirName or equivalent
if (!fnBody.includes('safeDirName') && !fnBody.includes('replace') && !fnBody.includes('replaceAll')) {
    console.log('FAIL: no path sanitization for package name');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_package]=1; echo "TEST behavioral_package: PASS"; else echo "TEST behavioral_package: FAIL"; fi

# ---------- PRIMARY 2 (30%): Skill archive path sanitized ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

const fnStart = src.indexOf('downloadClawHubSkillArchive');
if (fnStart < 0) {
    console.log('FAIL: downloadClawHubSkillArchive not found');
    process.exit(1);
}

const fnBody = src.substring(fnStart, src.indexOf('export', fnStart + 10) || src.length);

if (fnBody.includes('\`\${params.slug}.zip\`') && !fnBody.includes('safeDirName')) {
    console.log('FAIL: still uses raw params.slug in archive path');
    process.exit(1);
}

if (!fnBody.includes('safeDirName') && !fnBody.includes('replace') && !fnBody.includes('replaceAll')) {
    console.log('FAIL: no path sanitization for skill slug');
    process.exit(1);
}

console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[behavioral_skill]=1; echo "TEST behavioral_skill: PASS"; else echo "TEST behavioral_skill: FAIL"; fi

# ---------- SUPPLEMENTARY (20%): Structural ----------
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');

// Should import safeDirName
if (!src.includes('safeDirName') && !src.includes('sanitize')) {
    // Check for inline sanitization
    if (!src.includes('replace(/\\\\//g') && !src.includes('replaceAll')) {
        console.log('FAIL: no import of safeDirName or inline sanitization');
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
    [src.split('\n').length > 100, 'substantial content'],
    [src.includes('downloadClawHubPackageArchive'), 'package download fn'],
    [src.includes('downloadClawHubSkillArchive'), 'skill download fn'],
    [src.includes('archivePath'), 'archive path handling'],
    [src.includes('writeFile') || src.includes('fs.'), 'file operations'],
];
const f = checks.filter(([ok]) => !ok).map(([, d]) => d);
if (f.length > 0) { console.log('FAIL: ' + f.join(', ')); process.exit(1); }
console.log('PASS');
" 2>&1
if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi


# ---------- Config-derived test (0.05): "Never add @ts-nocheck" ----------
# Source: CLAUDE.md line 146 @ 7a16a481983e62bc3394c7c5f90d320b6be82f0e
node -e "
const fs = require('fs');
const {execSync} = require('child_process');
const files = execSync('find src/infra -name \"*.ts\" -not -name \"*.test.ts\" -not -name \"*.d.ts\" 2>/dev/null || true', {encoding: 'utf8'}).trim().split('\\n').filter(Boolean);
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
w = {'behavioral_package': ${WEIGHTS[behavioral_package]}, 'config_nocheck': ${WEIGHTS[config_nocheck]}, 'behavioral_skill': ${WEIGHTS[behavioral_skill]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'behavioral_package': ${RESULTS[behavioral_package]}, 'config_nocheck': ${RESULTS[config_nocheck]}, 'behavioral_skill': ${RESULTS[behavioral_skill]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
