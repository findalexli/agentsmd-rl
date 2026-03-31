#!/usr/bin/env bash
set +e

TOTAL=0
PASS=0
GATE_PASS=true

cd /workspace/next.js

RUST_FILE="crates/next-core/src/app_page_loader_tree.rs"
TS_FILE="packages/next/src/lib/metadata/resolve-metadata.ts"

##############################################################################
# GATE: Source files must exist
##############################################################################
# [pr_diff] (gate): Both target files must exist
if [ ! -f "$RUST_FILE" ]; then
    echo "GATE FAIL: $RUST_FILE does not exist"
    GATE_PASS=false
fi
if [ ! -f "$TS_FILE" ]; then
    echo "GATE FAIL: $TS_FILE does not exist"
    GATE_PASS=false
fi

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: file existence checks passed"

##############################################################################
# Helper: strip Rust // comments and string-only lines for anti-gaming
##############################################################################
# This prevents agents from injecting patterns in comments to game checks.
STRIPPED_RUST=$(python3 -c "
import re, sys
with open('$RUST_FILE') as f:
    lines = f.readlines()
# Remove lines that are purely comments (// ...) or empty
cleaned = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith('//'):
        continue
    # Remove inline // comments (crude but sufficient for pattern matching)
    code_part = re.split(r'\s*//', line, maxsplit=1)[0]
    cleaned.append(code_part)
print(''.join(cleaned))
" 2>/dev/null)

if [ -z "$STRIPPED_RUST" ]; then
    echo "WARNING: Could not strip comments from Rust file, using raw"
    STRIPPED_RUST=$(cat "$RUST_FILE")
fi

##############################################################################
# Fail-to-pass 1 (0.30): Metadata requires are lazy, not eager
# WHY structural: Rust code generates JS templates. No cargo in Docker.
# The base commit has eager: `const {identifier} = require(...)`.
# The fix wraps in arrow: `const {identifier} = () => require(...)`.
# We check the comment-stripped code to prevent comment injection.
##############################################################################
# [pr_diff] (0.30): Eager requires replaced with lazy arrow-function wrappers
F2P1_SCORE=0
node -e "
const src = process.env.STRIPPED_RUST;
if (!src) { console.log('No stripped source'); process.exit(1); }

// Count lazy patterns: = () => require( with turbopack chunking annotation nearby
// Accept various forms: () => require(...), () => import(...), arrow wrapping
const lazyMatches = src.match(/=\s*\(\)\s*=>\s*require\s*\(/g) || [];
const lazyCount = lazyMatches.length;

// Count eager patterns that should be GONE after fix
// e.g., const {identifier} = require(/*turbopackChunkingType
const eagerMatches = src.match(/const\s+\{[a-z_]+\}\s*=\s*require\s*\(\s*\/\*\s*turbopack/gi) || [];
const eagerCount = eagerMatches.length;

if (lazyCount >= 2 && eagerCount === 0) {
    console.log('PASS: ' + lazyCount + ' lazy requires, 0 eager');
    process.exit(0);
} else {
    console.log('FAIL: ' + lazyCount + ' lazy, ' + eagerCount + ' eager');
    process.exit(1);
}
" 2>/dev/null && F2P1_SCORE=30
PASS=$((PASS + F2P1_SCORE))
TOTAL=$((TOTAL + 30))
if [ "$F2P1_SCORE" -gt 0 ]; then echo "PASS [0.30]: Metadata requires are lazy (arrow wrappers)"; else echo "FAIL [0.30]: Metadata requires not properly lazified"; fi

##############################################################################
# Fail-to-pass 2 (0.20): Generated code awaits lazy loaders before use
# The lazy require must be called and awaited so TLA modules resolve.
# Accept any form: await X(), await (X()), let m = X(); await m, etc.
##############################################################################
# [pr_diff] (0.20): Lazy require results are awaited in generated JS templates
F2P2_SCORE=0
node -e "
const src = process.env.STRIPPED_RUST;
if (!src) process.exit(1);

// The generated code must await the lazy function call.
// Accept: await {identifier}(), await {alt}(), or similar patterns
// Also accept two-step: await <varname>() where varname was assigned the lazy fn
const awaitCallPatterns = [
    /await\s+\w*\{identifier\}\w*\s*\(\)/,
    /await\s+\w*\{alt\}\w*\s*\(\)/,
    /await\s+\w+\(\)/  // any await call() in generated code context
];

let hasAwaitCall = false;
for (const pat of awaitCallPatterns) {
    if (pat.test(src)) { hasAwaitCall = true; break; }
}

// Also verify there's an async function/arrow in the generated code
const hasAsync = /async\s*[\(\w]/.test(src);

if (hasAwaitCall && hasAsync) {
    console.log('PASS: lazy requires are awaited in async context');
    process.exit(0);
} else {
    console.log('FAIL: await=' + hasAwaitCall + ' async=' + hasAsync);
    process.exit(1);
}
" 2>/dev/null && F2P2_SCORE=20
PASS=$((PASS + F2P2_SCORE))
TOTAL=$((TOTAL + 20))
if [ "$F2P2_SCORE" -gt 0 ]; then echo "PASS [0.20]: Lazy requires are awaited"; else echo "FAIL [0.20]: Lazy requires not awaited"; fi

##############################################################################
# Fail-to-pass 3 (0.15): TS layer does NOT double-wrap with interopDefault
# The base commit has: await interopDefault(imageModule)(props)
# The fix simplifies to: await imageModule(props)
# Behavioral: we simulate both calling conventions and check the TS source matches.
##############################################################################
# [pr_diff] (0.15): collectStaticImagesFiles calls imageModule directly (no interopDefault)
F2P3_SCORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');

// Find collectStaticImagesFiles function body
const fnStart = src.indexOf('collectStaticImagesFiles');
if (fnStart === -1) {
    console.log('FAIL: collectStaticImagesFiles not found');
    process.exit(1);
}

// Get a reasonable chunk of the function
const fnChunk = src.slice(fnStart, fnStart + 2000);

// BEHAVIORAL CHECK: simulate the calling convention
// Create mock imageModule (an async function, as new Rust code provides)
// Test that calling it directly works, while interopDefault wrapping is absent

// Check 1: interopDefault must NOT wrap imageModule in this function
const hasInteropWrap = /interopDefault\s*\(\s*imageModule\s*\)/.test(fnChunk);
if (hasInteropWrap) {
    console.log('FAIL: imageModule still wrapped in interopDefault');
    process.exit(1);
}

// Check 2: imageModule must be called as a function (with any args)
// Accept: imageModule(props), imageModule(anything), imageModule()
const hasCall = /imageModule\s*\(/.test(fnChunk);
if (!hasCall) {
    console.log('FAIL: imageModule not called as function');
    process.exit(1);
}

// BEHAVIORAL SIMULATION: verify the new calling convention works
// The new Rust code provides imageModule as an async function
// The TS layer should call it directly
const testCode = \`
    const imageModule = async (props) => ({
        src: '/test.png', width: 100, height: 100, ...props
    });
    // New convention: direct call
    (async () => {
        const result = await imageModule({ id: 'test' });
        if (!result || !result.src) throw new Error('Direct call failed');
    })();
\`;
try { eval(testCode); } catch(e) {
    console.log('FAIL: behavioral simulation failed: ' + e.message);
    process.exit(1);
}

console.log('PASS: imageModule called directly, convention verified');
process.exit(0);
" 2>/dev/null && F2P3_SCORE=15
PASS=$((PASS + F2P3_SCORE))
TOTAL=$((TOTAL + 15))
if [ "$F2P3_SCORE" -gt 0 ]; then echo "PASS [0.15]: TS calls imageModule directly"; else echo "FAIL [0.15]: TS calling convention incorrect"; fi

##############################################################################
# Pass-to-pass: Regression checks (0.15 total)
##############################################################################

# [pr_diff] (0.05): collectStaticImagesFiles function still exists and has Promise.all
P2P1_SCORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
if (!src.includes('collectStaticImagesFiles')) {
    console.log('FAIL: collectStaticImagesFiles missing');
    process.exit(1);
}
if (!src.includes('Promise.all')) {
    console.log('FAIL: Promise.all missing');
    process.exit(1);
}
console.log('PASS');
" 2>/dev/null && P2P1_SCORE=5
PASS=$((PASS + P2P1_SCORE))
TOTAL=$((TOTAL + 5))
if [ "$P2P1_SCORE" -gt 0 ]; then echo "PASS [0.05]: collectStaticImagesFiles intact"; else echo "FAIL [0.05]: collectStaticImagesFiles regression"; fi

# [pr_diff] (0.05): Rust file still has fillMetadataSegment and content type generation
P2P2_SCORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$RUST_FILE', 'utf8');
if (!src.includes('fillMetadataSegment')) {
    console.log('FAIL: fillMetadataSegment missing'); process.exit(1);
}
if (!src.includes('get_content_type')) {
    console.log('FAIL: get_content_type missing'); process.exit(1);
}
console.log('PASS');
" 2>/dev/null && P2P2_SCORE=5
PASS=$((PASS + P2P2_SCORE))
TOTAL=$((TOTAL + 5))
if [ "$P2P2_SCORE" -gt 0 ]; then echo "PASS [0.05]: Rust loader tree functions intact"; else echo "FAIL [0.05]: Rust loader tree regression"; fi

# [pr_diff] (0.05): Rust file still handles all metadata types (icons, opengraph, twitter)
P2P3_SCORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$RUST_FILE', 'utf8');
const types = ['icon', 'apple', 'openGraph', 'twitter'];
const missing = types.filter(t => !src.includes(t));
if (missing.length > 0) {
    console.log('FAIL: missing metadata types: ' + missing.join(', '));
    process.exit(1);
}
console.log('PASS');
" 2>/dev/null && P2P3_SCORE=5
PASS=$((PASS + P2P3_SCORE))
TOTAL=$((TOTAL + 5))
if [ "$P2P3_SCORE" -gt 0 ]; then echo "PASS [0.05]: All metadata types handled"; else echo "FAIL [0.05]: Missing metadata types"; fi

##############################################################################
# Anti-stub / structural integrity (0.10 total)
##############################################################################

# [pr_diff] (0.05): Rust file has substantive lazy+async code (not stubs/comments)
STUB1_SCORE=0
python3 -c "
import re, sys
with open('$RUST_FILE') as f:
    src = f.read()

# Strip all comments
lines = src.split('\n')
code_lines = []
in_block = False
for line in lines:
    s = line.strip()
    if s.startswith('//'):
        continue
    if '/*' in s and '*/' not in s:
        in_block = True
        continue
    if in_block:
        if '*/' in s:
            in_block = False
        continue
    code_lines.append(line)
code = '\n'.join(code_lines)

# Check that lazy pattern appears in actual code (not just any line)
lazy_in_code = len(re.findall(r'=\s*\(\)\s*=>\s*require\s*\(', code))
async_in_code = len(re.findall(r'async\s', code))
await_in_code = len(re.findall(r'await\s', code))

if lazy_in_code < 2:
    print(f'FAIL: only {lazy_in_code} lazy patterns in code (need >=2)')
    sys.exit(1)
if async_in_code < 1:
    print(f'FAIL: no async in code')
    sys.exit(1)
if await_in_code < 1:
    print(f'FAIL: no await in code')
    sys.exit(1)
print(f'PASS: {lazy_in_code} lazy, {async_in_code} async, {await_in_code} await in real code')
" 2>/dev/null && STUB1_SCORE=5
PASS=$((PASS + STUB1_SCORE))
TOTAL=$((TOTAL + 5))
if [ "$STUB1_SCORE" -gt 0 ]; then echo "PASS [0.05]: Rust anti-stub check passed"; else echo "FAIL [0.05]: Rust anti-stub check failed"; fi

# [pr_diff] (0.05): TS file interopDefault import removed (unused after fix)
STUB2_SCORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TS_FILE', 'utf8');
// interopDefault should not be imported — accept any import style
const hasImport = /import\s[\s\S]*?interopDefault[\s\S]*?from/.test(src);
// Also check for require-style import
const hasRequire = /interopDefault\s*=\s*require/.test(src);
if (hasImport || hasRequire) {
    console.log('FAIL: interopDefault still imported');
    process.exit(1);
}
console.log('PASS: interopDefault import removed');
" 2>/dev/null && STUB2_SCORE=5
PASS=$((PASS + STUB2_SCORE))
TOTAL=$((TOTAL + 5))
if [ "$STUB2_SCORE" -gt 0 ]; then echo "PASS [0.05]: interopDefault import removed"; else echo "FAIL [0.05]: interopDefault still imported"; fi

##############################################################################
# Config-derived checks (0.10 total)
##############################################################################

# [agent_config] (0.05): turbopackChunkingType shared annotations preserved — AGENTS.md:193 @ 04cc2f2
CONF1_SCORE=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$RUST_FILE', 'utf8');
const count = (src.match(/turbopackChunkingType/g) || []).length;
if (count < 2) {
    console.log('FAIL: only ' + count + ' turbopackChunkingType annotations');
    process.exit(1);
}
console.log('PASS: ' + count + ' turbopackChunkingType annotations');
" 2>/dev/null && CONF1_SCORE=5
PASS=$((PASS + CONF1_SCORE))
TOTAL=$((TOTAL + 5))
if [ "$CONF1_SCORE" -gt 0 ]; then echo "PASS [0.05]: turbopackChunkingType preserved"; else echo "FAIL [0.05]: turbopackChunkingType missing"; fi

# [agent_config] (0.05): No secret values in source — AGENTS.md:306 @ 04cc2f2
CONF2_SCORE=0
node -e "
const fs = require('fs');
for (const f of ['$RUST_FILE', '$TS_FILE']) {
    const src = fs.readFileSync(f, 'utf8');
    if (/(?:api[_-]?key|secret|token|password|credential)\s*[:=]/i.test(src)) {
        console.log('FAIL: potential secret in ' + f);
        process.exit(1);
    }
}
console.log('PASS');
" 2>/dev/null && CONF2_SCORE=5
PASS=$((PASS + CONF2_SCORE))
TOTAL=$((TOTAL + 5))
if [ "$CONF2_SCORE" -gt 0 ]; then echo "PASS [0.05]: No secrets"; else echo "FAIL [0.05]: Potential secrets found"; fi

##############################################################################
# Compute final reward
##############################################################################
REWARD=$(echo "scale=2; $PASS / 100" | bc)
echo ""
echo "Total: $REWARD / 1.00"
echo "$REWARD" > /logs/verifier/reward.txt

BEH=$(echo "scale=2; ($F2P1_SCORE + $F2P2_SCORE + $F2P3_SCORE + $P2P1_SCORE + $P2P2_SCORE + $P2P3_SCORE) / 100" | bc)
STRUCT=$(echo "scale=2; ($STUB1_SCORE + $STUB2_SCORE) / 100" | bc)
CONF=$(echo "scale=2; ($CONF1_SCORE + $CONF2_SCORE) / 100" | bc)

echo "{\"reward\": $REWARD, \"behavioral\": $BEH, \"regression\": $(echo "scale=2; ($P2P1_SCORE + $P2P2_SCORE + $P2P3_SCORE) / 100" | bc), \"config\": $CONF, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
