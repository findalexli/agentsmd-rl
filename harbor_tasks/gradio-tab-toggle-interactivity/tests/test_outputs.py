"""
Task: gradio-tab-toggle-interactivity
Repo: gradio-app/gradio @ 75f8dceb679b505c8887f0a3c3b9fee98a931db9
PR:   13048

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All checks use structural inspection because the target files are
Svelte components + TypeScript that require the full Gradio build toolchain
(pnpm, Svelte compiler, etc.) to execute. We cannot import or call them.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
INIT_FILE = Path(REPO) / "js/core/src/init.svelte.ts"
TABS_FILE = Path(REPO) / "js/tabs/shared/Tabs.svelte"

_NODE_ENV = {**os.environ, "NODE_PATH": "/tmp/ts/node_modules"}


def _read_init() -> str:
    return INIT_FILE.read_text()


def _read_tabs_instance_script() -> str:
    """Extract the instance <script lang="ts"> block from Tabs.svelte."""
    src = TABS_FILE.read_text()
    blocks = list(re.finditer(
        r'<script(?P<attrs>[^>]*)>(.*?)</script>', src, re.DOTALL
    ))
    for m in blocks:
        if "context" not in m.group("attrs"):
            return m.group(2)
    if blocks:
        return blocks[-1].group(2)
    raise AssertionError("No instance <script> block found in Tabs.svelte")


def _get_class_body(src: str) -> str:
    """Extract the AppTree class body (before standalone function definitions)."""
    class_start = src.find("export class AppTree")
    assert class_start >= 0, "AppTree class not found"
    # Standalone functions are declared at column 0 after the class
    func_matches = list(re.finditer(r'^function\s+\w+', src[class_start:], re.MULTILINE))
    if func_matches:
        return src[class_start:class_start + func_matches[0].start()]
    return src[class_start:]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist_and_parse():
    """Both target files must exist, be non-empty, and parse as TypeScript."""
    assert INIT_FILE.exists() and INIT_FILE.stat().st_size > 0, \
        f"{INIT_FILE} missing or empty"
    assert TABS_FILE.exists() and TABS_FILE.stat().st_size > 0, \
        f"{TABS_FILE} missing or empty"

    # TypeScript parse check for init.svelte.ts
    r = subprocess.run(
        ["node", "-e",
         "var ts = require('typescript'); var fs = require('fs');"
         f"var src = fs.readFileSync('{INIT_FILE}', 'utf8');"
         "var sf = ts.createSourceFile('init.svelte.ts', src, ts.ScriptTarget.Latest, true);"
         "if (sf.statements.length === 0) process.exit(1);"],
        capture_output=True, timeout=30, env=_NODE_ENV,
    )
    assert r.returncode == 0, f"TS parse failed for init.svelte.ts: {r.stderr.decode()[:500]}"

    # TypeScript parse check for Tabs.svelte script blocks
    r2 = subprocess.run(
        ["node", "-e",
         "var ts = require('typescript'); var fs = require('fs');"
         f"var src = fs.readFileSync('{TABS_FILE}', 'utf8');"
         "var m = src.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/g);"
         "if (!m || m.length === 0) process.exit(1);"
         "for (var block of m) {"
         "  var inner = block.replace(/<script[^>]*>/, '').replace(/<\\/script>/, '');"
         "  var sf = ts.createSourceFile('t.ts', inner, ts.ScriptTarget.Latest, true);"
         "  if (sf.statements.length === 0) process.exit(1);"
         "}"],
        capture_output=True, timeout=30, env=_NODE_ENV,
    )
    assert r2.returncode == 0, f"TS parse failed for Tabs.svelte: {r2.stderr.decode()[:500]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# Structural because: Svelte/TS requires full Gradio build toolchain to execute
def test_update_state_detects_tabitem():
    """update_state must detect tabitem components and trigger parent tab update.

    The core bug: update_state had no special handling for tabitem nodes,
    so prop changes on non-mounted tabs were silently lost. The fix adds
    a check for node type === 'tabitem' inside update_state.
    """
    src = _read_init()

    # Extract update_state method body using node's TS parser for robustness
    r = subprocess.run(
        ["node", "-e",
         "var ts = require('typescript'); var fs = require('fs');"
         f"var src = fs.readFileSync('{INIT_FILE}', 'utf8');"
         "var sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);"
         "function visit(n) {"
         "  if (n.name && n.name.text === 'update_state') {"
         "    var body = src.substring(n.pos, n.end);"
         "    console.log(body);"
         "  }"
         "  ts.forEachChild(n, visit);"
         "}"
         "visit(sf);"],
        capture_output=True, timeout=30, env=_NODE_ENV,
    )
    us_body = r.stdout.decode()
    assert us_body, "Could not extract update_state method body via TS parser"

    # Must check for "tabitem" string literal
    assert '"tabitem"' in us_body or "'tabitem'" in us_body, \
        "update_state does not check for tabitem type"

    # The tabitem branch must call a function (not just a comment or empty if)
    tabitem_pos = us_body.find('"tabitem"') if '"tabitem"' in us_body else us_body.find("'tabitem'")
    call_region = us_body[tabitem_pos:tabitem_pos + 500]
    assert re.search(r'\w+\s*\(', call_region), \
        "tabitem detection has no function call (empty or stub branch)"


# [pr_diff] fail_to_pass
# Structural because: Svelte/TS requires full Gradio build toolchain to execute
def test_parent_tabs_update_logic():
    """The AppTree class must have logic that updates a PARENT component's
    initial_tabs when a tabitem's props change.

    The base has gather_initial_tabs/apply_initial_tabs as standalone functions,
    but no class method that writes to a parent's initial_tabs. The fix adds
    a method that finds the parent Tabs and updates its initial_tabs array.
    """
    src = _read_init()
    class_body = _get_class_body(src)

    # The fix must write to initial_tabs on a non-this object (parent's props).
    # Base only has: this.initial_tabs = {} (resetting own property).
    # Patched adds: parent.props.props.initial_tabs = [...initial_tabs]
    writes = re.findall(r'(\w+(?:\.\w+)*)\.initial_tabs\s*=', class_body)
    non_this_writes = [w for w in writes if w != "this"]
    assert len(non_this_writes) > 0, \
        "AppTree class has no code writing to a parent's initial_tabs"

    # The class must also call find_parent (or equivalent tree traversal)
    # to locate the parent Tabs component. Base never calls find_parent from class.
    has_parent_lookup = bool(re.search(
        r'find_parent\s*\(|getParent\s*\(|traverse.*parent',
        class_body, re.IGNORECASE,
    ))
    assert has_parent_lookup, \
        "AppTree class does not look up parent node (find_parent or equivalent)"


# [pr_diff] fail_to_pass
# Structural because: Svelte reactive syntax ($:) can't be tested outside Svelte compiler
def test_tabs_reactive_sync():
    """Tabs.svelte must have a reactive statement triggered BY initial_tabs
    that syncs changes to the internal tabs array for unmounted tab entries.

    The base has no reactive statement that fires when initial_tabs changes.
    The fix adds one (e.g. $: _sync_tabs(initial_tabs)) so tab buttons
    reflect updated non-mounted tab props.
    """
    script = _read_tabs_instance_script()

    # Must have a reactive statement ($: or $effect) triggered by initial_tabs
    has_reactive = bool(re.search(
        r'\$:\s+\w+\s*\(\s*initial_tabs\b|'          # $: fn(initial_tabs)
        r'\$:\s*\{[^}]*?\binitial_tabs\b|'            # $: { ... initial_tabs ... }
        r'\$:\s+\w+\s*=.*?\binitial_tabs\b|'          # $: x = f(initial_tabs)
        r'\$effect\s*\(\s*\(\)\s*=>[^)]*initial_tabs',  # $effect(() => { initial_tabs })
        script, re.DOTALL,
    ))
    assert has_reactive, \
        "Tabs.svelte has no reactive statement ($: / $effect) triggered by initial_tabs"

    # The sync logic must iterate and write to tabs[]
    has_iteration = bool(re.search(r'for\s*\(|\.forEach\s*\(|\.map\s*\(', script))
    has_tabs_assign = bool(re.search(r'\btabs\s*\[', script))
    assert has_iteration and has_tabs_assign, \
        f"Tabs.svelte missing iteration ({has_iteration}) or tabs[] assignment ({has_tabs_assign})"


# [pr_diff] fail_to_pass
# Structural because: Svelte component context (setContext/register_tab) can't be tested outside runtime
def test_mounted_tab_tracking():
    """register_tab and unregister_tab must track which tabs are mounted.

    Without this tracking, the reactive sync would overwrite tab entries
    that mounted TabItem components already manage via register_tab.
    """
    script = _read_tabs_instance_script()

    # Strip comments for cleaner matching
    clean = re.sub(r'//.*$', '', script, flags=re.MULTILINE)
    clean = re.sub(r'/\*.*?\*/', '', clean, flags=re.DOTALL)

    # Must declare a tracking data structure (Set, Map, Array, or object)
    tracking_match = re.search(
        r'(?:let|const|var)\s+(\w+)\s*'
        r'(?::\s*(?:Set|Map|Array|Record)<[^>]*>)?\s*'
        r'=\s*(?:new\s+(?:Set|Map)\s*\(|[\[\{])',
        clean,
    )
    assert tracking_match, \
        "No tracking data structure (Set/Map/Array/object) declared in Tabs.svelte"
    tracking_var = tracking_match.group(1)

    # register_tab must add to it
    reg_idx = clean.find('register_tab')
    unreg_idx = clean.find('unregister_tab')
    assert reg_idx >= 0, "register_tab not found"
    assert unreg_idx >= 0, "unregister_tab not found"

    reg_body = clean[reg_idx:unreg_idx] if unreg_idx > reg_idx else clean[reg_idx:reg_idx + 500]
    add_pat = re.compile(
        rf'{re.escape(tracking_var)}\s*\.\s*(?:add|set|push)\s*\(|'
        rf'{re.escape(tracking_var)}\s*\['
    )
    assert add_pat.search(reg_body), \
        f"register_tab does not add to {tracking_var}"

    # unregister_tab must remove from it
    unreg_body = clean[unreg_idx:unreg_idx + 500]
    remove_pat = re.compile(
        rf'{re.escape(tracking_var)}\s*\.\s*(?:delete|splice|pop|remove)\s*\(|'
        rf'delete\s+{re.escape(tracking_var)}\s*\['
    )
    assert remove_pat.search(unreg_body), \
        f"unregister_tab does not remove from {tracking_var}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_core_apis_preserved():
    """Essential methods/functions must still exist in both files."""
    init_src = _read_init()
    tabs_src = TABS_FILE.read_text()

    for fn in ["update_state", "find_node_by_id", "find_parent"]:
        assert fn in init_src, f"Missing {fn} in init.svelte.ts"

    for fn in ["register_tab", "unregister_tab", "selected_tab"]:
        assert fn in tabs_src, f"Missing {fn} in Tabs.svelte"


# [static] pass_to_pass
def test_files_not_gutted():
    """Both files must retain substantial content (reject gutting/rewriting)."""
    init_lines = len(_read_init().splitlines())
    tabs_lines = len(TABS_FILE.read_text().splitlines())
    # Base: init ~914 lines, tabs ~420 lines. Fix adds ~50 and ~20.
    assert init_lines >= 800, f"init.svelte.ts too short ({init_lines} lines, need >=800)"
    assert tabs_lines >= 350, f"Tabs.svelte too short ({tabs_lines} lines, need >=350)"


# [static] fail_to_pass
def test_init_file_grew():
    """init.svelte.ts must be longer than the base (~914 lines) since the fix adds ~50 lines of code."""
    init_lines = len(_read_init().splitlines())
    assert init_lines >= 950, \
        f"init.svelte.ts has {init_lines} lines (base had ~914, fix should add ~50)"
