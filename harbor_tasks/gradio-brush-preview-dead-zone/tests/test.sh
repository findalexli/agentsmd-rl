#!/usr/bin/env bash
set +e

SCORE=0
BRUSH_TS="/workspace/js/imageeditor/shared/brush/brush.ts"
TEXTURES_TS="/workspace/js/imageeditor/shared/brush/brush-textures.ts"

add() { SCORE=$(python3 -c "print(round($SCORE + $1, 4))"); }
log_pass() { echo "PASS ($1): $2"; add "$1"; }
log_fail() { echo "FAIL ($1): $2"; }

# ── GATE: TypeScript files must parse ──
# [pr_diff] (0.00): Syntax gate
for f in "$BRUSH_TS" "$TEXTURES_TS"; do
    if ! node -e "
        const fs = require('fs');
        const ts = require('/workspace/node_modules/typescript');
        const src = fs.readFileSync('$f', 'utf8');
        ts.createSourceFile('$f', src, ts.ScriptTarget.Latest, true);
    " 2>/dev/null; then
        echo "GATE FAIL: $f does not parse"
        echo "0.0" > /logs/verifier/reward.txt
        exit 0
    fi
done
echo "GATE PASS: TypeScript syntax OK"

# ══════════════════════════════════════════════
# FAIL-TO-PASS BEHAVIORAL (0.35)
# These checks FAIL on the buggy baseline, PASS on a correct fix.
# ══════════════════════════════════════════════

# [pr_diff] (0.20): reinitialize() must NOT use image_container.width/height for comparison
# Buggy baseline has: image_container.width !== this.dimensions.width
# Any correct fix must remove this pattern and use bounds or another approach.
# Uses AST to find PropertyAccessExpression chains — immune to comments/strings.
CHK1=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');
const src = fs.readFileSync('$TEXTURES_TS', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

// Find the reinitialize method
function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'reinitialize') {
        return node;
    }
    let found = null;
    ts.forEachChild(node, c => { if (!found) found = findMethod(c); });
    return found;
}

const method = findMethod(sf);
if (!method || !method.body) { console.log('NO_METHOD'); process.exit(0); }

// Walk the method body looking for property accesses like *.image_container.width or *.image_container.height
// used in comparison (BinaryExpression with !==, ===, !=, ==)
let usesBuggyPattern = false;
function walk(node) {
    if (ts.isBinaryExpression(node)) {
        const op = node.operatorToken.kind;
        const isComparison = [
            ts.SyntaxKind.ExclamationEqualsEqualsToken,
            ts.SyntaxKind.EqualsEqualsEqualsToken,
            ts.SyntaxKind.ExclamationEqualsToken,
            ts.SyntaxKind.EqualsEqualsToken,
        ].includes(op);
        if (isComparison) {
            const text = node.getText(sf);
            // Check if either side accesses image_container.width or image_container.height directly
            [node.left, node.right].forEach(side => {
                if (ts.isPropertyAccessExpression(side)) {
                    const prop = side.name.text;
                    if ((prop === 'width' || prop === 'height') && ts.isPropertyAccessExpression(side.expression)) {
                        if (side.expression.name.text === 'image_container') {
                            usesBuggyPattern = true;
                        }
                    }
                }
            });
        }
    }
    ts.forEachChild(node, walk);
}
walk(method.body);
console.log(usesBuggyPattern ? 'BUGGY' : 'FIXED');
" 2>/dev/null)

if [ "$CHK1" = "FIXED" ]; then
    log_pass 0.20 "reinitialize() no longer uses image_container.width/height for comparison (bug removed)"
elif [ "$CHK1" = "NO_METHOD" ]; then
    log_fail 0.20 "reinitialize() method not found"
else
    log_fail 0.20 "reinitialize() still uses buggy image_container.width/height comparison"
fi

# [pr_diff] (0.15): set_tool() must trigger reinitialization on dimension changes
# Buggy baseline only checks: mode_changed || !textures_initialized
# A correct fix adds a dimension-related condition. We check that the if-condition
# guarding initialize_textures() has more than 2 boolean terms.
CHK2=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');
const src = fs.readFileSync('$BRUSH_TS', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'set_tool') return node;
    let found = null;
    ts.forEachChild(node, c => { if (!found) found = findMethod(c); });
    return found;
}

const method = findMethod(sf);
if (!method || !method.body) { console.log('NO_METHOD'); process.exit(0); }

// Find call to initialize_textures within set_tool
let hasInitCall = false;
let conditionTerms = 0;

function countBooleanTerms(expr) {
    // Count leaf terms in || chains
    if (ts.isBinaryExpression(expr) && expr.operatorToken.kind === ts.SyntaxKind.BarBarToken) {
        return countBooleanTerms(expr.left) + countBooleanTerms(expr.right);
    }
    if (ts.isBinaryExpression(expr) && expr.operatorToken.kind === ts.SyntaxKind.AmpersandAmpersandToken) {
        return countBooleanTerms(expr.left) + countBooleanTerms(expr.right);
    }
    return 1;
}

function walk(node) {
    // Look for if-statements that contain initialize_textures call
    if (ts.isIfStatement(node)) {
        const bodyText = (node.thenStatement.getText ? node.thenStatement.getText(sf) : '');
        if (bodyText.includes('initialize_textures')) {
            hasInitCall = true;
            conditionTerms = countBooleanTerms(node.expression);
        }
    }
    ts.forEachChild(node, walk);
}
walk(method.body);

if (!hasInitCall) { console.log('NO_INIT_CALL'); }
else if (conditionTerms >= 3) { console.log('HAS_DIM_CHECK'); }
else { console.log('BASELINE_ONLY'); }
" 2>/dev/null)

if [ "$CHK2" = "HAS_DIM_CHECK" ]; then
    log_pass 0.15 "set_tool() condition for initialize_textures includes dimension check (>2 terms)"
elif [ "$CHK2" = "NO_INIT_CALL" ]; then
    log_fail 0.15 "set_tool() does not call initialize_textures"
elif [ "$CHK2" = "NO_METHOD" ]; then
    log_fail 0.15 "set_tool() method not found"
else
    log_fail 0.15 "set_tool() only checks mode_changed/textures_initialized (baseline bug)"
fi

# ══════════════════════════════════════════════
# SILVER BEHAVIORAL via AST (0.30)
# ══════════════════════════════════════════════

# [pr_diff] (0.15): reinitialize() must call a bounds-fetching method
# Accepts: getLocalBounds(), getBounds(), or any method returning bounds object.
# Uses AST CallExpression check — immune to comments.
CHK3=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');
const src = fs.readFileSync('$TEXTURES_TS', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'reinitialize') return node;
    let found = null;
    ts.forEachChild(node, c => { if (!found) found = findMethod(c); });
    return found;
}

const method = findMethod(sf);
if (!method || !method.body) { console.log('NO_METHOD'); process.exit(0); }

// Look for CallExpression where the method name is getLocalBounds, getBounds, or similar
let hasBoundsCall = false;
function walk(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
        const name = node.expression.name.text;
        if (['getLocalBounds', 'getBounds', 'get_bounds', 'get_local_bounds', 'getSize'].includes(name)) {
            hasBoundsCall = true;
        }
    }
    ts.forEachChild(node, walk);
}
walk(method.body);
console.log(hasBoundsCall ? 'HAS_BOUNDS' : 'NO_BOUNDS');
" 2>/dev/null)

if [ "$CHK3" = "HAS_BOUNDS" ]; then
    log_pass 0.15 "reinitialize() calls a bounds-fetching method (AST-verified)"
else
    log_fail 0.15 "reinitialize() missing bounds-fetching call (getLocalBounds/getBounds/etc)"
fi

# [pr_diff] (0.15): Dimension comparisons handle subpixel differences
# Accepts: Math.round, Math.floor, Math.ceil, Math.abs, parseInt, bitwise |0, ~~, Math.trunc
# Checks BOTH files via AST CallExpression — comments don't count.
CHK4=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');

const roundingMethods = new Set(['round', 'floor', 'ceil', 'abs', 'trunc']);

function hasSubpixelHandling(filePath) {
    const src = fs.readFileSync(filePath, 'utf8');
    const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

    let found = false;
    function walk(node) {
        // Math.round/floor/ceil/abs/trunc as CallExpression
        if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
            const obj = node.expression.expression;
            const method = node.expression.name.text;
            if (ts.isIdentifier(obj) && obj.text === 'Math' && roundingMethods.has(method)) {
                found = true;
            }
        }
        // parseInt as CallExpression
        if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'parseInt') {
            found = true;
        }
        // Bitwise OR with 0 (x|0) or prefix ~~
        if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.BarToken) {
            if (ts.isNumericLiteral(node.right) && node.right.text === '0') found = true;
        }
        if (ts.isPrefixUnaryExpression(node) && node.operator === ts.SyntaxKind.TildeToken) {
            found = true;
        }
        ts.forEachChild(node, walk);
    }
    walk(sf);
    return found;
}

const a = hasSubpixelHandling('$BRUSH_TS');
const b = hasSubpixelHandling('$TEXTURES_TS');
// At least one of the files must handle subpixel in dimension comparisons
console.log((a || b) ? 'HAS_ROUNDING' : 'NO_ROUNDING');
" 2>/dev/null)

if [ "$CHK4" = "HAS_ROUNDING" ]; then
    log_pass 0.15 "Dimension comparisons handle subpixel differences (AST-verified)"
else
    log_fail 0.15 "No subpixel handling found (Math.round/floor/ceil/abs/trunc, parseInt, bitwise)"
fi

# ══════════════════════════════════════════════
# PASS-TO-PASS REGRESSION (0.15)
# These pass on the baseline and must still pass after fix.
# ══════════════════════════════════════════════

# [pr_diff] (0.10): initialize_textures still creates render textures and preview sprite
CHK5=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');
const src = fs.readFileSync('$TEXTURES_TS', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'initialize_textures') return node;
    let found = null;
    ts.forEachChild(node, c => { if (!found) found = findMethod(c); });
    return found;
}

const method = findMethod(sf);
if (!method || !method.body) { console.log('MISSING'); process.exit(0); }

const bodyText = method.body.getText(sf);
const hasRenderTexture = bodyText.includes('RenderTexture');
const hasPreview = bodyText.includes('preview');
const hasDimensions = bodyText.includes('dimensions');
console.log((hasRenderTexture && hasPreview && hasDimensions) ? 'OK' : 'BROKEN');
" 2>/dev/null)

if [ "$CHK5" = "OK" ]; then
    log_pass 0.10 "initialize_textures creates render textures, preview, and sets dimensions"
else
    log_fail 0.10 "initialize_textures broken or missing key functionality"
fi

# [pr_diff] (0.05): cleanup_textures still destroys resources
CHK6=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');
const src = fs.readFileSync('$TEXTURES_TS', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'cleanup_textures') return node;
    let found = null;
    ts.forEachChild(node, c => { if (!found) found = findMethod(c); });
    return found;
}

const method = findMethod(sf);
if (!method || !method.body) { console.log('MISSING'); process.exit(0); }

// Must call destroy on at least one resource
let hasDestroy = false;
function walk(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
        if (node.expression.name.text === 'destroy') hasDestroy = true;
    }
    ts.forEachChild(node, walk);
}
walk(method.body);
console.log(hasDestroy ? 'OK' : 'BROKEN');
" 2>/dev/null)

if [ "$CHK6" = "OK" ]; then
    log_pass 0.05 "cleanup_textures calls destroy (AST-verified)"
else
    log_fail 0.05 "cleanup_textures missing destroy calls"
fi

# ══════════════════════════════════════════════
# ANTI-STUB (0.10)
# ══════════════════════════════════════════════

# [pr_diff] (0.05): set_tool must not be stubbed (>5 statements in body)
CHK7=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');
const src = fs.readFileSync('$BRUSH_TS', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'set_tool') return node;
    let found = null;
    ts.forEachChild(node, c => { if (!found) found = findMethod(c); });
    return found;
}

const method = findMethod(sf);
if (!method || !method.body) { console.log('MISSING'); process.exit(0); }

// Count non-trivial statements (excluding empty statements)
let stmtCount = 0;
function countStmts(node) {
    if (ts.isStatement(node) && !ts.isEmptyStatement(node) && !ts.isBlock(node)) {
        stmtCount++;
    }
    ts.forEachChild(node, countStmts);
}
countStmts(method.body);
console.log(stmtCount >= 5 ? 'OK' : 'STUBBED');
" 2>/dev/null)

if [ "$CHK7" = "OK" ]; then
    log_pass 0.05 "set_tool has >=5 statements (not stubbed)"
else
    log_fail 0.05 "set_tool appears stubbed or missing"
fi

# [pr_diff] (0.05): reinitialize must not be stubbed (>3 statements)
CHK8=$(node -e "
const fs = require('fs');
const ts = require('/workspace/node_modules/typescript');
const src = fs.readFileSync('$TEXTURES_TS', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'reinitialize') return node;
    let found = null;
    ts.forEachChild(node, c => { if (!found) found = findMethod(c); });
    return found;
}

const method = findMethod(sf);
if (!method || !method.body) { console.log('MISSING'); process.exit(0); }

let stmtCount = 0;
function countStmts(node) {
    if (ts.isStatement(node) && !ts.isEmptyStatement(node) && !ts.isBlock(node)) {
        stmtCount++;
    }
    ts.forEachChild(node, countStmts);
}
countStmts(method.body);
console.log(stmtCount >= 2 ? 'OK' : 'STUBBED');
" 2>/dev/null)

if [ "$CHK8" = "OK" ]; then
    log_pass 0.05 "reinitialize has >=2 statements (not stubbed)"
else
    log_fail 0.05 "reinitialize appears stubbed or missing"
fi

# ══════════════════════════════════════════════
# CONFIG-DERIVED (0.10)
# ══════════════════════════════════════════════

# [agent_config] (0.10): "Frontend code is formatted with prettier" — AGENTS.md:44 @ 911dc366
# Gradio frontend uses tabs. Check via AST source text, not grep.
INDENT_OK=$(node -e "
const fs = require('fs');
const files = ['$BRUSH_TS', '$TEXTURES_TS'];
let ok = true;
for (const f of files) {
    const lines = fs.readFileSync(f, 'utf8').split('\n');
    for (const line of lines) {
        // Lines starting with 2+ spaces followed by code = space indentation
        if (/^ {2,}[a-zA-Z_\$\{]/.test(line)) {
            ok = false;
            break;
        }
    }
    if (!ok) break;
}
console.log(ok ? 'OK' : 'BAD');
" 2>/dev/null)

if [ "$INDENT_OK" = "OK" ]; then
    log_pass 0.10 "Modified files use consistent tab indentation per prettier config"
else
    log_fail 0.10 "Modified files have inconsistent indentation (spaces instead of tabs)"
fi

# ══════════════════════════════════════════════
# FINAL SCORE
# ══════════════════════════════════════════════
echo ""
echo "Total score: $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
# Category breakdown based on check structure
behavioral = 0.0
regression = 0.0
structural = 0.0
config_score = 0.0

# Walk through what passed
remaining = score

# F2P behavioral: 0.35 max
behavioral = min(remaining, 0.35)
remaining = max(0, remaining - 0.35)

# Silver behavioral: 0.30 max
behavioral += min(remaining, 0.30)
remaining = max(0, remaining - 0.30)

# P2P regression: 0.15 max
regression = min(remaining, 0.15)
remaining = max(0, remaining - 0.15)

# Anti-stub: 0.10 max
structural = min(remaining, 0.10)
remaining = max(0, remaining - 0.10)

# Config: 0.10 max
config_score = min(remaining, 0.10)

json.dump({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'structural': round(structural, 4),
    'config': round(config_score, 4)
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
