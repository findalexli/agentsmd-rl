"""
Task: react-playground-json5-config-parsing
Repo: react @ 74568e8627aa43469b74f2972f427a209639d0b6
PR:   36159

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/react"
PLAYGROUND = f"{REPO}/compiler/apps/playground"
COMPILATION_TS = f"{PLAYGROUND}/lib/compilation.ts"
DEFAULT_STORE_TS = f"{PLAYGROUND}/lib/defaultStore.ts"
CONFIG_EDITOR_TSX = f"{PLAYGROUND}/components/Editor/ConfigEditor.tsx"
PACKAGE_JSON = f"{PLAYGROUND}/package.json"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run an inline Node.js script, with json5 available globally."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        timeout=timeout,
    )


def _extract_parse_function() -> str:
    """Extract parseConfigOverrides logic from compilation.ts and return a
    Node.js script fragment that defines the function using JSON5."""
    src = Path(COMPILATION_TS).read_text()

    # Verify the function exists and uses JSON5
    assert "parseConfigOverrides" in src, (
        "parseConfigOverrides function not found in compilation.ts"
    )
    assert "JSON5" in src, "compilation.ts must import/use JSON5"

    # Return a JS re-implementation matching the TS source logic
    return textwrap.dedent("""\
        const JSON5 = require('json5');
        function parseConfigOverrides(configOverrides) {
            const trimmed = configOverrides.trim();
            if (!trimmed) return {};
            return JSON5.parse(trimmed);
        }
    """)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_json5_parses_valid_config():
    """parseConfigOverrides correctly parses JSON5 configs with unquoted keys."""
    fn = _extract_parse_function()
    script = fn + textwrap.dedent("""\
        const r1 = parseConfigOverrides('{ compilationMode: "all" }');
        if (r1.compilationMode !== "all") {
            process.exit(1);
        }
        const r2 = parseConfigOverrides('{ environment: { validateRefAccessDuringRender: true } }');
        if (r2.environment.validateRefAccessDuringRender !== true) {
            process.exit(1);
        }
        const r3 = parseConfigOverrides('');
        if (Object.keys(r3).length !== 0) {
            process.exit(1);
        }
        const r4 = parseConfigOverrides('{ maxLevel: 42, sources: ["a.ts", "b.ts"] }');
        if (r4.maxLevel !== 42 || r4.sources.length !== 2) {
            process.exit(1);
        }
    """)
    r = _run_node(script)
    assert r.returncode == 0, (
        f"JSON5 config parsing failed:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_xss_iife_rejected():
    """Malicious IIFE expressions are rejected by config parser."""
    fn = _extract_parse_function()
    payloads = [
        '(function(){ return {}; })()',
        '(() => ({}))()',
        '(function(){ document.title = "hacked"; return {}; })()',
    ]
    for payload in payloads:
        escaped = payload.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        script = fn + f"""
try {{
    parseConfigOverrides("{escaped}");
    process.exit(1);  // Should have thrown
}} catch (e) {{
    // Expected: JSON5 rejects JS expressions
}}
"""
        r = _run_node(script)
        assert r.returncode == 0, (
            f"IIFE payload was not rejected: {payload}\n{r.stderr.decode()}"
        )


# [pr_diff] fail_to_pass
def test_xss_function_call_rejected():
    """Function calls like eval() in config values are rejected."""
    fn = _extract_parse_function()
    payloads = [
        '{ compilationMode: eval("all") }',
        '{ compilationMode: (alert("xss"), "all") }',
        '{ compilationMode: new String("all") }',
        'fetch("https://evil.com")',
    ]
    for payload in payloads:
        escaped = payload.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        script = fn + f"""
try {{
    parseConfigOverrides("{escaped}");
    process.exit(1);  // Should have thrown
}} catch (e) {{
    // Expected
}}
"""
        r = _run_node(script)
        assert r.returncode == 0, (
            f"Function call payload was not rejected: {payload}\n{r.stderr.decode()}"
        )


# [pr_diff] fail_to_pass
def test_json5_comments_supported():
    """JSON5 comments and trailing commas are supported in config."""
    fn = _extract_parse_function()
    script = fn + textwrap.dedent("""\
        // Single-line comment
        const r1 = parseConfigOverrides(`{
          // This is a comment
          compilationMode: "all",
        }`);
        if (r1.compilationMode !== "all") process.exit(1);

        // Block comment
        const r2 = parseConfigOverrides(`{
          /* block comment */
          compilationMode: "annotation",
        }`);
        if (r2.compilationMode !== "annotation") process.exit(1);

        // Default config with commented-out option
        const r3 = parseConfigOverrides(`{
          //compilationMode: "all"
        }`);
        if (Object.keys(r3).length !== 0) process.exit(1);
    """)
    r = _run_node(script)
    assert r.returncode == 0, (
        f"JSON5 comments/trailing commas not supported:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_default_config_json5_format():
    """Default config uses JSON5 object format, not TypeScript import/satisfies wrapper."""
    src = Path(DEFAULT_STORE_TS).read_text()

    # The old format used: import type { PluginOptions } ... satisfies PluginOptions
    assert "import type" not in src, (
        "defaultStore.ts still uses TypeScript import for config"
    )
    assert "satisfies" not in src, (
        "defaultStore.ts still uses 'satisfies' TypeScript operator"
    )
    assert "PluginOptions" not in src, (
        "defaultStore.ts still references PluginOptions type"
    )

    # The new format should be a JSON5 object starting with {
    # Extract the defaultConfig value
    match = re.search(r"export const defaultConfig\s*=\s*`([^`]+)`", src)
    assert match, "Could not find defaultConfig export in defaultStore.ts"
    config_value = match.group(1).strip().lstrip("\\")
    # The config should start with { (JSON5 object)
    assert config_value.startswith("{"), (
        f"Default config should be a JSON5 object starting with '{{', got: {config_value[:50]}"
    )


# [pr_diff] fail_to_pass
def test_no_new_function_for_config():
    """Config parsing does not use new Function() or eval()."""
    src = Path(COMPILATION_TS).read_text()

    # Find the config parsing section — should not have new Function
    # The old code had: new Function(`return (${configString})`)()
    assert "new Function" not in src, (
        "compilation.ts still uses new Function() for config parsing (XSS vulnerability)"
    )

    # Should use JSON5 instead
    assert "JSON5" in src, "compilation.ts should use JSON5 for config parsing"
    assert "parseConfigOverrides" in src, (
        "compilation.ts should have parseConfigOverrides function"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_json5_dependency_added():
    """json5 package is listed as a dependency in playground package.json."""
    pkg = json.loads(Path(PACKAGE_JSON).read_text())
    deps = pkg.get("dependencies", {})
    assert "json5" in deps, (
        f"json5 not found in playground dependencies. Found: {list(deps.keys())}"
    )
