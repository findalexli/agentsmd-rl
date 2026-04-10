"""
Task: gradio-walkthrough-selected-binding
Repo: gradio-app/gradio @ dcfc429a8125204c3aafeabcab251dd7580f9a60
PR:   12925

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "js" / "tabs" / "Index.svelte"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = REPO / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


def _read_clean():
    """Read Index.svelte with HTML comments stripped."""
    src = TARGET.read_text()
    return re.sub(r"<!--[\s\S]*?-->", "", src)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_integrity():
    """Index.svelte must exist and retain at least 8 of 10 original patterns."""
    assert TARGET.is_file() and TARGET.stat().st_size > 0, f"{TARGET} missing or empty"
    clean = _read_clean()
    patterns = [
        r"import\s.*Gradio.*from\s+['\"]@gradio/utils['\"]",
        r"import\s.*Tabs.*from\s+['\"]\.\/shared\/Tabs\.svelte['\"]",
        r"import\s.*Walkthrough.*from\s+['\"]\.\/shared\/Walkthrough\.svelte['\"]",
        r"\$effect\s*\(",
        r"gradio\.dispatch\(['\"]gradio_tab_select['\"]",
        r"initial_tabs",
        r"<slot\s*/?>",
        r"\{#if\b[^}]*walkthrough",
        r"\{:else\}",
        r"\{/if\}",
    ]
    passed = sum(1 for p in patterns if re.search(p, clean))
    assert passed >= 8, f"Integrity: only {passed}/10 original patterns found"


# [static] pass_to_pass
def test_not_stub():
    """File must not be truncated — original is ~65 lines."""
    lines = TARGET.read_text().splitlines()
    assert len(lines) >= 50, f"File only has {len(lines)} lines (expected >= 50)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using Node.js
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_walkthrough_bind_selected():
    """Walkthrough component must use bind:selected (two-way binding) in the
    {#if walkthrough} block — the core fix for back-and-forward navigation.

    Uses Node.js to parse the Svelte template, extract the Walkthrough tag
    within the conditional block, and verify the binding direction."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('js/tabs/Index.svelte', 'utf8');

// Strip HTML comments
const clean = src.replace(/<!--[\s\S]*?-->/g, '');

// Extract the {#if ...walkthrough} ... {:else} block
const ifMatch = clean.match(/\{#if[^}]*walkthrough[^}]*\}([\s\S]*?)\{:else\}/);
if (!ifMatch) {
    console.log(JSON.stringify({error: "No walkthrough block found"}));
    process.exit(1);
}
const walkthroughBlock = ifMatch[1];

// Find <Walkthrough ...> tag and extract attributes
const tagMatch = walkthroughBlock.match(/<Walkthrough\b([\s\S]*?)(?:\/>|>)/);
if (!tagMatch) {
    console.log(JSON.stringify({error: "No Walkthrough tag in walkthrough block"}));
    process.exit(1);
}
const attrs = tagMatch[1];
const hasBindSelected = /\bbind:selected\b/.test(attrs);

console.log(JSON.stringify({hasBindSelected, attrs: attrs.trim()}));
""")
    assert r.returncode == 0, f"Node script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("hasBindSelected"), (
        f"Walkthrough tag does not use bind:selected. "
        f"Found attrs: {data.get('attrs', '(none)')}"
    )


# [pr_diff] fail_to_pass
def test_no_oneway_selected_on_walkthrough():
    """Within the walkthrough block, <Walkthrough> must NOT retain a bare
    selected= (without bind:) — that one-way binding is the root cause.

    Uses Node.js to parse Walkthrough tag attributes and confirm the buggy
    one-way binding has been replaced."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('js/tabs/Index.svelte', 'utf8');

// Strip HTML comments
const clean = src.replace(/<!--[\s\S]*?-->/g, '');

// Extract the {#if ...walkthrough} ... {:else} block
const ifMatch = clean.match(/\{#if[^}]*walkthrough[^}]*\}([\s\S]*?)\{:else\}/);
if (!ifMatch) {
    console.log(JSON.stringify({error: "No walkthrough block found"}));
    process.exit(1);
}
const walkthroughBlock = ifMatch[1];

// Find <Walkthrough ...> tag
const tagMatch = walkthroughBlock.match(/<Walkthrough\b([\s\S]*?)(?:\/>|>)/);
if (!tagMatch) {
    console.log(JSON.stringify({error: "No Walkthrough tag in walkthrough block"}));
    process.exit(1);
}
const attrs = tagMatch[1];

// Neutralize bind:selected, then check for any remaining bare selected=
const neutralized = attrs.replace(/bind:selected/g, '__BOUND__');
const hasBareSelected = /\bselected\s*[={]/.test(neutralized);

console.log(JSON.stringify({hasBareSelected, attrs: attrs.trim()}));
""")
    assert r.returncode == 0, f"Node script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert not data.get("hasBareSelected"), (
        f"One-way selected= still present on Walkthrough. "
        f"Found attrs: {data.get('attrs', '(none)')}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_tabs_retains_bind_selected():
    """Tabs component in {:else} branch must keep its bind:selected."""
    clean = _read_clean()
    m = re.search(r"\{:else\}([\s\S]*?)\{/if\}", clean)
    assert m, "No {:else} ... {/if} block found"
    eblock = m.group(1)
    tags = re.findall(r"<Tabs\b([^>]*?)>", eblock, re.S)
    assert any(re.search(r"\bbind:selected\b", t) for t in tags), (
        "Tabs missing bind:selected in else block"
    )


# [pr_diff] pass_to_pass
def test_event_dispatches_both_branches():
    """Both Walkthrough and Tabs branches must fire on:change and on:select."""
    clean = _read_clean()
    w_match = re.search(r"\{#if\b[^}]*walkthrough[^}]*\}([\s\S]*?)\{:else\}", clean)
    assert w_match, "No walkthrough block found"
    wblock = w_match.group(1)
    e_match = re.search(r"\{:else\}([\s\S]*?)\{/if\}", clean)
    assert e_match, "No else block found"
    eblock = e_match.group(1)
    assert "on:change" in wblock and "on:select" in wblock, (
        "Walkthrough branch missing event handlers"
    )
    assert "on:change" in eblock and "on:select" in eblock, (
        "Tabs branch missing event handlers"
    )


# [pr_diff] pass_to_pass
def test_effect_gradio_tab_select():
    """The reactive $effect dispatching gradio_tab_select must remain intact."""
    clean = _read_clean()
    assert re.search(r"\$effect\s*\(\s*\(\)\s*=>\s*\{", clean), (
        "$effect block not found"
    )
    assert "gradio_tab_select" in clean, "gradio_tab_select dispatch missing"
    assert "gradio.props.selected" in clean, "gradio.props.selected reference missing"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates - verify existing functionality not broken
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit test suite passes (pass_to_pass) - 479 tests."""
    # First build the client (required for tests)
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"

    # Run the unit tests
    r = subprocess.run(
        ["pnpm", "test:run"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_client_tests():
    """Repo's client test suite passes (pass_to_pass) - 141 tests."""
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client tests failed: {r.stderr[-500:]} {r.stdout[-1000:]}"
