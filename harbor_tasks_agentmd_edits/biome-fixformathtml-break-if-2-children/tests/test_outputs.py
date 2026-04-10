"""
Task: biome-fixformathtml-break-if-2-children
Repo: biomejs/biome @ cb112ce872c8428414d78bc90c6ed26a102ac0e0
PR:   8833

Fix HTML formatter to correctly break a block-like element if it has more than
2 children, and at least one is not whitespace-sensitive.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — actual CI commands from the repo
# ---------------------------------------------------------------------------

def test_cargo_check():
    """Modified crates compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "biome_html_formatter"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed: {r.stderr[-500:]}"


def test_cargo_clippy():
    """Clippy lints pass for modified crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--package", "biome_html_formatter", "--", "--deny", "warnings"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Clippy failed: {r.stderr[-500:]}"


def test_cargo_fmt():
    """Code formatting passes for all files (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed: {r.stderr[-500:]}"


def test_cargo_test_lib():
    """Unit tests for modified crate pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "biome_html_formatter", "--lib"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed: {r.stderr[-500:]}"


def test_cargo_test_quick():
    """Quick test target for html_formatter passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "biome_html_formatter", "--test", "quick_test"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Quick test failed: {r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_element_list_imports_css_display():
    """element_list.rs imports CssDisplay from css_display module."""
    r = subprocess.run(
        ["python3", "-c", r"""
import sys

content = open('/workspace/biome/crates/biome_html_formatter/src/html/lists/element_list.rs').read()

# Must import CssDisplay from css_display module
if 'css_display::CssDisplay' not in content:
    print("FAIL: Missing css_display::CssDisplay import")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_block_like_element_break_logic():
    """element_list.rs handles visible block-like elements adjacent to text."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/crates/biome_html_formatter/src/html/lists/element_list.rs').read()

# Must have logic for visible block-like elements (css_display.is_block_like() && css_display != CssDisplay::None)
if 'css_display.is_block_like()' not in content:
    print("FAIL: Missing css_display.is_block_like() check")
    sys.exit(1)

if 'css_display != CssDisplay::None' not in content and 'css_display == CssDisplay::None' not in content:
    print("FAIL: Missing CssDisplay::None comparison")
    sys.exit(1)

# Must force multiline for block-like elements adjacent to text
# Check for the specific pattern: child_breaks = true; force_multiline = true;
pattern = r'child_breaks\s*=\s*true;\s*force_multiline\s*=\s*true;'
if not re.search(pattern, content):
    print("FAIL: Missing child_breaks = true; force_multiline = true; pattern")
    sys.exit(1)

# Must have the comment about Prettier behavior for cases like `<div>a<div>b</div> c</div>`
if '<div>a<div>b</div> c</div>' not in content:
    print("FAIL: Missing explanatory comment about the fix case")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_display_none_whitespace_handling():
    """element_list.rs handles display:none elements without introducing whitespace."""
    r = subprocess.run(
        ["python3", "-c", r"""
import sys

content = open('/workspace/biome/crates/biome_html_formatter/src/html/lists/element_list.rs').read()

# Must have the comment explaining display:none handling
if "display: none" not in content.lower():
    print("FAIL: Missing comment about display:none handling")
    sys.exit(1)

# Must reference the specific example: <div>123<meta attr />456</div>
if '<div>123<meta attr />456</div>' not in content:
    print("FAIL: Missing example for display:none case")
    sys.exit(1)

# Must handle CssDisplay::None case specially (empty block or specific handling)
if 'css_display == CssDisplay::None' not in content:
    print("FAIL: Missing CssDisplay::None handling")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_multiline_text_after_block():
    """element_list.rs keeps words after block-like elements on their own line when multiline."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/crates/biome_html_formatter/src/html/lists/element_list.rs').read()

# Check for the pattern that handles text after block-like elements in multiline mode
# Looking for: force_multiline && matches!(children_iter.peek(), Some(HtmlChild::Word(_)))
pattern = r'force_multiline\s*&&\s*matches!\(\s*children_iter\.peek\(\),\s*Some\(HtmlChild::Word\(_\)\)\)'
if not re.search(pattern, content):
    print("FAIL: Missing force_multiline pattern for words after block elements")
    sys.exit(1)

# Must check last_css_display.is_block_like() in this context
if 'last_css_display.is_block_like()' not in content:
    print("FAIL: Missing last_css_display.is_block_like() check")
    sys.exit(1)

# Must check last_css_display != CssDisplay::None
if 'last_css_display != CssDisplay::None' not in content:
    print("FAIL: Missing last_css_display != CssDisplay::None check")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_block_before_text_line_mode():
    """element_list.rs uses LineMode::Hard for block-like elements followed by text."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/crates/biome_html_formatter/src/html/lists/element_list.rs').read()

# Check for LineMode::Hard in the context of block-like elements
# Looking for: Some(LineMode::Hard) after block-like checks
pattern = r'Some\(LineMode::Hard\)'
if not re.search(pattern, content):
    print("FAIL: Missing Some(LineMode::Hard) for block-like elements")
    sys.exit(1)

# Must have comment about details element
if '<details><summary>' in content or 'details</details>' in content:
    print("PASS - found details element reference")
else:
    # Check for generic block-like element handling
    if 'Block-like elements followed by text should break before the text' not in content:
        print("FAIL: Missing comment about breaking before text for block elements")
        sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_css_display_comment():
    """css_display.rs has FIXME comment about display:none being whitespace sensitive."""
    r = subprocess.run(
        ["python3", "-c", r"""
import sys

content = open('/workspace/biome/crates/biome_html_formatter/src/utils/css_display.rs').read()

# Must have FIXME comment about Prettier treating display:none as whitespace sensitive
if 'FIXME' not in content:
    print("FAIL: Missing FIXME comment in css_display.rs")
    sys.exit(1)

if 'Prettier treats `display: none` as whitespace sensitive' not in content:
    print("FAIL: Missing specific FIXME comment about display:none")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

def test_prettier_compare_skill_created():
    """.claude/skills/prettier-compare/SKILL.md must exist with proper content."""
    skill_path = Path(f"{REPO}/.claude/skills/prettier-compare/SKILL.md")
    assert skill_path.exists(), "prettier-compare/SKILL.md must exist"
    content = skill_path.read_text()

    assert "name: prettier-compare" in content,         "SKILL.md must have correct frontmatter name"
    assert "prettier-compare" in content,         "Skill must reference prettier-compare"
    assert "--rebuild" in content,         "Skill must document --rebuild flag"
    assert "bun" in content,         "Skill must reference bun command"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_element_list_not_stub():
    """element_list.rs modifications have real logic, not just stubs."""
    content = Path(f"{REPO}/crates/biome_html_formatter/src/html/lists/element_list.rs").read_text()

    # Count the number of css_display checks - should be multiple
    block_like_checks = content.count("is_block_like()")
    assert block_like_checks >= 2,         f"element_list.rs should have at least 2 is_block_like() checks (has {block_like_checks})"

    # Must have hard_line_break() calls for the new logic
    hard_breaks = content.count("hard_line_break()")
    assert hard_breaks >= 3,         f"element_list.rs should have at least 3 hard_line_break() calls (has {hard_breaks})"
