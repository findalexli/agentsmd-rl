"""
Task: gradio-docs-table-styling
Repo: gradio-app/gradio @ e8dadd648483b6016913a9b7fa2580dbc08cb823
PR:   N/A (synthetic — adds general-purpose table CSS to docs stylesheet)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/gradio"
STYLE_FILE = Path(REPO) / "js/_website/src/lib/assets/style.css"

# ---------------------------------------------------------------------------
# CSS parsing helpers
# ---------------------------------------------------------------------------

def extract_rules(css: str) -> list[dict]:
    """Extract top-level CSS rules (selector → body)."""
    rules = []
    depth = 0
    start = -1
    sel_start = 0
    i = 0
    while i < len(css):
        # Skip comments
        if css[i] == "/" and i + 1 < len(css) and css[i + 1] == "*":
            end = css.find("*/", i + 2)
            if end != -1:
                i = end + 2
                continue
        if css[i] == "{":
            if depth == 0:
                start = i
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0 and start != -1:
                selector = css[sel_start:start].strip()
                body = css[start + 1 : i].strip()
                rules.append({"selector": selector, "body": body})
                sel_start = i + 1
        i += 1
    return rules


def get_properties(body: str) -> dict[str, str]:
    """Extract CSS property: value pairs from a rule body."""
    props = {}
    for m in re.finditer(r"([\w-]+)\s*:\s*([^;{}]+);", body):
        props[m.group(1).lower()] = m.group(2).strip()
    return props


def targets_element(selector: str, element: str) -> bool:
    parts = re.split(r"[\s>]+", selector.strip())
    return any(p == element or p.endswith(element) for p in parts)


def is_dark_mode(selector: str) -> bool:
    return bool(re.search(r"\.dark\b", selector) or
                re.search(r"\[data-theme.*dark\]", selector) or
                re.search(r"prefers-color-scheme:\s*dark", selector))


def is_general_purpose(selector: str) -> bool:
    """Reject selectors scoped under existing .obj or .max-h-96 containers."""
    return ".obj" not in selector and ".max-h-96" not in selector


VALID_COLOR_RE = re.compile(
    r"^(#[0-9a-fA-F]{3,8}|"
    r"(rgb|hsl)a?\s*\(.*\)|"
    r"var\s*\(.*\)|"
    r"[a-z]+)$"
)

VALID_SIZE_RE = re.compile(
    r"^(-?\d+(\.\d+)?(px|rem|em|%|vh|vw|vmin|vmax|pt|cm|mm|in|ch|ex)|"
    r"0|auto|inherit|initial|unset|var\s*\(.*\)|calc\s*\(.*\))$"
)


def is_valid_color(val: str) -> bool:
    val = val.strip().lower()
    return bool(VALID_COLOR_RE.match(val))


def is_valid_size(val: str) -> bool:
    return all(bool(VALID_SIZE_RE.match(p)) for p in val.strip().split())


def is_valid_border(val: str) -> bool:
    val = val.strip().lower()
    if val in ("none", "inherit", "initial"):
        return True
    if val.startswith("var("):
        return True
    styles = {"solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"}
    if any(s in val for s in styles):
        return True
    if re.search(r"\d+(px|rem|em)", val):
        return True
    return False


def _all_rules() -> list[dict]:
    """Parse all CSS rules, including nested ones (e.g. inside @media)."""
    css = STYLE_FILE.read_text()
    top = extract_rules(css)
    result = list(top)
    for r in top:
        if "{" in r["body"]:
            for inner in extract_rules(r["body"]):
                result.append({
                    "selector": r["selector"] + " " + inner["selector"],
                    "body": inner["body"],
                })
    return result


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_general_table_rules_added():
    """At least one general-purpose rule targeting table/th/td must exist."""
    rules = _all_rules()
    found = any(
        is_general_purpose(r["selector"])
        and (targets_element(r["selector"], "table")
             or targets_element(r["selector"], "th")
             or targets_element(r["selector"], "td"))
        for r in rules
    )
    assert found, "No general-purpose table/th/td rules found in stylesheet"


# [pr_diff] fail_to_pass
def test_table_base_styles():
    """Table must have border-collapse (collapse|separate) and a valid width."""
    rules = _all_rules()
    found = False
    for r in rules:
        if not targets_element(r["selector"], "table"):
            continue
        if not is_general_purpose(r["selector"]):
            continue
        props = get_properties(r["body"])
        bc = props.get("border-collapse", "")
        w = props.get("width", "")
        if bc in ("collapse", "separate") and is_valid_size(w):
            found = True
            break
    assert found, "No general-purpose table rule with valid border-collapse and width"


# [pr_diff] fail_to_pass
def test_table_header_styles():
    """Table headers must have a valid background color and padding."""
    rules = _all_rules()
    found = False
    for r in rules:
        if not (targets_element(r["selector"], "th") or targets_element(r["selector"], "thead")):
            continue
        if is_dark_mode(r["selector"]):
            continue
        if not is_general_purpose(r["selector"]):
            continue
        props = get_properties(r["body"])
        bg = props.get("background-color") or props.get("background")
        pad = props.get("padding") or props.get("padding-left") or props.get("padding-top")
        if bg and is_valid_color(bg) and pad and is_valid_size(pad):
            found = True
            break
    assert found, "No general-purpose light-mode table header rule with valid background + padding"


# [pr_diff] fail_to_pass
def test_table_cell_styles():
    """Table cells must have valid padding and border."""
    rules = _all_rules()
    found = False
    for r in rules:
        if not targets_element(r["selector"], "td"):
            continue
        if is_dark_mode(r["selector"]):
            continue
        if not is_general_purpose(r["selector"]):
            continue
        props = get_properties(r["body"])
        pad = props.get("padding") or props.get("padding-left") or props.get("padding-top")
        border = (props.get("border") or props.get("border-bottom")
                  or props.get("border-top") or props.get("border-left"))
        if pad and is_valid_size(pad) and border and is_valid_border(border):
            found = True
            break
    assert found, "No general-purpose light-mode table cell rule with valid padding + border"


# [pr_diff] fail_to_pass
def test_dark_mode_header():
    """Dark mode must style table headers (background or color)."""
    rules = _all_rules()
    found = False
    for r in rules:
        if not (targets_element(r["selector"], "th") or targets_element(r["selector"], "thead")):
            continue
        if not is_dark_mode(r["selector"]):
            continue
        props = get_properties(r["body"])
        bg = props.get("background-color") or props.get("background")
        color = props.get("color")
        if (bg and is_valid_color(bg)) or (color and is_valid_color(color)):
            found = True
            break
    assert found, "No dark-mode table header styling found"


# [pr_diff] fail_to_pass
def test_dark_mode_cell():
    """Dark mode must style table cells (border or color)."""
    rules = _all_rules()
    found = False
    for r in rules:
        if not targets_element(r["selector"], "td"):
            continue
        if not is_dark_mode(r["selector"]):
            continue
        props = get_properties(r["body"])
        border = (props.get("border") or props.get("border-bottom")
                  or props.get("border-top") or props.get("border-left"))
        color = props.get("color")
        if (border and is_valid_border(border)) or (color and is_valid_color(color)):
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
