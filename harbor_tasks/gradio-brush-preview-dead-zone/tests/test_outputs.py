"""
Task: gradio-brush-preview-dead-zone
Repo: gradio-app/gradio @ 911dc366e56e9210fd260300915d408058ae18c6
PR:   #12981

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace"
BRUSH_TS = f"{REPO}/js/imageeditor/shared/brush/brush.ts"
TEXTURES_TS = f"{REPO}/js/imageeditor/shared/brush/brush-textures.ts"

TS_MODULE = "/tests/node_modules/typescript"


def _run_node(script: str) -> str:
    """Run a Node.js script and return stdout."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=30, text=True,
    )
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_typescript_syntax():
    """Both brush.ts and brush-textures.ts must parse without errors."""
    for f in [BRUSH_TS, TEXTURES_TS]:
        r = subprocess.run(
            ["node", "-e", f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{f}', 'utf8');
ts.createSourceFile('{f}', src, ts.ScriptTarget.Latest, true);
console.log('OK');
"""],
            capture_output=True, timeout=15, text=True,
        )
        assert r.stdout.strip() == "OK", f"{f} does not parse as valid TypeScript"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_reinitialize_uses_bounds_not_container_dims():
    """reinitialize() must NOT compare image_container.width/height directly.

    The bug: reinitialize() compared image_container.width/height which
    incorporates CSS scale transforms, giving wrong results for portrait images.
    The fix must remove these direct property accesses from comparison expressions.
    """
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{TEXTURES_TS}', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {{
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'reinitialize') return node;
    let found = null;
    ts.forEachChild(node, c => {{ if (!found) found = findMethod(c); }});
    return found;
}}

const method = findMethod(sf);
if (!method || !method.body) {{ console.log('NO_METHOD'); process.exit(0); }}

let usesBuggyPattern = false;
function walk(node) {{
    if (ts.isBinaryExpression(node)) {{
        const op = node.operatorToken.kind;
        const isComparison = [
            ts.SyntaxKind.ExclamationEqualsEqualsToken,
            ts.SyntaxKind.EqualsEqualsEqualsToken,
            ts.SyntaxKind.ExclamationEqualsToken,
            ts.SyntaxKind.EqualsEqualsToken,
        ].includes(op);
        if (isComparison) {{
            [node.left, node.right].forEach(side => {{
                if (ts.isPropertyAccessExpression(side)) {{
                    const prop = side.name.text;
                    if ((prop === 'width' || prop === 'height') && ts.isPropertyAccessExpression(side.expression)) {{
                        if (side.expression.name.text === 'image_container') {{
                            usesBuggyPattern = true;
                        }}
                    }}
                }}
            }});
        }}
    }}
    ts.forEachChild(node, walk);
}}
walk(method.body);
console.log(usesBuggyPattern ? 'BUGGY' : 'FIXED');
""")
    assert result == "FIXED", \
        f"reinitialize() still uses buggy image_container.width/height comparison (got {result})"


# [pr_diff] fail_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_set_tool_detects_dimension_changes():
    """set_tool() must trigger reinitialization when canvas dimensions change.

    The bug: set_tool() only checked mode_changed || !textures_initialized,
    so loading a new image with different dimensions didn't reinitialize textures.
    The fix must add a dimension-change condition (>2 boolean terms in the
    if-guard around initialize_textures()).
    """
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{BRUSH_TS}', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {{
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'set_tool') return node;
    let found = null;
    ts.forEachChild(node, c => {{ if (!found) found = findMethod(c); }});
    return found;
}}

const method = findMethod(sf);
if (!method || !method.body) {{ console.log('NO_METHOD'); process.exit(0); }}

function countBooleanTerms(expr) {{
    if (ts.isBinaryExpression(expr) &&
        (expr.operatorToken.kind === ts.SyntaxKind.BarBarToken ||
         expr.operatorToken.kind === ts.SyntaxKind.AmpersandAmpersandToken)) {{
        return countBooleanTerms(expr.left) + countBooleanTerms(expr.right);
    }}
    return 1;
}}

let hasInitCall = false;
let conditionTerms = 0;
function walk(node) {{
    if (ts.isIfStatement(node)) {{
        const bodyText = node.thenStatement.getText ? node.thenStatement.getText(sf) : '';
        if (bodyText.includes('initialize_textures')) {{
            hasInitCall = true;
            conditionTerms = countBooleanTerms(node.expression);
        }}
    }}
    ts.forEachChild(node, walk);
}}
walk(method.body);

if (!hasInitCall) console.log('NO_INIT_CALL');
else if (conditionTerms >= 3) console.log('HAS_DIM_CHECK');
else console.log('BASELINE_ONLY');
""")
    assert result == "HAS_DIM_CHECK", \
        f"set_tool() condition for initialize_textures must include dimension check (got {result})"


# [pr_diff] fail_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_reinitialize_calls_bounds_method():
    """reinitialize() must call a bounds-fetching method like getLocalBounds().

    Instead of reading image_container.width/height (which reflect CSS transforms),
    the fix should fetch the actual local bounds of the container.
    """
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{TEXTURES_TS}', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {{
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'reinitialize') return node;
    let found = null;
    ts.forEachChild(node, c => {{ if (!found) found = findMethod(c); }});
    return found;
}}

const method = findMethod(sf);
if (!method || !method.body) {{ console.log('NO_METHOD'); process.exit(0); }}

let hasBoundsCall = false;
function walk(node) {{
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
        const name = node.expression.name.text;
        if (['getLocalBounds', 'getBounds', 'get_bounds', 'get_local_bounds', 'getSize'].includes(name)) {{
            hasBoundsCall = true;
        }}
    }}
    ts.forEachChild(node, walk);
}}
walk(method.body);
console.log(hasBoundsCall ? 'HAS_BOUNDS' : 'NO_BOUNDS');
""")
    assert result == "HAS_BOUNDS", \
        f"reinitialize() must call a bounds-fetching method (got {result})"


# [pr_diff] fail_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_subpixel_rounding_in_comparisons():
    """Dimension comparisons must handle subpixel differences.

    Canvas bounds can be fractional. Without rounding (Math.round, Math.floor, etc.),
    dimension comparisons may flicker or always mismatch. At least one of the two
    modified files must use rounding in dimension comparisons.
    """
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');

const roundingMethods = new Set(['round', 'floor', 'ceil', 'abs', 'trunc']);

function hasSubpixelHandling(filePath) {{
    const src = fs.readFileSync(filePath, 'utf8');
    const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);
    let found = false;
    function walk(node) {{
        if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
            const obj = node.expression.expression;
            const method = node.expression.name.text;
            if (ts.isIdentifier(obj) && obj.text === 'Math' && roundingMethods.has(method)) {{
                found = true;
            }}
        }}
        if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'parseInt') {{
            found = true;
        }}
        if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.BarToken) {{
            if (ts.isNumericLiteral(node.right) && node.right.text === '0') found = true;
        }}
        if (ts.isPrefixUnaryExpression(node) && node.operator === ts.SyntaxKind.TildeToken) {{
            found = true;
        }}
        ts.forEachChild(node, walk);
    }}
    walk(sf);
    return found;
}}

const a = hasSubpixelHandling('{BRUSH_TS}');
const b = hasSubpixelHandling('{TEXTURES_TS}');
console.log((a || b) ? 'HAS_ROUNDING' : 'NO_ROUNDING');
""")
    assert result == "HAS_ROUNDING", \
        f"No subpixel handling found in dimension comparisons (got {result})"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_initialize_textures_intact():
    """initialize_textures must still create render textures and preview sprite."""
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{TEXTURES_TS}', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {{
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'initialize_textures') return node;
    let found = null;
    ts.forEachChild(node, c => {{ if (!found) found = findMethod(c); }});
    return found;
}}

const method = findMethod(sf);
if (!method || !method.body) {{ console.log('MISSING'); process.exit(0); }}

const bodyText = method.body.getText(sf);
const hasRenderTexture = bodyText.includes('RenderTexture');
const hasPreview = bodyText.includes('preview');
const hasDimensions = bodyText.includes('dimensions');
console.log((hasRenderTexture && hasPreview && hasDimensions) ? 'OK' : 'BROKEN');
""")
    assert result == "OK", \
        f"initialize_textures is broken or missing key functionality (got {result})"


# [pr_diff] pass_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_cleanup_textures_intact():
    """cleanup_textures must still call destroy on resources."""
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{TEXTURES_TS}', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {{
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'cleanup_textures') return node;
    let found = null;
    ts.forEachChild(node, c => {{ if (!found) found = findMethod(c); }});
    return found;
}}

const method = findMethod(sf);
if (!method || !method.body) {{ console.log('MISSING'); process.exit(0); }}

let hasDestroy = false;
function walk(node) {{
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
        if (node.expression.name.text === 'destroy') hasDestroy = true;
    }}
    ts.forEachChild(node, walk);
}}
walk(method.body);
console.log(hasDestroy ? 'OK' : 'BROKEN');
""")
    assert result == "OK", \
        f"cleanup_textures missing destroy calls (got {result})"


# [static] pass_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_set_tool_not_stubbed():
    """set_tool must have >=5 statements (not a stub)."""
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{BRUSH_TS}', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {{
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'set_tool') return node;
    let found = null;
    ts.forEachChild(node, c => {{ if (!found) found = findMethod(c); }});
    return found;
}}

const method = findMethod(sf);
if (!method || !method.body) {{ console.log('MISSING'); process.exit(0); }}

let stmtCount = 0;
function countStmts(node) {{
    if (ts.isStatement(node) && !ts.isEmptyStatement(node) && !ts.isBlock(node)) stmtCount++;
    ts.forEachChild(node, countStmts);
}}
countStmts(method.body);
console.log(stmtCount >= 5 ? 'OK' : 'STUBBED');
""")
    assert result == "OK", f"set_tool appears stubbed or missing (got {result})"


# [static] pass_to_pass
# AST-only because: TS class methods require pixi.js WebGL runtime (cannot execute)
def test_reinitialize_not_stubbed():
    """reinitialize must have >=2 statements (not a stub)."""
    result = _run_node(f"""
const fs = require('fs');
const ts = require('{TS_MODULE}');
const src = fs.readFileSync('{TEXTURES_TS}', 'utf8');
const sf = ts.createSourceFile('file.ts', src, ts.ScriptTarget.Latest, true);

function findMethod(node) {{
    if (ts.isMethodDeclaration(node) && node.name && node.name.text === 'reinitialize') return node;
    let found = null;
    ts.forEachChild(node, c => {{ if (!found) found = findMethod(c); }});
    return found;
}}

const method = findMethod(sf);
if (!method || !method.body) {{ console.log('MISSING'); process.exit(0); }}

let stmtCount = 0;
function countStmts(node) {{
    if (ts.isStatement(node) && !ts.isEmptyStatement(node) && !ts.isBlock(node)) stmtCount++;
    ts.forEachChild(node, countStmts);
}}
countStmts(method.body);
console.log(stmtCount >= 2 ? 'OK' : 'STUBBED');
""")
    assert result == "OK", f"reinitialize appears stubbed or missing (got {result})"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md:44 @ 911dc366
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:44 @ 911dc366
def test_tab_indentation():
    """Modified files must use tab indentation per prettier config (AGENTS.md:44)."""
    for filepath in [BRUSH_TS, TEXTURES_TS]:
        content = Path(filepath).read_text()
        for i, line in enumerate(content.splitlines(), 1):
            assert not __import__('re').match(r'^ {2,}[a-zA-Z_${]', line), \
                f"{filepath}:{i} uses space indentation instead of tabs"
