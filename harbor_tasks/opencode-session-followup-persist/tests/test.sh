#!/usr/bin/env bash
set +e

REPO="/workspace/opencode"
FILE="$REPO/packages/app/src/pages/session.tsx"
REWARD=0

mkdir -p /logs/verifier

add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); }

echo "=== GATE: File exists and parses as TypeScript+JSX ==="
if [ ! -f "$FILE" ]; then
    echo "GATE FAIL: session.tsx not found"
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward":0,"behavioral":0,"regression":0,"config":0,"style_rubric":0}' > /logs/verifier/reward.json
    exit 0
fi

# Install babel parser for proper TypeScript+JSX AST analysis
# SolidJS component cannot execute without browser DOM — AST parsing justified
# Install in /tmp to avoid repo's pnpm catalog: protocol breaking npm install
mkdir -p /tmp/babel-env && cd /tmp/babel-env && npm install @babel/parser 2>/dev/null >/dev/null
export NODE_PATH="/tmp/babel-env/node_modules:${NODE_PATH:-}"
cd "$REPO"

# Gate: file must parse as valid TypeScript+JSX
# [static] (0.00): gate — malformed file aborts
PARSE_OK=$(node -e "
try {
  const fs = require('fs');
  const { parse } = require('@babel/parser');
  parse(fs.readFileSync('$FILE', 'utf8'), {
    sourceType: 'module',
    plugins: ['typescript', 'jsx'],
  });
  console.log('ok');
} catch(e) {
  console.log('fail: ' + e.message.split('\\n')[0]);
}
" 2>/dev/null)

if [ "$PARSE_OK" != "ok" ]; then
    echo "GATE FAIL: file does not parse as TypeScript ($PARSE_OK)"
    echo "0" > /logs/verifier/reward.txt
    echo '{"reward":0,"behavioral":0,"regression":0,"config":0,"style_rubric":0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASS: file parses as valid TypeScript+JSX"

echo ""
echo "=== Fail-to-pass: Core persistence fix (AST-verified) ==="

# [pr_diff] (0.35): Followup store must be wrapped with a persistence layer
# The core bug: followup state lived only in component memory — lost on unmount.
# ANY persistence wrapping is valid: persisted(), makePersisted(), custom wrapper.
# We check via AST that a function imported from a persist-related module wraps
# the createStore call associated with the followup variable.
# SolidJS component — cannot mount without browser DOM; AST check justified.
node -e "
const fs = require('fs');
const code = fs.readFileSync('$FILE', 'utf8');
const { parse } = require('@babel/parser');

const ast = parse(code, { sourceType: 'module', plugins: ['typescript', 'jsx'] });
const body = ast.program.body;

// Collect all names imported from any persist-related module
const persistNames = new Set();
for (const node of body) {
  if (node.type === 'ImportDeclaration' && /persist/i.test(node.source.value)) {
    for (const spec of (node.specifiers || [])) {
      persistNames.add(spec.local.name);
    }
  }
}

if (persistNames.size === 0) {
  console.log('No imports from persist module');
  process.exit(1);
}

// Check that a persist-imported function is called in context of followup store
const lines = code.split('\\n');
let found = false;

for (let i = 0; i < lines.length && !found; i++) {
  for (const name of persistNames) {
    // Function call: name( or name<...>(
    if (new RegExp(name + '\\\\s*[(<]').test(lines[i])) {
      const ctx = lines.slice(Math.max(0, i - 10), Math.min(lines.length, i + 10)).join('\\n');
      if (/createStore/.test(ctx) && /followup/i.test(ctx)) {
        found = true;
        break;
      }
    }
  }
}

// Alternative: followup variable declaration uses a persist function
if (!found) {
  for (let i = 0; i < lines.length && !found; i++) {
    if (/\bfollowup\b/i.test(lines[i]) && /=/.test(lines[i])) {
      const ctx = lines.slice(i, Math.min(lines.length, i + 15)).join('\\n');
      for (const name of persistNames) {
        if (ctx.includes(name + '(') || ctx.includes(name + '<')) {
          found = true;
          break;
        }
      }
    }
  }
}

process.exit(found ? 0 : 1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS: followup store wrapped with persistence function (0.35)"
    add 0.35
else
    echo "FAIL: followup store not wrapped with persistence (0.35)"
fi

# [pr_diff] (0.25): Persistence must be workspace-scoped (not global)
# Bug is specifically about losing state on PROJECT SWITCH. Global persistence
# would not fix the bug — data must be scoped per workspace/project directory.
# Accepts: Persist.workspace(), workspace-keyed storage, directory-based scoping.
node -e "
const fs = require('fs');
const code = fs.readFileSync('$FILE', 'utf8');
const lines = code.split('\\n');
let found = false;

// Strategy 1: Persist.workspace() or similar workspace-scoping API
for (let i = 0; i < lines.length && !found; i++) {
  if (/\.\s*workspace\s*\(/i.test(lines[i]) || /workspace\s*Persist/i.test(lines[i])) {
    const ctx = lines.slice(Math.max(0, i - 8), Math.min(lines.length, i + 8)).join('\\n');
    if (/followup|persist/i.test(ctx)) { found = true; }
  }
}

// Strategy 2: directory/project path used as key near followup persistence
if (!found) {
  for (let i = 0; i < lines.length && !found; i++) {
    if (/\b(?:workspace|directory|sdk\.dir)/i.test(lines[i])) {
      const ctx = lines.slice(Math.max(0, i - 6), Math.min(lines.length, i + 6)).join('\\n');
      if (/persist/i.test(ctx) && /followup/i.test(ctx)) { found = true; }
    }
  }
}

// Strategy 3: storage key that includes scope/project reference
if (!found) {
  for (let i = 0; i < lines.length && !found; i++) {
    if (/persist/i.test(lines[i]) && /followup/i.test(lines[i])) {
      const ctx = lines.slice(Math.max(0, i - 5), Math.min(lines.length, i + 5)).join('\\n');
      if (/workspace|directory|project|scope/i.test(ctx)) { found = true; }
    }
  }
}

process.exit(found ? 0 : 1);
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS: persistence is workspace-scoped (0.25)"
    add 0.25
else
    echo "FAIL: persistence is not workspace-scoped (0.25)"
fi

echo ""
echo "=== Pass-to-pass: Regression ==="

# [pr_diff] (0.05): Page function must remain the default export
if grep -qE 'export\s+default\s+function\s+Page' "$FILE"; then
    echo "PASS: Page function still default-exported (0.05)"
    add 0.05
else
    echo "FAIL: Page default export missing (0.05)"
fi

# [pr_diff] (0.05): Followup store must retain its core fields (items, failed, paused, edit)
python3 -c "
code = open('$FILE').read()
required = ['items', 'failed', 'paused', 'edit']
# Accept field: or 'field' or \"field\" in store object
found = sum(1 for r in required if r + ':' in code or r + ' :' in code or '\"' + r + '\"' in code or \"'\" + r + \"'\" in code)
exit(0 if found >= 3 else 1)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS: followup store retains core fields (0.05)"
    add 0.05
else
    echo "FAIL: followup store missing required fields (0.05)"
fi

echo ""
echo "=== Anti-stub: File substance ==="

# [static] (0.15): File must retain original component complexity — not gutted
# The original session.tsx is ~200+ lines with multiple SolidJS hooks, effects,
# and JSX rendering. A stub replacement must be caught.
python3 -c "
import re
code = open('$FILE').read()
lines = code.splitlines()

# Count non-empty, non-comment code lines
code_lines = [l for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('/*') and not l.strip().startswith('*')]
if len(code_lines) < 100:
    print(f'Only {len(code_lines)} code lines (need >=100)')
    exit(1)

# Must have multiple function/arrow-function definitions (original has many)
func_count = len(re.findall(r'(?:function\s+\w+|\b\w+\s*=\s*(?:async\s+)?\([^)]*\)\s*(?:=>|:))', code))
if func_count < 5:
    print(f'Only {func_count} functions (need >=5)')
    exit(1)

# Must use multiple SolidJS primitives (original uses createEffect, onCleanup, createStore, Show, For, etc.)
primitives = ['createEffect', 'createMemo', 'createStore', 'onCleanup', 'onMount', 'Show', 'For', 'createComputed']
found = sum(1 for p in primitives if p in code)
if found < 3:
    print(f'Only {found} SolidJS primitives (need >=3)')
    exit(1)

# Must contain JSX (it's a page component)
if not re.search(r'<\w+[\s/>]', code):
    print('No JSX found')
    exit(1)

exit(0)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS: file retains original complexity (0.15)"
    add 0.15
else
    echo "FAIL: file appears gutted or replaced with stub (0.15)"
fi

# [static] (0.05): No TODO/FIXME/stub markers near persistence code
python3 -c "
code = open('$FILE').read()
lines = code.splitlines()
for i, line in enumerate(lines):
    low = line.lower()
    if any(m in low for m in ['todo', 'fixme', 'stub', 'not implemented', 'placeholder']):
        context = '\n'.join(lines[max(0,i-10):i+10])
        if 'followup' in context.lower() or 'persist' in context.lower():
            exit(1)
exit(0)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS: no stubs near persistence code (0.05)"
    add 0.05
else
    echo "FAIL: TODO/FIXME/stub markers near persistence code (0.05)"
fi

echo ""
echo "=== Config-derived ==="

# [agent_config] (0.05): "Avoid using the any type" — AGENTS.md:16 @ 3fb60d0
# Check: no 'as any' or ': any' in the followup persistence block
python3 -c "
import re
code = open('$FILE').read()
# Find the followup store initialization block
match = re.search(r'(?:persisted|const\s+\[followup).*?(?=\n(?:const|let|function|export|//\s*=)|\Z)', code, re.DOTALL)
if match:
    block = match.group(0)
    if 'as any' in block or ': any ' in block or ': any;' in block or ': any,' in block:
        exit(1)
exit(0)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS: no 'any' type in followup persistence block (0.05)"
    add 0.05
else
    echo "FAIL: 'any' type used in followup persistence block (0.05)"
fi

# [agent_config] (0.05): "Always prefer createStore over multiple createSignal calls" — packages/app/AGENTS.md:8 @ 3fb60d0
python3 -c "
code = open('$FILE').read()
lines = code.splitlines()
signal_followup = 0
for i, line in enumerate(lines):
    if 'createSignal' in line:
        context = '\n'.join(lines[max(0,i-3):i+3])
        if 'followup' in context.lower() or 'items' in context or 'paused' in context:
            signal_followup += 1
exit(0 if signal_followup == 0 else 1)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS: createStore used for followup state (0.05)"
    add 0.05
else
    echo "FAIL: createSignal used for followup state instead of createStore (0.05)"
fi

echo ""
echo "=== Results ==="
FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $REWARD)):.4f}')")
echo "Reward: $FINAL"
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
json.dump({
    'reward': round(min(1.0, max(0.0, $REWARD)), 4),
    'behavioral': 0.60,
    'regression': 0.10,
    'config': 0.10,
    'style_rubric': 0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
