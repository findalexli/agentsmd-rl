"""
Task: react-flight-csp-eval-function-name
Repo: facebook/react @ 87ae75b33f71eb673c55ddb3a147a9e58b7d05bd
PR:   35650

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix: In createFakeFunction's eval-disabled fallback (catch block),
add Object.defineProperty(fn, 'name', {value: name}) so the function
retains its server-side name for stack traces in CSP environments.
"""

import subprocess
from pathlib import Path
import os
import json

REPO = "/workspace/react"
CLIENT_JS = f"{REPO}/packages/react-client/src/ReactFlightClient.js"


def _node_eval(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def _extract_catch_block(source: str) -> str:
    """Extract the catch block body from createFakeFunction."""
    func_start = source.find("function createFakeFunction")
    if func_start == -1:
        raise ValueError("createFakeFunction not found")

    catch_pos = source.find("catch (x)", func_start)
    if catch_pos == -1:
        raise ValueError("catch block not found in createFakeFunction")

    brace_start = source.find("{", catch_pos)
    depth = 1
    brace_end = -1
    for i in range(brace_start + 1, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                brace_end = i
                break

    if brace_end == -1:
        raise ValueError("Could not find end of catch block")

    return source[brace_start + 1 : brace_end].strip()


# -----------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_createfakefunction_exists():
    """ReactFlightClient.js exists and contains createFakeFunction with a catch block."""
    src = Path(CLIENT_JS).read_text()
    assert "createFakeFunction" in src, "createFakeFunction not found"
    func_start = src.find("function createFakeFunction")
    assert func_start != -1, "function createFakeFunction declaration not found"
    catch_pos = src.find("catch (x)", func_start)
    assert catch_pos != -1, "catch (x) block not found in createFakeFunction"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_csp_fallback_function_named():
    """CSP fallback function has correct name via Object.defineProperty.

    Verifies the fix is present in source and that executing the catch block
    code produces correctly named functions.
    """
    src = Path(CLIENT_JS).read_text()

    # Find the catch block and verify Object.defineProperty with 'name' is present
    catch_pos = src.find("catch (x)", src.find("function createFakeFunction"))
    brace_start = src.find("{", catch_pos)
    depth = 1
    brace_end = -1
    for i in range(brace_start + 1, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                brace_end = i
                break

    catch_body = src[brace_start + 1 : brace_end]

    # Verify the fix is present: Object.defineProperty with 'name'
    has_define_property = "Object.defineProperty" in catch_body
    has_name_property = "'name'" in catch_body or '"name"' in catch_body
    assert has_define_property, "Object.defineProperty not found in catch block"
    assert has_name_property, "'name' property not found in Object.defineProperty call"

    # Execute the actual catch block code to verify behavior
    node_script = f"""
const fs = require('fs');
const src = fs.readFileSync('{CLIENT_JS}', 'utf8');

const funcStart = src.indexOf('function createFakeFunction');
const catchStart = src.indexOf('catch (x)', funcStart);
const braceStart = src.indexOf('{{', catchStart);
let depth = 0, braceEnd = -1;
for (let i = braceStart; i < src.length; i++) {{
  if (src[i] === '{{') depth++;
  if (src[i] === '}}') {{ depth--; if (depth === 0) {{ braceEnd = i; break; }} }}
}}

let catchBody = src.substring(braceStart + 1, braceEnd);
// Strip Flow suppression comments to produce valid JS
catchBody = catchBody.replace(/\\/\\/ \\$FlowFixMe[^\\n]*/g, '');

const testNames = ['MyComponent', 'ServerAction', 'fetchData'];
const failures = [];

for (const name of testNames) {{
  try {{
    const fn = new Function('name', 'let fn;\\n' + catchBody + '\\nreturn fn;')(name);
    if (typeof fn !== 'function') {{
      failures.push(name + ': result is not a function (' + typeof fn + ')');
    }} else if (fn.name !== name) {{
      failures.push(name + ': expected "' + name + '", got "' + fn.name + '"');
    }}
  }} catch(e) {{
    failures.push(name + ': threw ' + e.message);
  }}
}}

if (failures.length > 0) {{
  console.error('FAILURES:');
  for (const f of failures) console.error(f);
  process.exit(1);
}}
console.log('PASS: all ' + testNames.length + ' names verified');
"""
    r = _node_eval(node_script)
    assert r.returncode == 0, f"CSP fallback function names not set correctly:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_csp_fallback_special_names():
    """CSP fallback handles edge-case names: single char, dotted, hyphenated, unicode."""
    node_script = f"""
const fs = require('fs');
const src = fs.readFileSync('{CLIENT_JS}', 'utf8');

const funcStart = src.indexOf('function createFakeFunction');
const catchStart = src.indexOf('catch (x)', funcStart);
const braceStart = src.indexOf('{{', catchStart);
let depth = 0, braceEnd = -1;
for (let i = braceStart; i < src.length; i++) {{
  if (src[i] === '{{') depth++;
  if (src[i] === '}}') {{ depth--; if (depth === 0) {{ braceEnd = i; break; }} }}
}}

let catchBody = src.substring(braceStart + 1, braceEnd);
catchBody = catchBody.replace(/\\/\\/ \\$FlowFixMe[^\\n]*/g, '');

const testNames = ['a', 'App.Header', 'my-action', 'Komponent'];
const failures = [];

for (const name of testNames) {{
  try {{
    const fn = new Function('name', 'let fn;\\n' + catchBody + '\\nreturn fn;')(name);
    if (typeof fn !== 'function') {{
      failures.push(name + ': result is not a function (' + typeof fn + ')');
    }} else if (fn.name !== name) {{
      failures.push(name + ': expected "' + name + '", got "' + fn.name + '"');
    }}
  }} catch(e) {{
    failures.push(name + ': threw ' + e.message);
  }}
}}

if (failures.length > 0) {{
  console.error('FAILURES:');
  for (const f of failures) console.error(f);
  process.exit(1);
}}
console.log('PASS: all special names verified');
"""
    r = _node_eval(node_script)
    assert r.returncode == 0, f"CSP fallback special names not set correctly:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_csp_fallback_function_callable():
    """CSP fallback function is callable (wraps thunk) and has correct name."""
    node_script = f"""
const fs = require('fs');
const src = fs.readFileSync('{CLIENT_JS}', 'utf8');

const funcStart = src.indexOf('function createFakeFunction');
const catchStart = src.indexOf('catch (x)', funcStart);
const braceStart = src.indexOf('{{', catchStart);
let depth = 0, braceEnd = -1;
for (let i = braceStart; i < src.length; i++) {{
  if (src[i] === '{{') depth++;
  if (src[i] === '}}') {{ depth--; if (depth === 0) {{ braceEnd = i; break; }} }}
}}

let catchBody = src.substring(braceStart + 1, braceEnd);
catchBody = catchBody.replace(/\\/\\/ \\$FlowFixMe[^\\n]*/g, '');

// Create fn with name "TestComp"
const fn = new Function('name', 'let fn;\\n' + catchBody + '\\nreturn fn;')('TestComp');

// Verify fn is callable and wraps a thunk correctly
const sentinel = {{value: 42}};
const result = fn(() => sentinel);
if (result !== sentinel) {{
  console.error('fn did not return thunk result: got ' + JSON.stringify(result));
  process.exit(1);
}}

// Verify name is set
if (fn.name !== 'TestComp') {{
  console.error('fn.name is "' + fn.name + '", expected "TestComp"');
  process.exit(1);
}}

console.log('PASS: fn is callable and correctly named');
"""
    r = _node_eval(node_script)
    assert r.returncode == 0, f"CSP fallback function not callable or not named:\n{r.stderr}\n{r.stdout}"


# -----------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_react_client():
    """ESLint passes on react-client package (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js", "packages/react-client"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on react-client:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_dom_browser():
    """Flow typecheck passes for dom-browser config (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/flow.js", "dom-browser"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Flow typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flags():
    """Feature flags check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flags"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Feature flags check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_version_check():
    """Version check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "version-check"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tests_react_client():
    """Jest tests pass for react-client package (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "packages/react-client", "--ci"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Jest tests failed for react-client:\n{r.stderr[-500:]}{r.stdout[-500:]}"
