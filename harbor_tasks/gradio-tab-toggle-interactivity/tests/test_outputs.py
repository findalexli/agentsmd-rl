"""
Task: gradio-tab-toggle-interactivity
Repo: gradio-app/gradio @ 75f8dceb679b505c8887f0a3c3b9fee98a931db9
PR:   13048

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All checks use structural/regex inspection because the target files are
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

# Merge NODE_PATH into existing env instead of replacing it
_NODE_ENV = {**os.environ, "NODE_PATH": "/tmp/ts/node_modules"}


def _get_tabs_instance_script() -> str:
    """Extract the instance <script lang="ts"> block from Tabs.svelte,
    skipping the module <script context="module"> block."""
    src = TABS_FILE.read_text()
    # Find all script blocks; the instance script is the one without context="module"
    blocks = list(re.finditer(
        r'<script(?P<attrs>[^>]*)>(.*?)</script>', src, re.DOTALL
    ))
    for m in blocks:
        attrs = m.group("attrs")
        if "context" not in attrs:
            return m.group(2)
    # Fallback: return the last script block (instance script is always last)
    if blocks:
        return blocks[-1].group(2)
    raise AssertionError("No <script> block found in Tabs.svelte")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist_and_parse():
    """Both target files must exist, be non-empty, and parse as TypeScript."""
    assert INIT_FILE.exists() and INIT_FILE.stat().st_size > 0, \
        f"{INIT_FILE} missing or empty"
    assert TABS_FILE.exists() and TABS_FILE.stat().st_size > 0, \
        f"{TABS_FILE} missing or empty"

    # TypeScript parse check for init.svelte.ts (pure TS file)
    r = subprocess.run(
        ["node", "-e", f"""
var ts = require('typescript');
var fs = require('fs');
var src = fs.readFileSync('{INIT_FILE}', 'utf8');
var sf = ts.createSourceFile('init.svelte.ts', src, ts.ScriptTarget.Latest, true);
if (sf.statements.length === 0) process.exit(1);
"""],
        capture_output=True, timeout=30, env=_NODE_ENV,
    )
    assert r.returncode == 0, f"TypeScript parse failed for init.svelte.ts: {r.stderr.decode()}"

    # TypeScript parse check for Tabs.svelte (extract <script> block first)
    r2 = subprocess.run(
        ["node", "-e", f"""
var ts = require('typescript');
var fs = require('fs');
var src = fs.readFileSync('{TABS_FILE}', 'utf8');
var m = src.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/g);
if (!m || m.length === 0) process.exit(1);
// Parse each script block
for (var block of m) {{
    var inner = block.replace(/<script[^>]*>/, '').replace(/<\\/script>/, '');
    var sf = ts.createSourceFile('Tabs.svelte.ts', inner, ts.ScriptTarget.Latest, true);
    if (sf.statements.length === 0) process.exit(1);
}}
"""],
        capture_output=True, timeout=30, env=_NODE_ENV,
    )
    assert r2.returncode == 0, f"TypeScript parse failed for Tabs.svelte: {r2.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# Structural because: Svelte/TS component methods can't be called from Python
def test_update_state_detects_tabitem():
    """update_state must detect tabitem components and invoke propagation logic.

    The core bug: update_state had no special handling for tabitem nodes,
    so prop changes on non-mounted tabs were silently lost. The fix adds
    a check for node type === 'tabitem' inside update_state that triggers
    parent tab state propagation.
    """
    src = INIT_FILE.read_text()

    # Verify update_state method exists
    assert "update_state" in src, "update_state method not found in init.svelte.ts"

    # Find update_state method body
    us_match = re.search(
        r'update_state\s*\([^)]*\)\s*\{(.+?)(?=\n\t(?:\w|#\w|/\*\*))',
        src, re.DOTALL,
    )
    assert us_match, "Could not extract update_state method body"
    us_body = us_match.group(1)

    # Must contain a check for "tabitem" string literal
    assert '"tabitem"' in us_body or "'tabitem'" in us_body, \
        "update_state does not check for tabitem type"

    # The tabitem branch must call a function (not just be a comment or empty if)
    tabitem_pos = us_body.find('"tabitem"') if '"tabitem"' in us_body else us_body.find("'tabitem'")
    after_tabitem = us_body[tabitem_pos:]
    call_region = after_tabitem[:500]
    assert re.search(r'\w+\s*\(', call_region), \
        "tabitem detection has no function call (empty or stub branch)"


# [pr_diff] fail_to_pass
# Structural because: Svelte/TS component methods can't be called from Python
def test_parent_tabs_update_logic():
    """A method/function must exist that finds the parent Tabs component and
    updates its initial_tabs array when a tabitem's props change.

    This is the helper that update_state delegates to. It must:
    1. Access a parent node (find_parent, parent.*, traverseUp, etc.)
    2. Read/write initial_tabs or equivalent tab list
    3. Trigger reactivity (spread, _set_data, or reassignment)
    """
    src = INIT_FILE.read_text()

    # Use a sliding window to find co-located patterns (within ~3000 chars)
    window = 3000
    found = False
    for i in range(0, max(1, len(src) - window), 100):
        chunk = src[i:i + window]
        has_parent = bool(re.search(
            r'find_parent|getParent|traverseUp|parent\s*[\.\[]|\.parent\b', chunk))
        has_tab_mod = bool(re.search(r'initial_tabs', chunk)) and \
            bool(re.search(r'=\s*[\[{]|=\s*\.\.\.|\.\s*set\s*\(|_set_data', chunk))
        if has_parent and has_tab_mod:
            found = True
            break

    assert found, \
        "No function found that both accesses parent node and modifies initial_tabs"


# [pr_diff] fail_to_pass
# Structural because: Svelte reactive syntax ($:) can't be tested outside Svelte compiler
def test_tabs_reactive_sync():
    """Tabs.svelte must have a reactive statement that is triggered BY initial_tabs
    and syncs its changes to the internal tabs array for unmounted tab entries.

    The base Tabs.svelte already has $: declarations (e.g. $: has_tabs = ...) and
    already reads initial_tabs in register_tab — but has NO reactive statement that
    triggers *on* initial_tabs changes. The fix adds a $: block that fires specifically
    when initial_tabs changes, so tab buttons reflect updated non-mounted tab props.
    """
    script = _get_tabs_instance_script()

    # The fix must add a reactive statement ($: or $effect) that is directly
    # triggered by initial_tabs — i.e. initial_tabs appears on the RHS of $:
    # or inside $effect(() => { ... }) where initial_tabs is referenced.
    has_reactive_on_initial_tabs = bool(re.search(
        r'\$:\s+\w+\s*\(\s*initial_tabs\b|'      # $: fn(initial_tabs)
        r'\$:\s*\{[^}]*\binitial_tabs\b|'          # $: { ... initial_tabs ... }
        r'\$:\s+\w+\s*=.*\binitial_tabs\b|'        # $: x = f(initial_tabs)
        r'\$effect\s*\([^)]*\)\s*\{[^}]*initial_tabs',  # $effect(() => { initial_tabs })
        script, re.DOTALL,
    ))
    assert has_reactive_on_initial_tabs, \
        "Tabs.svelte has no reactive statement ($: / $effect) triggered by initial_tabs"

    # The reactive sync must also iterate or assign into tabs[]
    # (so we know it's actually syncing, not just reading)
    has_iteration = bool(re.search(r'for\s*\(|\.forEach\s*\(|\.map\s*\(', script))
    has_tabs_assign = bool(re.search(r'tabs\s*\[', script))
    assert has_iteration and has_tabs_assign, \
        "Tabs.svelte missing iteration + tabs[] assignment (sync logic incomplete)"


# [pr_diff] fail_to_pass
# Structural because: Svelte component context (setContext/register_tab) can't be tested outside runtime
def test_mounted_tab_tracking():
    """register_tab and unregister_tab must track which tabs are mounted,
    so that the sync logic knows which tab entries it should NOT overwrite.

    Without this tracking, the reactive sync would overwrite tab entries
    that mounted TabItem components already manage via register_tab.
    """
    script = _get_tabs_instance_script()

    # Strip comments
    clean = re.sub(r'//.*$', '', script, flags=re.MULTILINE)
    clean = re.sub(r'/\*.*?\*/', '', clean, flags=re.DOTALL)

    # Must declare a tracking data structure (Set, Map, Array, or object)
    tracking_match = re.search(
        r'(?:let|const|var)\s+(\w+)\s*(?::\s*(?:Set|Map|Array)<[^>]*>)?\s*=\s*(?:new\s+(?:Set|Map)\s*\(|[\[\{])',
        clean,
    )
    assert tracking_match, \
        "No tracking data structure (Set/Map/Array/object) declared in Tabs.svelte"
    tracking_var = tracking_match.group(1)

    # register_tab must add to it
    reg_section = clean[clean.find('register_tab'):]
    reg_body = reg_section[:reg_section.find('unregister_tab') if 'unregister_tab' in reg_section else 500]
    add_pat = re.compile(
        rf'{re.escape(tracking_var)}\s*\.\s*(?:add|set|push)\s*\(|{re.escape(tracking_var)}\s*\['
    )
    assert add_pat.search(reg_body), \
        f"register_tab does not add to {tracking_var}"

    # unregister_tab must remove from it
    unreg_section = clean[clean.find('unregister_tab'):]
    unreg_body = unreg_section[:500]
    remove_pat = re.compile(
        rf'{re.escape(tracking_var)}\s*\.\s*(?:delete|splice|pop|remove)\s*\(|delete\s+{re.escape(tracking_var)}\s*\['
    )
    assert remove_pat.search(unreg_body), \
        f"unregister_tab does not remove from {tracking_var}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_core_apis_preserved():
    """Essential methods/functions must still exist in both files."""
    init_src = INIT_FILE.read_text()
    tabs_src = TABS_FILE.read_text()

    for fn in ["update_state", "find_node_by_id", "find_parent"]:
        assert fn in init_src, f"Missing {fn} in init.svelte.ts"

    for fn in ["register_tab", "unregister_tab", "selected_tab"]:
        assert fn in tabs_src, f"Missing {fn} in Tabs.svelte"


# [static] pass_to_pass
def test_files_not_gutted():
    """Both files must retain substantial content (reject gutting/rewriting)."""
    init_lines = len(INIT_FILE.read_text().splitlines())
    tabs_lines = len(TABS_FILE.read_text().splitlines())
    # Base: init ~914 lines, tabs ~180 lines. Fix adds ~50 and ~20.
    assert init_lines >= 800, f"init.svelte.ts too short ({init_lines} lines, need >=800)"
    assert tabs_lines >= 80, f"Tabs.svelte too short ({tabs_lines} lines, need >=80)"


# [static] fail_to_pass
def test_init_file_grew():
    """init.svelte.ts must be longer than the base (~914 lines) since the fix adds ~50 lines of code."""
    init_lines = len(INIT_FILE.read_text().splitlines())
    assert init_lines >= 950, \
        f"init.svelte.ts has {init_lines} lines (base had ~914, fix should add ~50)"
