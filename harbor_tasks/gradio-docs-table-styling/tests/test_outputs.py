"""
Task: gradio-docs-table-styling
Repo: gradio-app/gradio @ e8dadd648483b6016913a9b7fa2580dbc08cb823
PR:   N/A (synthetic — adds general-purpose table CSS to docs stylesheet)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import re
from pathlib import Path

REPO = "/workspace/gradio"
STYLE_FILE = Path(REPO) / "js/_website/src/lib/assets/style.css"

# ---------------------------------------------------------------------------
# Node.js CSS parser — runs as subprocess for behavioral testing
# ---------------------------------------------------------------------------

_NODE_PARSER_BODY = r"""
function extractRules(text) {
  const rules = [];
  let depth = 0, start = -1, selStart = 0, i = 0;
  while (i < text.length) {
    if (text[i] === '/' && text[i+1] === '*') {
      const end = text.indexOf('*/', i + 2);
      i = end !== -1 ? end + 2 : text.length;
      continue;
    }
    if (text[i] === '{') {
      if (depth === 0) start = i;
      depth++;
    } else if (text[i] === '}') {
      depth--;
      if (depth === 0 && start !== -1) {
        rules.push({
          selector: text.slice(selStart, start).trim(),
          body: text.slice(start + 1, i).trim()
        });
        selStart = i + 1;
      }
    }
    i++;
  }
  return rules;
}

function getProps(body) {
  const props = {};
  for (const m of body.matchAll(/([\w-]+)\s*:\s*([^;{}]+);/g)) {
    props[m[1].toLowerCase()] = m[2].trim();
  }
  return props;
}

function extractAll(css) {
  const top = extractRules(css);
  const all = [];
  for (const r of top) {
    all.push({ selector: r.selector, body: r.body, props: getProps(r.body) });
    if (r.body.includes('{')) {
      for (const inner of extractRules(r.body)) {
        all.push({
          selector: r.selector + ' ' + inner.selector,
          body: inner.body,
          props: getProps(inner.body)
        });
      }
    }
  }
  return all;
}

console.log(JSON.stringify(extractAll(css)));
"""


def _get_rules() -> list[dict]:
    """Parse CSS rules via Node.js subprocess and return structured data."""
    style_path = str(STYLE_FILE)
    header = (
        "const fs = require('fs');\n"
        f"const css = fs.readFileSync({style_path!r}, 'utf8');\n"
    )
    script = header + _NODE_PARSER_BODY
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"CSS parse failed: {r.stderr}"
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _targets_element(selector: str, element: str) -> bool:
    parts = re.split(r"[\s>]+", selector.strip())
    return any(p == element or p.endswith(element) for p in parts)


def _is_dark_mode(selector: str) -> bool:
    return bool(re.search(r"\.dark\b", selector))


def _is_general_purpose(selector: str) -> bool:
    return ".obj" not in selector and ".max-h-96" not in selector


def _is_valid_color(val: str) -> bool:
    return bool(re.match(
        r"^(#[0-9a-fA-F]{3,8}|(rgb|hsl)a?\s*\(.*\)|var\s*\(.*\)|[a-z]+)$",
        val.strip().lower()
    ))


def _is_valid_size(val: str) -> bool:
    return all(bool(re.match(
        r"^(-?\d+(\.\d+)?(px|rem|em|%|vh|vw|vmin|vmax|pt|cm|mm|in|ch|ex)|"
        r"0|auto|inherit|initial|unset|var\s*\(.*\)|calc\s*\(.*\))$",
        p.strip()
    )) for p in val.strip().split())


def _is_valid_border(val: str) -> bool:
    val = val.strip().lower()
    if val in ("none", "inherit", "initial") or val.startswith("var("):
        return True
    styles = {"solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"}
    return bool(any(s in val for s in styles) or re.search(r"\d+(px|rem|em)", val))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_general_table_rules_added():
    """At least one general-purpose rule targeting table/th/td must exist."""
    rules = _get_rules()
    found = any(
        _is_general_purpose(r["selector"])
        and (_targets_element(r["selector"], "table")
             or _targets_element(r["selector"], "th")
             or _targets_element(r["selector"], "td"))
        for r in rules
    )
    assert found, "No general-purpose table/th/td rules found in stylesheet"


# [pr_diff] fail_to_pass
def test_table_base_styles():
    """Table must have border-collapse (collapse|separate) and a valid width."""
    rules = _get_rules()
    found = False
    for r in rules:
        if not _targets_element(r["selector"], "table"):
            continue
        if not _is_general_purpose(r["selector"]):
            continue
        p = r["props"]
        bc = p.get("border-collapse", "")
        w = p.get("width", "")
        if bc in ("collapse", "separate") and _is_valid_size(w):
            found = True
            break
    assert found, "No general-purpose table rule with valid border-collapse and width"


# [pr_diff] fail_to_pass
def test_table_header_styles():
    """Table headers must have a valid background color and padding."""
    rules = _get_rules()
    found = False
    for r in rules:
        if not (_targets_element(r["selector"], "th") or _targets_element(r["selector"], "thead")):
            continue
        if _is_dark_mode(r["selector"]):
            continue
        if not _is_general_purpose(r["selector"]):
            continue
        p = r["props"]
        bg = p.get("background-color") or p.get("background")
        pad = p.get("padding") or p.get("padding-left") or p.get("padding-top")
        if bg and _is_valid_color(bg) and pad and _is_valid_size(pad):
            found = True
            break
    assert found, "No general-purpose light-mode table header rule with valid background + padding"


# [pr_diff] fail_to_pass
def test_table_cell_styles():
    """Table cells must have valid padding and border."""
    rules = _get_rules()
    found = False
    for r in rules:
        if not _targets_element(r["selector"], "td"):
            continue
        if _is_dark_mode(r["selector"]):
            continue
        if not _is_general_purpose(r["selector"]):
            continue
        p = r["props"]
        pad = p.get("padding") or p.get("padding-left") or p.get("padding-top")
        border = (p.get("border") or p.get("border-bottom")
                  or p.get("border-top") or p.get("border-left"))
        if pad and _is_valid_size(pad) and border and _is_valid_border(border):
            found = True
            break
    assert found, "No general-purpose light-mode table cell rule with valid padding + border"


# [pr_diff] fail_to_pass
def test_dark_mode_header():
    """Dark mode must style table headers (background or color)."""
    rules = _get_rules()
    found = False
    for r in rules:
        if not (_targets_element(r["selector"], "th") or _targets_element(r["selector"], "thead")):
            continue
        if not _is_dark_mode(r["selector"]):
            continue
        p = r["props"]
        bg = p.get("background-color") or p.get("background")
        color = p.get("color")
        if (bg and _is_valid_color(bg)) or (color and _is_valid_color(color)):
            found = True
            break
    assert found, "No dark-mode table header styling found"


# [pr_diff] fail_to_pass
def test_dark_mode_cell():
    """Dark mode must style table cells (border or color)."""
    rules = _get_rules()
    found = False
    for r in rules:
        if not _targets_element(r["selector"], "td"):
            continue
        if not _is_dark_mode(r["selector"]):
            continue
        p = r["props"]
        border = (p.get("border") or p.get("border-bottom")
                  or p.get("border-top") or p.get("border-left"))
        color = p.get("color")
        if (border and _is_valid_border(border)) or (color and _is_valid_color(color)):
            found = True
            break
    assert found, "No dark-mode table cell styling found"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_css_syntax_valid():
    """CSS file must have balanced braces (no broken syntax)."""
    css = STYLE_FILE.read_text()
    depth = 0
    in_comment = False
    i = 0
    while i < len(css):
        if not in_comment and i + 1 < len(css) and css[i] == "/" and css[i + 1] == "*":
            in_comment = True
            i += 2
            continue
        if in_comment and i + 1 < len(css) and css[i] == "*" and css[i + 1] == "/":
            in_comment = False
            i += 2
            continue
        if in_comment:
            i += 1
            continue
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
        assert depth >= 0, f"Unmatched closing brace at position {i}"
        i += 1
    assert depth == 0, f"Unmatched opening braces: depth={depth}"


# [repo_tests] pass_to_pass
def test_existing_scoped_dark_styles():
    """Existing .obj scoped dark table styles must not be removed."""
    css = STYLE_FILE.read_text()
    assert ".dark .obj .max-h-96.overflow-y-scroll table tbody td" in css, \
        "Existing scoped dark td styles were removed"
    assert ".dark .obj .max-h-96.overflow-y-scroll table tbody th" in css, \
        "Existing scoped dark th styles were removed"


# [repo_tests] pass_to_pass
def test_existing_summary_styles():
    """Existing summary::after styles must not be removed."""
    css = STYLE_FILE.read_text()
    assert "summary::after" in css, "Existing summary::after styles were removed"


# [static] pass_to_pass
def test_file_not_truncated():
    """CSS file must not be trivially small (anti-stub)."""
    line_count = len(STYLE_FILE.read_text().splitlines())
    assert line_count > 480, f"File suspiciously small ({line_count} lines, expected >480)"


# [repo_tests] pass_to_pass — CSS parseable with Node.js
def test_css_parseable_nodejs():
    """CSS file must be parseable by Node.js-based parser (no syntax errors)."""
    # This uses the same _get_rules() helper used by fail_to_pass tests
    rules = _get_rules()
    assert len(rules) > 50, f"CSS has suspiciously few rules ({len(rules)}, expected >50)"


# [repo_tests] pass_to_pass — Node.js available for CSS validation
def test_nodejs_available():
    """Node.js must be available for CSS parsing (CI environment check)."""
    r = subprocess.run(
        ["node", "--version"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Node.js not available: {r.stderr}"
    assert "v" in r.stdout, f"Unexpected Node.js version output: {r.stdout}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — verified to work on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — CSS theme generation (CI: css)
def test_repo_css_generation():
    """CSS theme generation works (pass_to_pass).

    This mirrors the CI command: pnpm css
    Ensures the theme CSS can be generated from pollen config.
    """
    # First ensure pnpm is available
    subprocess.run(
        ["npm", "install", "-g", "pnpm@10.17.0"],
        capture_output=True, text=True, timeout=120,
    )

    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "css"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"CSS generation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Client unit tests (CI: test:client)
def test_repo_client_unit_tests():
    """Client package unit tests pass (pass_to_pass).

    This mirrors the CI command: pnpm --filter @gradio/client test
    Runs the specific client library unit tests.
    """
    # First ensure pnpm is available
    subprocess.run(
        ["npm", "install", "-g", "pnpm@10.17.0"],
        capture_output=True, text=True, timeout=120,
    )

    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    # Build client first (required for tests)
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Client library build (CI: client build)
def test_repo_client_build():
    """Repo's client library builds successfully (pass_to_pass).

    This mirrors the CI command: pnpm --filter @gradio/client build
    Ensures the client library compiles without errors.
    """
    # First ensure pnpm is available (not installed by default in container)
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.17.0"],
        capture_output=True, text=True, timeout=120,
    )
    # pnpm install may already be present, continue regardless

    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Unit tests (CI: test:run)
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass).

    This mirrors the CI command: pnpm test:run
    Ensures the existing test suite continues to pass.
    """
    # First ensure pnpm is available
    subprocess.run(
        ["npm", "install", "-g", "pnpm@10.17.0"],
        capture_output=True, text=True, timeout=120,
    )

    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    # Build client first (required for tests)
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "test:run"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo formatting with prettier (CI: format:check)
def test_repo_format_check():
    """Repo code formatting passes prettier check (pass_to_pass).

    This mirrors the CI command: pnpm format:check
    Ensures candidate solutions don't break existing formatting.
    """
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CSS file specifically passes prettier check
def test_repo_css_prettier():
    """CSS file is properly formatted with prettier (pass_to_pass).

    This verifies the specific CSS file being modified passes formatting checks.
    """
    style_path = str(STYLE_FILE)
    r = subprocess.run(
        ["npx", "prettier", "--check", "--config", ".config/.prettierrc.json", style_path],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"CSS prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — pnpm install works (basic CI env check)
def test_repo_pnpm_install():
    """pnpm install completes successfully (pass_to_pass).

    Verifies the frontend dependencies can be installed (basic CI env health).
    """
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md line 45 @ e8dadd6
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:45 @ e8dadd648483b6016913a9b7fa2580dbc08cb823
def test_tab_indentation():
    """New table CSS rules must use tab indentation (matching file convention)."""
    css = STYLE_FILE.read_text()
    lines = css.splitlines()
    table_keywords = {"table {", "table,", "thead", "tbody", ".dark table"}
    new_lines = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if any(kw in stripped for kw in table_keywords):
            in_table = True
        if in_table:
            new_lines.append(line)
        if in_table and stripped == "}":
            in_table = False

    indented = [l for l in new_lines if l != l.lstrip()]
    assert indented, "No indented lines found in table rules"
    space_indented = sum(1 for l in indented if l.startswith("  "))
    tab_indented = sum(1 for l in indented if l.startswith("\t"))
    assert tab_indented > 0 and space_indented == 0, \
        f"Expected tab indentation, found {tab_indented} tab-indented and {space_indented} space-indented lines"
