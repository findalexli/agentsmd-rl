"""
Task: react-compiler-playground-json5-config
Repo: facebook/react @ 74568e8627aa43469b74f2972f427a209639d0b6

Replace unsafe new Function() config parsing with JSON5.parse() in the
React Compiler Playground to eliminate an XSS vulnerability.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

PLAYGROUND = "/workspace/react/compiler/apps/playground"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_new_function_xss():
    """new Function() XSS vulnerability removed from compilation.ts."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "new Function" not in src, (
        "new Function() still present in compilation.ts — XSS vulnerability not fixed"
    )


# [pr_diff] fail_to_pass
def test_parse_config_overrides_exported():
    """parseConfigOverrides function is exported from compilation.ts."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "export function parseConfigOverrides" in src, (
        "parseConfigOverrides not exported from compilation.ts"
    )


# [pr_diff] fail_to_pass
def test_json5_parse_used():
    """JSON5.parse() is used inside parseConfigOverrides."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "JSON5.parse" in src, "JSON5.parse not found in compilation.ts"


# [pr_diff] fail_to_pass
def test_json5_import_in_compilation_ts():
    """JSON5 is imported in compilation.ts."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "import JSON5 from 'json5'" in src, (
        "import JSON5 from 'json5' not found in compilation.ts"
    )


# [pr_diff] fail_to_pass
def test_json5_dependency_in_package_json():
    """json5 package is declared as a dependency in package.json."""
    src = Path(f"{PLAYGROUND}/package.json").read_text()
    assert '"json5"' in src, "json5 dependency not found in package.json"


# [pr_diff] fail_to_pass
def test_parse_options_calls_parse_config_overrides():
    """parseOptions delegates to parseConfigOverrides instead of calling new Function."""
    src = Path(f"{PLAYGROUND}/lib/compilation.ts").read_text()
    assert "parseConfigOverrides(configOverrides)" in src, (
        "parseOptions does not call parseConfigOverrides(configOverrides)"
    )


# [pr_diff] fail_to_pass
def test_defaultstore_ts_syntax_removed():
    """defaultStore.ts uses plain JSON5 format, not TypeScript-specific syntax."""
    src = Path(f"{PLAYGROUND}/lib/defaultStore.ts").read_text()
    assert "import type { PluginOptions }" not in src, (
        "TypeScript import type statement still present in defaultStore.ts"
    )
    assert "satisfies PluginOptions" not in src, (
        "'satisfies PluginOptions' still present in defaultStore.ts — must use plain JSON5"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (behavioral) — json5 parsing correctness
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_parse_config_overrides_behavior():
    """parseConfigOverrides logic: empty→{}, JSON5 features work, XSS payloads throw."""
    # Tests the algorithm the fixed function must implement.
    # Uses json5 from the installed node_modules (installed by Dockerfile).
    test_js = r"""
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const JSON5 = require('json5');

function parseConfigOverrides(s) {
  const trimmed = s.trim();
  if (!trimmed) return {};
  return JSON5.parse(trimmed);
}

// Empty string → {}
let r = parseConfigOverrides('');
console.assert(JSON.stringify(r) === '{}', 'empty string should return {}');

// Whitespace-only → {}
r = parseConfigOverrides('   \n\t  ');
console.assert(JSON.stringify(r) === '{}', 'whitespace-only should return {}');

// JSON5 single-line comment (must not throw)
r = parseConfigOverrides(`{ //compilationMode: "all"\n}`);
console.assert(JSON.stringify(r) === '{}', 'JSON5 with comment should parse to {}');

// JSON5 unquoted key
r = parseConfigOverrides(`{ compilationMode: "all" }`);
console.assert(r.compilationMode === 'all', 'unquoted key should parse');

// JSON5 trailing comma
r = parseConfigOverrides(`{ "compilationMode": "infer", }`);
console.assert(r.compilationMode === 'infer', 'trailing comma should be allowed');

// XSS: IIFE must throw
let threw = false;
try { parseConfigOverrides('(function(){ return {}; })()'); } catch(e) { threw = true; }
console.assert(threw, 'IIFE should throw');

// XSS: function call must throw
threw = false;
try { parseConfigOverrides('eval("alert(1)")'); } catch(e) { threw = true; }
console.assert(threw, 'eval() call should throw');

// XSS: variable reference (unquoted identifier at top-level) must throw
threw = false;
try { parseConfigOverrides('someVar'); } catch(e) { threw = true; }
console.assert(threw, 'bare identifier should throw');

process.exit(0);
"""
    r = subprocess.run(
        ["node", "--input-type=module"],
        input=test_js.encode(),
        cwd=PLAYGROUND,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"parseConfigOverrides behavioral tests failed:\n"
        f"stdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )
