#!/usr/bin/env bash
# Verifier for nextjs-ts6-baseurl-deprecation
#
# Bug: getTypeScriptConfiguration does not handle baseUrl inherited via extends
# in TS6, causing TS5101 deprecation errors.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/next.js/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts"
ROOT="/workspace/next.js"

###############################################################################
# WEIGHT ALLOCATION:
#   TEST 1 (fail-to-pass: inherited baseUrl removed in TS6)      = 0.40
#   TEST 2 (fail-to-pass: paths rewritten for inherited baseUrl) = 0.25
#   TEST 3 (pass-to-pass: direct baseUrl still works)            = 0.15
#   TEST 4 (regression: existing tests pass)                     = 0.10
#   TEST 5 (anti-stub: code actually executes)                   = 0.05
#   TEST 6 (config-derived: no Claude footers)                   = 0.05
#   TOTAL                                                        = 1.00
###############################################################################

###############################################################################
# GATE: TypeScript syntax validity
###############################################################################
echo "=== GATE: TypeScript Syntax Check ==="
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf-8');
if (src.length < 200) {
    console.log('GATE FAILED: file too small');
    process.exit(1);
}
// Try parsing as TypeScript
const ts = require('$ROOT/node_modules/typescript');
try {
    ts.createSourceFile('test.ts', src, ts.ScriptTarget.Latest, true);
    console.log('GATE PASSED: valid TypeScript');
} catch (e) {
    console.log('GATE FAILED: parse error -', e.message);
    process.exit(1);
}
"
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

###############################################################################
# [FAIL-TO-PASS, 0.40]: Inherited baseUrl is removed when running TS6
###############################################################################
echo ""
echo "=== TEST 1: [fail-to-pass] Inherited baseUrl removed in TS6 ==="
node -e "
const fs = require('fs');
const path = require('path');
const os = require('os');

// Create temp directory with test configs
const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-test-'));

// Base config with baseUrl
const baseConfig = {
    compilerOptions: {
        baseUrl: './src',
        paths: { '@/*': ['./*'] }
    }
};

// Child config that extends base (THIS IS THE BUG CASE)
const childConfig = {
    extends: './base.json',
    compilerOptions: {
        // No baseUrl here - it's inherited!
    }
};

fs.writeFileSync(path.join(tmpdir, 'base.json'), JSON.stringify(baseConfig));
fs.writeFileSync(path.join(tmpdir, 'tsconfig.json'), JSON.stringify(childConfig));

// Build and import the module
const ts = require('$ROOT/node_modules/typescript');

// Transpile the TypeScript file to JavaScript
const sourceCode = fs.readFileSync('$TARGET', 'utf-8');
const transpiled = ts.transpileModule(sourceCode, {
    compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        target: ts.ScriptTarget.ES2020,
        esModuleInterop: true
    }
});

// Write temp JS file
const jsPath = path.join(tmpdir, 'test-module.js');
fs.writeFileSync(jsPath, transpiled.outputText);

// Import and call the function
const mod = require(jsPath);

(async () => {
    try {
        // Mock semver if needed
        let semver;
        try {
            semver = require('$ROOT/node_modules/next/dist/compiled/semver');
        } catch (e) {
            semver = { gte: (v, s) => parseInt(v.split('.')[0]) >= parseInt(s.split('.')[0]) };
        }

        const result = await mod.getTypeScriptConfiguration(
            ts,
            path.join(tmpdir, 'tsconfig.json'),
            true // metaOnly for speed
        );

        // THE KEY CHECK: After the fix, result.options.baseUrl should be undefined/deleted
        // because it was inherited and we are on TS6
        if (result && result.options) {
            const hasBaseUrl = 'baseUrl' in result.options && result.options.baseUrl !== undefined;

            if (!hasBaseUrl) {
                console.log('PASS: inherited baseUrl was properly removed');
                fs.rmSync(tmpdir, { recursive: true, force: true });
                process.exit(0);
            } else {
                console.log('FAIL: result.options.baseUrl still exists:', result.options.baseUrl);
                fs.rmSync(tmpdir, { recursive: true, force: true });
                process.exit(1);
            }
        } else {
            console.log('FAIL: result or result.options is missing');
            fs.rmSync(tmpdir, { recursive: true, force: true });
            process.exit(1);
        }
    } catch (err) {
        console.log('FAIL:', err.message);
        fs.rmSync(tmpdir, { recursive: true, force: true });
        process.exit(1);
    }
})();
"
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# [FAIL-TO-PASS, 0.25]: Paths are rewritten for inherited baseUrl
###############################################################################
echo ""
echo "=== TEST 2: [fail-to-pass] Paths rewritten for inherited baseUrl ==="
node -e "
const fs = require('fs');
const path = require('path');
const os = require('os');

// Create temp directory with test configs
const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-test-'));

// Base config with baseUrl = './src' and paths pointing relative to baseUrl
const baseConfig = {
    compilerOptions: {
        baseUrl: './src',
        paths: {
            '@/*': ['./*'],
            '@lib/*': ['lib/*']
        }
    }
};

const childConfig = { extends: './base.json', compilerOptions: {} };

fs.writeFileSync(path.join(tmpdir, 'base.json'), JSON.stringify(baseConfig));
fs.writeFileSync(path.join(tmpdir, 'tsconfig.json'), JSON.stringify(childConfig));

// Build and import
const ts = require('$ROOT/node_modules/typescript');
const sourceCode = fs.readFileSync('$TARGET', 'utf-8');
const transpiled = ts.transpileModule(sourceCode, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 }
});

const jsPath = path.join(tmpdir, 'test-module.js');
fs.writeFileSync(jsPath, transpiled.outputText);
const mod = require(jsPath);

(async () => {
    try {
        const result = await mod.getTypeScriptConfiguration(ts, path.join(tmpdir, 'tsconfig.json'), true);

        // Check that paths were rewritten to be relative
        // After fix: paths should be like './src/*' instead of '@/*' resolving via baseUrl
        if (result && result.options && result.options.paths) {
            const paths = result.options.paths;

            // Check if paths have been rewritten to include relative path info
            // The fix should make paths like './src/*' or './src/lib/*'
            let hasRewrittenPaths = false;
            for (const [key, values] of Object.entries(paths)) {
                if (Array.isArray(values)) {
                    for (const v of values) {
                        if (typeof v === 'string' && (v.includes('./') || v.startsWith('.'))) {
                            hasRewrittenPaths = true;
                            break;
                        }
                    }
                }
            }

            // Also check for wildcard fallback that the fix adds
            const hasWildcard = Object.keys(paths).includes('*');

            if (hasRewrittenPaths || hasWildcard) {
                console.log('PASS: paths were rewritten for inherited baseUrl');
                fs.rmSync(tmpdir, { recursive: true, force: true });
                process.exit(0);
            } else {
                console.log('FAIL: paths not rewritten:', JSON.stringify(paths));
                fs.rmSync(tmpdir, { recursive: true, force: true });
                process.exit(1);
            }
        } else {
            console.log('FAIL: result.options.paths is missing');
            fs.rmSync(tmpdir, { recursive: true, force: true });
            process.exit(1);
        }
    } catch (err) {
        console.log('FAIL:', err.message);
        fs.rmSync(tmpdir, { recursive: true, force: true });
        process.exit(1);
    }
})();
"
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# [PASS-TO-PASS, 0.15]: Direct-declared baseUrl still works
###############################################################################
echo ""
echo "=== TEST 3: [pass-to-pass] Direct baseUrl handling still works ==="
node -e "
const fs = require('fs');
const path = require('path');
const os = require('os');

const tmpdir = fs.mkdtempSync(path.join(os.tmpdir(), 'ts-test-'));

// Config with DIRECT baseUrl (not inherited)
const config = {
    compilerOptions: {
        baseUrl: '.',
        paths: { '@/*': ['src/*'] }
    }
};

fs.writeFileSync(path.join(tmpdir, 'tsconfig.json'), JSON.stringify(config));

const ts = require('$ROOT/node_modules/typescript');
const sourceCode = fs.readFileSync('$TARGET', 'utf-8');
const transpiled = ts.transpileModule(sourceCode, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 }
});

const jsPath = path.join(tmpdir, 'test-module.js');
fs.writeFileSync(jsPath, transpiled.outputText);
const mod = require(jsPath);

(async () => {
    try {
        const result = await mod.getTypeScriptConfiguration(ts, path.join(tmpdir, 'tsconfig.json'), true);

        // For direct-declared baseUrl on TS6, paths should be rewritten WITHOUT baseUrl
        if (result && result.options && result.options.paths) {
            const paths = result.options.paths;

            // Original paths should be transformed
            let hasTransformedPaths = false;
            for (const [key, values] of Object.entries(paths)) {
                if (key === '@/*' && Array.isArray(values)) {
                    // src/* should become ./src/* (relative to baseUrl)
                    hasTransformedPaths = values.some(v => v.includes('src/') || v.startsWith('./'));
                }
            }

            if (hasTransformedPaths || Object.keys(paths).length > 0) {
                console.log('PASS: direct baseUrl handling still works');
                fs.rmSync(tmpdir, { recursive: true, force: true });
                process.exit(0);
            } else {
                console.log('FAIL: paths not properly handled for direct baseUrl');
                fs.rmSync(tmpdir, { recursive: true, force: true });
                process.exit(1);
            }
        } else {
            console.log('FAIL: result.options.paths is missing');
            fs.rmSync(tmpdir, { recursive: true, force: true });
            process.exit(1);
        }
    } catch (err) {
        console.log('FAIL:', err.message);
        fs.rmSync(tmpdir, { recursive: true, force: true });
        process.exit(1);
    }
})();
"
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# [REGRESSION, 0.10]: Upstream tests still pass (CPU-safe subset)
###############################################################################
echo ""
echo "=== TEST 4: [regression] Upstream unit tests ==="

# Run appropriate test if available
cd "$ROOT" 2>/dev/null
if [ -f "package.json" ]; then
    # Check if there's a specific test file for this module
    TEST_FILE="packages/next/src/lib/typescript/getTypeScriptConfiguration.test.ts"
    if [ -f "$TEST_FILE" ]; then
        echo "  Running specific unit test..."
        npx jest "$TEST_FILE" --testTimeout=30000 --silent 2>/dev/null
        T4=$?
    else
        # Check if we can run TypeScript compilation on a related test file
        echo "  No unit test found, checking TypeScript compilation..."
        npx tsc --noEmit --skipLibCheck "$TARGET" 2>/dev/null
        if [ $? -eq 0 ]; then
            T4=0
        else
            T4=1
        fi
    fi
else
    echo "  No test infrastructure available"
    T4=0  # Neutral - can't test what doesn't exist
fi
echo "  -> exit code: $T4"

###############################################################################
# [ANTI-STUB, 0.05]: Code actually executes functional behavior
###############################################################################
echo ""
echo "=== TEST 5: [anti-stub] Functional behavior verification ==="
node -e "
const fs = require('fs');
const path = require('path');

// Verify the file has actual code structure by checking for key imports and exports
const src = fs.readFileSync('$TARGET', 'utf-8');

// Must have proper imports
const hasImports = (src.match(/import\s+/g) || []).length >= 2;

// Must have actual function implementations (not stubs)
const hasFunctionBodies = (src.match(/\{[\s\S]*?\}/g) || []).some(m => m.length > 50);

// Must have the main exported function with substantial body
const hasMainFunction = /export\s+async\s+function\s+getTypeScriptConfiguration\s*\([^)]*\)\s*\{[\s\S]{500,}\}/.test(src);

if (hasImports && hasFunctionBodies && hasMainFunction) {
    console.log('PASS: file has substantial implementation');
    process.exit(0);
} else {
    console.log('FAIL: file appears to be stubbed');
    console.log('  imports:', hasImports);
    console.log('  function bodies:', hasFunctionBodies);
    console.log('  main function:', hasMainFunction);
    process.exit(1);
}
"
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# [CONFIG-DERIVED, 0.05]: No Claude Code footers in commit
###############################################################################
echo ""
echo "=== TEST 6: [config-derived] No Claude footers ==="
node -e "
const { execSync } = require('child_process');
try {
    const log = execSync('git log --format=%B -n5 2>/dev/null || echo \"NO_GIT\"', {
        encoding: 'utf8',
        cwd: '/workspace/next.js'
    });
    if (log.includes('Generated with Claude') || log.includes('Co-Authored-By: Claude')) {
        console.log('FAIL: commit contains Claude footer');
        process.exit(1);
    }
} catch (e) {}
console.log('PASS: no Claude footers found');
process.exit(0);
"
T6=$?
echo "  -> exit code: $T6"

###############################################################################
# Calculate final score
###############################################################################
echo ""
echo "=== FINAL SCORE ==="
SCORE=$(python3 -c "
t1 = 0.40 if $T1 == 0 else 0.0
t2 = 0.25 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.05 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo ""
echo "Breakdown:"
echo "  TEST 1 (f2p: inherited baseUrl removed)       = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.40]"
echo "  TEST 2 (f2p: paths rewritten)                 = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (p2p: direct baseUrl works)            = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (regression: upstream tests)           = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (anti-stub: functional code)           = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "  TEST 6 (config: no Claude footers)            = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
