"""
Task: gradio-load-event-inactive-tab
Repo: gradio-app/gradio @ 6011b00d0154b85532fa901dd73cf8fa7d86fd04
PR:   12904

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/gradio"
FILE = Path(REPO) / "js/core/src/init.svelte.ts"


def _read_source():
    return FILE.read_text()


def _strip_comments(code: str) -> str:
    code = re.sub(r"//.*", "", code)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


def _extract_method(src: str, signature: str, max_len: int = 4000) -> str:
    start = src.find(signature)
    assert start != -1, f"Method '{signature}' not found"
    depth = 0
    started = False
    body = []
    for i in range(start, min(start + max_len, len(src))):
        ch = src[i]
        if ch == "{":
            depth += 1
            started = True
        if ch == "}":
            depth -= 1
        if started:
            body.append(ch)
        if started and depth == 0:
            break
    return "".join(body)


def _meaningful_lines(code: str) -> int:
    stripped = _strip_comments(code)
    return len([l for l in stripped.splitlines()
                if l.strip() and l.strip() not in ("{", "}")])


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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: TypeScript/Svelte module with deep framework deps, cannot import in Python
def test_spread_replace_bug_removed():
    """The spread-replace pattern (node!.props.props = { ...spread })
    must be absent from the !_set_data branch in update_state.
    This pattern breaks Svelte 5 $state proxy tracking for unmounted components."""
    src = _read_source()
    update_body = _extract_method(src, "async update_state(")

    assert _meaningful_lines(update_body) >= 10, \
        "update_state appears to be a stub"

    stripped = _strip_comments(update_body)

    no_callback = update_body.find("if (!_set_data)")
    if no_callback == -1:
        # Method restructured — acceptable if substantial (verified above)
        return

    else_pos = update_body.find("else if (_set_data)", no_callback)
    branch = stripped[no_callback:else_pos] if else_pos > no_callback \
        else stripped[no_callback:no_callback + 600]

    assert not re.search(r"\.props\.props\s*=\s*\{[^}]*\.\.\.", branch), \
        "Spread-replace pattern still present — breaks Svelte $state proxy"


# [pr_diff] fail_to_pass
# AST-only because: TypeScript/Svelte module with deep framework deps, cannot import in Python
def test_deferred_state_stored():
    """update_state must store deferred state on the class instance when
    _set_data is unavailable (component hidden in inactive tab).
    Accepts: this.X.set(), this.X.push(), this.X[k]=v, this.X.add()."""
    src = _read_source()
    update_body = _extract_method(src, "async update_state(")
    stripped = _strip_comments(update_body)

    no_callback = update_body.find("if (!_set_data)")
    if no_callback == -1:
        target = stripped
    else:
        else_pos = update_body.find("else if (_set_data)", no_callback)
        target = stripped[no_callback:else_pos] if else_pos > no_callback \
            else stripped[no_callback:no_callback + 600]

    assert (
        re.search(r"this[.\[#]\S*\.(set|push|add)\s*\(", target) or
        re.search(r"this[.\[#]\S*\[.*\]\s*=", target)
    ), "update_state does not store deferred state on class instance"


# [pr_diff] fail_to_pass
# AST-only because: TypeScript/Svelte module with deep framework deps, cannot import in Python
def test_register_component_applies_deferred():
    """register_component must apply deferred state when a component mounts.
    It should read from the class-level store and be substantially longer
    than the buggy version (~6 lines)."""
    src = _read_source()
    method_body = _extract_method(src, "register_component(", max_len=3000)
    stripped = _strip_comments(method_body)

    ml = _meaningful_lines(method_body)
    assert ml >= 10, \
        f"register_component has only {ml} lines — expected deferred state logic"

    assert (
        re.search(r"this[.\[#]\S*\.(get|has|delete|size|length|shift|pop|keys|entries|forEach)\s*\(", stripped) or
        re.search(r"this[.\[#]\S*\[.*\]", stripped)
    ), "register_component does not read from any deferred state store"


# [pr_diff] fail_to_pass
# AST-only because: TypeScript/Svelte module with deep framework deps, cannot import in Python
def test_no_full_tree_traversal_in_render():
    """render_previously_invisible_children must not do a full tree traversal
    with root reassignment (this.root = this.traverse(this.root!, [...])),
    which triggers unnecessary Svelte reactive cascades."""
    src = _read_source()
    method_body = _extract_method(
        src, "render_previously_invisible_children(", max_len=2000)

    ml = _meaningful_lines(method_body)
    assert ml >= 2, "render_previously_invisible_children is a stub"

    stripped = _strip_comments(method_body)
    assert "this.root = this.traverse(this.root" not in stripped, \
        "Still does full tree traversal with root reassignment"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
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
