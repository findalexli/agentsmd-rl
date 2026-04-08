"""
Task: gradio-block-border-inheritance
Repo: gradio-app/gradio @ 01352c78e560c3a6de728a4aec07027e96c27acc
PR:   #12933

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import json
from pathlib import Path

REPO = "/repo"
FILE = Path(REPO) / "js/atoms/src/Block.svelte"


def _read_file():
    return FILE.read_text()


def _extract_style(content: str) -> str:
    """Extract <style> block content, strip CSS comments."""
    m = re.search(r"<style[^>]*>(.*?)</style>", content, re.DOTALL)
    assert m, "No <style> block found in Block.svelte"
    return re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.DOTALL)


def _extract_rule_body(style: str, selector_pattern: str) -> str:
    """Extract the body of a CSS rule matching the selector pattern."""
    m = re.search(selector_pattern + r"\s*\{([^}]*)\}", style, re.DOTALL)
    assert m, f"No CSS rule matching {selector_pattern!r}"
    return m.group(1)


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_file_is_valid_svelte():
    """Block.svelte must exist and be a valid Svelte component."""
    content = _read_file()
    assert len(content.splitlines()) >= 100, "File too small — likely gutted"
    assert "<script" in content, "Missing <script> section"
    assert "<style" in content, "Missing <style> section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral test using subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_child_block_retains_border():
    """Simulate CSS custom property inheritance: child .block inside hide-container retains border.

    The bug: .hide-container sets --block-border-width: 0 (a CSS custom property).
    Since custom properties inherit, all descendant blocks get border-width: 0.

    The fix: .hide-container uses border-width: 0 directly (not a custom property),
    so children keep the theme-provided --block-border-width value.

    Uses Node.js to parse the CSS and template, then simulates the cascade
    to determine a child block's effective border-width.
    """
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync('/repo/js/atoms/src/Block.svelte', 'utf8');

// 1. Extract CSS from <style> block
const styleMatch = content.match(/<style[^>]*>([\s\S]*?)<\/style>/);
if (!styleMatch) {
  console.log(JSON.stringify({error: "no style block"}));
  process.exit(1);
}
const css = styleMatch[1].replace(/\/\*[\s\S]*?\*\//g, '');

// 2. Parse CSS rules into selector -> properties map
function parseRules(cssText) {
  const rules = {};
  const re = /([^{]+)\{([^}]+)\}/g;
  let m;
  while ((m = re.exec(cssText)) !== null) {
    const selector = m[1].trim();
    const body = m[2].trim();
    const props = {};
    body.split(';').forEach(function(p) {
      var idx = p.indexOf(':');
      if (idx > 0) {
        var name = p.slice(0, idx).trim();
        var value = p.slice(idx + 1).trim();
        if (name && value) props[name] = value;
      }
    });
    rules[selector] = props;
  }
  return rules;
}

var rules = parseRules(css);

// 3. Find .hide-container rule
var hideProps = {};
for (var sel of Object.keys(rules)) {
  if (sel.includes('.hide-container')) {
    hideProps = Object.assign({}, rules[sel]);
    break;
  }
}

// 4. Find .block rule (standalone, not inside hide-container selector)
var blockProps = {};
for (var sel of Object.keys(rules)) {
  if (/\b\.block(?![-\w])/.test(sel) && !sel.includes('hide')) {
    blockProps = Object.assign({}, rules[sel]);
    break;
  }
}

// 5. Parse Svelte inline style: bindings from template
var inlineStyles = {};
var inlineRe = /style:([\w-]+)\s*=\s*"([^"]*)"/g;
var im;
while ((im = inlineRe.exec(content)) !== null) {
  inlineStyles[im[1]] = im[2];
}

// 6. Simulate CSS cascade for a child .block inside .hide-container

// Does hide-container set any --block*border* custom property to 0?
var inheritedBorderVarZeroed = false;
for (var prop of Object.keys(hideProps)) {
  if (/--block.*border/i.test(prop) && hideProps[prop].trim() === '0') {
    inheritedBorderVarZeroed = true;
    break;
  }
}

// Does the child element reference --block-border-width via inline Svelte style?
var hasInlineBorderWidth = 'border-width' in inlineStyles;
var inlineBorderRef = inlineStyles['border-width'] || '';
var inlineReferencesInheritedVar = inlineBorderRef.includes('var(--block-border-width)');

// BUG SCENARIO: parent zeros inherited CSS custom property + child references it inline
if (inheritedBorderVarZeroed && hasInlineBorderWidth && inlineReferencesInheritedVar) {
  console.log(JSON.stringify({
    pass: false,
    reason: "hide-container zeros --block-border-width (inherited custom property) AND child has inline style:border-width referencing it"
  }));
  process.exit(0);
}

// FIXED SCENARIO: parent uses direct border-width: 0, not a custom property
if (!inheritedBorderVarZeroed) {
  var childHasBorder = 'border-width' in blockProps || hasInlineBorderWidth;
  if (childHasBorder) {
    console.log(JSON.stringify({
      pass: true,
      reason: "hide-container uses direct border reset, child retains border-width"
    }));
    process.exit(0);
  }
}

console.log(JSON.stringify({
  pass: false,
  reason: "Could not verify child border retention",
  debug: {hideProps: hideProps, blockProps: blockProps, inlineStyles: inlineStyles, inheritedBorderVarZeroed: inheritedBorderVarZeroed}
}));
""")
    assert r.returncode == 0, f"Node.js execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("pass"), f"Child block loses border: {data.get('reason', data)}"


# [pr_diff] fail_to_pass
def test_hide_container_no_inherited_border_var():
    """hide-container must NOT set --block-border-width CSS variable (inherits to children)."""
    content = _read_file()
    style = _extract_style(content)
    hide_body = _extract_rule_body(style, r"\.hide-container[^{]*")
    inherited_vars = re.findall(r"--block[\w-]*border[\w-]*\s*:", hide_body)
    assert not inherited_vars, (
        f"hide-container still sets inherited CSS var(s): {inherited_vars}"
    )


# [pr_diff] fail_to_pass
def test_hide_container_uses_direct_border_zero():
    """hide-container must zero its own border directly, not via inherited CSS variable."""
    content = _read_file()
    style = _extract_style(content)
    hide_body = _extract_rule_body(style, r"\.hide-container[^{]*")
    has_direct = (
        bool(re.search(r"(?<!-)border-width\s*:\s*0", hide_body))
        or bool(re.search(r"(?<!-)border\s*:\s*(?:none|0)", hide_body))
        or bool(re.search(r"(?<!-)border-style\s*:\s*none", hide_body))
    )
    assert has_direct, (
        "hide-container needs a direct border zero (border-width:0, border:none, etc.)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_hide_container_preserves_other_resets():
    """hide-container preserves its other CSS resets (margin, box-shadow, background, padding, overflow)."""
    content = _read_file()
    style = _extract_style(content)
    hide_body = _extract_rule_body(style, r"\.hide-container[^{]*")
    required = {
        "margin": r"(?<!-)margin\s*:",
        "box-shadow": r"box-shadow\s*:",
        "background": r"background\s*:",
        "padding": r"(?<!-)padding\s*:",
        "overflow": r"overflow\s*:",
    }
    missing = [name for name, pat in required.items() if not re.search(pat, hide_body)]
    assert not missing, f"hide-container missing CSS resets: {missing}"


# [pr_diff] pass_to_pass
def test_block_class_preserves_styling():
    """.block CSS class retains core visual properties (box-shadow, border-color, etc.)."""
    content = _read_file()
    style = _extract_style(content)
    block_body = _extract_rule_body(style, r"(?<!\w)\.block(?!\w)")
    required = {
        "box-shadow": r"box-shadow\s*:",
        "border-color": r"border-color\s*:",
        "border-radius": r"border-radius\s*:",
        "background": r"background\s*:",
    }
    missing = [name for name, pat in required.items() if not re.search(pat, block_body)]
    assert not missing, f".block CSS missing properties: {missing}"


# [pr_diff] pass_to_pass
def test_svelte_template_integrity():
    """Key Svelte template bindings preserved (hide-container, fullscreen, flex-grow, etc.)."""
    content = _read_file()
    required = [
        (r"class:hide-container", "class:hide-container binding"),
        (r"class:fullscreen", "class:fullscreen binding"),
        (r"style:flex-grow", "style:flex-grow binding"),
        (r"style:min-width", "style:min-width binding"),
        (r"style:overflow", "style:overflow binding"),
    ]
    missing = [desc for pat, desc in required if not re.search(pat, content)]
    assert not missing, f"Missing template bindings: {missing}"
