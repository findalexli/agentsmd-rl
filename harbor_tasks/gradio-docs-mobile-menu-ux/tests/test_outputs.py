"""
Task: gradio-docs-mobile-menu-ux
Repo: gradio @ 7760161258abe6329b754dd6d2511fc3b61fed95
PR:   12991

Tests mobile menu UX improvements in the docs website Header.svelte component.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
HEADER = f"{REPO}/js/_website/src/lib/components/Header.svelte"


def _read():
    return Path(HEADER).read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_header_svelte_structure():
    """Header.svelte has valid Svelte structure with script and template blocks."""
    content = _read()
    assert "<script" in content and "</script>" in content, "Missing <script> block"
    assert "click_nav" in content, "Missing click_nav state variable"
    assert "Gradio logo" in content, "Missing logo alt text"

    # Validate Svelte block structure (each opening block has a closing block)
    # Note: Svelte blocks are like {#if condition}, not {#if}
    open_if = len(re.findall(r"\{#if\b", content))
    close_if = content.count("{/if}")
    assert open_if == close_if, f"Mismatched #if blocks: {open_if} open, {close_if} close"

    open_each = len(re.findall(r"\{#each\b", content))
    close_each = content.count("{/each}")
    assert open_each == close_each, f"Mismatched #each blocks: {open_each} open, {close_each} close"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.17.0"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pnpm: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile", "--ignore-scripts"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_build():
    """Repo's client package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.17.0"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install pnpm: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile", "--ignore-scripts"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mobile_fullscreen_overlay():
    """Mobile menu uses a full-screen overlay (fixed + inset-0), not inline in header."""
    content = _read()
    assert "{#if click_nav}" in content, "No {#if click_nav} block for mobile overlay"
    idx = content.index("{#if click_nav}")
    block = content[idx : idx + 600]
    assert "fixed" in block, "Mobile overlay missing fixed positioning"
    assert "inset-0" in block, "Mobile overlay missing inset-0 (full viewport coverage)"
    assert "lg:hidden" in block, "Mobile overlay should only appear on mobile (lg:hidden)"


# [pr_diff] fail_to_pass
def test_nav_links_data_driven():
    """Nav links extracted into a JS data array and rendered with {#each}."""
    r = subprocess.run(
        [
            "node",
            "-e",
            '''
const fs = require("fs");
const src = fs.readFileSync(process.argv[1], "utf8");
const script = (src.match(/<script[^>]*>([\s\S]*?)<\/script>/) || [])[1] || "";

// Check for array literal with link objects containing label+href in script
const hasLinkArray = /\[\s*\{[^\]]*label[^\]]*href[^\]]*\/docs[^\]]*\}/.test(script);

// Check for {#each} iteration over nav data in template
const hasEachNav = /\{#each\s+\w+\s+as\s+\{\s*label/.test(src);

// Count {#each} blocks (nav + community should yield at least 2)
const eachCount = (src.match(/\{#each/g) || []).length;

console.log(JSON.stringify({ hasLinkArray, hasEachNav, eachCount }));
''',
            HEADER,
        ],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Node error: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["hasLinkArray"], "Nav links should be defined as a data array in <script>"
    assert result["hasEachNav"], "Nav links should render via {#each} iteration"
    assert result["eachCount"] >= 2, (
        f"Expected at least 2 {{#each}} loops (nav + community), got {result['eachCount']}"
    )


# [pr_diff] fail_to_pass
def test_desktop_nav_decoupled():
    """Desktop nav always visible — not toggled by mobile show_nav state."""
    r = subprocess.run(
        [
            "node",
            "-e",
            '''
const fs = require("fs");
const src = fs.readFileSync(process.argv[1], "utf8");

// Old code coupled desktop/mobile nav via class:hidden={!show_nav}
const hasCoupledToggle = /class:hidden=\{!show_nav\}/.test(src);

// Old code had $: show_nav = click_nav || ... reactive statement
const hasShowNavReactive = /\$:\s*show_nav\s*=/.test(src);

// Fixed code uses "hidden lg:flex" on <nav> (desktop always visible, mobile hidden)
const hasHiddenLgFlex = /<nav[\s\S]{0,400}hidden[\s\S]{0,20}lg:flex/.test(src);

console.log(JSON.stringify({ hasCoupledToggle, hasShowNavReactive, hasHiddenLgFlex }));
''',
            HEADER,
        ],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Node error: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert not result["hasCoupledToggle"], (
        "Desktop nav should not use class:hidden={!show_nav}"
    )
    assert not result["hasShowNavReactive"], (
        "show_nav reactive variable ($: show_nav = ...) should be removed"
    )
    assert result["hasHiddenLgFlex"], "Desktop nav should use 'hidden lg:flex' pattern"


# [pr_diff] fail_to_pass
def test_mobile_menu_accessibility():
    """Mobile menu toggle is a <button> with aria-label for screen readers."""
    content = _read()
    assert re.search(r"aria-label.*[Mm]enu", content), (
        "Menu toggle should have aria-label mentioning 'menu' (accessibility)"
    )
    # Verify old bare-SVG click handler pattern is gone:
    # The toggle should be on a <button>, not directly on an <svg>
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "click_nav = !click_nav" in line:
            context = "\n".join(lines[max(0, i - 8) : i + 1])
            assert not ("<svg" in context and "<button" not in context), (
                    f"Line {i + 1}: click_nav toggle is on a bare <svg> — "
                    "should be wrapped in a <button> for accessibility"
                )


# [pr_diff] fail_to_pass
def test_mobile_nav_closes_on_navigate():
    """Mobile nav links close the menu when clicked (click_nav = false)."""
    content = _read()
    m = re.search(r"\{#if click_nav\}([\s\S]*?)\{/if\}", content)
    assert m, "No {#if click_nav} mobile overlay block found"
    overlay = m.group(1)

    close_handlers = re.findall(r"on:click=\{.*?click_nav\s*=\s*false", overlay)
    assert len(close_handlers) >= 3, (
        f"Expected at least 3 close-on-navigate handlers in mobile overlay, "
        f"found {len(close_handlers)}. Mobile links should close the menu on tap."
    )
