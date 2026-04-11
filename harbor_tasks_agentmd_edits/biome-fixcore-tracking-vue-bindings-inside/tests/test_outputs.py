"""
Task: biome-fixcore-tracking-vue-bindings-inside
Repo: biomejs/biome @ c047e86583434beb33ed4fb0b49e627d26a8afbd
PR:   9053

Fix Vue/Svelte directive variable tracking so variables used inside directive
attributes (e.g. @click="handler", bind:value={x}) are recognized as used.
Also adds biome-developer skill and updates AGENTS.md + testing-codegen SKILL.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence and module structure
# ---------------------------------------------------------------------------


def test_new_module_registered():
    """biome_html_syntax::lib.rs must declare the new directive_ext module."""
    lib_rs = Path(f"{REPO}/crates/biome_html_syntax/src/lib.rs").read_text()
    assert "mod directive_ext" in lib_rs, \
        "lib.rs should declare mod directive_ext"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests via subprocess
# ---------------------------------------------------------------------------


def test_directive_ext_initializer():
    """directive_ext.rs implements initializer() with a complete match over all 8 Svelte directive variants."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/crates/biome_html_syntax/src/directive_ext.rs').read()

# Must define the initializer method
if 'pub fn initializer' not in content:
    print("FAIL: No pub fn initializer method found")
    sys.exit(1)

# Must return HtmlAttributeInitializerClause
if 'HtmlAttributeInitializerClause' not in content:
    print("FAIL: Missing HtmlAttributeInitializerClause return type")
    sys.exit(1)

# Extract the match self block
match_block = re.search(r'match self \{(.*?)\}', content, re.DOTALL)
if not match_block:
    print("FAIL: No 'match self' block found")
    sys.exit(1)

arms_text = match_block.group(1)

# All 8 expected Svelte directive variants
expected = {
    'SvelteBindDirective', 'SvelteTransitionDirective', 'SvelteInDirective',
    'SvelteOutDirective', 'SvelteUseDirective', 'SvelteAnimateDirective',
    'SvelteStyleDirective', 'SvelteClassDirective',
}

# Extract variant names from match arms
variants = set(re.findall(r'Self::(\w+)\(', arms_text))
if variants != expected:
    missing = expected - variants
    extra = variants - expected
    parts = []
    if missing:
        parts.append(f"Missing variants: {missing}")
    if extra:
        parts.append(f"Unexpected variants: {extra}")
    print("FAIL: " + "; ".join(parts))
    sys.exit(1)

# Every arm must chain .value().ok()?.initializer()
if arms_text.count('.value().ok()?.initializer()') < 8:
    print("FAIL: Not all match arms call .value().ok()?.initializer()")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"directive_ext check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_vue_directive_tracking():
    """html.rs parses all 4 Vue directive types with cast_ref, initializer extraction, and EmbeddingKind::Vue."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/crates/biome_service/src/file_handlers/html.rs').read()

# 1) Imports — all 4 Vue directive types must be imported
import_block = re.search(r'use biome_html_syntax::\{([^}]+)\}', content)
if not import_block:
    print("FAIL: No biome_html_syntax import block found")
    sys.exit(1)

imports_text = import_block.group(1)
required_types = [
    'VueDirective',
    'VueVOnShorthandDirective',
    'VueVBindShorthandDirective',
    'VueVSlotShorthandDirective',
]
for t in required_types:
    if t not in imports_text:
        print(f"FAIL: Missing import for {t}")
        sys.exit(1)

# Also need TextSize import
if 'TextSize' not in content:
    print("FAIL: Missing TextSize import (needed for offset calculation)")
    sys.exit(1)

# 2) Each type must be cast with ::cast_ref
for t in required_types:
    if f'{t}::cast_ref' not in content:
        print(f"FAIL: No {t}::cast_ref call found")
        sys.exit(1)

# 3) Must call directive.initializer() to get the value clause
if 'directive.initializer()' not in content:
    print("FAIL: Must call directive.initializer() to extract Vue directive value")
    sys.exit(1)

# 4) Must use EmbeddingKind::Vue (at least once per directive type = 4)
vue_count = content.count('EmbeddingKind::Vue')
if vue_count < 4:
    print(f"FAIL: Expected >= 4 EmbeddingKind::Vue, got {vue_count}")
    sys.exit(1)

# 5) Must call parse_directive_string_value for Vue directives
if 'parse_directive_string_value' not in content:
    print("FAIL: Missing parse_directive_string_value function for Vue directives")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Vue tracking check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_svelte_directive_tracking():
    """html.rs parses AnySvelteDirective with initializer extraction and EmbeddingKind::Svelte."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/crates/biome_service/src/file_handlers/html.rs').read()

# 1) AnySvelteDirective must be imported
import_block = re.search(r'use biome_html_syntax::\{([^}]+)\}', content)
if not import_block or 'AnySvelteDirective' not in import_block.group(1):
    print("FAIL: Missing AnySvelteDirective import")
    sys.exit(1)

# 2) Must use AnySvelteDirective::cast_ref to match directives
if 'AnySvelteDirective::cast_ref' not in content:
    print("FAIL: No AnySvelteDirective::cast_ref call found")
    sys.exit(1)

# 3) Must use EmbeddingKind::Svelte
if 'EmbeddingKind::Svelte' not in content:
    print("FAIL: Missing EmbeddingKind::Svelte for Svelte directives")
    sys.exit(1)

# 4) Must call directive.initializer() to get value from directive
if 'directive.initializer()' not in content:
    print("FAIL: Must call directive.initializer() on Svelte directive")
    sys.exit(1)

# 5) Must use parse_directive_text_expression for Svelte (curly brace syntax)
if 'parse_directive_text_expression' not in content:
    print("FAIL: Missing parse_directive_text_expression for Svelte directives")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Svelte tracking check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_parse_directive_helpers():
    """parse_directive_string_value and parse_directive_text_expression have correct signatures and internal logic."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys

content = open('/workspace/biome/crates/biome_service/src/file_handlers/html.rs').read()

# --- parse_directive_string_value (Vue: extracts from quoted strings) ---
fn1 = re.search(
    r'fn parse_directive_string_value\((.*?)\)\s*->\s*Option<',
    content, re.DOTALL,
)
if not fn1:
    print("FAIL: parse_directive_string_value function not found")
    sys.exit(1)

# Takes HtmlAttributeInitializerClause parameter
if 'HtmlAttributeInitializerClause' not in fn1.group(1):
    print("FAIL: parse_directive_string_value must take HtmlAttributeInitializerClause param")
    sys.exit(1)

# Must use inner_string_text() to strip quotes
if 'inner_string_text()' not in content:
    print("FAIL: Must use inner_string_text() to extract quoted string content")
    sys.exit(1)

# Must offset by TextSize::from(1) for opening quote
if 'TextSize::from(1)' not in content:
    print("FAIL: Must offset by TextSize::from(1) for opening quote character")
    sys.exit(1)

# --- parse_directive_text_expression (Svelte: extracts from curly braces) ---
fn2 = re.search(
    r'fn parse_directive_text_expression\((.*?)\)\s*->\s*Option<',
    content, re.DOTALL,
)
if not fn2:
    print("FAIL: parse_directive_text_expression function not found")
    sys.exit(1)

if 'HtmlAttributeInitializerClause' not in fn2.group(1):
    print("FAIL: parse_directive_text_expression must take HtmlAttributeInitializerClause param")
    sys.exit(1)

# Must extract as_html_attribute_single_text_expression
if 'as_html_attribute_single_text_expression' not in content:
    print("FAIL: Must use as_html_attribute_single_text_expression for Svelte values")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Directive helpers check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------


def test_biome_developer_skill_created():
    """.claude/skills/biome-developer/SKILL.md must exist with frontmatter and key content."""
    skill_path = Path(f"{REPO}/.claude/skills/biome-developer/SKILL.md")
    assert skill_path.exists(), "biome-developer/SKILL.md must exist"
    content = skill_path.read_text()

    assert "name: biome-developer" in content, \
        "SKILL.md must have correct frontmatter name"
    assert "inner_string_text" in content, \
        "Skill must document inner_string_text() for string extraction"
    assert "quick_test" in content, \
        "Skill must reference quick_test for AST inspection"
    assert "EmbeddingKind" in content, \
        "Skill must cover embedded language handling with EmbeddingKind"
    assert "Common Gotchas" in content or "Common API Confusion" in content, \
        "Skill must include common gotchas or API confusion sections"


def test_agents_md_updated():
    """AGENTS.md must include new do's and don'ts about AST inspection and legacy syntax."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()

    assert "widely used" in agents_md.lower() and "without evidence" in agents_md.lower(), \
        "AGENTS.md must warn against claiming patterns are 'widely used' without evidence"
    assert "legacy" in agents_md.lower() and "deprecated" in agents_md.lower(), \
        "AGENTS.md must warn against implementing legacy/deprecated syntax without checking"
    assert "quick_test" in agents_md or "Inspect AST" in agents_md or "inspect" in agents_md.lower(), \
        "AGENTS.md must recommend inspecting AST structure before implementing"
    assert ".claude/skills/" in agents_md, \
        "AGENTS.md must reference skills directory for implementation details"


def test_testing_codegen_skill_updated():
    """testing-codegen SKILL.md must include parser quick test section with just qt and biome_html_parser."""
    skill_path = Path(f"{REPO}/.claude/skills/testing-codegen/SKILL.md")
    content = skill_path.read_text()

    assert "Quick Test for Parser" in content or "Parser Development" in content, \
        "testing-codegen SKILL.md must have parser quick test section"
    assert "just qt" in content, \
        "Must document 'just qt' command for quick test"
    assert "biome_html_parser" in content, \
        "Must reference biome_html_parser for HTML/embedded language testing"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub and code quality
# ---------------------------------------------------------------------------


def test_directive_ext_not_stub():
    """directive_ext.rs must have real match arms, not just return None."""
    content = Path(f"{REPO}/crates/biome_html_syntax/src/directive_ext.rs").read_text()
    match_arms = content.count(".value().ok()?.initializer()")
    assert match_arms >= 8, \
        f"directive_ext.rs must have 8 match arms (has {match_arms}) — not a stub"


def test_markdown_table_formatting():
    """SKILL.md files must use proper markdown table formatting with spaces around separators (pass_to_pass)."""
    import re

    # Check biome-developer SKILL.md for proper table formatting
    skill_path = Path(f"{REPO}/.claude/skills/biome-developer/SKILL.md")
    if skill_path.exists():
        content = skill_path.read_text()
        # Check for proper table separator format: | --- | --- | --- |
        # Not: |---|---|---| (without spaces)
        bad_tables = re.findall(r'\|[-]+\|', content)
        if bad_tables:
            assert False, f"Found improperly formatted markdown tables (missing spaces): {bad_tables[:3]}"

    # Check testing-codegen SKILL.md
    testing_skill_path = Path(f"{REPO}/.claude/skills/testing-codegen/SKILL.md")
    if testing_skill_path.exists():
        content = testing_skill_path.read_text()
        bad_tables = re.findall(r'\|[-]+\|', content)
        if bad_tables:
            assert False, f"Found improperly formatted markdown tables in testing-codegen (missing spaces): {bad_tables[:3]}"


def test_vue_svelte_test_specs_exist():
    """Vue and Svelte test spec files must exist in the HTML parser tests (pass_to_pass)."""
    import os

    # Check that Vue test specs exist
    vue_ok_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/ok/vue")
    vue_error_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/error/vue")

    vue_ok_count = len(list(vue_ok_dir.glob("*.vue"))) if vue_ok_dir.exists() else 0
    vue_error_count = len(list(vue_error_dir.glob("*.vue"))) if vue_error_dir.exists() else 0

    assert vue_ok_count >= 3, f"Expected at least 3 Vue ok test specs, found {vue_ok_count}"
    assert vue_error_count >= 3, f"Expected at least 3 Vue error test specs, found {vue_error_count}"

    # Check that Svelte test specs exist
    svelte_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/error/svelte")
    svelte_ok_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/ok/svelte")

    svelte_error_count = len(list(svelte_dir.glob("*.svelte"))) if svelte_dir.exists() else 0
    svelte_ok_count = len(list(svelte_ok_dir.glob("*.svelte"))) if svelte_ok_dir.exists() else 0

    # Svelte error specs should exist (the PR adds directive tracking for Svelte)
    assert svelte_error_count >= 5, f"Expected at least 5 Svelte error test specs, found {svelte_error_count}"


def test_lib_rs_module_declaration():
    """biome_html_syntax::lib.rs uses proper module declaration style (pass_to_pass)."""
    import re

    lib_rs = Path(f"{REPO}/crates/biome_html_syntax/src/lib.rs").read_text()

    # Check that mod directive_ext is declared (it will exist after the patch)
    # But also verify the existing style pattern for other modules
    # Look for 'mod module_name;' declarations without braces (inline modules)
    inline_mods = re.findall(r'^mod\s+(\w+)\s*;', lib_rs, re.MULTILINE)

    # At least some modules should be declared this way
    assert len(inline_mods) >= 1, "lib.rs should have inline module declarations"

    # Check for proper file structure - modules declared as 'mod name;' style
    # (as opposed to 'mod name { ... }' inline modules)
    brace_mods = re.findall(r'^mod\s+\w+\s*\{', lib_rs, re.MULTILINE)
    # There shouldn't be many inline brace-style modules in this file
    assert len(brace_mods) <= 2, f"Expected <=2 inline brace modules, found {len(brace_mods)}"
