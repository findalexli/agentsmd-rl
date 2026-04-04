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

REPO = "/workspace/react"
CLIENT_JS = f"{REPO}/packages/react-client/src/ReactFlightClient.js"


def _run_name_test(test_names):
    """Run a Node script that extracts the catch-block body from
    createFakeFunction and verifies fn.name is set for each input name."""

    names_json = str(test_names).replace("'", '"')
    node_script = f"""
const fs = require('fs');
const src = fs.readFileSync('{CLIENT_JS}', 'utf8');

const funcStart = src.indexOf('function createFakeFunction');
if (funcStart === -1) {{ console.error('createFakeFunction not found'); process.exit(10); }}

const catchStart = src.indexOf('catch (x)', funcStart);
if (catchStart === -1) {{ console.error('catch block not found'); process.exit(11); }}

const braceStart = src.indexOf('{{', catchStart);
let depth = 0, braceEnd = -1;
for (let i = braceStart; i < src.length; i++) {{
  if (src[i] === '{{') depth++;
  if (src[i] === '}}') {{ depth--; if (depth === 0) {{ braceEnd = i; break; }} }}
}}
if (braceEnd === -1) {{ console.error('catch brace not matched'); process.exit(12); }}

let catchBody = src.substring(braceStart + 1, braceEnd);
// Strip Flow suppression comments to produce valid JS
catchBody = catchBody.replace(/\\/\\/ \\$FlowFixMe[^\\n]*/g, '');

const testNames = {names_json};
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
  console.error('FAILURES:\\n' + failures.join('\\n'));
  process.exit(1);
}}
console.log('PASS: all ' + testNames.length + ' names verified');
"""
    r = subprocess.run(["node", "-e", node_script], capture_output=True, timeout=30)
    return r


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_createfakefunction_exists():
    """ReactFlightClient.js exists and contains createFakeFunction with a catch block."""
    src = Path(CLIENT_JS).read_text()
    assert "createFakeFunction" in src, "createFakeFunction not found"
    func_start = src.find("function createFakeFunction")
    assert func_start != -1, "function createFakeFunction declaration not found"
    catch_pos = src.find("catch (x)", func_start)
    assert catch_pos != -1, "catch (x) block not found in createFakeFunction"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_csp_fallback_function_named():
    """CSP fallback in createFakeFunction produces correctly named functions.

    Extracts the catch block body and executes it in Node to verify that
    the resulting function's .name property matches the input name.
    Tests common component/action names.
    """
    r = _run_name_test(["MyComponent", "ServerAction", "fetchData"])
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"CSP fallback function names not set correctly:\n{stderr}\n{stdout}"
    )


# [pr_diff] fail_to_pass
def test_csp_fallback_special_names():
    """CSP fallback handles edge-case names: single char, dotted, hyphenated, unicode."""
    r = _run_name_test(["a", "App.Header", "my-action", "Komponent"])
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"CSP fallback special names not set correctly:\n{stderr}\n{stdout}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — anti-stub: verify the function is still callable
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_csp_fallback_function_callable():
    """The CSP fallback function must still be callable (wraps inner call).

    The fallback fn should accept a thunk and return its result, matching
    the pattern `fn = function(_) { return _(); }`. This ensures the fix
    doesn't break the function's actual behavior while adding the name.
    """
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
    r = subprocess.run(["node", "-e", node_script], capture_output=True, timeout=30)
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"CSP fallback function not callable or not named:\n{stderr}\n{stdout}"
    )
