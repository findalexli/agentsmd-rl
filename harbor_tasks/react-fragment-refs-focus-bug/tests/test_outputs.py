"""
Task: react-fragment-refs-focus-bug
Repo: facebook/react @ 8f4150605449efe909822d8b20fe529d85851afe
PR:   36010

Tests for setFocusIfFocusable fix in ReactFiberConfigDOM.js.
Behavioral tests extract the function and run it in jsdom via Node.js subprocess.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/react"
TARGET = REPO + "/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared JS: read source, extract setFocusIfFocusable body, create jsdom env
_EXTRACT_FN = r"""
const fs = require('fs');
const { JSDOM } = require('jsdom');

const src = fs.readFileSync(
  'packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js', 'utf8'
);

// Extract setFocusIfFocusable function body
const fnMatch = src.match(/export function setFocusIfFocusable\b[^{]*\{/);
if (!fnMatch) { console.error('FAIL: setFocusIfFocusable not found'); process.exit(1); }
let start = fnMatch.index + fnMatch[0].length;
let depth = 1, i = start;
while (i < src.length && depth > 0) {
  if (src[i] === '{') depth++;
  else if (src[i] === '}') depth--;
  i++;
}
let body = src.substring(start, i - 1);

// Strip Flow type casts: ((expr: any): Type) -> (expr)
body = body.replace(/\(\((\w+)\s*:\s*any\)\s*:\s*\w+\)/g, '($1)');

// Set up jsdom
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
const { document } = dom.window;
global.HTMLElement = dom.window.HTMLElement;

// Create callable function from extracted body
const setFocusIfFocusable = new Function('node', 'focusOptions', body);
"""


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

def test_file_exists():
    """ReactFiberConfigDOM.js must exist and export setFocusIfFocusable."""
    p = Path(TARGET)
    assert p.exists(), f"File not found: {TARGET}"
    assert "setFocusIfFocusable" in p.read_text()


def test_function_not_stub():
    """setFocusIfFocusable must have a non-trivial implementation."""
    src = Path(TARGET).read_text()
    m = re.search(r'export function setFocusIfFocusable\b[^{]*\{', src)
    assert m, "setFocusIfFocusable not found"
    start = m.end()
    depth, i = 1, start
    while i < len(src) and depth > 0:
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        i += 1
    fn = src[start:i - 1]
    assert 'didFocus' in fn
    assert 'try' in fn
    lines = [l.strip() for l in fn.splitlines()
             if l.strip() and not l.strip().startswith('//')]
    assert len(lines) >= 8, f"Function body too short ({len(lines)} lines)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_already_focused_returns_true():
    """setFocusIfFocusable returns true when element is already the active element.

    Bug: base code adds a focus listener then calls .focus(), but an
    already-focused element fires no focus event, so the function returns false.
    Fix: short-circuit with `return true` when activeElement === element.
    """
    r = _run_node(_EXTRACT_FN + r"""
const input = document.createElement('input');
document.body.appendChild(input);
input.focus();

if (document.activeElement !== input) {
  console.error('FAIL: could not focus input in jsdom');
  process.exit(1);
}

const result = setFocusIfFocusable(input);
if (result !== true) {
  console.error('FAIL: returned ' + result + ' for already-focused element, expected true');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0 and "PASS" in r.stdout, (
        f"Already-focused test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


def test_delegated_focus_returns_true():
    """setFocusIfFocusable detects focus when it delegates to a child element.

    Bug: base code listens for 'focus' on the element itself. When .focus()
    delegates to a child (like label->input), the event fires on the child,
    not the element, so the listener misses it and returns false.
    Fix: listen on ownerDocument in capture phase to catch all focus events.
    """
    r = _run_node(_EXTRACT_FN + r"""
const container = document.createElement('div');
const input = document.createElement('input');
container.appendChild(input);
document.body.appendChild(container);

// Override focus to simulate delegation (like <label> or delegatesFocus)
container.focus = function(opts) { input.focus(opts); };

const result = setFocusIfFocusable(container);
if (result !== true) {
  console.error('FAIL: returned ' + result + ' for delegated focus, expected true');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0 and "PASS" in r.stdout, (
        f"Delegated focus test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


def test_capture_listener_cleanup():
    """Listener removal uses ownerDocument.removeEventListener with capture flag."""
    src = Path(TARGET).read_text()
    assert re.search(
        r'ownerDocument\.removeEventListener\(\s*[\'"]focus[\'"]\s*,'
        r'\s*handleFocus\s*,\s*true\s*\)',
        src,
    ), "Missing: ownerDocument.removeEventListener('focus', handleFocus, true)"
    assert not re.search(
        r'element\.removeEventListener\(\s*[\'"]focus[\'"]\s*,\s*handleFocus\s*\)',
        src,
    ), "Old element.removeEventListener still present; must use ownerDocument with capture"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI) — verify repo's own checks pass
# ---------------------------------------------------------------------------


def _run_yarn_command(cmd: list, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def test_repo_lint():
    """Repo's ESLint check passes on the modified file (pass_to_pass).

    The React repo runs ESLint on all source files. This test verifies that
    the modified ReactFiberConfigDOM.js passes linting.
    """
    r = _run_yarn_command(
        ["node", "./scripts/tasks/eslint.js", TARGET],
        timeout=60
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_flow():
    """Repo's Flow typecheck passes (pass_to_pass).

    React uses Flow for type checking. The 'dom' inline config includes
    the react-dom-bindings package where the fix is applied.
    """
    r = _run_yarn_command(
        ["node", "./scripts/tasks/flow.js", "dom"],
        timeout=120
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_unit_tests_relevant():
    """Unit tests for react-dom-bindings pass (pass_to_pass).

    The full test suite takes too long, so we run only tests for the
    package containing the modified file.
    """
    r = _run_yarn_command(
        ["yarn", "test", "--testPathPattern=react-dom-bindings", "-r=stable", "--env=development", "--ci"],
        timeout=120
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
