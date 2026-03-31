#!/usr/bin/env bash
set +e

SCORE=0.0
TOTAL=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/gradio

##############################################################################
# GATE: Key files must exist and not be empty
##############################################################################
# [pr_diff] (gate): Modified files must exist
for f in js/utils/src/utils.svelte.ts js/tootils/src/render.ts js/textbox/shared/Textbox.svelte; do
    if [ ! -s "$f" ]; then
        echo "GATE FAILED: $f is missing or empty"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done

##############################################################################
# BEHAVIORAL F2P-1 (0.30): No-op dispatcher removed from Gradio class
# Buggy code: __GRADIO_BROWSER_TEST__ -> dispatcher = () => {} -> early return
# The early return prevents register_component and dispatcher from being wired
# from shared props. ANY correct fix removes this early return.
# WHY structural: Svelte 5 runes file requires Svelte compiler (not in image)
##############################################################################
# [pr_diff] (0.30): No-op dispatcher override removed, shared props wired
add_total 0.30
node -e "
const src = require('fs').readFileSync('js/utils/src/utils.svelte.ts', 'utf8');

// F2P: buggy code has __GRADIO_BROWSER_TEST__ -> no-op -> early return
// This MUST be removed for any correct fix
if (src.includes('__GRADIO_BROWSER_TEST__')) {
    console.log('FAIL: __GRADIO_BROWSER_TEST__ no-op override still present');
    process.exit(1);
}

// The early return also skipped register_component assignment.
// After fix, both register_component and dispatcher must be assigned from shared.
// Accept ANY syntax: direct property access, optional chaining, destructuring, etc.
// Just verify the constructor references 'shared' and assigns both properties.

// Find the Gradio class constructor
const ctorMatch = src.match(/constructor\s*\([^)]*\)\s*\{([\s\S]*?)(?:\n\t\}|\n    \})/);
if (!ctorMatch) {
    console.log('FAIL: Gradio constructor not found');
    process.exit(1);
}
const ctorBody = ctorMatch[1];

// dispatcher must be assigned from shared (not standalone no-op)
// Accepts: this.shared.dispatcher, shared?.dispatcher, destructured, etc.
const dispatcherAssigned = ctorBody.includes('dispatcher') &&
    (ctorBody.includes('shared') || ctorBody.includes('_props'));
if (!dispatcherAssigned) {
    console.log('FAIL: dispatcher not wired from shared props in constructor');
    process.exit(1);
}

// register_component must also be assigned from shared
const registerAssigned = ctorBody.includes('register_component') &&
    (ctorBody.includes('shared') || ctorBody.includes('_props'));
if (!registerAssigned) {
    console.log('FAIL: register_component not wired from shared props in constructor');
    process.exit(1);
}

// Must NOT have early return before these assignments
// The buggy pattern: if (!is_browser || ...) { this.dispatcher = () => {}; return; }
// Check no return statement precedes dispatcher/register assignments
const dispIdx = ctorBody.indexOf('dispatcher');
const regIdx = ctorBody.indexOf('register_component');
const assignStart = Math.min(dispIdx, regIdx);
const beforeAssigns = ctorBody.substring(0, assignStart);
// If there's a return before the assignments that's in a block setting dispatcher to no-op, fail
if (/this\.dispatcher\s*=\s*\(\s*\)\s*=>\s*\{\s*\}[\s\S]*?return/m.test(beforeAssigns)) {
    console.log('FAIL: early return still sets dispatcher to no-op');
    process.exit(1);
}

console.log('PASS: no-op dispatcher removed, shared props wired');
" 2>&1
if [ $? -eq 0 ]; then
    echo "PASS: No-op dispatcher override removed"
    add_score 0.30
else
    echo "FAIL: No-op dispatcher override not properly removed"
fi

##############################################################################
# BEHAVIORAL F2P-2 (0.25): Event listener infrastructure in render.ts
# Buggy: mockDispatcher creates CustomEvent with no real listener tracking.
# listen() doesn't exist, no way for tests to observe dispatched events.
# register_component is () => {}, so set_data/get_data never captured.
# WHY structural: render.ts imports vitest, @testing-library/dom, svelte —
#   none installed in Docker image
##############################################################################
# [pr_diff] (0.25): Event infrastructure: listen, notify, non-noop wiring
add_total 0.25
node -e "
const src = require('fs').readFileSync('js/tootils/src/render.ts', 'utf8');

// F2P check: old buggy pattern had no listener infrastructure
// The old code: mockDispatcher dispatches CustomEvent, no Map, no listen function
// Any correct fix must add listener tracking

// 1. Must have some form of listener registry (Map, object, array)
const hasListenerStorage =
    /(?:event_listeners|eventListeners|listener_map|listenerMap|_listeners)\s*=\s*new\s+Map/.test(src) ||
    /(?:const|let|var)\s+(?:event_listeners|eventListeners|listeners)\s*[:=]/.test(src);
if (!hasListenerStorage) {
    console.log('FAIL: no listener registry found (need Map or equivalent)');
    process.exit(1);
}

// 2. Must have a listen function (any name style)
const hasListen = /function\s+listen\s*\(|(?:const|let)\s+listen\s*=/.test(src);
if (!hasListen) {
    console.log('FAIL: no listen function defined');
    process.exit(1);
}

// 3. listen must be returned from render()
const returnBlock = src.match(/return\s*\{[\s\S]*?\n\t\}/);
if (!returnBlock || !returnBlock[0].includes('listen')) {
    console.log('FAIL: listen not included in render return value');
    process.exit(1);
}

// 4. dispatcher must notify listeners, not just fire DOM CustomEvent
// Accept: any function that calls listener callbacks (forEach, for-of, etc.)
// Reject: old pattern of just new CustomEvent('gradio', ...)
const hasNotifyMechanism =
    src.includes('notify_listeners') ||
    src.includes('notifyListeners') ||
    // Generic: dispatcher body iterates listeners
    /dispatcher[\s\S]{0,200}(?:\.forEach|for\s*\(|\.get\()/.test(src);
const stillUsesCustomEvent = src.includes('new CustomEvent') &&
    !hasNotifyMechanism;
if (stillUsesCustomEvent) {
    console.log('FAIL: dispatcher still uses CustomEvent without listener notification');
    process.exit(1);
}
if (!hasNotifyMechanism) {
    console.log('FAIL: no mechanism to notify listeners when events dispatch');
    process.exit(1);
}

// 5. register_component must NOT be a no-op in shared_props
// Find the shared_props object and check register_component assignment
const sharedMatch = src.match(/(?:shared_props|sharedProps)[^=]*=\s*\{([\s\S]*?)\n\t\};/);
if (sharedMatch) {
    const sharedBody = sharedMatch[1];
    if (/register_component\s*:\s*\(\s*\)\s*=>\s*\{\s*\}/.test(sharedBody)) {
        console.log('FAIL: register_component is still a no-op () => {} in shared_props');
        process.exit(1);
    }
    if (/dispatcher\s*:\s*\(\s*\)\s*=>\s*\{\s*\}/.test(sharedBody)) {
        console.log('FAIL: dispatcher is still a no-op () => {} in shared_props');
        process.exit(1);
    }
}

// 6. set_data and get_data should be exposed (key part of the fix)
if (!src.includes('set_data') || !src.includes('get_data')) {
    console.log('FAIL: set_data/get_data not implemented (component data bridge missing)');
    process.exit(1);
}

console.log('PASS: event infrastructure implemented');
" 2>&1
if [ $? -eq 0 ]; then
    echo "PASS: Event listener infrastructure in render.ts"
    add_score 0.25
else
    echo "FAIL: Event listener infrastructure broken"
fi

##############################################################################
# BEHAVIORAL F2P-3 (0.15): Clipboard error handling in Textbox.svelte
# Buggy: navigator.clipboard.writeText() not wrapped in try/catch.
# If clipboard throws (permissions), copy_feedback() never runs.
# WHY structural: Svelte component requires Svelte compiler + DOM
##############################################################################
# [pr_diff] (0.15): handle_copy wraps clipboard in error handling
add_total 0.15
node -e "
const src = require('fs').readFileSync('js/textbox/shared/Textbox.svelte', 'utf8');

// Extract handle_copy function body
const match = src.match(/(?:async\s+)?function\s+handle_copy\b[\s\S]*?(?:\n\t\}|\n    \})/);
if (!match) {
    console.log('FAIL: handle_copy function not found');
    process.exit(1);
}
const fn = match[0];

// Must have error handling around clipboard API
// Accept: try/catch, .catch(), or Promise wrapper
const hasTryCatch = fn.includes('try') && fn.includes('catch');
const hasPromiseCatch = fn.includes('.catch(') || fn.includes('.catch (');
if (!hasTryCatch && !hasPromiseCatch) {
    console.log('FAIL: no error handling around clipboard API in handle_copy');
    process.exit(1);
}

// If using try/catch, clipboard.writeText must be inside the try block
if (hasTryCatch) {
    const tryIdx = fn.indexOf('try');
    const catchIdx = fn.indexOf('catch');
    const clipIdx = fn.indexOf('clipboard');
    if (clipIdx !== -1 && (clipIdx < tryIdx || clipIdx > catchIdx)) {
        console.log('FAIL: clipboard.writeText not inside try block');
        process.exit(1);
    }
}

// copy_feedback must be reachable regardless of error
// Accept: after catch block, in finally block, or via .finally()
if (!fn.includes('copy_feedback')) {
    console.log('FAIL: copy_feedback not called in handle_copy');
    process.exit(1);
}

console.log('PASS: clipboard error handling correct');
" 2>&1
if [ $? -eq 0 ]; then
    echo "PASS: Clipboard error handling in handle_copy"
    add_score 0.15
else
    echo "FAIL: Clipboard error handling broken"
fi

##############################################################################
# STRUCTURAL (0.10): Prop wiring and test attributes in Textbox.svelte
# [pr_diff] (0.05): on_custom_button_click prop wired to IconButtonWrapper
# [pr_diff] (0.05): data-testid on submit/stop buttons
##############################################################################
# [pr_diff] (0.05): on_custom_button_click prop wired
add_total 0.05
if grep -q 'on_custom_button_click' js/textbox/shared/Textbox.svelte; then
    echo "PASS: on_custom_button_click prop found"
    add_score 0.05
else
    echo "FAIL: on_custom_button_click prop not wired to IconButtonWrapper"
fi

# [pr_diff] (0.05): data-testid attributes on submit and stop buttons
add_total 0.05
TESTID_OK=true
if ! grep -qE 'data-testid.*submit' js/textbox/shared/Textbox.svelte; then
    echo "FAIL: submit button missing data-testid"
    TESTID_OK=false
fi
if ! grep -qE 'data-testid.*stop' js/textbox/shared/Textbox.svelte; then
    echo "FAIL: stop button missing data-testid"
    TESTID_OK=false
fi
if [ "$TESTID_OK" = true ]; then
    echo "PASS: data-testid attributes on submit/stop buttons"
    add_score 0.05
fi

##############################################################################
# PASS-TO-PASS (0.10): Existing exports preserved in render.ts
##############################################################################
# [pr_diff] (0.05): render and cleanup functions still exported
add_total 0.05
P2P_RENDER=true
if ! grep -qE 'export\s+(async\s+)?function\s+render' js/tootils/src/render.ts; then
    echo "FAIL: render function no longer exported"
    P2P_RENDER=false
fi
if ! grep -q 'export function cleanup' js/tootils/src/render.ts; then
    echo "FAIL: cleanup function no longer exported"
    P2P_RENDER=false
fi
if [ "$P2P_RENDER" = true ]; then
    echo "PASS: render and cleanup exports preserved"
    add_score 0.05
fi

# [pr_diff] (0.05): fireEvent export preserved
add_total 0.05
if grep -qE 'export\s+(const\s+)?fireEvent' js/tootils/src/render.ts; then
    echo "PASS: fireEvent export preserved"
    add_score 0.05
else
    echo "FAIL: fireEvent export missing"
fi

##############################################################################
# ANTI-STUB (0.10): Files have substantive content, not gutted
##############################################################################
# [pr_diff] (0.10): Modified files are non-trivially sized
add_total 0.10
STUB_OK=true

RENDER_LINES=$(wc -l < js/tootils/src/render.ts)
if [ "$RENDER_LINES" -lt 120 ]; then
    echo "FAIL: render.ts too short ($RENDER_LINES lines) — likely stubbed"
    STUB_OK=false
fi

UTILS_LINES=$(wc -l < js/utils/src/utils.svelte.ts)
if [ "$UTILS_LINES" -lt 150 ]; then
    echo "FAIL: utils.svelte.ts too short ($UTILS_LINES lines) — likely gutted"
    STUB_OK=false
fi

TEXTBOX_LINES=$(wc -l < js/textbox/shared/Textbox.svelte)
if [ "$TEXTBOX_LINES" -lt 250 ]; then
    echo "FAIL: Textbox.svelte too short ($TEXTBOX_LINES lines) — likely stubbed"
    STUB_OK=false
fi

if [ "$STUB_OK" = true ]; then
    echo "PASS: All modified files have substantive content"
    add_score 0.10
fi

##############################################################################
# FINAL SCORE
##############################################################################
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Score: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

BEHAVIORAL=$(python3 -c "print(min($SCORE, 0.70))")
REGRESSION=$(python3 -c "print(min(max($SCORE - 0.70, 0), 0.10))")
CONFIG="0.0"
STYLE="0.0"

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": $STYLE}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
