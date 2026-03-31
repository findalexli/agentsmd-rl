#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
SCORE=0
TOTAL=0
DETAILS=""

add() {
    local weight=$1 name=$2 pass=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $name\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $name\n"
    fi
}

gate_fail() {
    echo "GATE FAIL: $1"
    echo "0.0" > /logs/verifier/reward.txt
    python3 -c "
import json, sys
json.dump({'reward':0.0,'behavioral':0.0,'regression':0.0,'config':0.0,'style_rubric':0.0,'gate_fail':'$1'}, sys.stdout)
" > /logs/verifier/reward.json 2>/dev/null || true
    exit 0
}

mkdir -p /logs/verifier

PROMPT_FILE="$REPO/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx"
SESSION_FILE="$REPO/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx"
HEADER_FILE="$REPO/packages/opencode/src/cli/cmd/tui/routes/session/header.tsx"
APP_FILE="$REPO/packages/opencode/src/cli/cmd/tui/app.tsx"

# ============================================================
# GATE: Key files must exist and be non-trivial
# ============================================================

# [pr_diff] (gate): prompt/index.tsx exists and is valid TypeScript
if [ ! -f "$PROMPT_FILE" ]; then
    gate_fail "prompt/index.tsx does not exist"
fi
PROMPT_SIZE=$(wc -c < "$PROMPT_FILE" 2>/dev/null || echo "0")
if [ "$PROMPT_SIZE" -lt 100 ]; then
    gate_fail "prompt/index.tsx is empty or trivial"
fi

# [pr_diff] (gate): session/index.tsx exists
if [ ! -f "$SESSION_FILE" ]; then
    gate_fail "session/index.tsx does not exist"
fi

echo "=== Gates passed ==="

# ============================================================
# BEHAVIORAL: Fail-to-pass tests (0.65)
# ============================================================

# [pr_diff] (0.15): header.tsx must be deleted — the core refactor removes this file
if [ ! -f "$HEADER_FILE" ]; then
    add 0.15 "header.tsx deleted" 1
else
    add 0.15 "header.tsx deleted" 0
fi

# [pr_diff] (0.20): prompt/index.tsx has a working usage computation memo
# SolidJS components can't be rendered without @opentui/solid, but we CAN
# parse the TypeScript AST to verify real code (not comments/strings) contains
# a createMemo that computes token usage. This is more robust than grep.
USAGE_MEMO_PASS=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$PROMPT_FILE', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

// Walk AST to find createMemo calls whose body references token-related fields
let found = false;
function visit(node) {
  // Look for createMemo(() => { ... }) calls
  if (ts.isCallExpression(node) && node.expression.getText(sf) === 'createMemo') {
    const body = node.getText(sf);
    // The memo must compute tokens from messages — check for key behavioral signals
    // We check the AST text (not source comments) for token arithmetic and cost reduction
    const hasTokenAccess = /tokens\s*\.\s*(input|output|reasoning|cache)/.test(body);
    const hasCostReduce = /\.reduce|\.map|sumBy|cost/.test(body) && /role.*===.*assistant|assistant.*role/.test(body);
    const hasProviderLookup = /provider|model/.test(body) && /limit|context/.test(body);
    if (hasTokenAccess && (hasCostReduce || hasProviderLookup)) {
      found = true;
    }
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(found ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.20 "prompt has usage computation memo (AST-verified)" "$USAGE_MEMO_PASS"

# [pr_diff] (0.10): prompt/index.tsx has currency formatting
# Verify via AST that there's an actual Intl.NumberFormat (or toLocaleString)
# with currency config — not just a comment
CURRENCY_PASS=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$PROMPT_FILE', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let found = false;
function visit(node) {
  // Match: new Intl.NumberFormat(..., { currency: ... })
  if (ts.isNewExpression(node)) {
    const text = node.getText(sf);
    if (/Intl\.NumberFormat/.test(text) && /currency/i.test(text)) {
      found = true;
    }
  }
  // Also accept: .toLocaleString(..., { style: 'currency' })
  if (ts.isCallExpression(node) && /toLocaleString/.test(node.expression.getText(sf))) {
    const text = node.getText(sf);
    if (/currency/i.test(text)) {
      found = true;
    }
  }
  // Also accept: .format() on a NumberFormat variable used for currency
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(found ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.10 "prompt formats cost as currency (AST-verified)" "$CURRENCY_PASS"

# [pr_diff] (0.10): session/index.tsx no longer imports or renders Header
# Verify there is no import from "./header" and no <Header JSX element in actual code
SESSION_CLEAN_PASS=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$SESSION_FILE', 'utf8');
const sf = ts.createSourceFile('session.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let hasHeaderImport = false;
let hasHeaderJsx = false;
function visit(node) {
  // Check imports from ./header
  if (ts.isImportDeclaration(node)) {
    const mod = node.moduleSpecifier.getText(sf).replace(/[\"']/g, '');
    if (mod === './header' || mod.endsWith('/header')) {
      hasHeaderImport = true;
    }
  }
  // Check JSX: <Header ... />
  if (ts.isJsxSelfClosingElement(node) || ts.isJsxOpeningElement(node)) {
    const tag = node.tagName.getText(sf);
    if (tag === 'Header') {
      hasHeaderJsx = true;
    }
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(!hasHeaderImport && !hasHeaderJsx ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.10 "session cleaned of Header import and JSX (AST-verified)" "$SESSION_CLEAN_PASS"

# [pr_diff] (0.05): variant.cycle command is not hidden in app.tsx
# Parse app.tsx AST and find the object literal containing value: "variant.cycle",
# then check it does NOT have hidden: true
VARIANT_PASS=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$APP_FILE', 'utf8');
const sf = ts.createSourceFile('app.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let result = '0'; // default fail (not found)
function visit(node) {
  if (ts.isObjectLiteralExpression(node)) {
    let isVariantCycle = false;
    let isHidden = false;
    for (const prop of node.properties) {
      if (ts.isPropertyAssignment(prop)) {
        const name = prop.name.getText(sf);
        const val = prop.initializer.getText(sf);
        if (name === 'value' && /variant\.cycle/.test(val)) isVariantCycle = true;
        if (name === 'hidden' && val === 'true') isHidden = true;
      }
    }
    if (isVariantCycle && !isHidden) result = '1';
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(result);
" 2>/dev/null || echo "0")
add 0.05 "variant.cycle not hidden (AST-verified)" "$VARIANT_PASS"

# [pr_diff] (0.05): session/index.tsx removed the header toggle state
# Check there's no kv.signal call with "header_visible" in the AST
TOGGLE_PASS=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$SESSION_FILE', 'utf8');
const sf = ts.createSourceFile('session.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let hasHeaderToggle = false;
function visit(node) {
  if (ts.isCallExpression(node)) {
    const text = node.getText(sf);
    if (/header_visible/.test(text) || /showHeader/.test(text)) {
      hasHeaderToggle = true;
    }
  }
  // Also check variable declarations for showHeader
  if (ts.isVariableDeclaration(node) && /showHeader|setShowHeader/.test(node.name.getText(sf))) {
    hasHeaderToggle = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(!hasHeaderToggle ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.05 "session header toggle state removed (AST-verified)" "$TOGGLE_PASS"

# ============================================================
# REGRESSION: Pass-to-pass (0.15)
# ============================================================

# [regression] (0.05): prompt still exports Prompt function and has input handling
P2P_PROMPT=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$PROMPT_FILE', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let hasExportedPrompt = false;
function visit(node) {
  if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'Prompt') {
    const mods = ts.getModifiers(node) || [];
    if (mods.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) {
      hasExportedPrompt = true;
    }
  }
  ts.forEachChild(node, visit);
}
visit(sf);
// Also check file has textarea handling (core feature)
const hasTextarea = /TextareaRenderable|textarea/i.test(src);
console.log(hasExportedPrompt && hasTextarea ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.05 "prompt exports Prompt function with input handling" "$P2P_PROMPT"

# [regression] (0.05): session still exports Session function with scrollbox
P2P_SESSION=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$SESSION_FILE', 'utf8');
const sf = ts.createSourceFile('session.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let hasExportedSession = false;
function visit(node) {
  if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'Session') {
    const mods = ts.getModifiers(node) || [];
    if (mods.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) {
      hasExportedSession = true;
    }
  }
  ts.forEachChild(node, visit);
}
visit(sf);
const hasScrollbox = /scrollbox/i.test(src);
console.log(hasExportedSession && hasScrollbox ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.05 "session exports Session function with scrollbox" "$P2P_SESSION"

# [regression] (0.05): prompt file is not stubbed (substantial content)
PROMPT_LINES=$(wc -l < "$PROMPT_FILE" 2>/dev/null || echo "0")
if [ "$PROMPT_LINES" -gt 500 ]; then
    add 0.05 "prompt not stubbed ($PROMPT_LINES lines)" 1
else
    add 0.05 "prompt not stubbed ($PROMPT_LINES lines)" 0
fi

# ============================================================
# CONFIG-DERIVED (0.10)
# ============================================================

# [agent_config] (0.05): "Avoid using the `any` type" — AGENTS.md:19
# Count `any` type annotations in actual code via AST, not grep
ANY_PASS=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$PROMPT_FILE', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let anyCount = 0;
function visit(node) {
  // Count 'any' keyword type nodes
  if (node.kind === ts.SyntaxKind.AnyKeyword) {
    anyCount++;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(anyCount < 5 ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.05 "minimal use of any type (AST-verified)" "$ANY_PASS"

# [agent_config] (0.05): "Prefer const over let" — AGENTS.md:59
# Count let vs const declarations in AST
CONST_PASS=$(node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$PROMPT_FILE', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let letCount = 0, constCount = 0;
function visit(node) {
  if (ts.isVariableDeclarationList(node)) {
    if (node.flags & ts.NodeFlags.Let) letCount++;
    if (node.flags & ts.NodeFlags.Const) constCount++;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(constCount > letCount ? '1' : '0');
" 2>/dev/null || echo "0")
add 0.05 "const preferred over let (AST-verified)" "$CONST_PASS"

# ============================================================
# STYLE RUBRIC (0.10) — reserved for LLM judge
# ============================================================

# ============================================================
# RESULTS
# ============================================================

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Score: $SCORE / $TOTAL"

REWARD=$(python3 -c "print(round($SCORE, 4))")
echo "$REWARD" > /logs/verifier/reward.txt

# Compute category scores for reward.json
python3 -c "
import json, sys
reward = $REWARD
behavioral = min(reward, 0.65)
regression = round(min(max(reward - 0.65, 0), 0.15), 4)
config = round(min(max(reward - 0.80, 0), 0.10), 4)
json.dump({
    'reward': reward,
    'behavioral': round(behavioral, 4),
    'regression': regression,
    'config': config,
    'style_rubric': 0.0
}, sys.stdout)
" > /logs/verifier/reward.json 2>/dev/null || true

echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
