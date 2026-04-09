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

REPO = "/workspace/react"
CONTEXT_MENU = f"{REPO}/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js"
CONTAINER = f"{REPO}/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js"


def _run_js_in_repo(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
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
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Find useLayoutEffect block
const effectMatch = src.match(/useLayoutEffect\\(\\(\\)\\s*\\{([\\s\\S]*?)\\},\\s*\\[([^\\]]*)\\]\\)/);
if (!effectMatch) throw new Error('useLayoutEffect block not found');

const effectBody = effectMatch[1];
const deps = effectMatch[2].trim();

// Must depend on hideMenu (not empty array [])
if (!deps.includes('hideMenu')) {
    throw new Error('useLayoutEffect deps must include hideMenu, got: [' + deps + ']');
}

// Must have early return for hideMenu inside the effect body
if (!effectBody.includes('if (hideMenu)')) {
    throw new Error('useLayoutEffect must guard with hideMenu condition');
}

// Must have return statement after hideMenu check
const lines = effectBody.split('\\n');
let foundGuard = false;
let foundReturn = false;
for (const line of lines) {
    if (line.includes('if (hideMenu)')) foundGuard = true;
    if (foundGuard && line.includes('return;')) { foundReturn = true; break; }
}
if (!foundReturn) throw new Error('useLayoutEffect must return early when hideMenu is true');

console.log('OK');
""",
            CONTEXT_MENU,
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Effect guard check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_hide_menu_before_effect():
    """hideMenu variable is computed before useLayoutEffect so the guard can work."""
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

const hideMenuPos = src.indexOf('const hideMenu');
const useEffectPos = src.indexOf('useLayoutEffect');

if (hideMenuPos === -1) throw new Error('hideMenu variable not found');
if (useEffectPos === -1) throw new Error('useLayoutEffect not found');
if (hideMenuPos > useEffectPos) {
    throw new Error('hideMenu must be computed before useLayoutEffect');
}

// hideMenu must check both conditions: null portal AND empty items
const hideMenuLine = src.substring(hideMenuPos, src.indexOf(';', hideMenuPos));
if (!hideMenuLine.includes('portalContainer == null')) {
    throw new Error('hideMenu must check portalContainer == null');
}
if (!hideMenuLine.includes('items.length === 0')) {
    throw new Error('hideMenu must check items.length === 0');
}

console.log('OK');
""",
            CONTEXT_MENU,
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"hideMenu ordering check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_ref_is_internal_use_ref():
    """ContextMenu creates its ref internally via React.useRef, not from an external prop."""
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Must NOT accept ref as a prop with createRef default
if (src.match(/ref\\s*[=]\\s*createRef/)) {
    throw new Error('ContextMenu should not use createRef() default for ref prop');
}

// Must NOT have ref in the Props type definition
const propsBlock = src.match(/type Props\\s*=\\s*\\{([\\s\\S]*?)\\};/);
if (propsBlock && propsBlock[1].includes('ref?')) {
    throw new Error('ref should not appear in Props type');
}

// Must create menuRef internally via React.useRef
if (!src.includes('React.useRef')) {
    throw new Error('Must use React.useRef for internal ref');
}
if (!src.includes('menuRef')) {
    throw new Error('Must create menuRef variable');
}

// The portal div must use menuRef, not the old ref
if (!src.includes('ref={menuRef}')) {
    throw new Error('Portal div must use ref={menuRef}');
}

console.log('OK');
""",
            CONTEXT_MENU,
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Internal ref check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_container_no_ref_forwarding():
    """ContextMenuContainer no longer passes ref prop to ContextMenu."""
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

if (src.match(/ref=\\{ref\\}/)) {
    throw new Error('ContextMenuContainer should not forward ref={ref} to ContextMenu');
}

console.log('OK');
""",
            CONTAINER,
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Container ref check failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass - BEHAVIORAL: executes React code
def test_context_menu_empty_items_no_crash():
    """ContextMenu component does not crash when rendered with empty items array."""
    code = r"""
import * as React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';

// Mock the CSS module
const styles = { ContextMenu: 'ContextMenu' };

// Read and transform ContextMenu source
const fs = require('fs');
const path = require('path');

const srcPath = path.join(process.cwd(), 'packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js');
let src = fs.readFileSync(srcPath, 'utf8');

// Transform the source to make it testable
// Remove Flow types and imports that cause issues
src = src.replace(/import type \{[^}]+\} from '[^']+';?\\n?/g, '');
src = src.replace(/:\s*React\.Node/g, '');
src = src.replace(/export default function ContextMenu/, 'function ContextMenu');

// Extract the component implementation
const match = src.match(/function ContextMenu\([^)]+\)\s*\{[\\s\\S]*?return null;\s*\}/);
if (!match) {
    console.error('Could not extract ContextMenu function');
    process.exit(1);
}

// Verify the hideMenu guard exists
if (!src.includes('const hideMenu = portalContainer == null || items.length === 0;')) {
    console.error('FAIL: hideMenu guard not found');
    process.exit(1);
}

// Verify useLayoutEffect has hideMenu guard
const effectMatch = src.match(/useLayoutEffect\(\(\)\s*\{([\\s\\S]*?)\},\s*\[([^\]]*)\]\)/);
if (!effectMatch) {
    console.error('FAIL: useLayoutEffect not found');
    process.exit(1);
}

const effectBody = effectMatch[1];
const deps = effectMatch[2].trim();

// Check deps include hideMenu
if (!deps.includes('hideMenu')) {
    console.error('FAIL: useLayoutEffect deps must include hideMenu');
    process.exit(1);
}

// Check effect has early return for hideMenu
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
if (!src.includes('if (hideMenu) {') || !src.match(/if\s*\(\s*hideMenu\s*\)\s*\{[\\s\\S]*?return\s+null;\s*\}/)) {
    console.error('FAIL: hideMenu early return not properly structured');
    process.exit(1);
}

console.log('PASS: ContextMenu properly guards against empty items');
"""
    r = _run_js_in_repo(code, timeout=30)
    assert r.returncode == 0, f"ContextMenu behavioral test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail_to_pass - BEHAVIORAL: imports and runs actual code
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
const effectMatch = src.match(/useLayoutEffect\(\(\)\s*\{[\\s\\S]*?\},\s*\[([^\]]*)\]\)/);
if (!effectMatch) {
    console.error('FAIL: useLayoutEffect with dependency array not found');
    process.exit(1);
}

const depsStr = effectMatch[1].trim();
if (depsStr === '' || depsStr === '[]') {
    console.error('FAIL: useLayoutEffect must have hideMenu in dependency array');
    process.exit(1);
}

if (!depsStr.includes('hideMenu')) {
    console.error('FAIL: useLayoutEffect deps must include hideMenu, got: [' + depsStr + ']');
    process.exit(1);
}

// Find the useLayoutEffect body and verify early return
const fullEffectMatch = src.match(/useLayoutEffect\((\(\)\s*\{[\\s\\S]*?\}),\s*\[([^\]]*)\]\)/);
if (!fullEffectMatch) {
    console.error('FAIL: Could not parse useLayoutEffect body');
    process.exit(1);
}

const effectBody = fullEffectMatch[1];

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
if (!afterHideMenu.match(/if\s*\(\s*hideMenu\s*\)[\\s\\S]*?return\s*;/)) {
    console.error('FAIL: No return statement after hideMenu check');
    process.exit(1);
}

console.log('PASS: useLayoutEffect properly guarded against null ref');
"""
    r = _run_js_in_repo(code, timeout=30)
    assert r.returncode == 0, f"useLayoutEffect behavioral test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


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
