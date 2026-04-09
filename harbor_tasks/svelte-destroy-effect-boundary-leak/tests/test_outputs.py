"""
Task: svelte-destroy-effect-boundary-leak
Repo: svelte @ 6b33dd2a1e8aa48dc88c9ce6e19c4a49a2eac51a
PR:   17980

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import textwrap
from pathlib import Path

REPO = "/workspace/svelte"
EFFECTS_JS = f"{REPO}/packages/svelte/src/internal/client/reactivity/effects.js"


def _read_destroy_effect_body():
    """Extract the destroy_effect function body from effects.js."""
    src = Path(EFFECTS_JS).read_text()
    # Match from 'export function destroy_effect' to the closing brace at the same indent
    match = re.search(
        r'export function destroy_effect\b[^{]*\{(.*?)^\}',
        src,
        re.DOTALL | re.MULTILINE,
    )
    assert match, "Could not find destroy_effect function in effects.js"
    return match.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """effects.js must parse without syntax errors."""
    src = Path(EFFECTS_JS).read_text()
    assert len(src) > 1000, "effects.js is too small or missing"
    assert "export function destroy_effect" in src, "destroy_effect function not found"
    # Basic structural integrity: braces should be balanced
    assert src.count("{") == src.count("}"), "Unbalanced braces in effects.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_boundary_ref_cleared():
    """destroy_effect must null out effect.b (boundary reference) during cleanup."""
    # Run a Node.js script that reads the source and checks effect.b is cleared
    script = textwrap.dedent("""\
        const fs = require('fs');
        const src = fs.readFileSync(process.argv[1], 'utf8');

        // Extract destroy_effect function body
        const fnMatch = src.match(/export function destroy_effect\\b[^{]*\\{([\\s\\S]*?)^\\}/m);
        if (!fnMatch) {
            console.error('destroy_effect function not found');
            process.exit(1);
        }
        const body = fnMatch[1];

        // Check that effect.b is assigned null somewhere in the function
        // Accept both chained assignment (effect.b = \\n ... null) and standalone (effect.b = null)
        const hasEffectB = /effect\\.b\\s*=\\s*(\\n[\\s\\S]*?)?null/.test(body);
        if (!hasEffectB) {
            console.error('effect.b is NOT nulled in destroy_effect — boundary reference leaks');
            process.exit(1);
        }
        console.log('OK: effect.b is cleared in destroy_effect');
    """)
    r = subprocess.run(
        ["node", "-e", script, EFFECTS_JS],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"effect.b not cleared in destroy_effect:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_effect_cleanup_behavior():
    """Executing the cleanup assignments must set effect.b to null on a mock effect."""
    # Extract the null-assignment chain(s) from destroy_effect, eval against a mock
    script = textwrap.dedent("""\
        const fs = require('fs');
        const src = fs.readFileSync(process.argv[1], 'utf8');

        // Extract destroy_effect body
        const fnMatch = src.match(/export function destroy_effect\\b[^{]*\\{([\\s\\S]*?)^\\}/m);
        if (!fnMatch) { console.error('destroy_effect not found'); process.exit(1); }
        const body = fnMatch[1];

        // Find ALL null-assignment statements (chained or standalone)
        // Pattern: effect.X = effect.Y = ... = null;  OR  effect.X = null;
        const assignments = body.match(/effect\\.\\w+\\s*=[\\s\\S]*?null\\s*;/g);
        if (!assignments || assignments.length === 0) {
            console.error('No null assignments found in destroy_effect');
            process.exit(1);
        }

        // Create a mock effect with .b set to a complex object (simulating Boundary)
        const effect = {
            next: {id: 1}, prev: {id: 2}, teardown: () => {},
            ctx: {state: 'active'}, deps: [1, 2], fn: () => 'test',
            nodes: {start: {}, end: {}, t: null}, ac: new AbortController(),
            b: { children: [{}, {}], state: {count: 42}, parent: {} },
            f: 0, parent: null, first: null, last: null
        };

        // Execute all null-assignment statements
        for (const assignment of assignments) {
            try { eval(assignment); } catch(e) { /* ignore eval errors */ }
        }

        if (effect.b !== null) {
            console.error('effect.b was NOT cleared to null. Value:', JSON.stringify(effect.b));
            process.exit(1);
        }
        console.log('OK: effect.b correctly nulled after cleanup');
    """)
    r = subprocess.run(
        ["node", "-e", script, EFFECTS_JS],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"effect.b not cleared in cleanup chain:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """destroy_effect has substantial logic, not a stub."""
    body = _read_destroy_effect_body()
    # The function should have significant content: conditionals, loops, assignments
    lines = [l.strip() for l in body.strip().splitlines() if l.strip() and not l.strip().startswith('//')]
    assert len(lines) >= 15, (
        f"destroy_effect body too short ({len(lines)} non-empty lines), likely a stub"
    )
    # Must contain key operations: status setting, child destruction, null chain
    assert 'effect.next' in body, "Missing effect.next cleanup"
    assert 'effect.fn' in body, "Missing effect.fn cleanup"
    assert 'null' in body, "Missing null assignments"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI/CD)
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_lint():
    """Repo's lint (eslint + prettier) passes (pass_to_pass)."""
    # Build first (needed for prettier-plugin-svelte)
    build_r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert build_r.returncode == 0, f"Build failed before lint:\\n{build_r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_signals_tests():
    """Repo's signals tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "test", "signals", "--", "--reporter=basic"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Signals tests failed:\\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_build():
    """Repo's build passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\\n{r.stderr[-500:]}"
