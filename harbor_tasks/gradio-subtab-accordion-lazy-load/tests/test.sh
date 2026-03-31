#!/usr/bin/env bash
set +e

REPO="/workspace/gradio"
SCORE=0
INIT_TS="$REPO/js/core/src/_init.ts"
SVELTE_TS="$REPO/js/core/src/init.svelte.ts"

pass() { echo "PASS: $1"; SCORE=$(python3 -c "print($SCORE + $2)"); }
fail() { echo "FAIL: $1"; }

# ── GATE (0.00): TypeScript syntax check ─────────────────────────────
echo "=== GATE: Syntax check ==="
node -e "
const fs = require('fs');
const ts = require('$REPO/node_modules/typescript');
const files = ['$INIT_TS', '$SVELTE_TS'];
let errors = false;
for (const f of files) {
  try {
    const src = fs.readFileSync(f, 'utf8');
    const result = ts.transpileModule(src, {
      compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.ESNext },
      reportDiagnostics: true
    });
    const diags = result.diagnostics || [];
    const realErrors = diags.filter(d => d.category === ts.DiagnosticCategory.Error);
    if (realErrors.length > 0) {
      console.error('Syntax errors in ' + f);
      errors = true;
    }
  } catch(e) {
    console.error('Failed to parse ' + f + ':', e.message);
    errors = true;
  }
}
if (errors) process.exit(1);
" 2>&1 || {
    echo "GATE FAILED: TypeScript syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
    exit 0
}
echo "GATE PASSED"

# ── BEHAVIORAL FAIL-TO-PASS (0.35): tabs filtering in make_visible_if_not_rendered ──
# [pr_diff] (0.35): On buggy code, ALL tab children are made visible; fix should only visit selected tab
echo "=== F2P: make_visible_if_not_rendered filters by selected tab ==="
node -e "
const fs = require('fs');
const ts = require('$REPO/node_modules/typescript');

// Extract make_visible_if_not_rendered from source
const src = fs.readFileSync('$SVELTE_TS', 'utf8');
const fnStart = src.indexOf('function make_visible_if_not_rendered');
if (fnStart === -1) { console.error('function make_visible_if_not_rendered not found'); process.exit(1); }

const rest = src.substring(fnStart);
let depth = 0, fnEnd = 0, started = false;
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '{') { depth++; started = true; }
  if (rest[i] === '}') { depth--; }
  if (started && depth === 0) { fnEnd = i + 1; break; }
}
const fnSource = rest.substring(0, fnEnd);

// Transpile TS -> JS (strip type annotations)
const jsResult = ts.transpileModule(fnSource, {
  compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.None }
});
const jsCode = jsResult.outputText;

// Evaluate the function into scope
eval(jsCode);

// Build a mock tabs node with two tab items, each with a child
// Tab 10 is selected, tab 20 is not
const mkNode = (id, type, props, children) => ({
  id, type, props: { props: props || {}, shared_props: { visible: false } }, children: children || []
});

const child1 = mkNode(100, 'textbox');
const child2 = mkNode(200, 'textbox');
const tab1 = mkNode(10, 'tabitem', { id: 10 }, [child1]);
const tab2 = mkNode(20, 'tabitem', { id: 20 }, [child2]);
const tabsNode = mkNode(1, 'tabs', { selected: 10 }, [tab1, tab2]);

const hidden = new Set([1, 10, 20, 100, 200]);

// Call the function (with is_target_node=false if it accepts 3 args, or 2 args for buggy version)
try {
  make_visible_if_not_rendered(tabsNode, hidden, false);
} catch(e) {
  // Buggy version only takes 2 args but that's fine - extra args are ignored in JS
  make_visible_if_not_rendered(tabsNode, hidden);
}

// CRITICAL CHECK: non-selected tab's child must NOT be made visible
// Buggy code recurses into ALL children, so child2 (id:200) becomes visible
// Fixed code only recurses into selected tab (id:10), so child2 stays hidden
if (child2.props.shared_props.visible === true) {
  console.error('BUG: non-selected tab child (id:200) was made visible - tabs not filtered');
  process.exit(1);
}

// Selected tab's child should be visible
if (!child1.props.shared_props.visible) {
  console.error('Selected tab child (id:100) was not made visible');
  process.exit(1);
}

console.log('Tab filtering works: only selected tab children made visible');
" 2>&1 && pass "[pr_diff] make_visible_if_not_rendered filters by selected tab" 0.35 \
        || fail "[pr_diff] make_visible_if_not_rendered filters by selected tab" 0.35

# ── BEHAVIORAL FAIL-TO-PASS (0.25): closed accordion skipped ─────────
# [pr_diff] (0.25): On buggy code, closed accordion children are made visible; fix should skip them
echo "=== F2P: make_visible_if_not_rendered skips closed accordion children ==="
node -e "
const fs = require('fs');
const ts = require('$REPO/node_modules/typescript');

const src = fs.readFileSync('$SVELTE_TS', 'utf8');
const fnStart = src.indexOf('function make_visible_if_not_rendered');
if (fnStart === -1) { console.error('function not found'); process.exit(1); }

const rest = src.substring(fnStart);
let depth = 0, fnEnd = 0, started = false;
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '{') { depth++; started = true; }
  if (rest[i] === '}') { depth--; }
  if (started && depth === 0) { fnEnd = i + 1; break; }
}
const fnSource = rest.substring(0, fnEnd);
const jsCode = ts.transpileModule(fnSource, {
  compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.None }
}).outputText;

eval(jsCode);

const mkNode = (id, type, props, children) => ({
  id, type, props: { props: props || {}, shared_props: { visible: false } }, children: children || []
});

// Closed accordion with a child textbox
const child = mkNode(100, 'textbox');
const accordion = mkNode(1, 'accordion', { open: false }, [child]);
const hidden = new Set([1, 100]);

try {
  make_visible_if_not_rendered(accordion, hidden, false);
} catch(e) {
  make_visible_if_not_rendered(accordion, hidden);
}

// CRITICAL CHECK: closed accordion's child must NOT be made visible
// Buggy code recurses unconditionally, so child becomes visible
// Fixed code skips recursion for closed accordion (when not target node)
if (child.props.shared_props.visible === true) {
  console.error('BUG: closed accordion child was made visible - accordion not respected');
  process.exit(1);
}

// The accordion itself should be visible (it's in hidden_on_startup)
if (!accordion.props.shared_props.visible) {
  console.error('Accordion itself should be made visible');
  process.exit(1);
}

console.log('Closed accordion children correctly skipped');
" 2>&1 && pass "[pr_diff] make_visible_if_not_rendered skips closed accordion children" 0.25 \
        || fail "[pr_diff] make_visible_if_not_rendered skips closed accordion children" 0.25

# ── BEHAVIORAL (0.10): accordion IS_TARGET bypasses closed skip ──────
# [pr_diff] (0.10): When accordion is the direct target (user clicks it), children should render
echo "=== Behavioral: target accordion renders children even when closed ==="
node -e "
const fs = require('fs');
const ts = require('$REPO/node_modules/typescript');

const src = fs.readFileSync('$SVELTE_TS', 'utf8');
const fnStart = src.indexOf('function make_visible_if_not_rendered');
if (fnStart === -1) { process.exit(1); }

const rest = src.substring(fnStart);
let depth = 0, fnEnd = 0, started = false;
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '{') { depth++; started = true; }
  if (rest[i] === '}') { depth--; }
  if (started && depth === 0) { fnEnd = i + 1; break; }
}
const fnSource = rest.substring(0, fnEnd);
const jsCode = ts.transpileModule(fnSource, {
  compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.None }
}).outputText;

eval(jsCode);

const mkNode = (id, type, props, children) => ({
  id, type, props: { props: props || {}, shared_props: { visible: false } }, children: children || []
});

// Closed accordion, but this time it IS the target node
const child = mkNode(100, 'textbox');
const accordion = mkNode(1, 'accordion', { open: false }, [child]);
const hidden = new Set([1, 100]);

// When is_target_node=true, even a closed accordion should render children
try {
  make_visible_if_not_rendered(accordion, hidden, true);
} catch(e) {
  // If function doesn't accept 3rd arg, this test is N/A (buggy version)
  console.error('Function does not accept is_target_node parameter');
  process.exit(1);
}

if (!child.props.shared_props.visible) {
  console.error('Target accordion should render children even when closed');
  process.exit(1);
}

console.log('Target accordion correctly renders children');
" 2>&1 && pass "[pr_diff] target accordion renders children even when closed" 0.10 \
        || fail "[pr_diff] target accordion renders children even when closed" 0.10

# ── BEHAVIORAL (0.10): determine_visible_components handles accordion ─
# [pr_diff] (0.10): _init.ts must add accordion to visible set and conditionally recurse
echo "=== Behavioral: determine_visible_components handles accordion type ==="
node -e "
const fs = require('fs');
const ts = require('$REPO/node_modules/typescript');

// Use TypeScript AST to verify there's an actual conditional branch for accordion
// (not just a keyword - must be a real if/else-if with type check and open check)
const src = fs.readFileSync('$INIT_TS', 'utf8');
const sourceFile = ts.createSourceFile('_init.ts', src, ts.ScriptTarget.ESNext, true);

let found_accordion_branch = false;
let has_open_check = false;
let has_recursion_in_branch = false;

function visit(node) {
  // Look for: if/else-if with condition checking component.type === 'accordion'
  if (ts.isIfStatement(node) || (ts.isIfStatement(node.parent) && node === node.parent.elseStatement)) {
    const text = node.getText(sourceFile);
    // Check if this branch tests for accordion type
    const condition = ts.isIfStatement(node) ? node.expression.getText(sourceFile) : '';
    if (condition.includes('accordion') && condition.includes('type')) {
      found_accordion_branch = true;
      const body = node.thenStatement.getText(sourceFile);
      // Must check open prop
      if (body.includes('open') || body.includes('props')) {
        has_open_check = true;
      }
      // Must have conditional recursion (process_children_visibility or similar)
      if (body.includes('process_children') || body.includes('determine_visible') || body.includes('forEach')) {
        has_recursion_in_branch = true;
      }
    }
  }
  ts.forEachChild(node, visit);
}
visit(sourceFile);

if (!found_accordion_branch) {
  console.error('No if-branch found that tests for accordion type');
  process.exit(1);
}
if (!has_open_check) {
  console.error('Accordion branch does not check open state');
  process.exit(1);
}
if (!has_recursion_in_branch) {
  console.error('Accordion branch does not conditionally recurse into children');
  process.exit(1);
}

console.log('determine_visible_components has proper accordion handling branch');
" 2>&1 && pass "[pr_diff] determine_visible_components has accordion handling with open-state check" 0.10 \
        || fail "[pr_diff] determine_visible_components has accordion handling with open-state check" 0.10

# ── PASS-TO-PASS (0.10): Existing functionality preserved ────────────

# [pr_diff] (0.05): tabs/tabitem handling preserved in _init.ts
echo "=== P2P: tabs handling preserved ==="
node -e "
const fs = require('fs');
const ts = require('$REPO/node_modules/typescript');
const src = fs.readFileSync('$INIT_TS', 'utf8');
const sourceFile = ts.createSourceFile('_init.ts', src, ts.ScriptTarget.ESNext, true);

// Verify there are if-branches checking for tabs and tabitem types
let has_tabs = false, has_tabitem = false;
function visit(node) {
  if (ts.isIfStatement(node)) {
    const cond = node.expression.getText(sourceFile);
    if (cond.includes('tabs') && cond.includes('type')) has_tabs = true;
    if (cond.includes('tabitem') && cond.includes('type')) has_tabitem = true;
  }
  ts.forEachChild(node, visit);
}
visit(sourceFile);

if (!has_tabs || !has_tabitem) {
  console.error('tabs/tabitem handling removed from determine_visible_components');
  process.exit(1);
}
console.log('tabs/tabitem handling preserved');
" 2>&1 && pass "[pr_diff] existing tabs/tabitem handling preserved" 0.05 \
        || fail "[pr_diff] existing tabs/tabitem handling preserved" 0.05

# [pr_diff] (0.05): make_visible_if_not_rendered still sets visibility from hidden_on_startup
echo "=== P2P: basic visibility setting works ==="
node -e "
const fs = require('fs');
const ts = require('$REPO/node_modules/typescript');

const src = fs.readFileSync('$SVELTE_TS', 'utf8');
const fnStart = src.indexOf('function make_visible_if_not_rendered');
if (fnStart === -1) { process.exit(1); }
const rest = src.substring(fnStart);
let depth = 0, fnEnd = 0, started = false;
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '{') { depth++; started = true; }
  if (rest[i] === '}') { depth--; }
  if (started && depth === 0) { fnEnd = i + 1; break; }
}
const fnSource = rest.substring(0, fnEnd);
const jsCode = ts.transpileModule(fnSource, {
  compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.None }
}).outputText;

eval(jsCode);

const mkNode = (id, type, props, children) => ({
  id, type, props: { props: props || {}, shared_props: { visible: false } }, children: children || []
});

// Basic test: a simple node in hidden_on_startup should become visible
const node = mkNode(1, 'column', {}, [mkNode(2, 'textbox')]);
const hidden = new Set([1, 2]);
try { make_visible_if_not_rendered(node, hidden, false); } catch(e) { make_visible_if_not_rendered(node, hidden); }

if (!node.props.shared_props.visible) {
  console.error('Node in hidden_on_startup was not made visible');
  process.exit(1);
}
if (!node.children[0].props.shared_props.visible) {
  console.error('Child in hidden_on_startup was not made visible');
  process.exit(1);
}

// Node NOT in hidden_on_startup should keep original visibility
const node2 = mkNode(5, 'column', {}, []);
node2.props.shared_props.visible = false;
try { make_visible_if_not_rendered(node2, new Set(), false); } catch(e) { make_visible_if_not_rendered(node2, new Set()); }
if (node2.props.shared_props.visible !== false) {
  console.error('Node not in hidden_on_startup had visibility changed');
  process.exit(1);
}

console.log('Basic visibility setting works correctly');
" 2>&1 && pass "[pr_diff] basic visibility setting preserved" 0.05 \
        || fail "[pr_diff] basic visibility setting preserved" 0.05

# ── STRUCTURAL (0.10): Anti-stub ─────────────────────────────────────

# [pr_diff] (0.05): Both files non-trivially modified
echo "=== Structural: anti-stub file size ==="
INIT_LINES=$(wc -l < "$INIT_TS")
SVELTE_LINES=$(wc -l < "$SVELTE_TS")
# Original: _init.ts ~968 lines, init.svelte.ts ~505 lines
# Fix adds ~10 lines to _init.ts and ~20 lines to init.svelte.ts
if [ "$INIT_LINES" -gt 970 ] && [ "$SVELTE_LINES" -gt 510 ]; then
    pass "[pr_diff] both files show non-trivial growth" 0.05
else
    fail "[pr_diff] files don't show expected growth (init:$INIT_LINES svelte:$SVELTE_LINES)" 0.05
fi

# [pr_diff] (0.05): render_previously_invisible_children passes is_target_node flag
echo "=== Structural: target node flag in caller ==="
node -e "
const fs = require('fs');
const src = fs.readFileSync('$SVELTE_TS', 'utf8');
// Find the call site in render_previously_invisible_children
const callerIdx = src.indexOf('render_previously_invisible_children');
if (callerIdx === -1) { console.error('render_previously_invisible_children not found'); process.exit(1); }
// Look for make_visible_if_not_rendered call within the next 1000 chars
const section = src.substring(callerIdx, callerIdx + 1000);
const callMatch = section.match(/make_visible_if_not_rendered\s*\([^)]+\)/);
if (!callMatch) { console.error('call to make_visible_if_not_rendered not found'); process.exit(1); }
const args = callMatch[0].split(',');
if (args.length < 3) {
  console.error('make_visible_if_not_rendered called without target flag (' + args.length + ' args)');
  process.exit(1);
}
console.log('Target node flag correctly passed');
" 2>&1 && pass "[pr_diff] target node flag passed in caller" 0.05 \
        || fail "[pr_diff] target node flag passed in caller" 0.05

# ── FINAL SCORING ─────────────────────────────────────────────────────
echo ""
echo "=== RESULTS ==="
echo "Score: $SCORE / 1.0"

FINAL=$(python3 -c "print(max(0.0, min(1.0, $SCORE)))")
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
s = $SCORE
behavioral = min(s, 0.80)
regression = min(max(s - 0.80, 0), 0.10)
structural = min(max(s - 0.90, 0), 0.10)
json.dump({
    'reward': round(s, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'structural': round(structural, 4),
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

echo "Final reward: $FINAL"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
