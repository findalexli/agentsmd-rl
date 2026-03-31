#!/usr/bin/env bash
set +e

SCORE=0
FILE="js/core/src/init.svelte.ts"

add() { SCORE=$(python3 -c "print(round($SCORE + $1, 4))"); }

###############################################################################
# GATE: File exists and is non-empty
###############################################################################
# [pr_diff] (gate): Target file must exist
if [ ! -s "$FILE" ]; then
  echo "GATE FAIL: $FILE missing or empty"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
  exit 0
fi

###############################################################################
# Extract _gather_initial_tabs and execute it against mock node trees.
# The function is plain JS once we strip TS type annotations, so we can
# run it in Node directly.
###############################################################################

# Helper: strip TypeScript type annotations so Node can evaluate the function.
# We extract the function source, then do minimal TS-to-JS conversion.
EXTRACT_AND_RUN=$(cat <<'NODEEOF'
const fs = require("fs");
const src = fs.readFileSync(process.env.FILE, "utf-8");

// ---- locate function ----
const fnRe = /function\s+_gather_initial_tabs\s*\(/;
const m = fnRe.exec(src);
if (!m) { console.log("EXTRACT_FAIL: function not found"); process.exit(99); }
const start = m.index;

// find matching closing brace
let depth = 0, bodyStart = -1, bodyEnd = -1;
for (let i = start; i < src.length; i++) {
  if (src[i] === "{") { if (depth === 0) bodyStart = i; depth++; }
  if (src[i] === "}") { depth--; if (depth === 0) { bodyEnd = i + 1; break; } }
}
if (bodyEnd === -1) { console.log("EXTRACT_FAIL: unbalanced braces"); process.exit(99); }

let fnSrc = src.substring(start, bodyEnd);

// ---- strip TS annotations ----
// Remove type parameters and type assertions that would break Node
fnSrc = fnSrc
  // Remove parameter type annotations  e.g. (node: Foo, tabs: Bar)
  .replace(/:\s*ProcessedComponentMeta/g, "")
  .replace(/:\s*Record<[^>]+>/g, "")
  .replace(/:\s*number\s*\|\s*null/g, "")
  .replace(/:\s*void/g, "")
  // Remove "as Type" casts
  .replace(/\s+as\s+\([^)]+\)\s*\|\s*undefined/g, "")
  .replace(/\s+as\s+\w+/g, "")
  // Remove remaining type annotations on local variables
  .replace(/:\s*\(\([^)]*\)\s*=>\s*\w+\)\s*\|\s*undefined/g, "");

// ---- make it available globally ----
// Wrap so we can call it
const wrapped = fnSrc + "\nmodule.exports = _gather_initial_tabs;";
// Write to temp file for require()
const tmp = "/tmp/_gather_initial_tabs.js";
fs.writeFileSync(tmp, wrapped);

// Export the source so tests can verify extraction worked
console.log("EXTRACT_OK");
NODEEOF
)

FILE="$FILE" node -e "$EXTRACT_AND_RUN" 2>/tmp/extract_err.txt
EXTRACT_STATUS=$?

if [ $EXTRACT_STATUS -eq 99 ]; then
  echo "GATE FAIL: Could not extract _gather_initial_tabs"
  echo "0.0" > /logs/verifier/reward.txt
  echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
  exit 0
fi

###############################################################################
# BEHAVIORAL FAIL-TO-PASS (0.65 total)
###############################################################################

# [pr_diff] (0.35): Tab labels are translated when i18n function is present
# This is THE core bug: _gather_initial_tabs must apply the i18n function
# to tab labels. We build a mock node tree and check the output.
echo "--- Check 1: i18n translation applied to tab labels ---"
node -e '
const fn = require("/tmp/_gather_initial_tabs.js");

// Build a mock "tabs" parent with one "tabitem" child that has i18n
const tabItem = {
  type: "tabitem",
  id: 42,
  props: {
    shared_props: {
      label: "lion",
      elem_id: "tab-lion",
      visible: true,
      interactive: true,
      scale: null
    },
    props: {
      id: "42",
      i18n: function(s) { return s === "lion" ? "Leon" : s; }
    }
  },
  children: []
};

const tabsNode = {
  type: "tabs",
  id: 100,
  props: { shared_props: {}, props: {} },
  children: [tabItem]
};

// Root node wrapping the tabs
const root = {
  type: "column",
  id: 0,
  props: { shared_props: {}, props: {} },
  children: [tabsNode]
};

const initial_tabs = {};
fn(root, initial_tabs, null, null);

// The tab should have been collected under parent id 100
const tabs = initial_tabs[100];
if (!tabs || tabs.length === 0) {
  console.log("FAIL: no tabs collected");
  process.exit(1);
}

const label = tabs[0].label;
if (label === "Leon") {
  console.log("PASS: label correctly translated to Leon");
  process.exit(0);
} else if (label === "lion") {
  console.log("FAIL: label is raw lion — i18n not applied (this is the bug)");
  process.exit(1);
} else {
  console.log("FAIL: unexpected label: " + label);
  process.exit(1);
}
' 2>/dev/null && add 0.35 || echo "  -> 0 points"

# [pr_diff] (0.15): Multiple tabs with different i18n translations
echo "--- Check 2: Multiple tabs all get translated ---"
node -e '
const fn = require("/tmp/_gather_initial_tabs.js");

const translations = { lion: "Leon", tiger: "Tigre", bear: "Oso" };
const i18nFn = (s) => translations[s] || s;

function makeTabItem(id, label) {
  return {
    type: "tabitem", id: id,
    props: {
      shared_props: { label: label, elem_id: "t-"+id, visible: true, interactive: true, scale: null },
      props: { id: String(id), i18n: i18nFn }
    },
    children: []
  };
}

const tabsNode = {
  type: "tabs", id: 200,
  props: { shared_props: {}, props: {} },
  children: [makeTabItem(1, "lion"), makeTabItem(2, "tiger"), makeTabItem(3, "bear")]
};

const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
const initial_tabs = {};
fn(root, initial_tabs, null, null);

const tabs = initial_tabs[200] || [];
if (tabs.length !== 3) { console.log("FAIL: expected 3 tabs, got " + tabs.length); process.exit(1); }

const labels = tabs.map(t => t.label);
if (labels[0] === "Leon" && labels[1] === "Tigre" && labels[2] === "Oso") {
  console.log("PASS: all tabs translated correctly: " + labels.join(", "));
  process.exit(0);
} else {
  console.log("FAIL: labels are " + labels.join(", ") + " — expected Leon, Tigre, Oso");
  process.exit(1);
}
' 2>/dev/null && add 0.15 || echo "  -> 0 points"

# [pr_diff] (0.15): i18n function that returns identity still works
# (tests that the i18n function is actually *called*, not just checked for existence)
echo "--- Check 3: i18n function is actually called (identity function) ---"
node -e '
const fn = require("/tmp/_gather_initial_tabs.js");

let callCount = 0;
const i18nSpy = (s) => { callCount++; return s.toUpperCase(); };

const tabItem = {
  type: "tabitem", id: 50,
  props: {
    shared_props: { label: "hello", elem_id: "t-50", visible: true, interactive: true, scale: null },
    props: { id: "50", i18n: i18nSpy }
  },
  children: []
};

const tabsNode = { type: "tabs", id: 300, props: { shared_props: {}, props: {} }, children: [tabItem] };
const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
const initial_tabs = {};
fn(root, initial_tabs, null, null);

const tabs = initial_tabs[300] || [];
if (tabs.length === 0) { console.log("FAIL: no tabs"); process.exit(1); }
if (callCount === 0) { console.log("FAIL: i18n function was never called"); process.exit(1); }
if (tabs[0].label === "HELLO") {
  console.log("PASS: i18n function was called and result used (label=HELLO, calls=" + callCount + ")");
  process.exit(0);
} else {
  console.log("FAIL: label is " + tabs[0].label + " — expected HELLO");
  process.exit(1);
}
' 2>/dev/null && add 0.15 || echo "  -> 0 points"

###############################################################################
# REGRESSION PASS-TO-PASS (0.20 total)
###############################################################################

# [pr_diff] (0.10): When i18n is NOT present, raw label is used (backward compat)
echo "--- Check 4: No i18n — raw label preserved ---"
node -e '
const fn = require("/tmp/_gather_initial_tabs.js");

const tabItem = {
  type: "tabitem", id: 60,
  props: {
    shared_props: { label: "Settings", elem_id: "t-60", visible: true, interactive: true, scale: null },
    props: { id: "60" }  // NO i18n property
  },
  children: []
};

const tabsNode = { type: "tabs", id: 400, props: { shared_props: {}, props: {} }, children: [tabItem] };
const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
const initial_tabs = {};
fn(root, initial_tabs, null, null);

const tabs = initial_tabs[400] || [];
if (tabs.length === 0) { console.log("FAIL: no tabs"); process.exit(1); }
if (tabs[0].label === "Settings") {
  console.log("PASS: raw label preserved when no i18n");
  process.exit(0);
} else {
  console.log("FAIL: label is " + tabs[0].label + " — expected Settings");
  process.exit(1);
}
' 2>/dev/null && add 0.10 || echo "  -> 0 points"

# [pr_diff] (0.05): All other tab properties still collected correctly
echo "--- Check 5: Other tab properties preserved ---"
node -e '
const fn = require("/tmp/_gather_initial_tabs.js");

const tabItem = {
  type: "tabitem", id: 70,
  props: {
    shared_props: { label: "Tab1", elem_id: "my-tab", visible: false, interactive: true, scale: 2 },
    props: { id: "70", i18n: (s) => "translated_" + s }
  },
  children: []
};

const tabsNode = { type: "tabs", id: 500, props: { shared_props: {}, props: {} }, children: [tabItem] };
const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
const initial_tabs = {};
fn(root, initial_tabs, null, null);

const tab = (initial_tabs[500] || [])[0];
if (!tab) { console.log("FAIL: no tab collected"); process.exit(1); }

const checks = [
  [tab.id, "70", "id"],
  [tab.elem_id, "my-tab", "elem_id"],
  [tab.visible, false, "visible"],
  [tab.interactive, true, "interactive"],
  [tab.component_id, 70, "component_id"],
];
for (const [actual, expected, name] of checks) {
  if (actual !== expected) {
    console.log("FAIL: " + name + " = " + actual + ", expected " + expected);
    process.exit(1);
  }
}
console.log("PASS: all tab properties correct");
process.exit(0);
' 2>/dev/null && add 0.05 || echo "  -> 0 points"

# [pr_diff] (0.05): Recursive children traversal still works (nested tabs)
echo "--- Check 6: Recursive traversal collects nested tabs ---"
node -e '
const fn = require("/tmp/_gather_initial_tabs.js");

// tabs > tabitem > column > tabs > tabitem (nested)
const innerTabItem = {
  type: "tabitem", id: 81,
  props: {
    shared_props: { label: "Inner", elem_id: "inner", visible: true, interactive: true, scale: null },
    props: { id: "81" }
  },
  children: []
};
const innerTabs = {
  type: "tabs", id: 80,
  props: { shared_props: {}, props: {} },
  children: [innerTabItem]
};
const column = {
  type: "column", id: 79,
  props: { shared_props: {}, props: {} },
  children: [innerTabs]
};
const outerTabItem = {
  type: "tabitem", id: 78,
  props: {
    shared_props: { label: "Outer", elem_id: "outer", visible: true, interactive: true, scale: null },
    props: { id: "78" }
  },
  children: [column]
};
const outerTabs = {
  type: "tabs", id: 77,
  props: { shared_props: {}, props: {} },
  children: [outerTabItem]
};
const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [outerTabs] };
const initial_tabs = {};
fn(root, initial_tabs, null, null);

const outerCollected = initial_tabs[77] || [];
const innerCollected = initial_tabs[80] || [];
if (outerCollected.length === 1 && innerCollected.length === 1 &&
    outerCollected[0].label === "Outer" && innerCollected[0].label === "Inner") {
  console.log("PASS: nested tabs collected correctly");
  process.exit(0);
} else {
  console.log("FAIL: outer=" + JSON.stringify(outerCollected) + " inner=" + JSON.stringify(innerCollected));
  process.exit(1);
}
' 2>/dev/null && add 0.05 || echo "  -> 0 points"

###############################################################################
# STRUCTURAL: Anti-stub (0.15)
###############################################################################

# [pr_diff] (0.10): Function body is substantive, not a stub
echo "--- Check 7: Anti-stub — function body substantive ---"
node -e '
const fs = require("fs");
const src = fs.readFileSync(process.env.FILE, "utf-8");

const fnRe = /function\s+_gather_initial_tabs\s*\(/;
const m = fnRe.exec(src);
if (!m) { process.exit(1); }

let depth = 0, bodyStart = -1, bodyEnd = -1;
for (let i = m.index; i < src.length; i++) {
  if (src[i] === "{") { if (depth === 0) bodyStart = i; depth++; }
  if (src[i] === "}") { depth--; if (depth === 0) { bodyEnd = i; break; } }
}
if (bodyEnd === -1) { process.exit(1); }

const body = src.substring(bodyStart + 1, bodyEnd);
// Count non-empty, non-comment lines
const meaningful = body.split("\n").filter(l => {
  const t = l.trim();
  return t.length > 0 && !t.startsWith("//") && !t.startsWith("/*") && !t.startsWith("*");
}).length;

if (meaningful < 8) {
  console.log("FAIL: only " + meaningful + " meaningful lines — likely stubbed");
  process.exit(1);
}
console.log("PASS: " + meaningful + " meaningful lines");
' 2>/dev/null && add 0.10 || echo "  -> 0 points"

# [pr_diff] (0.05): Function handles both tabitem and non-tabitem nodes
echo "--- Check 8: Non-tabitem nodes are skipped correctly ---"
node -e '
const fn = require("/tmp/_gather_initial_tabs.js");

// A tabs node with a non-tabitem child (e.g. a row) — should not crash or create bad entries
const rowChild = {
  type: "row", id: 90,
  props: { shared_props: { label: "NotATab" }, props: {} },
  children: []
};
const tabItem = {
  type: "tabitem", id: 91,
  props: {
    shared_props: { label: "RealTab", elem_id: "rt", visible: true, interactive: true, scale: null },
    props: { id: "91" }
  },
  children: []
};
const tabsNode = {
  type: "tabs", id: 600,
  props: { shared_props: {}, props: {} },
  children: [rowChild, tabItem]
};
const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
const initial_tabs = {};
fn(root, initial_tabs, null, null);

const tabs = initial_tabs[600] || [];
if (tabs.length === 1 && tabs[0].label === "RealTab") {
  console.log("PASS: only tabitem collected, non-tabitem skipped");
  process.exit(0);
} else {
  console.log("FAIL: expected 1 tab, got " + tabs.length);
  process.exit(1);
}
' 2>/dev/null && add 0.05 || echo "  -> 0 points"

###############################################################################
# Final score
###############################################################################
REWARD=$(python3 -c "print(round($SCORE, 2))")
BEHAVIORAL=$(python3 -c "print(round(min($SCORE, 0.65), 2))")
echo ""
echo "=== SCORE: $REWARD / 1.00 ==="
echo "$REWARD" > /logs/verifier/reward.txt
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": 0.20, \"structural\": 0.15}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
