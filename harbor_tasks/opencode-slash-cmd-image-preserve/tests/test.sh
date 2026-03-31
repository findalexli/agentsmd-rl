#!/usr/bin/env bash
set +e

SCORE=0
DETAILS=""

add() {
  local weight=$1 pass=$2 tag=$3 desc=$4
  SCORE=$(python3 -c "print(round($SCORE + $weight * $pass, 4))")
  if [ "$pass" = "1" ]; then
    DETAILS="${DETAILS}\n  PASS ($weight) $tag: $desc"
  else
    DETAILS="${DETAILS}\n  FAIL ($weight) $tag: $desc"
  fi
}

TARGET="packages/app/src/components/prompt-input.tsx"
cd /workspace/opencode

# ── GATE: TypeScript syntax ────────────────────────────────────────
# [pr_diff] (gate): File must parse without syntax errors
if npx tsc --noEmit --pretty false "$TARGET" 2>/dev/null || node -e "
  const ts = require('typescript');
  const src = require('fs').readFileSync('$TARGET','utf8');
  const sf = ts.createSourceFile('$TARGET', src, ts.ScriptTarget.Latest, true);
  const diag = ts.createProgram(['$TARGET'], {noEmit:true, allowJs:true, jsx: ts.JsxEmit.Preserve}).getSyntacticDiagnostics(sf);
  if(diag.length > 0) process.exit(1);
" 2>/dev/null; then
  echo "GATE PASS: Syntax valid"
else
  echo "GATE FAIL: Syntax errors in $TARGET"
  echo "0.0" > /logs/verifier/reward.txt
  exit 0
fi

# ── Extract handleSlashSelect and transpile to JS ──────────────────
# This extracts the function body, strips TypeScript, and writes callable JS
export TARGET
EXTRACT_OK=0
node << 'EXTRACT_EOF'
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(process.env.TARGET, 'utf8');

// Find handleSlashSelect declaration
const fnIdx = src.indexOf('handleSlashSelect');
if (fnIdx === -1) { console.error('handleSlashSelect not found'); process.exit(1); }

// Find the arrow: handleSlashSelect = (...) => {
const eqIdx = src.indexOf('=', fnIdx);
if (eqIdx === -1 || eqIdx > fnIdx + 60) { console.error('= not found'); process.exit(1); }

const parenIdx = src.indexOf('(', eqIdx);
if (parenIdx === -1 || parenIdx > eqIdx + 30) { console.error('( not found'); process.exit(1); }

const closeParenIdx = src.indexOf(')', parenIdx);
if (closeParenIdx === -1) { console.error(') not found'); process.exit(1); }

// Strip type annotations from parameter
const rawParam = src.slice(parenIdx + 1, closeParenIdx);
const param = rawParam.replace(/\s*\??\s*:\s*[^,)]+/g, '').trim() || 'cmd';

// Find => and body {
const arrowIdx = src.indexOf('=>', closeParenIdx);
if (arrowIdx === -1 || arrowIdx > closeParenIdx + 20) { console.error('=> not found'); process.exit(1); }

const bodyStart = src.indexOf('{', arrowIdx);
if (bodyStart === -1) { console.error('{ not found'); process.exit(1); }

// Brace-match to find function end (skip strings and template literals)
let depth = 0, i = bodyStart;
while (i < src.length) {
  const ch = src[i];
  if (ch === "'" || ch === '"' || ch === '`') {
    const quote = ch;
    i++;
    while (i < src.length) {
      if (src[i] === '\\') { i++; }
      else if (src[i] === quote) break;
      i++;
    }
  } else if (ch === '{') {
    depth++;
  } else if (ch === '}') {
    depth--;
    if (depth === 0) break;
  }
  i++;
}

const fnBody = src.slice(bodyStart, i + 1);

// Wrap as named function and transpile TS → JS
const wrapped = 'function handleSlashSelect(' + param + ') ' + fnBody;
const result = ts.transpileModule(wrapped, {
  compilerOptions: {
    target: ts.ScriptTarget.ES2020,
    module: ts.ModuleTarget.CommonJS,
  }
});

fs.writeFileSync('/tmp/handleSlashSelect.js', result.outputText);
console.log('Extracted handleSlashSelect (' + fnBody.length + ' chars)');
EXTRACT_EOF
[ $? -eq 0 ] && EXTRACT_OK=1

if [ "$EXTRACT_OK" = "0" ]; then
  echo "WARNING: Could not extract handleSlashSelect — behavioral tests will fail"
fi

# ── Helper: Create base VM context with mocks ─────────────────────
# Written to /tmp/create_context.js and sourced by each behavioral test
cat > /tmp/create_context.js << 'CTXEOF'
function createTestContext(testImages, overrides) {
  let promptSetArgs = null;
  let closePopoverCalled = false;
  let focusEditorEndCalled = false;
  let triggerArgs = null;
  let setEditorTextArg = null;
  let clearEditorCalled = false;

  const allParts = [
    { type: 'text', content: '/test hello', start: 0, end: 11 },
    ...testImages,
  ];

  // Make parts work as both property and SolidJS accessor (callable)
  const partsAccessor = function() { return allParts; };
  partsAccessor.filter = allParts.filter.bind(allParts);
  partsAccessor.map = allParts.map.bind(allParts);
  partsAccessor.some = allParts.some.bind(allParts);
  partsAccessor.length = allParts.length;
  partsAccessor[Symbol.iterator] = allParts[Symbol.iterator].bind(allParts);

  const ctx = {
    imageAttachments: () => [...testImages],
    closePopover: () => { closePopoverCalled = true; },
    setEditorText: (t) => { setEditorTextArg = t; },
    focusEditorEnd: () => { focusEditorEndCalled = true; },
    editor: () => ({
      getText: () => '/test hello',
      getLength: () => 11,
    }),
    prompt: {
      set: function() { promptSetArgs = Array.from(arguments); },
      parts: partsAccessor,
    },
    promptProbe: { select: () => {} },
    DEFAULT_PROMPT: [{ type: 'text', content: '', start: 0, end: 0 }],
    command: { trigger: function() { triggerArgs = Array.from(arguments); } },
    clearEditor: () => { clearEditorCalled = true; },
    Array, Object, Error, TypeError, RangeError, String, Number,
    parseInt, parseFloat, isNaN, isFinite, undefined,
    console,
    ...overrides,
  };

  return {
    ctx,
    get promptSetArgs() { return promptSetArgs; },
    get closePopoverCalled() { return closePopoverCalled; },
    get focusEditorEndCalled() { return focusEditorEndCalled; },
    get triggerArgs() { return triggerArgs; },
    get setEditorTextArg() { return setEditorTextArg; },
    get clearEditorCalled() { return clearEditorCalled; },
  };
}
module.exports = { createTestContext };
CTXEOF

# ── F2P BEHAVIORAL (0.35): Custom slash command preserves images ───
# [pr_diff] (0.35): Selecting a custom command with images must keep them in prompt.set
CUSTOM_F2P=0
if [ "$EXTRACT_OK" = "1" ]; then
node << 'F2P_CUSTOM_EOF'
const vm = require('vm');
const fs = require('fs');
const { createTestContext } = require('/tmp/create_context.js');
const fnCode = fs.readFileSync('/tmp/handleSlashSelect.js', 'utf8');

const testImages = [
  { type: 'image_attachment', url: 'data:image/png;base64,abc', start: 0, end: 0 },
  { type: 'image_attachment', url: 'data:image/png;base64,def', start: 0, end: 0 },
];

const t = createTestContext(testImages, {});
vm.createContext(t.ctx);
vm.runInContext(fnCode, t.ctx);

try {
  vm.runInContext('handleSlashSelect({ type: "custom", trigger: "mycmd", id: "c1" })', t.ctx);
} catch(e) {
  console.error('Custom cmd threw:', e.message);
  process.exit(1);
}

if (!t.promptSetArgs) {
  console.error('prompt.set never called for custom command');
  process.exit(1);
}

const parts = t.promptSetArgs[0];
if (!Array.isArray(parts)) {
  console.error('prompt.set first arg not an array, got:', typeof parts);
  process.exit(1);
}

const imageParts = parts.filter(p => p && p.type === 'image_attachment');
if (imageParts.length < testImages.length) {
  console.error('Custom cmd lost images: expected ' + testImages.length + ', got ' + imageParts.length);
  process.exit(1);
}

const textParts = parts.filter(p => p && p.type === 'text');
if (textParts.length === 0) {
  console.error('Custom cmd lost text part');
  process.exit(1);
}

console.log('Custom slash cmd preserves ' + imageParts.length + ' images + ' + textParts.length + ' text part(s)');
F2P_CUSTOM_EOF
[ $? -eq 0 ] && CUSTOM_F2P=1
fi
add 0.35 $CUSTOM_F2P "[pr_diff]" "F2P: Custom slash cmd preserves image attachments"

# ── F2P BEHAVIORAL (0.25): Built-in slash command preserves images ──
# [pr_diff] (0.25): Selecting a built-in command with images must keep them in prompt.set
BUILTIN_F2P=0
if [ "$EXTRACT_OK" = "1" ]; then
node << 'F2P_BUILTIN_EOF'
const vm = require('vm');
const fs = require('fs');
const { createTestContext } = require('/tmp/create_context.js');
const fnCode = fs.readFileSync('/tmp/handleSlashSelect.js', 'utf8');

const testImages = [
  { type: 'image_attachment', url: 'data:image/png;base64,single', start: 0, end: 0 },
];

const t = createTestContext(testImages, {});
vm.createContext(t.ctx);
vm.runInContext(fnCode, t.ctx);

try {
  // Use a non-"custom" type so it goes to the built-in branch
  vm.runInContext('handleSlashSelect({ type: "builtin", id: "help" })', t.ctx);
} catch(e) {
  console.error('Builtin cmd threw:', e.message);
  process.exit(1);
}

if (!t.promptSetArgs) {
  console.error('prompt.set never called for builtin command');
  process.exit(1);
}

const parts = t.promptSetArgs[0];
if (!Array.isArray(parts)) {
  console.error('prompt.set first arg not an array');
  process.exit(1);
}

const imageParts = parts.filter(p => p && p.type === 'image_attachment');
if (imageParts.length < testImages.length) {
  console.error('Builtin cmd lost images: expected ' + testImages.length + ', got ' + imageParts.length);
  process.exit(1);
}

console.log('Builtin slash cmd preserves ' + imageParts.length + ' image(s)');
F2P_BUILTIN_EOF
[ $? -eq 0 ] && BUILTIN_F2P=1
fi
add 0.25 $BUILTIN_F2P "[pr_diff]" "F2P: Built-in slash cmd preserves image attachments"

# ── P2P BEHAVIORAL (0.05): Undefined cmd returns early ──────────────
# [pr_diff] (0.05): handleSlashSelect(undefined) must not crash or call prompt.set
P2P_GUARD=0
if [ "$EXTRACT_OK" = "1" ]; then
node << 'P2P_GUARD_EOF'
const vm = require('vm');
const fs = require('fs');
const { createTestContext } = require('/tmp/create_context.js');
const fnCode = fs.readFileSync('/tmp/handleSlashSelect.js', 'utf8');

const t = createTestContext([], {});
vm.createContext(t.ctx);
vm.runInContext(fnCode, t.ctx);

try {
  vm.runInContext('handleSlashSelect(undefined)', t.ctx);
} catch(e) {
  console.error('Threw on undefined cmd:', e.message);
  process.exit(1);
}

if (t.promptSetArgs !== null) {
  console.error('prompt.set should not be called for undefined cmd');
  process.exit(1);
}

if (t.closePopoverCalled) {
  console.error('closePopover should not be called for undefined cmd');
  process.exit(1);
}

console.log('Undefined cmd handled gracefully');
P2P_GUARD_EOF
[ $? -eq 0 ] && P2P_GUARD=1
fi
add 0.05 $P2P_GUARD "[pr_diff]" "P2P: Undefined cmd returns early without side effects"

# ── P2P BEHAVIORAL (0.05): closePopover called on selection ─────────
# [pr_diff] (0.05): Selecting any command must close the popover
P2P_CLOSE=0
if [ "$EXTRACT_OK" = "1" ]; then
node << 'P2P_CLOSE_EOF'
const vm = require('vm');
const fs = require('fs');
const { createTestContext } = require('/tmp/create_context.js');
const fnCode = fs.readFileSync('/tmp/handleSlashSelect.js', 'utf8');

const t = createTestContext([], {});
vm.createContext(t.ctx);
vm.runInContext(fnCode, t.ctx);

vm.runInContext('handleSlashSelect({ type: "custom", trigger: "test", id: "c1" })', t.ctx);

if (!t.closePopoverCalled) {
  console.error('closePopover not called');
  process.exit(1);
}

console.log('closePopover called on command selection');
P2P_CLOSE_EOF
[ $? -eq 0 ] && P2P_CLOSE=1
fi
add 0.05 $P2P_CLOSE "[pr_diff]" "P2P: closePopover called on slash select"

# ── P2P BEHAVIORAL (0.05): command.trigger called for built-in cmd ──
# [pr_diff] (0.05): Built-in command path must call command.trigger with cmd id
P2P_TRIGGER=0
if [ "$EXTRACT_OK" = "1" ]; then
node << 'P2P_TRIGGER_EOF'
const vm = require('vm');
const fs = require('fs');
const { createTestContext } = require('/tmp/create_context.js');
const fnCode = fs.readFileSync('/tmp/handleSlashSelect.js', 'utf8');

const t = createTestContext([], {});
vm.createContext(t.ctx);
vm.runInContext(fnCode, t.ctx);

vm.runInContext('handleSlashSelect({ type: "builtin", id: "run-task" })', t.ctx);

if (!t.triggerArgs) {
  console.error('command.trigger not called for builtin command');
  process.exit(1);
}

if (t.triggerArgs[0] !== 'run-task') {
  console.error('command.trigger called with wrong id: ' + t.triggerArgs[0]);
  process.exit(1);
}

console.log('command.trigger called with id: ' + t.triggerArgs[0]);
P2P_TRIGGER_EOF
[ $? -eq 0 ] && P2P_TRIGGER=1
fi
add 0.05 $P2P_TRIGGER "[pr_diff]" "P2P: command.trigger called for built-in cmd"

# ── STRUCTURAL (0.10): Anti-stub ────────────────────────────────────
# [pr_diff] (0.10): handleSlashSelect must not be stubbed out
ANTI_STUB=0
node -e "
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const sf = ts.createSourceFile('input.tsx', src, ts.ScriptTarget.Latest, true);

// Walk AST to find handleSlashSelect
function findFn(node) {
  if (ts.isVariableDeclaration(node) && node.name.getText(sf) === 'handleSlashSelect') {
    return node.initializer;
  }
  let result;
  ts.forEachChild(node, child => { if (!result) result = findFn(child); });
  return result;
}

const fn = findFn(sf);
if (!fn) { console.error('handleSlashSelect not found in AST'); process.exit(1); }

// Count statements recursively
function countStmts(node) {
  let count = 0;
  function walk(n) {
    if (ts.isExpressionStatement(n) || ts.isReturnStatement(n) ||
        ts.isIfStatement(n) || ts.isVariableStatement(n)) count++;
    ts.forEachChild(n, walk);
  }
  walk(node);
  return count;
}

const stmts = countStmts(fn);
if (stmts < 6) {
  console.error('Too few statements (' + stmts + '), likely stubbed');
  process.exit(1);
}

// Verify branching on cmd.type
const text = fn.getText(sf);
if (!text.includes('custom') && !text.includes('type')) {
  console.error('No cmd.type branching');
  process.exit(1);
}

// At least 2 prompt.set calls
const setCount = (text.match(/prompt\\.set/g) || []).length;
if (setCount < 2) {
  console.error('Fewer than 2 prompt.set calls (' + setCount + ')');
  process.exit(1);
}

console.log('Anti-stub OK: ' + stmts + ' stmts, ' + setCount + ' prompt.set calls');
" 2>&1 && ANTI_STUB=1
add 0.10 $ANTI_STUB "[pr_diff]" "Anti-stub: handleSlashSelect has adequate complexity"

# ── CONFIG (0.05): No 'any' type ────────────────────────────────────
# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:13
CONFIG_ANY=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const fnStart = src.indexOf('handleSlashSelect');
if (fnStart === -1) process.exit(1);
const window = src.slice(fnStart, fnStart + 1500);
const lines = window.split('\n');
for (const line of lines) {
  // Strip comments and string literals before checking
  const stripped = line.replace(/\\/\\/.*$/, '').replace(/(['\"\`]).*?\\1/g, '');
  if (stripped.match(/:\\s*any(?![a-zA-Z])/)) {
    console.error('Found any type: ' + line.trim());
    process.exit(1);
  }
}
process.exit(0);
" 2>&1 && CONFIG_ANY=1
add 0.05 $CONFIG_ANY "[agent_config]" "No 'any' type in handleSlashSelect — AGENTS.md:13"

# ── CONFIG (0.05): Const over let ───────────────────────────────────
# [agent_config] (0.05): "Prefer const over let" — AGENTS.md:68-79
CONFIG_CONST=0
node -e "
const fs = require('fs');
const src = fs.readFileSync('$TARGET', 'utf8');
const fnStart = src.indexOf('handleSlashSelect');
if (fnStart === -1) process.exit(1);
const window = src.slice(fnStart, fnStart + 1500);
const letMatches = window.match(/\\blet\\s+/g);
if (!letMatches || letMatches.length === 0) process.exit(0);
console.error('Found ' + letMatches.length + ' let usage(s) — prefer const');
process.exit(1);
" 2>&1 && CONFIG_CONST=1
add 0.05 $CONFIG_CONST "[agent_config]" "Prefers const over let — AGENTS.md:68-79"

# ── Output ─────────────────────────────────────────────────────────
echo ""
echo "=== Results ==="
printf "$DETAILS\n"
echo ""
echo "Score: $SCORE / 0.95"

# Write reward
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = $SCORE
beh = round($CUSTOM_F2P * 0.35 + $BUILTIN_F2P * 0.25 + $P2P_GUARD * 0.05 + $P2P_CLOSE * 0.05 + $P2P_TRIGGER * 0.05, 4)
struct = round($ANTI_STUB * 0.10, 4)
config = round(($CONFIG_ANY + $CONFIG_CONST) * 0.05, 4)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': beh,
    'structural': struct,
    'config': config,
}))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
