"""
Task: gradio-test-event-dispatch-noop
Repo: gradio-app/gradio @ 6f8a0533ad0247e709fefe406961b864473d344d
PR:   13028

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Gradio's JS/Svelte source cannot be executed in the test container
(no node_modules installed). All checks use structural/regex analysis.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/gradio")


def _strip_comments(src: str) -> str:
    """Remove JS single-line and block comments."""
    src = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    return src


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """All files touched by the fix must exist and not be empty."""
    for rel in [
        "js/utils/src/utils.svelte.ts",
        "js/tootils/src/render.ts",
        "js/textbox/shared/Textbox.svelte",
        "js/spa/vite.config.ts",
    ]:
        p = REPO / rel
        assert p.exists(), f"{rel} does not exist"
        assert p.stat().st_size > 0, f"{rel} is empty"


# [static] pass_to_pass
def test_not_stub():
    """Modified files have substantive content, not gutted."""
    render = (REPO / "js/tootils/src/render.ts").read_text()
    assert len(render.splitlines()) >= 100, "render.ts too short — likely stubbed"

    utils = (REPO / "js/utils/src/utils.svelte.ts").read_text()
    assert len(utils.splitlines()) >= 100, "utils.svelte.ts too short — likely gutted"

    textbox = (REPO / "js/textbox/shared/Textbox.svelte").read_text()
    assert len(textbox.splitlines()) >= 200, "Textbox.svelte too short — likely stubbed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# Structural checks because: JS/Svelte code, no node_modules in container
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_noop_dispatcher_removed():
    """The __GRADIO_BROWSER_TEST__ no-op dispatcher override must be removed
    from the Gradio class constructor so events are properly wired."""
    src = (REPO / "js/utils/src/utils.svelte.ts").read_text()
    stripped = _strip_comments(src)

    # The buggy code checks __GRADIO_BROWSER_TEST__ and sets dispatcher to no-op
    assert "__GRADIO_BROWSER_TEST__" not in stripped, \
        "__GRADIO_BROWSER_TEST__ no-op override still present"

    # Find the Gradio class body (not other classes like ShareError)
    gradio_class = re.search(
        r"class\s+Gradio\b[\s\S]*?constructor\s*\([\s\S]*?\)\s*\{([\s\S]*?)(?=\n\t\w|\n\t\$effect|\Z)",
        stripped
    )
    assert gradio_class, "Gradio class constructor not found"
    body = gradio_class.group(1)

    # Constructor must assign both dispatcher and register_component from shared props
    assert re.search(r"(?:this\.)?dispatcher\s*=", body), \
        "dispatcher not assigned in Gradio constructor"
    assert re.search(r"(?:this\.)?register_component\s*=", body), \
        "register_component not assigned in Gradio constructor"

    # Must NOT have early-return pattern that sets dispatcher to no-op
    assert not re.search(
        r"this\.dispatcher\s*=\s*\(\s*\)\s*=>\s*\{\s*\}[\s\S]*?return\b", body
    ), "early return still sets dispatcher to no-op"


# [pr_diff] fail_to_pass
def test_listener_registry():
    """render.ts must have an event listener Map (distinct from containerCache)
    with a listen/on function that registers callbacks into it."""
    src = (REPO / "js/tootils/src/render.ts").read_text()
    stripped = _strip_comments(src)

    # Must have a Map for event/listener storage (not just containerCache)
    # Look for a Map that stores listeners/callbacks/event handlers
    listener_map = re.search(
        r"(?:listener|event|handler)\w*\s*[=:]\s*new\s+Map", stripped, re.IGNORECASE
    )
    typed_listener_map = re.search(
        r"new\s+Map\s*<\s*string\s*,\s*(?:Set|Array)", stripped
    )
    assert listener_map or typed_listener_map, \
        "No event listener Map found (only containerCache exists)"

    # Must have a listen/on function that adds to the listener map
    assert re.search(r"function\s+(?:listen|on)\s*\(", stripped), \
        "No listen/on function found for event registration"


# [pr_diff] fail_to_pass
def test_render_returns_event_helpers():
    """render() must return listen, set_data, and get_data (or equivalent
    data mutation functions) in addition to the standard container/component."""
    src = (REPO / "js/tootils/src/render.ts").read_text()
    stripped = _strip_comments(src)

    # Find the render function's return statement
    render_fn = re.search(r"async\s+function\s+render[\s\S]*?^}", stripped, re.MULTILINE)
    assert render_fn, "render function not found"

    ret = re.search(r"return\s*\{([\s\S]*?)\};", render_fn.group(0))
    assert ret, "No return statement in render()"

    ret_body = ret.group(1)
    # Must return at least 6 fields: container, component, listen, set_data/get_data, debug, unmount
    field_count = len(re.findall(r"\w+\s*[,:]", ret_body))
    assert field_count >= 6, \
        f"render() returns only {field_count} fields, expected >= 6 (need listen + data helpers)"


# [pr_diff] fail_to_pass
def test_dispatcher_notifies_listeners():
    """The dispatcher must call registered listener callbacks, not just fire
    a DOM CustomEvent. The fix adds a notify function that iterates listener Sets."""
    src = (REPO / "js/tootils/src/render.ts").read_text()
    stripped = _strip_comments(src)

    # The buggy pattern: dispatcher only calls target.dispatchEvent(new CustomEvent(...))
    # The fix: dispatcher calls a notify function that iterates registered listeners
    # Check that there's NO dispatchEvent-only dispatcher, but instead listener iteration

    # Find all dispatcher/mock_dispatcher definitions (arrow or const)
    dispatchers = re.findall(
        r"(?:const\s+\w*[Dd]ispatch\w*|(?:let|var)\s+\w*[Dd]ispatch\w*)"
        r"\s*=\s*\([^)]*\)\s*(?::\s*\w+\s*)?=>\s*\{([^}]*)\}",
        stripped
    )

    if dispatchers:
        # At least one dispatcher must NOT use dispatchEvent but reference listeners/notify
        uses_listeners = any(
            ("dispatchEvent" not in body and
             re.search(r"(?:notify|listener|emit|callback|fn)", body, re.IGNORECASE))
            for body in dispatchers
        )
        assert uses_listeners, \
            "All dispatchers use dispatchEvent — must notify registered listeners instead"
    else:
        # Maybe the dispatcher is a function declaration
        assert re.search(
            r"function\s+\w*dispatch\w*[^{]*\{[^}]*(?:notify|listener|emit)",
            stripped, re.IGNORECASE
        ), "No dispatcher that notifies listeners found"


# [pr_diff] fail_to_pass
def test_register_component_wired():
    """register_component passed to Gradio shared props must not be a no-op.
    It must accept set_data/get_data callbacks to wire the component data bridge."""
    src = (REPO / "js/tootils/src/render.ts").read_text()
    stripped = _strip_comments(src)

    assert "register_component" in stripped, "register_component not referenced"

    # Must NOT be: register_component: () => {}
    noop = re.search(r"register_component\s*:\s*\(\s*\)\s*=>\s*\{\s*\}", stripped)
    assert not noop, "register_component is still a no-op"

    # The wired version should accept parameters (id, set_data, get_data)
    mock_register = re.search(
        r"(?:const|let|function)\s+\w*[Rr]egister\w*\s*(?:=\s*\(|[\s(])"
        r"[^)]*\w+[^)]*\)", stripped
    )
    assert mock_register, \
        "No register function with parameters found — must accept set_data/get_data"


# [pr_diff] fail_to_pass
def test_clipboard_error_handling():
    """handle_copy in Textbox.svelte must wrap clipboard API in error handling
    so copy_feedback() still runs even when clipboard throws."""
    src = (REPO / "js/textbox/shared/Textbox.svelte").read_text()

    # Extract script block
    script_m = re.search(r"<script[^>]*>([\s\S]*?)</script>", src)
    assert script_m, "No <script> tag found in Textbox.svelte"
    script = script_m.group(1)

    # Find handle_copy function
    fn_m = re.search(r"(?:async\s+)?function\s+handle_copy\b[\s\S]*?\n\t\}", script)
    assert fn_m, "handle_copy function not found"
    fn = fn_m.group(0)

    # Must have try/catch or .catch() around clipboard
    has_try_catch = "try" in fn and "catch" in fn
    has_promise_catch = bool(re.search(r"\.catch\s*\(", fn))
    assert has_try_catch or has_promise_catch, \
        "No error handling around clipboard API in handle_copy"

    if has_try_catch:
        try_pos = fn.index("try")
        catch_pos = fn.index("catch", try_pos)
        clip_pos = fn.find("clipboard", try_pos)
        assert clip_pos != -1 and clip_pos < catch_pos, \
            "clipboard.writeText not inside try block"

    # copy_feedback must still be called (outside catch, so it always runs)
    assert "copy_feedback" in fn, "copy_feedback not called in handle_copy"


# [pr_diff] fail_to_pass
def test_vitest_browser_permissions():
    """Permissions must be in playwright provider contextOptions,
    not in browser instance context (the old buggy pattern)."""
    src = (REPO / "js/spa/vite.config.ts").read_text()
    stripped = _strip_comments(src)

    has_context_options = bool(
        re.search(r"contextOptions\s*:\s*\{[\s\S]*?permissions", stripped)
    )
    has_old_pattern = bool(
        re.search(r"instances\s*:\s*\[[\s\S]*?context\s*:\s*\{[\s\S]*?permissions", stripped)
    )

    assert has_context_options, "contextOptions with permissions not found"
    assert not has_old_pattern, \
        "Permissions still in instance context (old buggy pattern)"


# [pr_diff] fail_to_pass
def test_custom_button_prop_wired():
    """IconButtonWrapper must receive on_custom_button_click as a prop
    (the old code used the wrong prop name 'oncustombuttonclick' directly)."""
    src = (REPO / "js/textbox/shared/Textbox.svelte").read_text()
    assert re.search(r"on_custom_button_click\s*=", src), \
        "on_custom_button_click not wired as prop to IconButtonWrapper"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/gradio && corepack enable && pnpm install >/dev/null 2>&1 && pnpm run format:check"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_node_tests():
    """Repo's @gradio/client node tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/gradio && corepack enable && pnpm install >/dev/null 2>&1 && NODE_NO_WARNINGS=1 TEST_MODE=node pnpm --filter @gradio/client test:node"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Client node tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regressions
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_render_cleanup_exports():
    """render and cleanup functions must still be exported from render.ts."""
    src = (REPO / "js/tootils/src/render.ts").read_text()
    assert re.search(r"export\s+(async\s+)?function\s+render", src), \
        "render function no longer exported"
    assert re.search(r"export\s+function\s+cleanup", src), \
        "cleanup function no longer exported"


# [pr_diff] pass_to_pass
def test_fire_event_export():
    """fireEvent must still be exported from render.ts."""
    src = (REPO / "js/tootils/src/render.ts").read_text()
    assert re.search(r"export\s+(const\s+)?fireEvent", src), \
        "fireEvent export missing"
