#!/usr/bin/env bash
set +e

REPO="/workspace/gradio"
INIT_FILE="$REPO/js/core/src/init.svelte.ts"
TABS_FILE="$REPO/js/tabs/shared/Tabs.svelte"

behavioral=0
p2p=0
structural=0
config=0

mkdir -p /logs/verifier

# ── GATE (0.00): Files must exist and not be empty ───────────────────
# [pr_diff] (0.00): Target files must exist and parse
echo "GATE: Checking files exist and are non-empty..."
if [ ! -s "$INIT_FILE" ] || [ ! -s "$TABS_FILE" ]; then
    echo "GATE FAILED: Required files missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE passed."

# ── CHECK 1 (0.30): F2P — update_state propagates tabitem to parent ──
# [pr_diff] (0.30): When update_state processes a tabitem component,
# it must find the parent Tabs and update its tab entries so the tab
# button reflects the new state. This code path is ABSENT in the base.
# Justified structural: Svelte/TS requires browser runtime to execute.
echo "CHECK 1: update_state propagates tabitem changes to parent Tabs..."
if node -e "
const fs = require('fs');
const src = fs.readFileSync('$INIT_FILE', 'utf8');

// Strip comments to prevent comment-injection gaming
let code = src.replace(/\\/\\/.*$/gm, '');
code = code.replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');

// The fix must add a code path that:
// 1. Detects the component is a tabitem (string literal check)
// 2. Finds or accesses the parent component
// 3. Updates the parent's tab list (initial_tabs, tab_entries, etc.)
//
// Accepts: any method name, inline or extracted, any variable names

// 1a: 'tabitem' string literal must appear in actual code
const hasTabitemLiteral = /['\"]tabitem['\"]/.test(code);
if (!hasTabitemLiteral) {
    console.error('No tabitem type check found in code (comment-free)');
    process.exit(1);
}

// 1b: Parent access — find_parent, parent.props, parent.type, traverseUp, getParent, etc.
const hasParentAccess = /find_parent|parent\\s*[\\.\\[]|parent_node|getParent|traverseUp|parent_component/.test(code);
if (!hasParentAccess) {
    console.error('No parent component access found in code');
    process.exit(1);
}

// 1c: Updates tab list on parent — initial_tabs, tab_entries, tabs property
const hasTabListUpdate = /initial_tabs|tab_entries|tabs\\s*[=\\[]/.test(code);
// Must be in init.svelte.ts specifically (not just any mention of 'tabs')
// Verify by checking co-location with tabitem check
const tabitemIdx = code.indexOf(\"'tabitem'\") !== -1
    ? code.indexOf(\"'tabitem'\")
    : code.indexOf('\"tabitem\"');
// Within 2000 chars of the tabitem check, parent access and tab update must exist
const regionStart = Math.max(0, tabitemIdx - 1000);
const regionEnd = Math.min(code.length, tabitemIdx + 2000);
const region = code.substring(regionStart, regionEnd);

const regionHasParent = /find_parent|parent\\s*[\\.\\[]|parent_node|getParent|traverseUp/.test(region);
const regionHasTabUpdate = /initial_tabs|tab_entries/.test(region);

if (!regionHasParent) {
    console.error('tabitem check and parent access are not co-located');
    process.exit(1);
}
if (!regionHasTabUpdate) {
    console.error('tabitem check and tab list update are not co-located');
    process.exit(1);
}

console.log('PASS');
" 2>&1; then
    behavioral=$(echo "$behavioral + 0.30" | bc)
    echo "  +0.30"
else
    echo "  FAIL"
fi

# ── CHECK 2 (0.25): F2P — Tabs syncs tab entries for non-mounted tabs ─
# [pr_diff] (0.25): The Tabs component must reactively sync changes to
# its tab entries when initial_tabs updates, but only for tabs that
# have not yet been mounted. This logic is ABSENT in the base.
echo "CHECK 2: Tabs.svelte syncs tab entries for non-mounted tabs..."
if node -e "
const fs = require('fs');
const src = fs.readFileSync('$TABS_FILE', 'utf8');

// Extract script block from Svelte
const scriptMatch = src.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/);
if (!scriptMatch) {
    console.error('No script block in Tabs.svelte');
    process.exit(1);
}
let script = scriptMatch[1];

// Strip comments
script = script.replace(/\\/\\/.*$/gm, '');
script = script.replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');

// The fix needs:
// 1. A reactive mechanism responding to initial_tabs changes
//    (\$:, \$effect, afterUpdate, watch, or function called reactively)
// 2. Iteration over tab entries
// 3. Conditional update skipping mounted/registered tabs
// 4. Assignment to internal tabs array

// Check for iteration pattern
const hasIteration = /for\\s*\\(|forEach\\s*\\(|\\.map\\s*\\(|\\.entries\\s*\\(/.test(script);
if (!hasIteration) {
    console.error('No iteration over tabs found in sync logic');
    process.exit(1);
}

// Check for mounted/registered tracking usage (reading from a Set, Map, array, or flag)
// Accepts: .has(), array[i], .get(), boolean flags, includes()
const hasMountedGuard = /\\.has\\s*\\(|\\.get\\s*\\(|\\.includes\\s*\\(|mounted|registered|tracked/.test(script);
if (!hasMountedGuard) {
    console.error('No mounted/registered state guard found');
    process.exit(1);
}

// Check for tabs array assignment in the context of a sync/update function
// Must have tabs[...] = ... pattern (assigning into the array)
const hasTabsAssignment = /tabs\\s*\\[.*\\]\\s*=/.test(script);
if (!hasTabsAssignment) {
    console.error('No tabs array element assignment found');
    process.exit(1);
}

// Verify co-location: iteration + mounted guard must be in the same function
// Find functions that contain both
const funcBlocks = [];
const funcRegex = /(?:function\\s+\\w+|(?:const|let|var)\\s+\\w+\\s*=\\s*(?:function|\\([^)]*\\)\\s*=>))[^{]*\\{/g;
let fmatch;
while ((fmatch = funcRegex.exec(script)) !== null) {
    const start = fmatch.index;
    // Simple brace matching to find function end
    let depth = 0;
    let end = start;
    for (let i = start; i < script.length; i++) {
        if (script[i] === '{') depth++;
        if (script[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
    }
    funcBlocks.push(script.substring(start, end + 1));
}

const hasSyncFunc = funcBlocks.some(block =>
    (/for\\s*\\(|forEach/.test(block)) &&
    (/\\.has\\s*\\(|mounted|registered/.test(block)) &&
    (/tabs\\s*\\[/.test(block))
);

if (!hasSyncFunc) {
    console.error('No function found combining iteration + mounted guard + tabs update');
    process.exit(1);
}

console.log('PASS');
" 2>&1; then
    behavioral=$(echo "$behavioral + 0.25" | bc)
    echo "  +0.25"
else
    echo "  FAIL"
fi

# ── CHECK 3 (0.15): F2P — register/unregister track mounted state ────
# [pr_diff] (0.15): register_tab must mark a tab as mounted and
# unregister_tab must unmark it, using any tracking structure.
echo "CHECK 3: register/unregister track mounted tab state..."
if node -e "
const fs = require('fs');
const src = fs.readFileSync('$TABS_FILE', 'utf8');

const scriptMatch = src.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/);
if (!scriptMatch) { process.exit(1); }
let script = scriptMatch[1];
script = script.replace(/\\/\\/.*$/gm, '');
script = script.replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');

// There must be a tracking data structure (Set, Map, Array, or object)
// that is written to in register_tab and removed from in unregister_tab
const hasTrackingStructure = /new\\s+Set|new\\s+Map|:\\s*Set<|:\\s*Map<|mounted|registered|tracked/.test(script);
if (!hasTrackingStructure) {
    console.error('No tracking data structure for mounted tabs');
    process.exit(1);
}

// Find register_tab region (up to next closing brace block end)
const regIdx = script.indexOf('register_tab');
if (regIdx === -1) { console.error('register_tab not found'); process.exit(1); }
const regRegion = script.substring(regIdx, regIdx + 1000);

// Find unregister_tab region
const unregIdx = script.indexOf('unregister_tab');
if (unregIdx === -1) { console.error('unregister_tab not found'); process.exit(1); }
const unregRegion = script.substring(unregIdx, unregIdx + 1000);

// register_tab must ADD to tracking:
// .add(), .set(), .push(), [idx]=true, or assignment
const regAdds = /\\.add\\s*\\(|\\.set\\s*\\(|\\.push\\s*\\(|=\\s*true/.test(regRegion);

// unregister_tab must REMOVE from tracking:
// .delete(), .splice(), .pop(), [idx]=false, or removal
const unregRemoves = /\\.delete\\s*\\(|\\.splice\\s*\\(|\\.pop\\s*\\(|=\\s*false/.test(unregRegion);

if (!regAdds) {
    console.error('register_tab does not add to tracking structure');
    process.exit(1);
}
if (!unregRemoves) {
    console.error('unregister_tab does not remove from tracking structure');
    process.exit(1);
}

console.log('PASS');
" 2>&1; then
    behavioral=$(echo "$behavioral + 0.15" | bc)
    echo "  +0.15"
else
    echo "  FAIL"
fi

echo "Behavioral total: $behavioral"

# ── CHECK 4 (0.10): P2P — Core APIs preserved ───────────────────────
# [pr_diff] (0.10): Essential methods/functions must still exist
echo "CHECK 4: Core APIs preserved..."
p2p_pass=true
for fn in update_state find_node_by_id; do
    if ! grep -q "$fn" "$INIT_FILE" 2>/dev/null; then
        echo "  Missing $fn in init.svelte.ts"
        p2p_pass=false
    fi
done
for fn in register_tab unregister_tab setContext selected_tab; do
    if ! grep -q "$fn" "$TABS_FILE" 2>/dev/null; then
        echo "  Missing $fn in Tabs.svelte"
        p2p_pass=false
    fi
done
if [ "$p2p_pass" = true ]; then
    p2p=$(echo "$p2p + 0.10" | bc)
    echo "  +0.10"
else
    echo "  FAIL"
fi

echo "Pass-to-pass total: $p2p"

# ── CHECK 5 (0.10): Anti-stub — Files not gutted ────────────────────
# [pr_diff] (0.10): Files must retain substantial content
echo "CHECK 5: Files not gutted..."
init_lines=$(wc -l < "$INIT_FILE")
tabs_lines=$(wc -l < "$TABS_FILE")
if [ "$init_lines" -ge 400 ] && [ "$tabs_lines" -ge 80 ]; then
    structural=$(echo "$structural + 0.10" | bc)
    echo "  +0.10 (init=$init_lines, tabs=$tabs_lines)"
else
    echo "  FAIL (init=$init_lines, tabs=$tabs_lines)"
fi

echo "Structural total: $structural"

# ── CHECK 6 (0.10): Config — Consistent indentation ─────────────────
# [agent_config] (0.10): "Be consistent with the style of the surrounding code." — AGENTS.md:45
echo "CHECK 6: Consistent indentation style..."
if node -e "
const fs = require('fs');
const initSrc = fs.readFileSync('$INIT_FILE', 'utf8');
const tabsSrc = fs.readFileSync('$TABS_FILE', 'utf8');
const lines = [...initSrc.split('\\n'), ...tabsSrc.split('\\n')];
let tabCount = 0, spaceCount = 0;
for (const line of lines) {
    if (/^\\t/.test(line)) tabCount++;
    else if (/^  [^ ]/.test(line)) spaceCount++;
}
const ratio = tabCount / (tabCount + spaceCount + 1);
if (ratio < 0.7) {
    console.error('Tab ratio too low: ' + ratio.toFixed(2));
    process.exit(1);
}
console.log('PASS (tab ratio: ' + ratio.toFixed(2) + ')');
" 2>&1; then
    config=$(echo "$config + 0.10" | bc)
    echo "  +0.10"
else
    echo "  FAIL"
fi

echo "Config total: $config"

# ── Final score ──────────────────────────────────────────────────────
total=$(echo "$behavioral + $p2p + $structural + $config" | bc)
echo ""
echo "=== FINAL SCORE ==="
echo "behavioral=$behavioral p2p=$p2p structural=$structural config=$config"
echo "total=$total"

echo "$total" > /logs/verifier/reward.txt

cat > /logs/verifier/reward.json <<EOF
{"reward": $total, "behavioral": $behavioral, "regression": $p2p, "config": $config, "style_rubric": 0}
EOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
