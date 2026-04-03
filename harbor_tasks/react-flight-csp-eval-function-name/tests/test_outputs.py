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


def _extract_catch_body():
    """Extract the catch block body from createFakeFunction for behavioral testing."""
    src = Path(CLIENT_JS).read_text()
    func_start = src.index("function createFakeFunction")
    catch_start = src.index("catch (x)", func_start)
    brace_start = src.index("{", catch_start)
    depth = 0
    brace_end = -1
    for i in range(brace_start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                brace_end = i
                break
    assert brace_end != -1, "Could not find matching brace for catch block"
    return src[brace_start + 1 : brace_end]


def _run_name_test(test_names):
    """Run a node script that extracts the catch block and verifies fn.name is set."""
    node_script = r"""
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');

const funcStart = src.indexOf('function createFakeFunction');
if (funcStart === -1) { console.error('createFakeFunction not found'); process.exit(10); }

const catchStart = src.indexOf('catch (x)', funcStart);
if (catchStart === -1) { console.error('catch block not found'); process.exit(11); }

const braceStart = src.indexOf('{', catchStart);
let depth = 0, braceEnd = -1;
for (let i = braceStart; i < src.length; i++) {
  if (src[i] === '{') depth++;
  if (src[i] === '}') { depth--; if (depth === 0) { braceEnd = i; break; } }
}
if (braceEnd === -1) { console.error('catch brace not matched'); process.exit(12); }

let catchBody = src.substring(braceStart + 1, braceEnd);
// Strip Flow suppression comments to produce valid JS
catchBody = catchBody.replace(/\/\/ \$FlowFixMe[^\n]*/g, '');

const testNames = %s;
const failures = [];

for (const name of testNames) {
  try {
    const fn = new Function('name', 'let fn;\n' + catchBody + '\nreturn fn;')(name);
    if (typeof fn !== 'function') {
      failures.push(name + ': result is not a function');
    } else if (fn.name !== name) {
      failures.push(name + ': expected "' + name + '", got "' + fn.name + '"');
    }
  } catch(e) {
    failures.push(name + ': threw ' + e.message);
  }
}

if (failures.length > 0) {
  console.error('FAILURES:\n' + failures.join('\n'));
  process.exit(1);
}
console.log('PASS: all ' + testNames.length + ' names verified');
""" % (CLIENT_JS, str(test_names).replace("'", '"'))

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
    r = _run_name_test(["a", "App.Header", "my-action", "Résumé"])
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"CSP fallback special names not set correctly:\n{stderr}\n{stdout}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — formatting from .claude/skills/fix/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .claude/skills/fix/SKILL.md:10 @ 87ae75b
def test_prettier_format():
    """Changed file passes yarn prettier formatting check."""
    r = subprocess.run(
        ["yarn", "prettier", "--check",
         "packages/react-client/src/ReactFlightClient.js"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Prettier formatting check failed:\n{stdout}\n{stderr}"
    )
