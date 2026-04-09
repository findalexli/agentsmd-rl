"""
Task: react-snap-minimization-error-description
Repo: facebook/react @ f84ce5a45c47b1081a09c17eea58c16ef145c113

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/react"
COMPILER = f"{REPO}/compiler"
MINIMIZE_TS = f"{REPO}/compiler/packages/snap/src/minimize.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        env = os.environ.copy()
        env["NODE_PATH"] = f"{REPO}/compiler/node_modules:{REPO}/node_modules"
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
            env=env,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_minimize_ts_exists():
    """minimize.ts must exist and be non-empty."""
    content = Path(MINIMIZE_TS).read_text()
    assert len(content) > 1000, "minimize.ts appears empty or truncated"
    assert "errorsMatch" in content, "minimize.ts missing expected function errorsMatch"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI) - TypeScript compilation
# ---------------------------------------------------------------------------

def test_snap_typescript_compiles():
    """Snap package TypeScript must compile (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "snap", "run", "tsc", "--build"],
        capture_output=True, text=True, timeout=120, cwd=COMPILER,
    )
    assert r.returncode == 0, f"Snap TypeScript compilation failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_snap_builds():
    """Snap package must build successfully (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "snap", "build"],
        capture_output=True, text=True, timeout=120, cwd=COMPILER,
    )
    assert r.returncode == 0, f"Snap build failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral: errorsMatch
# ---------------------------------------------------------------------------

def test_errorsMatch_rejects_different_descriptions():
    """errorsMatch must return false when error descriptions differ."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('compiler/packages/snap/src/minimize.ts', 'utf-8');

// Extract the errorsMatch function by finding its start and matching braces
const funcStart = src.indexOf('function errorsMatch(');
if (funcStart === -1) {
  console.error('errorsMatch function not found');
  process.exit(1);
}

let braceCount = 0, endIdx = funcStart, started = false;
for (let i = funcStart; i < src.length; i++) {
  if (src[i] === '{') { braceCount++; started = true; }
  else if (src[i] === '}') {
    braceCount--;
    if (started && braceCount === 0) { endIdx = i + 1; break; }
  }
}

// Strip TypeScript type annotations to get valid JS
let fnSrc = src.slice(funcStart, endIdx)
  .replace(/:\s*CompileErrors/g, '')
  .replace(/:\s*CompileResult/g, '')
  .replace(/:\s*boolean/g, '');

eval(fnSrc);

// Core test: same category+reason but DIFFERENT description must NOT match
const a = { kind: 'errors', errors: [{ category: 'InvalidReact', reason: 'hook-rule', description: 'Cannot call hook inside condition' }] };
const b = { kind: 'errors', errors: [{ category: 'InvalidReact', reason: 'hook-rule', description: 'Cannot call hook inside loop' }] };

if (errorsMatch(a, b) === true) {
  console.error('FAIL: errorsMatch returned true for different descriptions');
  process.exit(1);
}

// Sanity: identical errors should still match
const c = { kind: 'errors', errors: [{ category: 'X', reason: 'Y', description: 'Z' }] };
const d = { kind: 'errors', errors: [{ category: 'X', reason: 'Y', description: 'Z' }] };
if (!errorsMatch(c, d)) {
  console.error('FAIL: errorsMatch returned false for identical errors');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"errorsMatch behavioral test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - description field in type definitions
# ---------------------------------------------------------------------------

def test_description_in_error_types():
    """CompileErrors and error.details types must include description: string | null."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('compiler/packages/snap/src/minimize.ts', 'utf-8');
const parser = require('@babel/parser');

const ast = parser.parse(src, {
  sourceType: 'module',
  plugins: ['typescript'],
});

// Count TSPropertySignature nodes with key 'description'
let descriptionTypeCount = 0;

function walk(node) {
  if (!node || typeof node !== 'object') return;
  if (node.type === 'TSPropertySignature' &&
      node.key && node.key.type === 'Identifier' &&
      node.key.name === 'description') {
    descriptionTypeCount++;
  }
  for (const key of Object.keys(node)) {
    if (key === 'type' || key === 'start' || key === 'end' || key === 'loc') continue;
    const child = node[key];
    if (Array.isArray(child)) child.forEach(c => walk(c));
    else if (child && typeof child === 'object' && child.type) walk(child);
  }
}

walk(ast.program);

// The fix adds description to two type definitions:
// 1. CompileErrors type alias
// 2. error.details type in the catch block
if (descriptionTypeCount < 2) {
  console.error('FAIL: Expected at least 2 description type annotations, found ' + descriptionTypeCount);
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Type definition check failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - error mapping preserves description
# ---------------------------------------------------------------------------

def test_error_mapping_copies_description():
    """error.details.map must copy description field onto each mapped error object."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('compiler/packages/snap/src/minimize.ts', 'utf-8');
const parser = require('@babel/parser');

const ast = parser.parse(src, {
  sourceType: 'module',
  plugins: ['typescript'],
});

// Look for ObjectProperty: description: detail.description
let found = false;

function walk(node) {
  if (!node || typeof node !== 'object') return;
  if (node.type === 'ObjectProperty' &&
      node.key && node.key.name === 'description' &&
      node.value && node.value.type === 'MemberExpression' &&
      node.value.object && node.value.object.name === 'detail' &&
      node.value.property && node.value.property.name === 'description') {
    found = true;
  }
  for (const key of Object.keys(node)) {
    if (key === 'type' || key === 'start' || key === 'end' || key === 'loc') continue;
    const child = node[key];
    if (Array.isArray(child)) child.forEach(c => walk(c));
    else if (child && typeof child === 'object' && child.type) walk(child);
  }
}

walk(ast.program);

if (!found) {
  console.error('FAIL: description: detail.description not found in error mapping');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Error mapping check failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - new generator functions
# ---------------------------------------------------------------------------

def test_new_generators_defined():
    """Generator functions removeFunctionParameters, removeArrayPatternElements, removeObjectPatternProperties must be defined."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('compiler/packages/snap/src/minimize.ts', 'utf-8');
const parser = require('@babel/parser');

const ast = parser.parse(src, {
  sourceType: 'module',
  plugins: ['typescript'],
});

const generatorNames = [];

function walk(node) {
  if (!node || typeof node !== 'object') return;
  if (node.type === 'FunctionDeclaration' && node.generator && node.id) {
    generatorNames.push(node.id.name);
  }
  for (const key of Object.keys(node)) {
    if (key === 'type' || key === 'start' || key === 'end' || key === 'loc') continue;
    const child = node[key];
    if (Array.isArray(child)) child.forEach(c => walk(c));
    else if (child && typeof child === 'object' && child.type) walk(child);
  }
}

walk(ast.program);

const required = ['removeFunctionParameters', 'removeArrayPatternElements', 'removeObjectPatternProperties'];
const missing = required.filter(name => !generatorNames.includes(name));

if (missing.length > 0) {
  console.error('FAIL: Missing generator functions: ' + missing.join(', '));
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Generator check failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - strategies registered
# ---------------------------------------------------------------------------

def test_new_strategies_registered():
    """All three new strategies must be registered in simplificationStrategies array."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('compiler/packages/snap/src/minimize.ts', 'utf-8');
const parser = require('@babel/parser');

const ast = parser.parse(src, {
  sourceType: 'module',
  plugins: ['typescript'],
});

let strategyNames = [];

function walk(node) {
  if (!node || typeof node !== 'object') return;
  if (node.type === 'VariableDeclarator' &&
      node.id && node.id.name === 'simplificationStrategies' &&
      node.init && node.init.type === 'ArrayExpression') {
    for (const elem of node.init.elements) {
      if (elem && elem.type === 'ObjectExpression') {
        for (const prop of elem.properties) {
          if (prop.key && prop.key.name === 'name' && prop.value && prop.value.value) {
            strategyNames.push(prop.value.value);
          }
        }
      }
    }
  }
  for (const key of Object.keys(node)) {
    if (key === 'type' || key === 'start' || key === 'end' || key === 'loc') continue;
    const child = node[key];
    if (Array.isArray(child)) child.forEach(c => walk(c));
    else if (child && typeof child === 'object' && child.type) walk(child);
  }
}

walk(ast.program);

const required = ['removeFunctionParameters', 'removeArrayPatternElements', 'removeObjectPatternProperties'];
const missing = required.filter(name => !strategyNames.includes(name));

if (missing.length > 0) {
  console.error('FAIL: Missing strategies: ' + missing.join(', '));
  console.error('Found strategies: ' + strategyNames.join(', '));
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Strategy registration check failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout
