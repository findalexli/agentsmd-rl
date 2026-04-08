"""
Task: gradio-dev-console-log-noise
Repo: gradio-app/gradio @ 424a4e4bcfeace96f7f5a678b56a578ad2002cf4
PR:   12970

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace")


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node."""
    script = REPO / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — console.log removal verified via Node execution
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_mount_component_log_removed():
    """MountCustomComponent.svelte must not contain console.log({ el, comp, runtime })."""
    r = _run_node(
        r"""
import { readFileSync } from 'fs';
const content = readFileSync('js/core/src/MountCustomComponent.svelte', 'utf8');
const lines = content.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('/*') && !t.startsWith('*');
});
const hasLog = codeLines.some(
    line => /console\.log\s*\(\s*\{\s*el\s*,\s*comp\s*,\s*runtime\s*\}\s*\)/.test(line)
);
if (hasLog) {
    console.error('console.log({ el, comp, runtime }) still present in executable code');
    process.exit(1);
}
console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_plugins_init_log_removed():
    """plugins.ts must not contain console.log('init gradio')."""
    r = _run_node(
        r"""
import { readFileSync } from 'fs';
const content = readFileSync('js/preview/src/plugins.ts', 'utf8');
const lines = content.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('/*') && !t.startsWith('*');
});
const hasLog = codeLines.some(
    line => /console\.log\s*\(\s*['"]init gradio['"]\s*\)/.test(line)
);
if (hasLog) {
    console.error('console.log("init gradio") still present in executable code');
    process.exit(1);
}
console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_main_mode_log_removed():
    """main.ts must not contain console.log('mode', mode)."""
    r = _run_node(
        r"""
import { readFileSync } from 'fs';
const content = readFileSync('js/spa/src/main.ts', 'utf8');
const lines = content.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t.length > 0 && !t.startsWith('//') && !t.startsWith('/*') && !t.startsWith('*');
});
const hasLog = codeLines.some(
    line => /console\.log\s*\(\s*['"]mode['"]\s*,\s*mode\s*\)/.test(line)
);
if (hasLog) {
    console.error('console.log("mode", mode) still present in executable code');
    process.exit(1);
}
console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: surrounding code intact
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_svelte_core_mounting_intact():
    """MountCustomComponent.svelte core mounting logic is preserved."""
    content = (REPO / "js/core/src/MountCustomComponent.svelte").read_text()
    markers = [
        "$effect",
        "comp = runtime.mount(component.default",
        "runtime.umount(comp)",
        "shared_props: node.props.shared_props",
        "bind:this={el}",
    ]
    for marker in markers:
        assert marker in content, f"Missing core marker: {marker}"


# [pr_diff] pass_to_pass
def test_plugins_core_intact():
    """plugins.ts plugin factory and module resolution are preserved."""
    content = (REPO / "js/preview/src/plugins.ts").read_text()
    markers = [
        "export function make_gradio_plugin(",
        "function resolve_svelte_entry(id",
        "window.__GRADIO_DEV__",
        "prebundleSvelteLibraries",
        "const resolved_v_id_2",
        "virtual:cc-init",
    ]
    for marker in markers:
        assert marker in content, f"Missing core marker: {marker}"


# [pr_diff] pass_to_pass
def test_main_core_intact():
    """main.ts custom element registration and lifecycle are preserved."""
    content = (REPO / "js/spa/src/main.ts").read_text()
    markers = [
        "async function get_index",
        "function create_custom_element",
        "GradioApp extends HTMLElement",
        'customElements.define("gradio-app"',
        "connectedCallback",
        "attributeChangedCallback",
    ]
    for marker in markers:
        assert marker in content, f"Missing core marker: {marker}"
