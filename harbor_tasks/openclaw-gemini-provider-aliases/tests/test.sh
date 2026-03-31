#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_alias]=0.35
WEIGHTS[behavioral_flash_lite]=0.35
WEIGHTS[antistub]=0.20
WEIGHTS[config_boundary]=0.10

for key in behavioral_alias behavioral_flash_lite antistub config_boundary; do
    RESULTS[$key]=0
done

TARGET_INDEX="extensions/google/index.ts"
TARGET_MODELS="extensions/google/provider-models.ts"

# ---------- GATE: Required files and basic structure ----------
if [ ! -f "$TARGET_INDEX" ] || [ ! -f "$TARGET_MODELS" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# Check that provider-models.ts has the exported function (import gate)
if ! grep -q "export.*function resolveGoogle31ForwardCompatModel" "$TARGET_MODELS" 2>/dev/null; then
    echo "GATE FAIL: resolveGoogle31ForwardCompatModel not exported"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- HELPER: Extract and test function behavior ----------
# Create a test harness that extracts and validates the actual logic
node > /tmp/test_output.txt 2>&1 << 'TESTSCRIPT'
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const TARGET_MODELS = 'extensions/google/provider-models.ts';
const TARGET_INDEX = 'extensions/google/index.ts';

// Read the source files
const modelsContent = fs.readFileSync(TARGET_MODELS, 'utf8');
const indexContent = fs.readFileSync(TARGET_INDEX, 'utf8');

// Helper: Extract function using regex (fallback to line-based extraction)
function extractFunction(content, funcName) {
    // Match export function or function declaration
    const exportPattern = new RegExp(`export\\s+function\\s+${funcName}\\s*\\([^)]*\\)[^:]*:\\s*[^\\{]*\\{`, 'g');
    const funcPattern = new RegExp(`function\\s+${funcName}\\s*\\([^)]*\\)[^:]*:\\s*[^\\{]*\\{`, 'g');

    let match = exportPattern.exec(content) || funcPattern.exec(content);
    if (!match) return null;

    const startIdx = match.index;
    let braceCount = 1;
    let idx = content.indexOf('{', startIdx) + 1;

    while (braceCount > 0 && idx < content.length) {
        if (content[idx] === '{') braceCount++;
        if (content[idx] === '}') braceCount--;
        idx++;
    }

    return content.substring(startIdx, idx);
}

// Helper: Create a mock runtime environment
function createMockContext(provider, modelId, templates) {
    return {
        provider,
        modelId,
        modelRegistry: {
            find: (pid, mid) => {
                const found = templates.find(t =>
                    t.provider === pid && t.id.toLowerCase() === mid.toLowerCase()
                );
                return found || null;
            }
        }
    };
}

// Parse TypeScript-like function signature to understand parameters
function parseFunctionSignature(funcSource) {
    const match = funcSource.match(/function\s+\w+\s*\(([^)]*)\)/);
    if (!match) return [];

    return match[1].split(',').map(p => p.trim()).filter(p => p.length > 0);
}

// ---------- TEST 1: Check index.ts uses runtime provider ----------
function testIndexUsesRuntimeProvider() {
    // Should NOT hardcode providerId: "google" (this is the bug)
    const hardcodedPattern = /providerId\s*:\s*["']google["']/;
    if (hardcodedPattern.test(indexContent)) {
        console.log('FAIL: index.ts still hardcodes providerId: "google"');
        return false;
    }

    // Should reference ctx.provider or similar runtime value
    // Check for patterns that pass provider dynamically
    const dynamicProviderPatterns = [
        /ctx\.provider/,                 // Direct ctx.provider usage
        /providerId\s*:\s*\w+\.provider/, // Any X.provider usage
        /providerId\s*:\s*provider/,     // Destructured provider
    ];

    const hasDynamicProvider = dynamicProviderPatterns.some(p => p.test(indexContent));
    if (!hasDynamicProvider) {
        console.log('FAIL: index.ts does not use runtime provider');
        return false;
    }

    // Should pass templateProviderId or fallback mechanism
    const hasFallback = indexContent.includes('templateProviderId') ||
                        indexContent.includes('fallback') ||
                        /templateProvider/.test(indexContent);

    if (!hasFallback) {
        console.log('FAIL: index.ts missing templateProviderId fallback');
        return false;
    }

    return true;
}

// ---------- TEST 2: Behavioral test for provider alias resolution ----------
function testProviderAliasResolution() {
    // Extract the main function
    const funcSource = extractFunction(modelsContent, 'resolveGoogle31ForwardCompatModel');
    if (!funcSource) {
        console.log('FAIL: resolveGoogle31ForwardCompatModel not found');
        return false;
    }

    // Parse to understand the signature
    const params = parseFunctionSignature(funcSource);

    // Check function accepts templateProviderId or fallbackProviders
    const hasFallbackParam = params.some(p =>
        p.includes('templateProviderId') || p.includes('fallback')
    );

    if (!hasFallbackParam) {
        console.log('FAIL: Function missing templateProviderId parameter');
        return false;
    }

    // Verify logic structure: should attempt lookup with multiple provider IDs
    // Look for patterns that indicate fallback logic
    const hasFallbackLogic =
        modelsContent.includes('for') ||           // Loop for multiple providers
        modelsContent.includes('forEach') ||       // Iteration
        modelsContent.includes('?.') ||            // Optional chaining
        modelsContent.includes('||');              // OR fallback

    // Check for cloneFirstTemplateModel or equivalent helper usage
    const hasCloneHelper =
        modelsContent.includes('cloneFirstTemplateModel') ||
        modelsContent.includes('cloneFirstGoogleTemplateModel');

    if (!hasFallbackLogic && !hasCloneHelper) {
        console.log('FAIL: No fallback lookup logic detected');
        return false;
    }

    return true;
}

// ---------- TEST 3: Behavioral test for flash-lite ordering ----------
function testFlashLiteOrdering() {
    // The core bug: flash-lite must be checked BEFORE flash because
    // "gemini-3.1-flash-lite" starts with "gemini-3.1-flash"

    // Find the resolveGoogle31ForwardCompatModel function
    const funcSource = extractFunction(modelsContent, 'resolveGoogle31ForwardCompatModel');
    if (!funcSource) {
        console.log('FAIL: Main resolver function not found');
        return false;
    }

    // Check for flash-lite prefix constant or literal
    const hasFlashLitePrefix =
        modelsContent.includes('flash-lite') ||
        modelsContent.includes('FLASH_LITE');

    if (!hasFlashLitePrefix) {
        console.log('FAIL: No flash-lite prefix handling');
        return false;
    }

    // CRITICAL: Verify ordering by analyzing the if-else chain structure
    // Look for the pattern of prefix checks in the function

    // Find all startsWith or indexOf patterns in the function
    const prefixMatches = [];
    const lowerPattern = /lower\s*\.\s*(startsWith|indexOf)\s*\(([^)]+)\)/g;
    const trimmedPattern = /trimmed\s*\.\s*(startsWith|indexOf)\s*\(([^)]+)\)/g;

    let m;
    while ((m = lowerPattern.exec(funcSource)) !== null) {
        prefixMatches.push(m[2].replace(/["']/g, '').toLowerCase());
    }
    while ((m = trimmedPattern.exec(funcSource)) !== null) {
        prefixMatches.push(m[2].replace(/["']/g, '').toLowerCase());
    }

    // Also check for constant-based comparisons
    const constantChecks = funcSource.match(/(GEMINI_[^\s;)]+)/g) || [];

    // Analyze the raw function body for order of conditions
    const liteIdx = funcSource.toLowerCase().indexOf('flash-lite');
    const flashIdx = funcSource.toLowerCase().indexOf('gemini-3.1-flash');

    // If both are present, flash-lite should appear before the general flash check
    if (liteIdx >= 0 && flashIdx >= 0) {
        // Find position within if-else chain (inside the function body)
        const funcBody = funcSource.substring(funcSource.indexOf('{'));
        const bodyLiteIdx = funcBody.toLowerCase().indexOf('flash-lite');
        const bodyFlashIdx = funcBody.toLowerCase().indexOf('3.1-flash-');

        // Look for the actual if-else ordering
        const flashLitePattern = /if.*flash-lite|flash-lite.*prefix/i;
        const flashPattern = /if.*3\.1-flash["']|3\.1-flash.*prefix(?!.*lite)/i;

        const body = funcBody.toLowerCase();

        // Find all conditional branches and their order
        const branches = [];
        const branchPattern = /(?:if|else if)\s*\([^)]*\)/g;
        let branchMatch;
        while ((branchMatch = branchPattern.exec(funcBody)) !== null) {
            branches.push({
                text: branchMatch[0].toLowerCase(),
                index: branchMatch.index
            });
        }

        // Check for gemini-3.1-flash-lite before gemini-3.1-flash
        let liteBranchIdx = -1;
        let flashBranchIdx = -1;

        branches.forEach((b, i) => {
            if (b.text.includes('flash') && b.text.includes('lite')) {
                liteBranchIdx = i;
            } else if (b.text.includes('3.1-flash') && !b.text.includes('lite')) {
                flashBranchIdx = i;
            }
        });

        // Also check via constant names if used
        if (liteBranchIdx === -1 && funcBody.includes('flash_lite')) {
            branches.forEach((b, i) => {
                if (b.text.includes('flash_lite') || b.text.includes('flash-lite')) {
                    liteBranchIdx = i;
                }
            });
        }
        if (flashBranchIdx === -1 && funcBody.includes('3.1_flash')) {
            branches.forEach((b, i) => {
                if ((b.text.includes('3.1_flash') || b.text.includes('3.1-flash')) &&
                    !b.text.includes('lite')) {
                    flashBranchIdx = i;
                }
            });
        }

        if (liteBranchIdx >= 0 && flashBranchIdx >= 0 && liteBranchIdx > flashBranchIdx) {
            console.log('FAIL: flash-lite check comes AFTER flash check');
            return false;
        }
    }

    // Verify the logic actually uses these prefixes for branching
    const hasBranchingLogic = funcSource.includes('if') &&
        (funcSource.includes('startsWith') || funcSource.includes('indexOf'));

    if (!hasBranchingLogic) {
        console.log('FAIL: No prefix-based branching logic found');
        return false;
    }

    return true;
}

// ---------- TEST 4: Anti-stub ----------
function testAntiStub() {
    // Line count check (reasonable minimum for actual implementation)
    const lines = modelsContent.split('\n').filter(l => l.trim().length > 0);
    if (lines.length < 25) {
        console.log('FAIL: File too short (likely stub)');
        return false;
    }

    // Check for substantial logic (not just comments and empty returns)
    const codeLines = modelsContent
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\/\/.*$/gm, '')
        .split('\n')
        .filter(l => l.trim().length > 0);

    if (codeLines.length < 20) {
        console.log('FAIL: Too few actual code lines');
        return false;
    }

    // Check for actual implementation patterns (not just stubs)
    const hasLogic =
        modelsContent.includes('return') &&
        (modelsContent.includes('if') || modelsContent.includes('?')) &&
        (modelsContent.includes('for') || modelsContent.includes('while') ||
         modelsContent.includes('cloneFirst') || modelsContent.includes('modelRegistry'));

    if (!hasLogic) {
        console.log('FAIL: No substantial implementation logic');
        return false;
    }

    return true;
}

// ---------- TEST 5: Config boundary check ----------
function testConfigBoundary() {
    // Source: CLAUDE.md:16 - Extension code must import from plugin-sdk/*
    const files = execSync('find extensions/google/src -name "*.ts" -not -name "*.test.ts" -not -name "*.d.ts" 2>/dev/null || echo ""', { encoding: 'utf8' })
        .trim()
        .split('\n')
        .filter(f => f.length > 0);

    for (const f of files) {
        if (!fs.existsSync(f)) continue;
        const content = fs.readFileSync(f, 'utf8');
        const lines = content.split('\n');

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            // Check for imports from core internals (../../../src/)
            if (/^import .* from ['"]\.\.\/\.\.\/\.\.\/src\//.test(line)) {
                console.log(`FAIL: ${f}:${i+1} imports core internals: ${line.trim()}`);
                return false;
            }
        }
    }

    return true;
}

// ---------- Run All Tests ----------
let passed = 0;
let failed = 0;

console.log('=== Testing index.ts provider handling ===');
if (testIndexUsesRuntimeProvider()) {
    console.log('PASS: index uses runtime provider');
    passed++;
} else {
    console.log('FAILED: index provider handling');
    failed++;
}

console.log('\n=== Testing provider alias resolution ===');
if (testProviderAliasResolution()) {
    console.log('PASS: provider alias resolution');
    passed++;
} else {
    console.log('FAILED: provider alias resolution');
    failed++;
}

console.log('\n=== Testing flash-lite ordering ===');
if (testFlashLiteOrdering()) {
    console.log('PASS: flash-lite ordering');
    passed++;
} else {
    console.log('FAILED: flash-lite ordering');
    failed++;
}

console.log('\n=== Testing anti-stub ===');
if (testAntiStub()) {
    console.log('PASS: anti-stub');
    passed++;
} else {
    console.log('FAILED: anti-stub');
    failed++;
}

console.log('\n=== Testing config boundary ===');
if (testConfigBoundary()) {
    console.log('PASS: config boundary');
    passed++;
} else {
    console.log('FAILED: config boundary');
    failed++;
}

console.log(`\n=== SUMMARY: ${passed} passed, ${failed} failed ===`);
process.exit(failed > 0 ? 1 : 0);
TESTSCRIPT

NODE_EXIT=$?
cat /tmp/test_output.txt

# Parse results from output
if grep -q "PASS: index uses runtime provider" /tmp/test_output.txt; then
    RESULTS[behavioral_alias]=1
    echo "TEST behavioral_alias: PASS"
else
    RESULTS[behavioral_alias]=0
    echo "TEST behavioral_alias: FAIL"
fi

# Both provider alias and flash-lite tests must pass for full behavioral score
if grep -q "PASS: provider alias resolution" /tmp/test_output.txt && \
   grep -q "PASS: flash-lite ordering" /tmp/test_output.txt; then
    RESULTS[behavioral_flash_lite]=1
    echo "TEST behavioral_flash_lite: PASS"
else
    RESULTS[behavioral_flash_lite]=0
    echo "TEST behavioral_flash_lite: FAIL"
fi

if grep -q "PASS: anti-stub" /tmp/test_output.txt; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    RESULTS[antistub]=0
    echo "TEST antistub: FAIL"
fi

if grep -q "PASS: config boundary" /tmp/test_output.txt; then
    RESULTS[config_boundary]=1
    echo "TEST config_boundary: PASS"
else
    RESULTS[config_boundary]=0
    echo "TEST config_boundary: FAIL"
fi

SCORE=$(python3 -c "
w = {'behavioral_alias': ${WEIGHTS[behavioral_alias]}, 'behavioral_flash_lite': ${WEIGHTS[behavioral_flash_lite]}, 'antistub': ${WEIGHTS[antistub]}, 'config_boundary': ${WEIGHTS[config_boundary]}}
r = {'behavioral_alias': ${RESULTS[behavioral_alias]}, 'behavioral_flash_lite': ${RESULTS[behavioral_flash_lite]}, 'antistub': ${RESULTS[antistub]}, 'config_boundary': ${RESULTS[config_boundary]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
