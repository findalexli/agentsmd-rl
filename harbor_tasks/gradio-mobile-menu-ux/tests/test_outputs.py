"""
Task: gradio-mobile-menu-ux
Repo: gradio-app/gradio @ 7760161258abe6329b754dd6d2511fc3b61fed95

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import json
from pathlib import Path

REPO = "/workspace"
HEADER = f"{REPO}/js/_website/src/lib/components/Header.svelte"
SVELTE_TOOLS = "/svelte-tools"

# Ensure NODE_PATH is set for subprocess calls (E2B may not inherit Dockerfile ENV)
_NODE_ENV = {**os.environ, "NODE_PATH": f"{SVELTE_TOOLS}/node_modules"}

# Node.js script that parses the Svelte file's HTML template via the compiler
# AST and returns a JSON object with structural properties.
# We strip <script> content to avoid TypeScript parse errors, then analyse
# the HTML AST.  Script-level checks use plain-text regex instead.
_AST_SCRIPT = r"""
const svelte = require('svelte/compiler');
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Strip script blocks to avoid TypeScript parse failures
const stripped = src.replace(/<script[^>]*>[\s\S]*?<\/script>/g, '<script></script>');
const ast = svelte.parse(stripped);

const results = {};

function walk(node, fn) {
  if (!node || typeof node !== 'object') return;
  fn(node);
  for (const key of ['children', 'else', 'body', 'pending', 'then', 'catch']) {
    const child = node[key];
    if (Array.isArray(child)) child.forEach(c => walk(c, fn));
    else if (child) walk(child, fn);
  }
}

function attrStaticText(attr) {
  if (!attr || !attr.value || attr.value === true) return '';
  return attr.value.filter(v => v.type === 'Text').map(v => v.data || '').join(' ');
}

function attrRawSrc(attr) {
  if (!attr) return '';
  return stripped.substring(attr.start, attr.end);
}

function getAttr(node, name) {
  return (node.attributes || []).find(a => a.name === name);
}

// Check: IfBlock containing a fixed/absolute full-screen overlay element
let overlayIfNode = null;
walk(ast.html, (node) => {
  if (node.type === 'IfBlock' && !overlayIfNode) {
    walk({type: 'Fragment', children: node.children || []}, (child) => {
      if (child.type === 'Element') {
        const cls = attrStaticText(getAttr(child, 'class'));
        const style = attrStaticText(getAttr(child, 'style'));
        const combined = cls + ' ' + style;
        const isFixed = /\bfixed\b/.test(combined) || /\babsolute\b/.test(combined) || /position:\s*(fixed|absolute)/.test(combined);
        const isFullScreen = /\binset-0\b/.test(combined) ||
          (/\btop-0\b/.test(combined) && /\bleft-0\b/.test(combined)) ||
          (/\bw-full\b/.test(combined) && /\bh-full\b/.test(combined)) ||
          (/\bw-screen\b/.test(combined) && /\bh-screen\b/.test(combined)) ||
          /inset:\s*0/.test(combined) ||
          (/\btop:\s*0/.test(combined) && /\bleft:\s*0/.test(combined) && /\bwidth:\s*100/.test(combined));
        if (isFixed && isFullScreen) overlayIfNode = node;
      }
    });
  }
});
results.hasOverlay = !!overlayIfNode;

// Check: Close button with aria-label containing "close" or "dismiss" inside overlay
let hasCloseButton = false;
if (overlayIfNode) {
  walk({type: 'Fragment', children: overlayIfNode.children || []}, (node) => {
    if (node.type === 'Element' && (node.name === 'button' || node.name === 'a')) {
      const ariaLabel = getAttr(node, 'aria-label');
      if (ariaLabel) {
        const raw = attrRawSrc(ariaLabel).toLowerCase();
        if (raw.includes('close') || raw.includes('dismiss')) hasCloseButton = true;
      }
    }
  });
}
results.hasCloseButton = hasCloseButton;

// Check: Search and ThemeToggle components appear >= 2 times (desktop + mobile)
let searchCount = 0, themeCount = 0;
walk(ast.html, (node) => {
  if (node.type === 'InlineComponent') {
    if (node.name === 'Search') searchCount++;
    if (node.name === 'ThemeToggle') themeCount++;
  }
});
results.searchDual = searchCount >= 2;
results.themeDual = themeCount >= 2;

// Check: Overlay contains navigation links (>= 2 <a> elements)
// Count all <a> elements — dynamic {href} from {#each} won't have static text
let overlayLinkCount = 0;
if (overlayIfNode) {
  walk({type: 'Fragment', children: overlayIfNode.children || []}, (node) => {
    if (node.type === 'Element' && node.name === 'a') overlayLinkCount++;
  });
}
results.overlayHasLinks = overlayLinkCount >= 2;

// Check: Desktop elements preserved (logo, nav links, Community text)
let hasLogo = false, hasNavLink = false, hasCommunity = false;
walk(ast.html, (node) => {
  if (node.type === 'Element' && node.name === 'img') {
    const alt = attrStaticText(getAttr(node, 'alt'));
    if (/logo/i.test(alt)) hasLogo = true;
  }
  if (node.type === 'Element' && node.name === 'a') {
    const href = attrStaticText(getAttr(node, 'href'));
    if (href === '/docs' || href === '/guides') hasNavLink = true;
  }
  if (node.type === 'Text' && node.data && /Community/i.test(node.data)) hasCommunity = true;
});
results.desktopElements = hasLogo && hasNavLink && hasCommunity;

// Check: File substance (anti-stub) — >100 lines and >15 elements
let elementCount = 0;
walk(ast.html, (node) => {
  if (node.type === 'Element' || node.type === 'InlineComponent') elementCount++;
});
results.lineCount = src.split('\n').length;
results.elementCount = elementCount;

console.log(JSON.stringify(results));
"""

_cached_ast = None


def _get_ast_results():
    """Parse Header.svelte HTML template via the Svelte compiler and return analysis dict."""
    global _cached_ast
    if _cached_ast is not None:
        return _cached_ast
    r = subprocess.run(
        ["node", "-e", _AST_SCRIPT, HEADER],
        capture_output=True, text=True, timeout=30,
        env=_NODE_ENV,
    )
    assert r.returncode == 0, f"AST analysis failed:\n{r.stderr}"
    _cached_ast = json.loads(r.stdout.strip())
    return _cached_ast


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — Svelte syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svelte_syntax():
    """Header.svelte HTML template must parse without errors via Svelte compiler."""
    # AST-only because: Svelte component uses SvelteKit imports ($app/navigation,
    # $lib/stores) and TypeScript — full compilation needs the full SvelteKit
    # build toolchain.  We strip TS and validate the HTML template parses.
    ast = _get_ast_results()
    assert ast["lineCount"] > 0, "File appears empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fullscreen_overlay():
    """Mobile menu renders as a full-screen overlay inside a conditional block."""
    # AST-only because: Svelte template, cannot import/call
    ast = _get_ast_results()
    assert ast["hasOverlay"], (
        "No conditional block with a fixed/absolute full-screen overlay found"
    )


# [pr_diff] fail_to_pass
def test_close_button_accessible():
    """Overlay has a close button with an aria-label containing 'close' or 'dismiss'."""
    # AST-only because: Svelte template, cannot import/call
    ast = _get_ast_results()
    assert ast["hasCloseButton"], (
        "No button/link with aria-label='close'/'dismiss' found inside the overlay"
    )


# [pr_diff] fail_to_pass
def test_search_and_theme_on_mobile():
    """Search and ThemeToggle components appear in both desktop and mobile sections."""
    # AST-only because: Svelte template, cannot import/call
    ast = _get_ast_results()
    assert ast["searchDual"], "Search component appears fewer than 2 times"
    assert ast["themeDual"], "ThemeToggle component appears fewer than 2 times"


# [pr_diff] fail_to_pass
def test_overlay_has_nav_links():
    """Mobile overlay contains at least 2 internal navigation links."""
    # AST-only because: Svelte template, cannot import/call
    ast = _get_ast_results()
    assert ast["overlayHasLinks"], (
        "Overlay has fewer than 2 internal <a href='/...'> links"
    )


# [pr_diff] fail_to_pass
def test_state_decoupled():
    """Desktop/mobile visibility state is not coupled via reactive $: show_nav = click_nav || $store."""
    # Plain-text regex on the script block — no AST needed for this check
    src = Path(HEADER).read_text()
    # Extract the script block content
    script_match = re.search(r"<script[^>]*>([\s\S]*?)</script>", src)
    assert script_match, "No script block found"
    script_src = script_match.group(1)
    # The base commit has: $: show_nav = click_nav || $store?.lg;
    # A correct fix should remove this coupling
    has_coupling = bool(re.search(
        r"\$:\s*\w+\s*=.*click.*\$.*store|\$:\s*\w+\s*=.*\$.*store.*click",
        script_src,
    ))
    assert not has_coupling, (
        "Reactive statement still couples click_nav with $store for show_nav"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_desktop_elements_preserved():
    """Logo, nav links (/docs, /guides), and Community section still exist."""
    # Use raw text check — gold patch uses {#each} with dynamic {href} so
    # static AST attribute extraction misses the links.
    src = Path(HEADER).read_text()
    assert re.search(r'logo', src, re.IGNORECASE), "No logo reference found"
    assert '"/docs"' in src or "'/docs'" in src or "/docs" in src, (
        "No /docs link found"
    )
    assert '"/guides"' in src or "'/guides'" in src or "/guides" in src, (
        "No /guides link found"
    )
    assert "Community" in src, "No Community text found"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Header.svelte has real content (>100 lines, >15 elements)."""
    # AST-only because: Svelte template, cannot import/call
    ast = _get_ast_results()
    assert ast["lineCount"] > 100, f"File too small: {ast['lineCount']} lines"
    assert ast["elementCount"] > 15, f"Too few elements: {ast['elementCount']}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md:44, js/README.md:65
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:44, js/README.md:65 @ 7760161258abe6329b754dd6d2511fc3b61fed95
def test_prettier_formatting():
    """Frontend code is formatted with prettier (AGENTS.md line 44)."""
    # Use the project's pnpm format:check for consistency with CI
    r = subprocess.run(
        ["bash", "-c",
         f"corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm prettier --check --plugin prettier-plugin-svelte --config .config/.prettierrc.json --ignore-path .config/.prettierignore {HEADER}"],
        capture_output=True, text=True, timeout=60,
        cwd=REPO, env={**os.environ, "NODE_PATH": f"{SVELTE_TOOLS}/node_modules"},
    )
    assert r.returncode == 0, f"File does not pass prettier:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — CI workflow: .github/workflows/tests-js.yml
# AGENTS.md requires "pnpm format:check" to pass
# This test ensures the gold patch doesn't break repo-wide formatting rules.
def test_repo_format_check():
    """Repo-wide frontend formatting check (pnpm format:check) passes."""
    # Install dependencies and run format check
    r = subprocess.run(
        ["bash", "-c",
         "corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm format:check"],
        capture_output=True, text=True, timeout=120,
        cwd=REPO, env={**os.environ, "NODE_PATH": f"{SVELTE_TOOLS}/node_modules"},
    )
    assert r.returncode == 0, f"pnpm format:check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
