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

import re
from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence and module structure
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_new_module_registered():
    """biome_html_syntax::lib.rs must declare the new directive_ext module."""
    lib_rs = Path(f"{REPO}/crates/biome_html_syntax/src/lib.rs").read_text()
    assert "mod directive_ext" in lib_rs, \
        "lib.rs should declare mod directive_ext"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_directive_ext_initializer():
    """directive_ext.rs must provide initializer() covering all 8 Svelte directive types."""
    directive_ext = Path(f"{REPO}/crates/biome_html_syntax/src/directive_ext.rs")
    assert directive_ext.exists(), "directive_ext.rs must exist"
    content = directive_ext.read_text()

    # Must define initializer() method on AnySvelteDirective
    assert "pub fn initializer" in content, \
        "AnySvelteDirective must have a public initializer() method"
    assert "HtmlAttributeInitializerClause" in content, \
        "initializer() must return HtmlAttributeInitializerClause"

    # Must handle all 8 Svelte directive variants
    expected_variants = [
        "SvelteBindDirective",
        "SvelteTransitionDirective",
        "SvelteInDirective",
        "SvelteOutDirective",
        "SvelteUseDirective",
        "SvelteAnimateDirective",
        "SvelteStyleDirective",
        "SvelteClassDirective",
    ]
    for variant in expected_variants:
        assert variant in content, \
            f"initializer() must handle {variant}"


# [pr_diff] fail_to_pass
def test_vue_directive_tracking():
    """html.rs must parse all 4 Vue directive variants as embedded JS."""
    html_rs = Path(f"{REPO}/crates/biome_service/src/file_handlers/html.rs").read_text()

    # Must handle all 4 Vue directive types
    vue_types = [
        "VueVOnShorthandDirective",     # @click
        "VueVBindShorthandDirective",    # :prop
        "VueVSlotShorthandDirective",    # #slot
        "VueDirective",                  # v-if, v-show, etc.
    ]
    for vue_type in vue_types:
        assert f"{vue_type}::cast_ref" in html_rs, \
            f"html.rs must cast {vue_type}"

    # Must use EmbeddingKind::Vue for all Vue directive handling
    assert html_rs.count("EmbeddingKind::Vue") >= 4, \
        "Each Vue directive handler should use EmbeddingKind::Vue"

    # Must call initializer() on directives
    assert "directive.initializer()" in html_rs, \
        "Must extract initializer from directive to get the value"

    # Must call parse_directive_string_value for Vue directives
    assert "parse_directive_string_value" in html_rs, \
        "Must use parse_directive_string_value to extract Vue directive JS"


# [pr_diff] fail_to_pass
def test_svelte_directive_tracking():
    """html.rs must parse Svelte directives (bind:, class:, etc.) as embedded JS."""
    html_rs = Path(f"{REPO}/crates/biome_service/src/file_handlers/html.rs").read_text()

    # Must handle AnySvelteDirective
    assert "AnySvelteDirective::cast_ref" in html_rs, \
        "html.rs must cast AnySvelteDirective"

    # Must use EmbeddingKind::Svelte
    assert "EmbeddingKind::Svelte" in html_rs, \
        "Must use EmbeddingKind::Svelte for Svelte directives"

    # Must call initializer() on the directive
    assert "directive.initializer()" in html_rs, \
        "Must extract initializer from Svelte directive"

    # Must use parse_directive_text_expression for Svelte directives
    assert "parse_directive_text_expression" in html_rs, \
        "Must use parse_directive_text_expression to extract Svelte directive JS"


# [pr_diff] fail_to_pass
def test_parse_directive_helpers():
    """parse_directive_string_value and parse_directive_text_expression must exist with correct logic."""
    html_rs = Path(f"{REPO}/crates/biome_service/src/file_handlers/html.rs").read_text()

    # parse_directive_string_value: for Vue (quoted strings)
    assert "fn parse_directive_string_value" in html_rs, \
        "parse_directive_string_value function must exist"
    assert "inner_string_text()" in html_rs, \
        "parse_directive_string_value must use inner_string_text() to strip quotes"
    assert "TextSize::from(1)" in html_rs, \
        "Must offset by 1 for the opening quote character"

    # parse_directive_text_expression: for Svelte (curly braces)
    assert "fn parse_directive_text_expression" in html_rs, \
        "parse_directive_text_expression function must exist"
    assert "as_html_attribute_single_text_expression" in html_rs, \
        "Must extract text expression from Svelte directive value"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_biome_developer_skill_created():
    """.claude/skills/biome-developer/SKILL.md must exist with key content."""
    skill_path = Path(f"{REPO}/.claude/skills/biome-developer/SKILL.md")
    assert skill_path.exists(), "biome-developer/SKILL.md must exist"
    content = skill_path.read_text()

    # Must have frontmatter with correct name
    assert "name: biome-developer" in content, \
        "SKILL.md must have correct frontmatter name"

    # Must cover key topics relevant to the fix
    assert "inner_string_text" in content, \
        "Skill must document inner_string_text() for string extraction"
    assert "quick_test" in content, \
        "Skill must reference quick_test for AST inspection"
    assert "EmbeddingKind" in content, \
        "Skill must cover embedded language handling with EmbeddingKind"

    # Must have the common gotchas section
    assert "Common Gotchas" in content or "Common API Confusion" in content, \
        "Skill must include common gotchas or API confusion sections"


# [pr_diff] fail_to_pass
def test_agents_md_updated():
    """AGENTS.md must include new do's and don'ts about AST inspection and legacy syntax."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()

    # New "don't" rules
    assert "widely used" in agents_md.lower() and "without evidence" in agents_md.lower(), \
        "AGENTS.md must warn against claiming patterns are 'widely used' without evidence"
    assert "legacy" in agents_md.lower() and "deprecated" in agents_md.lower(), \
        "AGENTS.md must warn against implementing legacy/deprecated syntax without checking"

    # New "do" rules
    assert "quick_test" in agents_md or "Inspect AST" in agents_md or "inspect" in agents_md.lower(), \
        "AGENTS.md must recommend inspecting AST structure before implementing"
    assert ".claude/skills/" in agents_md, \
        "AGENTS.md must reference skills directory for implementation details"


# [pr_diff] fail_to_pass
def test_testing_codegen_skill_updated():
    """testing-codegen SKILL.md must include parser quick test section."""
    skill_path = Path(f"{REPO}/.claude/skills/testing-codegen/SKILL.md")
    content = skill_path.read_text()

    # Must have parser quick test section
    assert "Quick Test for Parser" in content or "Parser Development" in content, \
        "testing-codegen SKILL.md must have parser quick test section"

    # Must mention just qt command
    assert "just qt" in content, \
        "Must document 'just qt' command for quick test"

    # Must mention biome_html_parser for HTML/embedded language work
    assert "biome_html_parser" in content, \
        "Must reference biome_html_parser for HTML/embedded language testing"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_directive_ext_not_stub():
    """directive_ext.rs must have real match arms, not just return None."""
    content = Path(f"{REPO}/crates/biome_html_syntax/src/directive_ext.rs").read_text()
    # Count match arms — should have all 8 Svelte directive variants
    match_arms = content.count(".value().ok()?.initializer()")
    assert match_arms >= 8, \
        f"directive_ext.rs must have 8 match arms (has {match_arms}) — not a stub"
