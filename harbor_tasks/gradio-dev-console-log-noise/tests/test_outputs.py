"""
Task: gradio-dev-console-log-noise
Repo: gradio-app/gradio @ 424a4e4bcfeace96f7f5a678b56a578ad2002cf4
PR:   12970

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

WORKSPACE = Path("/workspace")
MOUNT_SVELTE = WORKSPACE / "js/core/src/MountCustomComponent.svelte"
PLUGINS_TS = WORKSPACE / "js/preview/src/plugins.ts"
MAIN_TS = WORKSPACE / "js/spa/src/main.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — console.log removal
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mount_component_log_removed():
    """MountCustomComponent.svelte must not log reactive state."""
    content = MOUNT_SVELTE.read_text()
    # Match any console.log that dumps el, comp, runtime (with or without whitespace variations)
    assert not re.search(r"console\.log\(\s*\{\s*el\s*,\s*comp\s*,\s*runtime\s*\}\s*\)", content), (
        "MountCustomComponent.svelte still has console.log({ el, comp, runtime })"
    )


# [pr_diff] fail_to_pass
def test_plugins_init_log_removed():
    """plugins.ts must not log 'init gradio'."""
    content = PLUGINS_TS.read_text()
    # Match console.log with "init gradio" in either quote style
    assert not re.search(r"""console\.log\(\s*["']init gradio["']\s*\)""", content), (
        'plugins.ts still has console.log("init gradio")'
    )


# [pr_diff] fail_to_pass
def test_main_mode_log_removed():
    """main.ts must not log mode."""
    content = MAIN_TS.read_text()
    # Match console.log("mode", mode) with whitespace variations
    assert not re.search(r"""console\.log\(\s*["']mode["']\s*,\s*mode\s*\)""", content), (
        'main.ts still has console.log("mode", mode)'
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: surrounding code intact
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_svelte_core_mounting_intact():
    """MountCustomComponent.svelte core mounting logic is preserved."""
    content = MOUNT_SVELTE.read_text()
    markers = [
        "$effect",
        "comp = runtime.mount(component.default",
        "runtime.umount(comp)",
        "shared_props: node.props.shared_props",
        "bind:this={el}",
    ]
    for marker in markers:
        assert marker in content, (
            f"MountCustomComponent.svelte missing core marker: {marker}"
        )


# [pr_diff] pass_to_pass
def test_plugins_core_intact():
    """plugins.ts plugin factory and module resolution are preserved."""
    content = PLUGINS_TS.read_text()
    markers = [
        "export function make_gradio_plugin(",
        "function resolve_svelte_entry(id",
        "window.__GRADIO_DEV__",
        "prebundleSvelteLibraries",
        "const resolved_v_id_2",
        "virtual:cc-init",
    ]
    for marker in markers:
        assert marker in content, (
            f"plugins.ts missing core marker: {marker}"
        )


# [pr_diff] pass_to_pass
def test_main_core_intact():
    """main.ts custom element registration and lifecycle are preserved."""
    content = MAIN_TS.read_text()
    markers = [
        "async function get_index",
        "function create_custom_element",
        "GradioApp extends HTMLElement",
        'customElements.define("gradio-app"',
        "connectedCallback",
        "attributeChangedCallback",
    ]
    for marker in markers:
        assert marker in content, (
            f"main.ts missing core marker: {marker}"
        )
