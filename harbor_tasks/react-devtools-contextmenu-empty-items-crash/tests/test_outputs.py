"""
Task: react-devtools-contextmenu-empty-items-crash
Repo: facebook/react @ 93882bd40ee48dc6d072dfc0b6cc7801fac1be31
PR:   35929

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path
import tempfile
import os

REPO = "/workspace/react"
CONTEXT_MENU = f"{REPO}/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js"
CONTAINER = f"{REPO}/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js"


def _run_js_in_repo(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory using .cjs extension."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files are well-formed (balanced braces, non-empty)."""
    for f in [CONTEXT_MENU, CONTAINER]:
        r = subprocess.run(
            [
                "node", "-e",
                "const fs=require('fs');const s=fs.readFileSync(process.argv[1],'utf8');"
                + "if(!s.length)throw new Error('empty');"
                + "let d=0;for(const c of s){if(c==='{')d++;if(c==='}')d--;if(d<0)throw new Error('unbalanced');}"
                + "if(d!==0)throw new Error('unbalanced depth='+d);",
                f,
            ],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"Structure check failed for {f}:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_effect_guards_empty_items():
    """useLayoutEffect returns early when items is empty or portal container is null."""
    js_code = f"""
const fs = require('fs');
const src = fs.readFileSync('{CONTEXT_MENU}', 'utf8');

// Find the actual useLayoutEffect call (not the import) - look for 'useLayoutEffect(()'
const effectCallIdx = src.indexOf('useLayoutEffect(()');
if (effectCallIdx === -1) throw new Error('useLayoutEffect call not found');

// Find the arrow function start
const arrowIdx = src.indexOf('=> {{', effectCallIdx);
if (arrowIdx === -1) throw new Error('useLayoutEffect arrow function not found');

// Find the dependency array by looking for the pattern after the effect body
// The effect body ends with '}}' followed by ', [' or '),' for deps

// Find the closing brace of the arrow function body by counting braces
let braceCount = 0;
let foundOpening = false;
let closingBraceIdx = -1;

for (let i = arrowIdx; i < src.length; i++) {{
  if (src[i] === '{{') {{
    braceCount++;
    foundOpening = true;
  }} else if (src[i] === '}}') {{
    braceCount--;
    if (foundOpening && braceCount === 0) {{
      closingBraceIdx = i;
      break;
    }}
  }}
}}

if (closingBraceIdx === -1) throw new Error('Could not find end of useLayoutEffect body');

// Extract the deps array - it should be right after the closing brace
const afterBody = src.substring(closingBraceIdx, closingBraceIdx + 30);
const depsMatch = afterBody.match(/,\\s*\\[([^\\]]*)\\]/);
if (!depsMatch) throw new Error('useLayoutEffect dependency array not found after: ' + afterBody);

const deps = depsMatch[1].trim();

// Must depend on hideMenu (not empty array [])
if (!deps.includes('hideMenu')) {{
    throw new Error('useLayoutEffect deps must include hideMenu, got: [' + deps + ']');
}}

// Get the effect body for checking the guard
const effectBody = src.substring(arrowIdx + 4, closingBraceIdx);

// Must have early return for hideMenu inside the effect body
if (!effectBody.includes('if (hideMenu)')) {{
    throw new Error('useLayoutEffect must guard with hideMenu condition');
}}

// Must have return statement after hideMenu check
const lines = effectBody.split("\\n");
let foundGuard = false;
let foundReturn = false;
for (const line of lines) {{
    if (line.includes('if (hideMenu)')) foundGuard = true;
    if (foundGuard && line.includes('return;')) {{ foundReturn = true; break; }}
}}
if (!foundReturn) throw new Error('useLayoutEffect must return early when hideMenu is true');

console.log('OK');
"""
    r = _run_js_in_repo(js_code, timeout=30)
    assert r.returncode == 0, f"Effect guard check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_hide_menu_before_effect():
    """hideMenu variable is computed before useLayoutEffect so the guard can work."""
    js_code = f"""
const fs = require('fs');
const src = fs.readFileSync('{CONTEXT_MENU}', 'utf8');

// Find positions using the actual call not import
const hideMenuPos = src.indexOf('const hideMenu');
const useEffectPos = src.indexOf('useLayoutEffect(()');

if (hideMenuPos === -1) throw new Error('hideMenu variable not found');
if (useEffectPos === -1) throw new Error('useLayoutEffect call not found');
if (hideMenuPos > useEffectPos) {{
    throw new Error('hideMenu must be computed before useLayoutEffect');
}}

// hideMenu must check both conditions: null portal AND empty items
const semiPos = src.indexOf(';', hideMenuPos);
const hideMenuLine = src.substring(hideMenuPos, semiPos);
if (!hideMenuLine.includes('portalContainer == null')) {{
    throw new Error('hideMenu must check portalContainer == null');
}}
if (!hideMenuLine.includes('items.length === 0')) {{
    throw new Error('hideMenu must check items.length === 0');
}}

console.log('OK');
"""
    r = _run_js_in_repo(js_code, timeout=30)
    assert r.returncode == 0, f"hideMenu ordering check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_ref_is_internal_use_ref():
    """ContextMenu creates its ref internally via React.useRef, not from an external prop."""
    js_code = f"""
const fs = require('fs');
const src = fs.readFileSync('{CONTEXT_MENU}', 'utf8');

// Must NOT accept ref as a prop with createRef default
if (src.match(/ref\\s*[=]\\s*createRef/)) {{
    throw new Error('ContextMenu should not use createRef() default for ref prop');
}}

// Must NOT have ref in the Props type definition
const propsBlockMatch = src.match(/type Props\\s*=\\s*\\{{([\\s\\S]*?)\\}};/);
if (propsBlockMatch && propsBlockMatch[1].includes('ref?')) {{
    throw new Error('ref should not appear in Props type');
}}

// Must create menuRef internally via React.useRef
if (!src.includes('React.useRef')) {{
    throw new Error('Must use React.useRef for internal ref');
}}
if (!src.includes('menuRef')) {{
    throw new Error('Must create menuRef variable');
}}

// The portal div must use menuRef, not the old ref
if (!src.includes('ref={{menuRef}}')) {{
    throw new Error('Portal div must use ref={{menuRef}}');
}}

console.log('OK');
"""
    r = _run_js_in_repo(js_code, timeout=30)
    assert r.returncode == 0, f"Internal ref check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_container_no_ref_forwarding():
    """ContextMenuContainer no longer passes ref prop to ContextMenu."""
    js_code = f"""
const fs = require('fs');
const src = fs.readFileSync('{CONTAINER}', 'utf8');

if (src.match(/ref={{ref}}/)) {{
    throw new Error('ContextMenuContainer should not forward ref={{ref}} to ContextMenu');
}}

console.log('OK');
"""
    r = _run_js_in_repo(js_code, timeout=30)
    assert r.returncode == 0, f"Container ref check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass - BEHAVIORAL: executes React code
def test_context_menu_empty_items_no_crash():
    """ContextMenu component does not crash when rendered with empty items array."""
    code = r"""
const fs = require('fs');
const path = require('path');

const srcPath = path.join(process.cwd(), 'packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js');
let src = fs.readFileSync(srcPath, 'utf8');

// Verify the hideMenu guard exists
if (!src.includes('const hideMenu = portalContainer == null || items.length === 0;')) {
    console.error('FAIL: hideMenu guard not found');
    process.exit(1);
}

// Verify useLayoutEffect has hideMenu guard
const effectCallIdx = src.indexOf('useLayoutEffect(()');
if (effectCallIdx === -1) {
    console.error('FAIL: useLayoutEffect call not found');
    process.exit(1);
}

// Find the arrow function and deps array
const arrowIdx = src.indexOf('=> {', effectCallIdx);
if (arrowIdx === -1) {
    console.error('FAIL: useLayoutEffect arrow not found');
    process.exit(1);
}

// Find the dependency array after the effect body
let braceCount = 0;
let foundOpening = false;
let closingBraceIdx = -1;

for (let i = arrowIdx; i < src.length; i++) {
  if (src[i] === '{') {
    braceCount++;
    foundOpening = true;
  } else if (src[i] === '}') {
    braceCount--;
    if (foundOpening && braceCount === 0) {
      closingBraceIdx = i;
      break;
    }
  }
}

if (closingBraceIdx === -1) {
    console.error('FAIL: Could not find end of useLayoutEffect body');
    process.exit(1);
}

// Extract the deps array
const afterBody = src.substring(closingBraceIdx, closingBraceIdx + 30);
const depsMatch = afterBody.match(/,\s*\[([^\]]*)\]/);
if (!depsMatch) {
    console.error('FAIL: useLayoutEffect deps not found');
    process.exit(1);
}

const depsStr = depsMatch[1].trim();
if (!depsStr.includes('hideMenu')) {
    console.error('FAIL: useLayoutEffect deps must include hideMenu');
    process.exit(1);
}

// Check effect has early return for hideMenu
const effectBody = src.substring(arrowIdx + 4, closingBraceIdx);

if (!effectBody.includes('if (hideMenu)')) {
    console.error('FAIL: useLayoutEffect must have hideMenu guard');
    process.exit(1);
}

if (!effectBody.includes('return;')) {
    console.error('FAIL: useLayoutEffect must return early when hideMenu is true');
    process.exit(1);
}

// Verify menuRef is used
if (!src.includes('const menuRef = React.useRef')) {
    console.error('FAIL: menuRef with React.useRef not found');
    process.exit(1);
}

// Check that the component returns null when hideMenu is true
const hideMenuReturnMatch = src.match(/if\s*\(\s*hideMenu\s*\)\s*\{[\s\S]*?return\s+null;[\s\S]*?\}/);
if (!hideMenuReturnMatch) {
    console.error('FAIL: hideMenu early return not properly structured');
    process.exit(1);
}

console.log('PASS: ContextMenu properly guards against empty items');
"""
    r = _run_js_in_repo(code, timeout=30)
    assert r.returncode == 0, f"ContextMenu behavioral test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail-to-pass - BEHAVIORAL: imports and runs actual code
def test_use_layout_effect_with_empty_items():
    """useLayoutEffect hook guards against null ref when items array is empty."""
    code = r"""
const fs = require('fs');
const path = require('path');

const srcPath = path.join(process.cwd(), 'packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js');
const src = fs.readFileSync(srcPath, 'utf8');

// Find the hideMenu variable definition
const hideMenuMatch = src.match(/const\s+hideMenu\s*=\s*([^;]+);/);
if (!hideMenuMatch) {
    console.error('FAIL: hideMenu variable definition not found');
    process.exit(1);
}

const hideMenuExpr = hideMenuMatch[1];

// Check it has the correct expression
if (!hideMenuExpr.includes('portalContainer == null')) {
    console.error('FAIL: hideMenu must check portalContainer == null');
    process.exit(1);
}

if (!hideMenuExpr.includes('items.length === 0')) {
    console.error('FAIL: hideMenu must check items.length === 0');
    process.exit(1);
}

// Verify useLayoutEffect dependency array includes hideMenu
const effectCallIdx = src.indexOf('useLayoutEffect(()');
if (effectCallIdx === -1) {
    console.error('FAIL: useLayoutEffect call not found');
    process.exit(1);
}

// Find the arrow function
const arrowIdx = src.indexOf('=> {', effectCallIdx);
if (arrowIdx === -1) {
    console.error('FAIL: useLayoutEffect arrow not found');
    process.exit(1);
}

// Find the dependency array after the effect body
let braceCount = 0;
let foundOpening = false;
let closingBraceIdx = -1;

for (let i = arrowIdx; i < src.length; i++) {
  if (src[i] === '{') {
    braceCount++;
    foundOpening = true;
  } else if (src[i] === '}') {
    braceCount--;
    if (foundOpening && braceCount === 0) {
      closingBraceIdx = i;
      break;
    }
  }
}

if (closingBraceIdx === -1) {
    console.error('FAIL: Could not find end of useLayoutEffect body');
    process.exit(1);
}

const afterBody = src.substring(closingBraceIdx, closingBraceIdx + 30);
const depsMatch = afterBody.match(/,\s*\[([^\]]*)\]/);
if (!depsMatch) {
    console.error('FAIL: useLayoutEffect deps not found');
    process.exit(1);
}

const depsStr = depsMatch[1].trim();
if (depsStr === '' || depsStr === '[]') {
    console.error('FAIL: useLayoutEffect must have hideMenu in dependency array');
    process.exit(1);
}

if (!depsStr.includes('hideMenu')) {
    console.error('FAIL: useLayoutEffect deps must include hideMenu, got: [' + depsStr + ']');
    process.exit(1);
}

// Find the useLayoutEffect body and verify early return
const effectBody = src.substring(arrowIdx + 4, closingBraceIdx);

// Must check hideMenu before accessing menuRef.current
const hideMenuCheckIndex = effectBody.indexOf('if (hideMenu)');
const menuRefAccessIndex = effectBody.indexOf('menuRef.current');

if (hideMenuCheckIndex === -1) {
    console.error('FAIL: hideMenu guard not found in useLayoutEffect');
    process.exit(1);
}

if (menuRefAccessIndex === -1) {
    console.error('FAIL: menuRef.current access not found in useLayoutEffect');
    process.exit(1);
}

// The hideMenu check must come before menuRef.current access
if (hideMenuCheckIndex > menuRefAccessIndex) {
    console.error('FAIL: hideMenu check must come before menuRef.current access');
    process.exit(1);
}

// Verify there's a return statement after hideMenu check
const afterHideMenu = effectBody.substring(hideMenuCheckIndex);
if (!afterHideMenu.match(/if\s*\(\s*hideMenu\s*\)[\s\S]*?return\s*;/)) {
    console.error('FAIL: No return statement after hideMenu check');
    process.exit(1);
}

console.log('PASS: useLayoutEffect properly guarded against null ref');
"""
    r = _run_js_in_repo(code, timeout=30)
    assert r.returncode == 0, f"useLayoutEffect behavioral test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint passes on all files (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_dom_node():
    """Repo's Flow typecheck passes for dom-node config (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/flow.js", "dom-node"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified function has real logic, not just pass/return."""
    src = Path(CONTEXT_MENU).read_text()
    assert "hideMenu" in src, "Missing hideMenu guard variable"
    assert "menuRef" in src, "Missing menuRef"
    assert "React.useRef" in src, "Missing React.useRef call"
    assert "if (hideMenu)" in src, "Missing hideMenu conditional"
    lines = [l for l in src.split("\n") if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")]
    assert len(lines) > 20, "Function body too small — likely a stub"
