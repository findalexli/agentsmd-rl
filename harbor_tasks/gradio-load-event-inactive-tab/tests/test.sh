#!/usr/bin/env bash
set +e

TOTAL=0.0
PASS=0.0

add() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }
award() { PASS=$(python3 -c "print($PASS + $1)"); }

cd /workspace/gradio

FILE="js/core/src/init.svelte.ts"

########################################
# GATE: File exists and has AppTree class
########################################
# [pr_diff] (0.00): init.svelte.ts must exist and contain AppTree
if [ ! -f "$FILE" ]; then
    echo "GATE FAILED: $FILE not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
node -e "
const src = require('fs').readFileSync('$FILE', 'utf8');
if (!src.includes('class AppTree')) {
    console.error('GATE FAILED: AppTree class not found');
    process.exit(1);
}
" 2>&1
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

########################################
# Helper: strip comments from JS/TS code for pattern matching
########################################
STRIP_COMMENTS='function strip(code) { return code.replace(/\/\/.*/g, "").replace(/\/\*[\s\S]*?\*\//g, ""); }'

########################################
# Fail-to-pass: Behavioral tests (0.75)
########################################

# [pr_diff] (0.30): Core bug removed — spread-replace pattern absent in !_set_data branch
# BUG: node!.props.props = { ...node?.props.props, ...new_props.props }
# replaces the entire props object, breaking Svelte 5 $state proxy tracking.
# ANY correct fix must remove this pattern. We test bug ABSENCE, not fix shape.
add 0.30
node -e "
const fs = require('fs');
const src = fs.readFileSync('$FILE', 'utf8');
${STRIP_COMMENTS}

// Extract update_state method body
const updateStart = src.indexOf('async update_state(');
if (updateStart === -1) { console.error('FAIL: update_state method not found'); process.exit(1); }

// Get method body by brace matching
let depth = 0, started = false, updateBody = '';
for (let i = updateStart; i < src.length && i < updateStart + 4000; i++) {
    if (src[i] === '{') { depth++; started = true; }
    if (src[i] === '}') depth--;
    if (started) updateBody += src[i];
    if (started && depth === 0) break;
}

// Verify method is substantial (not a stub)
const meaningful = strip(updateBody).split('\n').map(l=>l.trim()).filter(l=>l&&l!=='{'&&l!=='}').length;
if (meaningful < 10) {
    console.error('FAIL: update_state appears to be a stub (' + meaningful + ' lines)');
    process.exit(1);
}

// Find the !_set_data branch
const noCallbackStart = updateBody.indexOf('if (!_set_data)');
if (noCallbackStart === -1) {
    // Method restructured — acceptable if method is substantial (verified above)
    console.log('PASS: update_state restructured, spread-replace bug absent');
    process.exit(0);
}

const elseCallback = updateBody.indexOf('else if (_set_data)', noCallbackStart);
const noCallbackBranch = (elseCallback > noCallbackStart)
    ? updateBody.substring(noCallbackStart, elseCallback)
    : updateBody.substring(noCallbackStart, noCallbackStart + 600);

const code = strip(noCallbackBranch);

// The bug: replacing props.props via spread — .props.props = { ... ...
if (code.match(/\.props\.props\s*=\s*\{[^}]*\.\.\./)) {
    console.error('FAIL: spread-replace pattern still present in !_set_data branch');
    console.error('This breaks Svelte \$state proxy tracking');
    process.exit(1);
}

console.log('PASS: spread-replace bug removed from update_state');
" 2>&1
[ $? -eq 0 ] && award 0.30

# [pr_diff] (0.20): update_state stores deferred state for unmounted components
# When _set_data callback is unavailable, updates must be stored on the class
# instance for later application by register_component. We check that the
# !_set_data branch writes to a class-level data structure (any Map/array/object).
# Accepts: this.X.set(), this.X.push(), this.X[k]=v, this.X.add()
add 0.20
node -e "
const fs = require('fs');
const src = fs.readFileSync('$FILE', 'utf8');
${STRIP_COMMENTS}

const updateStart = src.indexOf('async update_state(');
if (updateStart === -1) { console.error('FAIL: update_state not found'); process.exit(1); }

let depth = 0, started = false, updateBody = '';
for (let i = updateStart; i < src.length && i < updateStart + 4000; i++) {
    if (src[i] === '{') { depth++; started = true; }
    if (src[i] === '}') depth--;
    if (started) updateBody += src[i];
    if (started && depth === 0) break;
}

const noCallbackStart = updateBody.indexOf('if (!_set_data)');
let targetBlock;
if (noCallbackStart === -1) {
    // Method restructured — check entire body for class-level storage
    targetBlock = strip(updateBody);
} else {
    const elseCallback = updateBody.indexOf('else if (_set_data)', noCallbackStart);
    targetBlock = strip(
        (elseCallback > noCallbackStart)
            ? updateBody.substring(noCallbackStart, elseCallback)
            : updateBody.substring(noCallbackStart, noCallbackStart + 600)
    );
}

// Must write to a class-level store (this.something.method() or this.something[key])
const writesToClassStore =
    targetBlock.match(/this[.\[#]\S*\.(set|push|add)\s*\(/) ||
    targetBlock.match(/this[.\[#]\S*\[.*\]\s*=/);

if (!writesToClassStore) {
    console.error('FAIL: update_state does not store deferred state on class instance');
    process.exit(1);
}

console.log('PASS: update_state stores deferred state on class instance');
" 2>&1
[ $? -eq 0 ] && award 0.20

# [pr_diff] (0.15): register_component applies deferred state upon mounting
# The buggy register_component is ~6 lines: it just stores callbacks and resolves ready.
# Any correct fix must add logic to check for and apply deferred state, making the
# method substantially longer and include reads from a shared data structure.
add 0.15
node -e "
const fs = require('fs');
const src = fs.readFileSync('$FILE', 'utf8');
${STRIP_COMMENTS}

const regStart = src.indexOf('register_component(');
if (regStart === -1) { console.error('FAIL: register_component not found'); process.exit(1); }

// Extract method body by brace matching
let depth = 0, started = false, methodBody = '';
for (let i = regStart; i < src.length && i < regStart + 3000; i++) {
    if (src[i] === '{') { depth++; started = true; }
    if (src[i] === '}') depth--;
    if (started) methodBody += src[i];
    if (started && depth === 0) break;
}

const code = strip(methodBody);
const meaningfulLines = code.split('\n').map(l => l.trim())
    .filter(l => l && l !== '{' && l !== '}').length;

// Buggy version has ~6 meaningful lines. Any deferred state fix adds significant logic.
if (meaningfulLines < 10) {
    console.error('FAIL: register_component has only ' + meaningfulLines + ' meaningful lines');
    console.error('Expected: deferred state application logic (>= 10 lines)');
    process.exit(1);
}

// Must read from a class-level data structure (the same one update_state writes to)
const readsFromStore =
    code.match(/this[.\[#]\S*\.(get|has|delete|size|length|shift|pop|keys|entries|forEach)\s*\(/) ||
    code.match(/this[.\[#]\S*\[.*\]/);

if (!readsFromStore) {
    console.error('FAIL: register_component does not read from any deferred state store');
    process.exit(1);
}

console.log('PASS: register_component applies deferred state (' + meaningfulLines + ' meaningful lines)');
" 2>&1
[ $? -eq 0 ] && award 0.15

# [pr_diff] (0.10): render_previously_invisible_children avoids full tree traversal
# BUG: this.root = this.traverse(this.root!, [...]) does a full tree traversal
# and root reassignment, triggering unnecessary Svelte reactive cascades.
# ANY correct fix must remove this pattern from this method.
add 0.10
node -e "
const fs = require('fs');
const src = fs.readFileSync('$FILE', 'utf8');
${STRIP_COMMENTS}

const methodStart = src.indexOf('render_previously_invisible_children(');
if (methodStart === -1) { console.error('FAIL: render_previously_invisible_children not found'); process.exit(1); }

// Extract method body
let depth = 0, started = false, methodBody = '';
for (let i = methodStart; i < src.length && i < methodStart + 2000; i++) {
    if (src[i] === '{') { depth++; started = true; }
    if (src[i] === '}') depth--;
    if (started) methodBody += src[i];
    if (started && depth === 0) break;
}

const code = strip(methodBody);
const meaningfulLines = code.split('\n').map(l => l.trim())
    .filter(l => l && l !== '{' && l !== '}').length;

// Verify method has content (not a stub)
if (meaningfulLines < 2) {
    console.error('FAIL: render_previously_invisible_children appears to be a stub');
    process.exit(1);
}

// The bug: full tree traversal with root reassignment
if (code.includes('this.root = this.traverse(this.root')) {
    console.error('FAIL: still does full tree traversal with root reassignment');
    process.exit(1);
}

console.log('PASS: render_previously_invisible_children avoids full tree traversal');
" 2>&1
[ $? -eq 0 ] && award 0.10

########################################
# Pass-to-pass: Regression (0.10)
########################################

# [repo_tests] (0.05): Core AppTree methods still present and functional
add 0.05
node -e "
const src = require('fs').readFileSync('$FILE', 'utf8');
const required = [
    'register_component(', 'update_state(', 'render_previously_invisible_children(',
    'get_state(', 'traverse(', 'create_node(', 'postprocess('
];
for (const sig of required) {
    if (!src.includes(sig)) {
        console.error('FAIL: method ' + sig.slice(0,-1) + ' is missing');
        process.exit(1);
    }
}
console.log('PASS: all core AppTree methods present');
" 2>&1
[ $? -eq 0 ] && award 0.05

# [repo_tests] (0.05): Standalone helper functions and tab/accordion handling intact
add 0.05
node -e "
const src = require('fs').readFileSync('$FILE', 'utf8');
const required = ['make_visible_if_not_rendered', 'handle_visibility', 'find_node_by_id',
    'gather_initial_tabs', 'create_props_shared_props', 'set_visibility_for_updated_node'];
for (const fn of required) {
    if (!src.includes('function ' + fn) && !src.includes(fn + '(')) {
        console.error('FAIL: function ' + fn + ' is missing');
        process.exit(1);
    }
}
// Verify tab/accordion handling in make_visible_if_not_rendered
const mvirStart = src.indexOf('make_visible_if_not_rendered');
const mvirBlock = src.substring(mvirStart, mvirStart + 1000);
if (!mvirBlock.includes('tab')) {
    console.error('FAIL: tab handling removed from make_visible_if_not_rendered');
    process.exit(1);
}
if (!mvirBlock.includes('accordion')) {
    console.error('FAIL: accordion handling removed from make_visible_if_not_rendered');
    process.exit(1);
}
console.log('PASS: helper functions and tab/accordion handling intact');
" 2>&1
[ $? -eq 0 ] && award 0.05

########################################
# Config-derived (0.10)
########################################

# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:56 @ 6011b00d
add 0.05
node -e "
const src = require('fs').readFileSync('$FILE', 'utf8');
const lines = src.split('\n');
const tabIndented = lines.filter(l => /^\t/.test(l)).length;
const spaceIndented = lines.filter(l => /^  \S/.test(l)).length;
if (spaceIndented > tabIndented) {
    console.error('FAIL: uses spaces instead of tabs (inconsistent with repo style)');
    process.exit(1);
}
console.log('PASS: consistent indentation style');
" 2>&1
[ $? -eq 0 ] && award 0.05

# [agent_config] (0.05): "Frontend code is formatted with prettier" — AGENTS.md:55 @ 6011b00d
# Check for common formatting issues and debug artifacts
add 0.05
node -e "
const src = require('fs').readFileSync('$FILE', 'utf8');
const lines = src.split('\n');
let trailingWS = 0;
for (const l of lines) {
    if (/\S\s+$/.test(l)) trailingWS++;
}
if (trailingWS > 10) {
    console.error('FAIL: excessive trailing whitespace (' + trailingWS + ' lines)');
    process.exit(1);
}
// No debug logging in AppTree class
const classBody = src.substring(src.indexOf('class AppTree'));
if (/console\.(log|debug)\(/.test(classBody)) {
    console.error('FAIL: debug logging artifacts in AppTree class');
    process.exit(1);
}
console.log('PASS: formatting clean, no debug artifacts');
" 2>&1
[ $? -eq 0 ] && award 0.05

########################################
# Style rubric (0.05)
########################################

# [agent_config] (0.05): TypeScript quality — no @ts-ignore added, proper typing
add 0.05
node -e "
const fs = require('fs');
const src = fs.readFileSync('$FILE', 'utf8');

// Count @ts-ignore comments — the buggy version has a few; adding many more is a smell
const tsIgnoreCount = (src.match(/@ts-ignore/g) || []).length;
// Buggy version has ~3 @ts-ignore. Allow up to 6 (some tolerance), but flag excessive use.
if (tsIgnoreCount > 8) {
    console.error('FAIL: excessive @ts-ignore usage (' + tsIgnoreCount + '), suggests typing workarounds');
    process.exit(1);
}

// Verify no 'any' type annotations added around the changed methods
// (The existing codebase uses 'any' in a few places, so just check it's not excessive)
const anyCount = (src.match(/:\s*any[^_\w]/g) || []).length;
if (anyCount > 15) {
    console.error('FAIL: excessive any types (' + anyCount + '), suggests typing shortcuts');
    process.exit(1);
}

console.log('PASS: TypeScript quality acceptable');
" 2>&1
[ $? -eq 0 ] && award 0.05

########################################
# Compute final reward
########################################

REWARD=$(python3 -c "print(round($PASS, 2))")
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
reward = round($PASS, 2)
behavioral = round(min($PASS, 0.75), 2)
remaining = max($PASS - 0.75, 0.0)
regression = round(min(remaining, 0.10), 2)
remaining2 = max(remaining - 0.10, 0.0)
config = round(min(remaining2, 0.10), 2)
remaining3 = max(remaining2 - 0.10, 0.0)
style = round(min(remaining3, 0.05), 2)
print(json.dumps({
    'reward': reward,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
    'style_rubric': style
}))
" > /logs/verifier/reward.json

echo "Total reward: $REWARD"
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
