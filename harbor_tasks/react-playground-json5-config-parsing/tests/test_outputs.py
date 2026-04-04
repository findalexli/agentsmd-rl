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
PACKAGE_JSON = f"{PLAYGROUND}/package.json"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run an inline Node.js script, with json5 available globally."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _extract_parse_function_js() -> str:
    """Extract parseConfigOverrides from compilation.ts, strip TS types,
    return executable JS that defines the function with JSON5 available."""
    src = Path(COMPILATION_TS).read_text()

    # Find the function definition (may or may not have 'export')
    pattern = re.compile(
        r'(?:export\s+)?function\s+parseConfigOverrides'
        r'\s*\([^)]*\)'       # params (may have TS types)
        r'(?:\s*:\s*\w+)?\s*' # optional return type
        r'\{',
        re.DOTALL,
    )
    match = pattern.search(src)
    assert match, "parseConfigOverrides function not found in compilation.ts"

    # Find the matching closing brace
    start = match.end() - 1  # opening {
    depth = 0
    end = start
    for i in range(start, len(src)):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        if depth == 0:
            end = i
            break

    func_body = src[match.start():end + 1]

    # Strip TS type annotations from parameters and return type
    func_body = re.sub(r'configOverrides\s*:\s*string', 'configOverrides', func_body)
    func_body = re.sub(r'\)\s*:\s*\w+\s*\{', ') {', func_body)
    # Remove 'export' keyword
    func_body = re.sub(r'^export\s+', '', func_body)

    return f"const JSON5 = require('json5');\n{func_body}\n"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_json5_parses_valid_config():
    """parseConfigOverrides correctly parses JSON5 configs with unquoted keys."""
    fn_js = _extract_parse_function_js()
    script = fn_js + textwrap.dedent("""\
        // Test 1: simple unquoted key
        const r1 = parseConfigOverrides('{ compilationMode: "all" }');
        if (r1.compilationMode !== "all") {
            process.stderr.write("Test 1 failed: " + JSON.stringify(r1));
            process.exit(1);
        }
        // Test 2: nested object
        const r2 = parseConfigOverrides('{ environment: { validateRefAccessDuringRender: true } }');
        if (r2.environment.validateRefAccessDuringRender !== true) {
            process.stderr.write("Test 2 failed: " + JSON.stringify(r2));
            process.exit(1);
        }
        // Test 3: empty string returns empty object
        const r3 = parseConfigOverrides('');
        if (Object.keys(r3).length !== 0) {
            process.stderr.write("Test 3 failed: " + JSON.stringify(r3));
            process.exit(1);
        }
        // Test 4: whitespace-only returns empty object
        const r4 = parseConfigOverrides('   ');
        if (Object.keys(r4).length !== 0) {
            process.stderr.write("Test 4 failed: " + JSON.stringify(r4));
            process.exit(1);
        }
        // Test 5: mixed value types
        const r5 = parseConfigOverrides('{ maxLevel: 42, sources: ["a.ts", "b.ts"], enabled: null }');
        if (r5.maxLevel !== 42 || r5.sources.length !== 2 || r5.enabled !== null) {
            process.stderr.write("Test 5 failed: " + JSON.stringify(r5));
            process.exit(1);
        }
    """)
    r = _run_node(script)
    assert r.returncode == 0, f"JSON5 config parsing failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_xss_iife_rejected():
    """Malicious IIFE expressions are rejected by config parser."""
    fn_js = _extract_parse_function_js()
    payloads = [
        '(function(){ return {}; })()',
        '(() => ({}))()',
        '(function(){ document.title = "hacked"; return {}; })()',
    ]
    for payload in payloads:
        escaped = json.dumps(payload)  # proper JS string escaping
        script = fn_js + f"""
try {{
    parseConfigOverrides({escaped});
    process.stderr.write("Should have thrown for: " + {escaped});
    process.exit(1);
}} catch (e) {{
    // Expected: safe parser rejects JS expressions
}}
"""
        r = _run_node(script)
        assert r.returncode == 0, (
            f"IIFE payload was not rejected: {payload}\n{r.stderr}"
        )


# [pr_diff] fail_to_pass
def test_xss_function_call_rejected():
    """Function calls like eval() in config values are rejected."""
    fn_js = _extract_parse_function_js()
    payloads = [
        '{ compilationMode: eval("all") }',
        '{ compilationMode: (alert("xss"), "all") }',
        '{ compilationMode: new String("all") }',
        'fetch("https://evil.com")',
    ]
    for payload in payloads:
        escaped = json.dumps(payload)
        script = fn_js + f"""
try {{
    parseConfigOverrides({escaped});
    process.stderr.write("Should have thrown for: " + {escaped});
    process.exit(1);
}} catch (e) {{
    // Expected: safe parser rejects function calls
}}
"""
        r = _run_node(script)
        assert r.returncode == 0, (
            f"Function call payload was not rejected: {payload}\n{r.stderr}"
        )


# [pr_diff] fail_to_pass
def test_json5_comments_supported():
    """JSON5 comments and trailing commas are supported in config."""
    fn_js = _extract_parse_function_js()
    script = fn_js + textwrap.dedent("""\
        // Single-line comment in config
        const r1 = parseConfigOverrides(`{
          // This is a comment
          compilationMode: "all",
        }`);
        if (r1.compilationMode !== "all") {
            process.stderr.write("Single-line comment test failed");
            process.exit(1);
        }

        // Block comment in config
        const r2 = parseConfigOverrides(`{
          /* block comment */
          compilationMode: "annotation",
        }`);
        if (r2.compilationMode !== "annotation") {
            process.stderr.write("Block comment test failed");
            process.exit(1);
        }

        // Default config with commented-out option (should be empty)
        const r3 = parseConfigOverrides(`{
          //compilationMode: "all"
        }`);
        if (Object.keys(r3).length !== 0) {
            process.stderr.write("Commented-out option should yield empty object");
            process.exit(1);
        }

        // Trailing comma after last property
        const r4 = parseConfigOverrides(`{
          compilationMode: "all",
          environment: { validateRefAccessDuringRender: false, },
        }`);
        if (r4.compilationMode !== "all" || r4.environment.validateRefAccessDuringRender !== false) {
            process.stderr.write("Trailing comma test failed");
            process.exit(1);
        }
    """)
    r = _run_node(script)
    assert r.returncode == 0, (
        f"JSON5 comments/trailing commas not supported:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_default_config_json5_format():
    """Default config uses JSON5 object format, not TypeScript import/satisfies wrapper."""
    src = Path(DEFAULT_STORE_TS).read_text()

    # Old format wrapped config in: import type { PluginOptions } ... satisfies PluginOptions
    # The defaultConfig value must not contain these TypeScript constructs
    match = re.search(r"export const defaultConfig\s*=\s*`([^`]+)`", src)
    assert match, "Could not find defaultConfig template literal in defaultStore.ts"
    config_text = match.group(1)
    assert "PluginOptions" not in config_text, (
        "defaultConfig still references PluginOptions type"
    )
    assert "satisfies" not in config_text, (
        "defaultConfig still uses 'satisfies' TypeScript operator"
    )

    # New format: defaultConfig should be a JSON5 object starting with {
    config_value = config_text.strip().lstrip("\\").strip()
    assert config_value.startswith("{"), (
        f"Default config should be a JSON5 object starting with '{{', got: {config_value[:80]}"
    )


# [pr_diff] fail_to_pass
def test_no_new_function_for_config():
    """Config parsing does not use new Function() or eval() — the XSS vulnerability."""
    src = Path(COMPILATION_TS).read_text()

    # The old code had: new Function(`return (${configString})`)()
    assert "new Function" not in src, (
        "compilation.ts still uses new Function() for config parsing (XSS vulnerability)"
    )

    # Must use a safe data-only parser (JSON5 or equivalent)
    assert "JSON5" in src, "compilation.ts should use JSON5 for safe config parsing"


# [pr_diff] fail_to_pass
def test_json5_dependency_added():
    """json5 package is listed as a dependency in playground package.json."""
    pkg = json.loads(Path(PACKAGE_JSON).read_text())
    deps = pkg.get("dependencies", {})
    assert "json5" in deps, (
        f"json5 not found in playground dependencies. Found: {list(deps.keys())}"
    )
