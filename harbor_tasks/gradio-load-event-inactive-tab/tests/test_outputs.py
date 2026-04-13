"""
Task: gradio-load-event-inactive-tab
Repo: gradio-app/gradio @ 6011b00d0154b85532fa901dd73cf8fa7d86fd04
PR:   12904

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/gradio"
FILE = Path(REPO) / "js/core/src/init.svelte.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path("/tmp") / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _read_source():
    return FILE.read_text()


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_with_apptree():
    """init.svelte.ts must exist and contain the AppTree class."""
    assert FILE.exists(), f"{FILE} not found"
    src = _read_source()
    assert "class AppTree" in src, "AppTree class not found in source"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_spread_replace_bug_removed():
    """The spread-replace pattern (node!.props.props = { ...spread })
    must be replaced with in-place for...in modification in update_state."""
    r = _run_node("""\
import { readFileSync } from 'node:fs';
const src = readFileSync('js/core/src/init.svelte.ts', 'utf8');

const methodStart = src.indexOf('async update_state(');
if (methodStart === -1) {
    console.log(JSON.stringify({pass:false, reason:'update_state method not found'}));
    process.exit(0);
}

let depth = 0, started = false, bs = -1, be = -1;
for (let i = methodStart; i < src.length; i++) {
    if (src[i] === '{') { depth++; if (!started) { started = true; bs = i; } }
    if (src[i] === '}') { depth--; if (started && depth === 0) { be = i + 1; break; } }
}
const body = src.substring(bs, be);

// Bug pattern: spread-replace overwrites entire props object
if (/\\.props\\.props\\s*=\\s*\\{[^}]*\\.\\./.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'spread-replace pattern still present in update_state'}));
    process.exit(0);
}

// Fix: must use for...in in-place modification
if (!/for\\s*\\(\\s*const\\s+key\\s+in\\s+new_props\\.props\\s*\\)/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'for...in in-place prop loop not found in update_state'}));
    process.exit(0);
}

console.log(JSON.stringify({pass:true}));
""")
    assert r.returncode == 0, f"Node script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), result.get("reason", "spread-replace pattern still present")


# [pr_diff] fail_to_pass
def test_deferred_state_stored():
    """update_state must store deferred state in #pending_updates map.
    The map must be declared on the class and used with .get()/.set()."""
    r = _run_node("""\
import { readFileSync } from 'node:fs';
const src = readFileSync('js/core/src/init.svelte.ts', 'utf8');

// #pending_updates Map must be declared as a class field
if (!/#pending_updates\\s*=\\s*new\\s+Map/.test(src)) {
    console.log(JSON.stringify({pass:false, reason:'#pending_updates Map not declared on class'}));
    process.exit(0);
}

// update_state must write to #pending_updates
const ms = src.indexOf('async update_state(');
let d = 0, s = false, bs = -1, be = -1;
for (let i = ms; i < src.length; i++) {
    if (src[i] === '{') { d++; if (!s) { s = true; bs = i; } }
    if (src[i] === '}') { d--; if (s && d === 0) { be = i + 1; break; } }
}
const body = src.substring(bs, be);

if (!/this\\.#pending_updates\\.set\\s*\\(/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'update_state does not write to #pending_updates'}));
    process.exit(0);
}
if (!/this\\.#pending_updates\\.get\\s*\\(/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'update_state does not read #pending_updates (missing merge with existing)'}));
    process.exit(0);
}

console.log(JSON.stringify({pass:true}));
""")
    assert r.returncode == 0, f"Node script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), result.get("reason", "deferred state not stored in update_state")


# [pr_diff] fail_to_pass
def test_register_component_applies_deferred():
    """register_component must read from #pending_updates, delete the entry,
    and apply it via _set_data after tick()."""
    r = _run_node("""\
import { readFileSync } from 'node:fs';
const src = readFileSync('js/core/src/init.svelte.ts', 'utf8');

// Extract register_component method body
const ms = src.indexOf('register_component(');
let d = 0, s = false, bs = -1, be = -1;
for (let i = ms; i < src.length; i++) {
    if (src[i] === '{') { d++; if (!s) { s = true; bs = i; } }
    if (src[i] === '}') { d--; if (s && d === 0) { be = i + 1; break; } }
}
const body = src.substring(bs, be);

// Must read pending updates for the component
if (!/this\\.#pending_updates\\.get\\s*\\(/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'register_component does not read #pending_updates'}));
    process.exit(0);
}

// Must clean up after reading
if (!/this\\.#pending_updates\\.delete\\s*\\(/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'register_component does not delete from #pending_updates'}));
    process.exit(0);
}

// Must defer application until after Svelte tick
if (!/tick\\s*\\(\\s*\\)\\.then/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'register_component does not defer via tick().then()'}));
    process.exit(0);
}

// Must apply via _set callback
if (!/_set\\s*\\(\\s*pending\\s*\\)/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'register_component does not call _set(pending)'}));
    process.exit(0);
}

console.log(JSON.stringify({pass:true}));
""")
    assert r.returncode == 0, f"Node script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), result.get("reason", "register_component does not apply deferred state")


# [pr_diff] fail_to_pass
def test_no_full_tree_traversal_in_render():
    """render_previously_invisible_children must use targeted node lookup
    (find_node_by_id) instead of full tree traversal with root reassignment."""
    r = _run_node("""\
import { readFileSync } from 'node:fs';
const src = readFileSync('js/core/src/init.svelte.ts', 'utf8');

// Extract render_previously_invisible_children method body
const ms = src.indexOf('render_previously_invisible_children(');
let d = 0, s = false, bs = -1, be = -1;
for (let i = ms; i < src.length; i++) {
    if (src[i] === '{') { d++; if (!s) { s = true; bs = i; } }
    if (src[i] === '}') { d--; if (s && d === 0) { be = i + 1; break; } }
}
const body = src.substring(bs, be);

// Bug: full tree traversal with root reassignment
if (/this\\.root\\s*=\\s*this\\.traverse\\s*\\(\\s*this\\.root/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'full tree traversal with this.root reassignment still present'}));
    process.exit(0);
}

// Fix: must use targeted find_node_by_id
if (!/find_node_by_id\\s*\\(/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'does not use find_node_by_id for targeted lookup'}));
    process.exit(0);
}

// Fix: must check hidden_on_startup for early return optimization
if (!/#hidden_on_startup\\.has/.test(body)) {
    console.log(JSON.stringify({pass:false, reason:'no #hidden_on_startup check for early return'}));
    process.exit(0);
}

console.log(JSON.stringify({pass:true}));
""")
    assert r.returncode == 0, f"Node script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("pass"), result.get("reason", "full tree traversal still present")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file content checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_core_methods_present():
    """All core AppTree methods must still be present."""
    src = _read_source()
    required = [
        "register_component(", "update_state(",
        "render_previously_invisible_children(",
        "get_state(", "traverse(", "create_node(", "postprocess(",
    ]
    for sig in required:
        assert sig in src, f"Method {sig[:-1]} is missing from AppTree"


# [static] pass_to_pass
def test_helper_functions_intact():
    """Standalone helper functions and tab/accordion handling must remain."""
    src = _read_source()
    helpers = [
        "make_visible_if_not_rendered", "handle_visibility", "find_node_by_id",
        "gather_initial_tabs", "create_props_shared_props",
        "set_visibility_for_updated_node",
    ]
    for fn in helpers:
        assert f"function {fn}" in src or f"{fn}(" in src, \
            f"Function {fn} is missing"

    mvir_start = src.find("make_visible_if_not_rendered")
    mvir_block = src[mvir_start:mvir_start + 1000]
    assert "tab" in mvir_block, "Tab handling removed from make_visible_if_not_rendered"
    assert "accordion" in mvir_block, \
        "Accordion handling removed from make_visible_if_not_rendered"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands via subprocess.run()
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — CI: pnpm format:check
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/gradio && corepack enable && corepack prepare pnpm@10.17.0 --activate && pnpm install --frozen-lockfile --ignore-scripts >/dev/null 2>&1 && pnpm format:check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: pnpm --filter @gradio/client build
def test_repo_client_build():
    """Repo's client package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/gradio && corepack enable && corepack prepare pnpm@10.17.0 --activate && pnpm install --frozen-lockfile --ignore-scripts >/dev/null 2>&1 && pnpm --filter @gradio/client build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: pnpm --filter @gradio/client test
def test_repo_client_tests():
    """Repo's client package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/gradio && corepack enable && corepack prepare pnpm@10.17.0 --activate && pnpm install --frozen-lockfile --ignore-scripts >/dev/null 2>&1 && pnpm --filter @gradio/client test"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Client tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"



# [repo_tests] pass_to_pass — CI: pnpm test:run
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/gradio && corepack enable && corepack prepare pnpm@10.17.0 --activate && pnpm install --frozen-lockfile --ignore-scripts >/dev/null 2>&1 && pnpm css >/dev/null 2>&1 && pnpm --filter @gradio/client build >/dev/null 2>&1 && pnpm test:run"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: vitest run for js/core tests (tests the modified file)
def test_repo_core_tests():
    """Repo's js/core tests pass - directly tests the modified init.svelte.ts (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/gradio && corepack enable && corepack prepare pnpm@10.17.0 --activate && pnpm install --frozen-lockfile --ignore-scripts >/dev/null 2>&1 && pnpm --filter @gradio/client build >/dev/null 2>&1 && pnpm vitest run --config .config/vitest.config.ts js/core"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Core tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:45 @ 6011b00d
def test_consistent_indentation():
    """File uses tabs consistent with surrounding code style."""
    src = _read_source()
    lines = src.splitlines()
    tab_indented = sum(1 for l in lines if l.startswith("\t"))
    space_indented = sum(1 for l in lines if re.match(r"^  \S", l))
    assert space_indented <= tab_indented, \
        f"Uses spaces ({space_indented}) over tabs ({tab_indented}) — inconsistent"


# [agent_config] pass_to_pass — js/README.md:65 @ 6011b00d
def test_no_debug_artifacts():
    """No debug logging in AppTree class; no excessive trailing whitespace."""
    src = _read_source()
    class_body = src[src.find("class AppTree"):]
    assert not re.search(r"console\.(log|debug)\(", class_body), \
        "Debug logging artifacts in AppTree class"

    lines = src.splitlines()
    trailing_ws = sum(1 for l in lines if re.search(r"\S\s+$", l))
    assert trailing_ws <= 10, \
        f"Excessive trailing whitespace ({trailing_ws} lines)"


# [agent_config] pass_to_pass — js/README.md:80-81 @ 6011b00d
def test_typescript_quality():
    """No excessive @ts-ignore or any types (typing workarounds)."""
    src = _read_source()
    ts_ignore_count = len(re.findall(r"@ts-ignore", src))
    assert ts_ignore_count <= 8, \
        f"Excessive @ts-ignore ({ts_ignore_count})"

    any_count = len(re.findall(r":\s*any[^_\w]", src))
    assert any_count <= 15, \
        f"Excessive any types ({any_count})"
