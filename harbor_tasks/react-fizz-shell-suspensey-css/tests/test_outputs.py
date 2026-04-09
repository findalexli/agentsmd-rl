"""
Task: react-fizz-shell-suspensey-css
Repo: react @ f247ebaf44317ac6648b62f99ceaed1e4fc4dc01
PR:   35824

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/react"

FIZZ_CONFIG_DOM = f"{REPO}/packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js"
FIZZ_SERVER = f"{REPO}/packages/react-server/src/ReactFizzServer.js"


def _extract_and_eval_has_suspensey(state_json: str, flushing_in_shell: str) -> str:
    """Use Node subprocess to extract hasSuspenseyContent from DOM config and evaluate it."""
    script = f"""
const fs = require('fs');
const src = fs.readFileSync('{FIZZ_CONFIG_DOM}', 'utf8');

// Find the function by name
const funcStart = src.indexOf('function hasSuspenseyContent');
if (funcStart === -1) {{ console.error('hasSuspenseyContent not found'); process.exit(1); }}

// Find opening brace of function body
const bodyStart = src.indexOf('{{', funcStart);
let depth = 1, i = bodyStart + 1;
while (depth > 0 && i < src.length) {{
  if (src[i] === '{{') depth++;
  else if (src[i] === '}}') depth--;
  i++;
}}
const body = src.substring(bodyStart + 1, i - 1);

// Create callable function (Flow types in the body are just identifiers, not syntax errors)
const fn = new Function('hoistableState', 'flushingInShell', body);

const state = {state_json};
const result = fn(state, {flushing_in_shell});
console.log(JSON.stringify({{ result: !!result }}));
"""
    r = subprocess.run(["node", "-e", script], capture_output=True, timeout=30)
    assert r.returncode == 0, (
        f"Node eval failed:\nstdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )
    return r.stdout.decode().strip()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files must have balanced braces."""
    files = [FIZZ_CONFIG_DOM, FIZZ_SERVER]
    for f in files:
        content = Path(f).read_text()
        assert content.count("{") == content.count("}"), f"Unbalanced braces in {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_shell_flush_skips_css_only_outlining():
    """During shell flush, stylesheets-only content should NOT trigger outlining."""
    # Test with varying stylesheet counts — all should return false when in shell
    for size in [1, 3, 7]:
        state = f'{{ stylesheets: {{ size: {size} }}, suspenseyImages: false }}'
        output = _extract_and_eval_has_suspensey(state, "true")
        assert '"result":false' in output, (
            f"Expected false for stylesheets.size={size} during shell flush, got: {output}"
        )


# [pr_diff] fail_to_pass
def test_flushing_shell_tracked_in_server():
    """ReactFizzServer must declare flushingShell and set it true around root segment flush."""
    src = Path(FIZZ_SERVER).read_text()

    # flushingShell must be declared
    assert re.search(r'let\s+flushingShell\s*=\s*false', src), (
        "flushingShell variable not declared in ReactFizzServer.js"
    )

    # flushingShell must be set to true before flushSegment for root and false after
    # Pattern: flushingShell = true; ... flushSegment(...completedRootSegment...); ... flushingShell = false
    assert re.search(r'flushingShell\s*=\s*true', src), (
        "flushingShell is never set to true in ReactFizzServer.js"
    )
    assert re.search(r'flushingShell\s*=\s*false', src, re.MULTILINE), (
        "flushingShell is never reset to false in ReactFizzServer.js"
    )

    # Verify ordering: true is set BEFORE the root segment flush call
    true_pos = src.index("flushingShell = true")
    false_pos = src.rindex("flushingShell = false")
    root_flush = src.find("completedRootSegment, null")
    assert true_pos < root_flush < false_pos, (
        "flushingShell must be set true before root segment flush and false after"
    )


# [pr_diff] fail_to_pass
def test_shell_awareness_in_flush_segment():
    """flushSegment must pass shell awareness to hasSuspenseyContent."""
    src = Path(FIZZ_SERVER).read_text()

    # In the flushSegment function, hasSuspenseyContent must receive a second argument
    # that conveys whether we're flushing the shell.
    # Find the flushSegment function
    flush_seg_start = src.find("function flushSegment")
    assert flush_seg_start != -1, "flushSegment function not found"

    # Look for hasSuspenseyContent call within flushSegment with 2 args
    flush_seg_section = src[flush_seg_start:flush_seg_start + 5000]
    match = re.search(
        r'hasSuspenseyContent\s*\(\s*boundary\.contentState\s*,\s*(\w+)\s*\)',
        flush_seg_section,
    )
    assert match, (
        "hasSuspenseyContent in flushSegment must be called with a second argument "
        "for shell-awareness"
    )
    arg_name = match.group(1)
    # The argument should reference the shell flushing state (not a literal false)
    assert arg_name != "false", (
        f"flushSegment should pass dynamic shell state, not literal false (got {arg_name})"
    )


# [pr_diff] fail_to_pass
def test_all_renderers_updated():
    """All renderer configs must accept flushingInShell in hasSuspenseyContent."""
    configs = [
        FIZZ_CONFIG_DOM,
        f"{REPO}/packages/react-dom-bindings/src/server/ReactFizzConfigDOMLegacy.js",
        f"{REPO}/packages/react-markup/src/ReactFizzConfigMarkup.js",
        f"{REPO}/packages/react-noop-renderer/src/ReactNoopServer.js",
    ]
    for filepath in configs:
        content = Path(filepath).read_text()
        # Find hasSuspenseyContent signature — must include flushingInShell or equivalent 2nd param
        fn_match = re.search(
            r'hasSuspenseyContent\s*\(([^)]*)\)',
            content,
            re.DOTALL,
        )
        assert fn_match, f"hasSuspenseyContent not found in {filepath}"
        params = fn_match.group(1)
        # Must have at least 2 parameters (comma-separated)
        param_parts = [p.strip() for p in params.split(",") if p.strip()]
        assert len(param_parts) >= 2, (
            f"hasSuspenseyContent in {Path(filepath).name} must accept 2 parameters, "
            f"found: {params.strip()}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_streaming_still_outlines_for_css():
    """When NOT flushing shell, stylesheets must still trigger outlining."""
    for size in [1, 4]:
        state = f'{{ stylesheets: {{ size: {size} }}, suspenseyImages: false }}'
        output = _extract_and_eval_has_suspensey(state, "false")
        assert '"result":true' in output, (
            f"Expected true for stylesheets.size={size} during streaming, got: {output}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow():
    """Repo's Flow typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_version_check():
    """Repo's version check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/version-check.js"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_license_check():
    """Repo's license check passes (pass_to_pass)."""
    r = subprocess.run(
        ["./scripts/ci/check_license.sh"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"License check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_fizz_server():
    """Repo's ReactDOMFizzServer tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern=ReactDOMFizzServer-test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Fizz server tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_fizz_shell_hydration():
    """Repo's ReactDOMFizzShellHydration tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern=ReactDOMFizzShellHydration"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Fizz shell hydration tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_fizz_static():
    """Repo's ReactDOMFizzStatic tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern=ReactDOMFizzStatic-test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Fizz static tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_fizz_server_node():
    """Repo's ReactDOMFizzServerNode tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern=ReactDOMFizzServerNode"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Fizz server node tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
