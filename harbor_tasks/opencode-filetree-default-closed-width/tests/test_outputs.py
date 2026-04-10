"""
Task: opencode-filetree-default-closed-width
Repo: anomalyco/opencode @ d36b38e4a6f5b778644669ba281fb5a35cf2f028
PR:   19426

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
LAYOUT = f"{REPO}/packages/app/src/context/layout.tsx"
SESSION = f"{REPO}/packages/app/src/pages/session.tsx"
BASE_COMMIT = "d36b38e4a6f5b778644669ba281fb5a35cf2f028"
CHANGED_FILES = [
    "packages/app/src/context/layout.tsx",
    "packages/app/src/pages/session.tsx",
]


def _node(script: str, timeout: int = 15) -> str:
    """Run a Node.js one-liner and return stdout."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )
    assert r.returncode == 0, f"node failed: {r.stderr}"
    return r.stdout.strip()


def _transpile_ts(ts_code: str) -> str:
    """Strip TypeScript types to make code runnable in Node.js."""
    # Remove type annotations from variable declarations (const x: number = 1 -> const x = 1)
    result = re.sub(r'(\w+)\s*:\s*\w+\s*=', r'\1 =', ts_code)
    # Remove type assertions (x as Type -> x)
    result = re.sub(r'\s+as\s+(?:"[^"]*"|\'[^\']*\'|\w+)', '', result)
    # Remove generic type parameters from function calls
    result = re.sub(r'<[^<>]*>', '', result)
    return result


def _run_in_node(ts_code: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Execute TypeScript code by transpiling and running in Node.js."""
    js_code = _transpile_ts(ts_code)
    return subprocess.run(
        ["node", "-e", js_code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _eval_store() -> dict:
    """Extract createStore initial state by evaluating the JS with constants injected."""
    return json.loads(_node(f"""
        const src = require('fs').readFileSync('{LAYOUT}', 'utf8');
        const constants = {{}};
        const cre = /(?:const|let|var)\\s+(\\w+)\\s*(?::\\s*\\w+)?\\s*=\\s*(\\d+)/g;
        let cm;
        while ((cm = cre.exec(src)) !== null) constants[cm[1]] = parseInt(cm[2]);

        const csIdx = src.indexOf('createStore(');
        if (csIdx === -1) {{ console.log(JSON.stringify({{error: 'no_createStore'}})); process.exit(0); }}
        let start = src.indexOf('{{', csIdx);
        let depth = 0, end = start;
        for (let i = start; i < src.length; i++) {{
            if (src[i] === '{{') depth++;
            if (src[i] === '}}') {{ depth--; if (depth === 0) {{ end = i; break; }} }}
        }}
        let block = src.substring(start, end + 1);
        block = block.replace(/\\bas\\s+(?:"[^"]*"|'[^']*')\\s*(?:\\|[^,}}]*)?/g, '');
        block = block.replace(/\\bas\\s+(?:Record|Map|Set|Array|typeof)\\s*<[^>]*>/g, '');
        block = block.replace(/\\bas\\s*\\([^)]*\\)/g, '');
        block = block.replace(/\\bas\\s*\\w+(?:\\[\\])?/g, '');
        const constDefs = Object.entries(constants).map(([k,v]) => 'const ' + k + '=' + v + ';').join('');
        const store = new Function(constDefs + 'return (' + block + ')')();
        console.log(JSON.stringify({{
            fileTree: store.fileTree,
            sidebar: store.sidebar,
            terminal: {{ height: store.terminal?.height, opened: store.terminal?.opened }},
            review: {{ panelOpened: store.review?.panelOpened }},
            session: {{ width: store.session?.width }},
        }}));
    """))


def _get_constants() -> dict:
    """Extract top-level numeric constants from layout.tsx."""
    return json.loads(_node(f"""
        const src = require('fs').readFileSync('{LAYOUT}', 'utf8');
        const constants = {{}};
        const re = /(?:const|let|var)\\s+(\\w+)\\s*(?::\\s*\\w+)?\\s*=\\s*(\\d+)/g;
        let m;
        while ((m = re.exec(src)) !== null) constants[m[1]] = parseInt(m[2]);
        console.log(JSON.stringify(constants));
    """))


def _added_lines() -> list[str]:
    """Get added lines from diff against base commit."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--"] + CHANGED_FILES,
        capture_output=True, text=True, cwd=REPO, timeout=10,
    )
    return [l for l in r.stdout.splitlines()
            if l.startswith("+") and not l.startswith("+++")]


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — file integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_layout_module_structure():
    """layout.tsx exists with core module structure (not a stub)."""
    src = Path(LAYOUT).read_text()
    assert len(src.splitlines()) >= 700, "layout.tsx is a stub (too few lines)"
    for keyword in ["createStore", "LayoutProvider", "createSimpleContext",
                    "persisted", "createMemo", "fileTree", "sidebar"]:
        assert keyword in src, f"Missing core keyword: {keyword}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filetree_defaults_closed():
    """fileTree must default to opened: false in createStore initial state."""
    # Run Node.js code that checks the actual initial state in the source
    script = """
    const fs = require('fs');
    const src = fs.readFileSync('LAYOUT_PATH', 'utf8');

    // Find the createStore call and extract fileTree.opened value
    const csIdx = src.indexOf('createStore(');
    if (csIdx === -1) {
        console.log(JSON.stringify({passed: false, error: 'createStore not found'}));
        process.exit(0);
    }

    // Find the fileTree object within createStore
    const afterCreate = src.substring(csIdx);
    const ftMatch = afterCreate.match(/fileTree:\s*\{[^}]*opened:\s*(true|false)/);
    if (!ftMatch) {
        console.log(JSON.stringify({passed: false, error: 'fileTree.opened not found'}));
        process.exit(0);
    }

    const openedValue = ftMatch[1] === 'true';
    console.log(JSON.stringify({passed: !openedValue, opened: openedValue}));
    """.replace("LAYOUT_PATH", LAYOUT)

    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"

    result = json.loads(r.stdout.strip())
    assert result.get("passed"), f"fileTree.opened = {result.get('opened')}, expected false"


# [pr_diff] fail_to_pass
def test_filetree_width_less_than_sidebar():
    """fileTree default width must be less than sidebar default width."""
    # Execute code that extracts and compares the widths
    script = """
    const fs = require('fs');
    const src = fs.readFileSync('LAYOUT_PATH', 'utf8');

    // Extract all top-level numeric constants
    const constants = {};
    const cre = /(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(\d+)/g;
    let cm;
    while ((cm = cre.exec(src)) !== null) constants[cm[1]] = parseInt(cm[2]);

    // Find createStore and extract widths
    const csIdx = src.indexOf('createStore(');
    const afterCreate = src.substring(csIdx);

    // Get sidebar width
    const sbMatch = afterCreate.match(/sidebar:\s*\{[^}]*width:\s*(\d+|\w+)/);
    const sbWidth = sbMatch ? (parseInt(sbMatch[1]) || constants[sbMatch[1]] || null) : null;

    // Get fileTree width
    const ftMatch = afterCreate.match(/fileTree:\s*\{[^}]*width:\s*(\d+|\w+)/);
    const ftWidth = ftMatch ? (parseInt(ftMatch[1]) || constants[ftMatch[1]] || null) : null;

    console.log(JSON.stringify({
        ftWidth: ftWidth,
        sbWidth: sbWidth,
        passed: ftWidth !== null && sbWidth !== null && ftWidth < sbWidth && ftWidth > 0
    }));
    """.replace("LAYOUT_PATH", LAYOUT)

    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert r.returncode == 0, "Node execution failed: " + r.stderr

    result = json.loads(r.stdout.strip())
    assert result.get("passed"), \
        "fileTree width (" + str(result.get('ftWidth')) + ") must be > 0 and < sidebar width (" + str(result.get('sbWidth')) + ")"


# [pr_diff] fail_to_pass
def test_helper_methods_use_filetree_width():
    """open/close/toggle/setTab setStore calls must use narrower width, not sidebar width."""
    result = json.loads(_node(f"""
        const src = require('fs').readFileSync('{LAYOUT}', 'utf8');
        const constants = {{}};
        const re = /(?:const|let|var)\\s+(\\w+)\\s*(?::\\s*\\w+)?\\s*=\\s*(\\d+)/g;
        let m;
        while ((m = re.exec(src)) !== null) constants[m[1]] = parseInt(m[2]);

        // Get sidebar width from createStore
        const csIdx = src.indexOf('createStore(');
        const sbMatch = src.substring(csIdx).match(/sidebar:\\s*\\{{[^}}]*width:\\s*(\\w+)/);
        let sbWidth = null;
        if (sbMatch) {{
            const n = parseInt(sbMatch[1]);
            sbWidth = !isNaN(n) ? n : (constants[sbMatch[1]] || null);
        }}

        // Find all setStore('fileTree', {{...width:X...}}) calls
        const setStoreRe = /setStore\\s*\\(\\s*['"]fileTree['"].*?\\{{[^}}]*width\\s*:\\s*(\\w+)/g;
        const widths = [];
        let sm;
        while ((sm = setStoreRe.exec(src)) !== null) {{
            const raw = sm[1];
            const n = parseInt(raw);
            if (!isNaN(n)) widths.push(n);
            else if (constants[raw] !== undefined) widths.push(constants[raw]);
            else widths.push('unresolved:' + raw);
        }}

        console.log(JSON.stringify({{ widths, sbWidth }}));
    """))
    widths = result["widths"]
    sb_width = result["sbWidth"]
    assert len(widths) > 0, "No setStore('fileTree', {width:...}) calls found"
    assert sb_width is not None, "Could not determine sidebar width"
    for w in widths:
        assert isinstance(w, (int, float)), f"Unresolved width: {w}"
        assert 0 < w < sb_width, \
            f"Helper width {w} must be >0 and < sidebar width {sb_width}"


# [pr_diff] fail_to_pass
def test_memo_fallback_uses_filetree_width():
    """createMemo fallback for fileTree width must use narrow default, not sidebar width."""
    constants = _get_constants()
    src = Path(LAYOUT).read_text()

    match = re.search(r'store\.fileTree\?\.width\s*\?\?\s*(\w+)', src)
    assert match, "No createMemo fallback for fileTree width found"

    raw = match.group(1)
    try:
        memo_width = int(raw)
    except ValueError:
        memo_width = constants.get(raw)
        assert memo_width is not None, f"Unresolved memo fallback constant: {raw}"

    # Determine sidebar width
    sb_width = constants.get("DEFAULT_SIDEBAR_WIDTH") or constants.get("DEFAULT_PANEL_WIDTH", 344)
    assert 0 < memo_width < sb_width, \
        f"Memo fallback width ({memo_width}) must be < sidebar width ({sb_width})"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sidebar_width_unchanged():
    """Sidebar default width must remain at 344."""
    store = _eval_store()
    assert "error" not in store, f"Store eval failed: {store}"
    assert store["sidebar"]["width"] == 344, \
        f"Sidebar width changed to {store['sidebar']['width']}, expected 344"


# [pr_diff] pass_to_pass
def test_store_structure_preserved():
    """Other store panels (terminal, review, session) must not be broken."""
    store = _eval_store()
    assert "error" not in store, f"Store eval failed: {store}"
    assert store["terminal"]["height"] == 280, \
        f"terminal.height={store['terminal']['height']}, expected 280"
    assert store["terminal"]["opened"] is False, \
        f"terminal.opened={store['terminal']['opened']}, expected false"
    assert store["review"]["panelOpened"] is True, \
        f"review.panelOpened={store['review']['panelOpened']}, expected true"
    assert store["session"]["width"] == 600, \
        f"session.width={store['session']['width']}, expected 600"


# [static] pass_to_pass
def test_session_keyboard_handling():
    """session.tsx must preserve onMount keyboard event handling."""
    src = Path(SESSION).read_text()
    assert "onMount" in src, "onMount missing from session.tsx"
    assert re.search(r'addEventListener\s*\(\s*[\'"]keydown[\'"]', src) or \
           "handleKeyDown" in src, \
        "Keyboard event handling missing from session.tsx"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ d36b38e4
def test_no_any_type_in_diff():
    """Changed lines must not introduce the `any` type (AGENTS.md:13)."""
    added = _added_lines()
    any_violations = [l for l in added if re.search(r':\s*any\b', l)]
    assert not any_violations, \
        f"Added `any` type annotations:\n" + "\n".join(any_violations)


# [agent_config] pass_to_pass — AGENTS.md:70,84 @ d36b38e4
def test_prefer_const_no_else():
    """Changed lines should prefer const over let and avoid else (AGENTS.md:70,84)."""
    added = _added_lines()
    let_lines = [l for l in added if "\tlet " in l or " let " in l]
    else_lines = [l for l in added if "\telse " in l or " else " in l or "\telse{" in l]
    violations = let_lines + else_lines
    assert not violations, \
        f"Style violations (let/else) in changed code:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — AGENTS.md:12 @ d36b38e4
def test_no_try_catch_in_diff():
    """Changed lines must not introduce try/catch blocks (AGENTS.md:12)."""
    added = _added_lines()
    try_catch = [l for l in added if re.search(r'\btry\s*\{', l) or re.search(r'\bcatch\s*\(', l)]
    assert not try_catch, \
        f"Added try/catch blocks:\n" + "\n".join(try_catch)


# [agent_config] pass_to_pass — AGENTS.md:17 @ d36b38e4
def test_no_for_loops_in_diff():
    """Changed lines should use functional array methods, not for loops (AGENTS.md:17)."""
    added = _added_lines()
    for_loops = [l for l in added if re.search(r'\bfor\s*\(', l)]
    assert not for_loops, \
        f"Added for loops (prefer flatMap/filter/map):\n" + "\n".join(for_loops)


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass gates — verify repo tests/lint pass on base and fix
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass - Prettier formatting
def test_repo_prettier_layout():
    """layout.tsx matches repo prettier config (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "--yes", "-p", "prettier", "prettier", "--check", "packages/app/src/context/layout.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"

# [repo_ci] pass_to_pass - Prettier formatting
def test_repo_prettier_session():
    """session.tsx matches repo prettier config (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "--yes", "-p", "prettier", "prettier", "--check", "packages/app/src/pages/session.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
