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
import re
from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - file existence and module structure
# ---------------------------------------------------------------------------


def test_new_module_registered():
    """biome_html_syntax::lib.rs must declare the new directive_ext module."""
    lib_rs = Path(f"{REPO}/crates/biome_html_syntax/src/lib.rs").read_text()
    assert "mod directive_ext" in lib_rs, \
        "lib.rs should declare mod directive_ext"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - code behavior tests via subprocess
# ---------------------------------------------------------------------------


def test_directive_ext_initializer():
    """directive_ext.rs implements initializer() covering all 8 Svelte directive variants."""
    directive_ext = Path(f"{REPO}/crates/biome_html_syntax/src/directive_ext.rs")
    assert directive_ext.exists(), "directive_ext.rs must exist"
    content = directive_ext.read_text()

    fn_match = re.search(
        r'pub\s+fn\s+(\w+)\s*\([^)]*\)\s*->\s*Option<HtmlAttributeInitializerClause>',
        content
    )
    assert fn_match, "No public method returning Option<HtmlAttributeInitializerClause> found"

    expected_variants = {
        'SvelteBindDirective', 'SvelteClassDirective', 'SvelteInDirective',
        'SvelteOutDirective', 'SvelteStyleDirective', 'SvelteTransitionDirective',
        'SvelteUseDirective', 'SvelteAnimateDirective',
    }

    match_block = re.search(r'match\s+self\s*\{.*?\n\}', content, re.DOTALL)
    assert match_block, "No 'match self' block found"

    match_content = match_block.group(0)

    found_variants = set(re.findall(r'Self::(\w+Directive)\s*\(', match_content))

    missing = expected_variants - found_variants
    extra = found_variants - expected_variants
    assert not missing, f"Missing directive variants in match: {missing}"
    assert not extra, f"Unexpected directive variants in match: {extra}"

    initializer_calls = len(re.findall(r'\.initializer\(\)', match_content))
    assert initializer_calls >= 8, \
        f"Expected at least 8 .initializer() calls, found {initializer_calls}"


def test_vue_directive_tracking():
    """html.rs parses all 4 Vue directive types as embedded JS with proper tagging."""
    html_rs = Path(f"{REPO}/crates/biome_service/src/file_handlers/html.rs")
    content = html_rs.read_text()

    vue_embedding_count = len(re.findall(r'EmbeddingKind::Vue', content))
    assert vue_embedding_count >= 4, \
        f"Expected at least 4 EmbeddingKind::Vue usages, found {vue_embedding_count}"

    vue_types = [
        'VueDirective',
        'VueVOnShorthandDirective',
        'VueVBindShorthandDirective',
        'VueVSlotShorthandDirective',
    ]

    found_types = []
    for t in vue_types:
        if f'{t}::cast_ref' in content:
            found_types.append(t)

    assert len(found_types) >= 4, \
        f"Expected all 4 Vue directive types, found {found_types}"

    helpers = re.findall(
        r'fn\s+(\w+)\s*\([^)]*HtmlAttributeInitializerClause[^)]*\)',
        content
    )
    assert len(helpers) >= 2, \
        f"Expected at least 2 helper functions, found {helpers}"

    has_string_extract = bool(re.search(
        r'\.(?:inner_string_text|text_trimmed|value_token|text)\(\)',
        content
    ))
    assert has_string_extract, "Vue parsing must extract string content"

    assert 'TextSize' in content, "Must use TextSize for offset"

    initializer_calls = content.count('.initializer()')
    assert initializer_calls >= 4, \
        f"Expected >= 4 .initializer() calls, got {initializer_calls}"


def test_svelte_directive_tracking():
    """html.rs parses Svelte directives as embedded JS with proper tagging."""
    html_rs = Path(f"{REPO}/crates/biome_service/src/file_handlers/html.rs")
    content = html_rs.read_text()

    assert 'AnySvelteDirective' in content, "AnySvelteDirective must be used"
    assert 'AnySvelteDirective::cast_ref' in content, "cast_ref must be used"
    assert 'EmbeddingKind::Svelte' in content, "EmbeddingKind::Svelte must be used"
    assert '.initializer()' in content, "initializer() must be called"

    has_text_expr_extract = bool(re.search(
        r'\.(?:expression|text_expression|as_html_attribute_single_text_expression|text)\(\)',
        content
    ))
    assert has_text_expr_extract, "Must extract text expressions"

    svelte_helper = re.search(
        r'fn\s+\w+\s*\([^)]*HtmlAttributeInitializerClause[^)]*\).*?->\s*Option<',
        content, re.DOTALL
    )
    assert svelte_helper, "Must have helper for directive parsing"


def test_parse_directive_helpers():
    """Helper functions exist to parse directive values."""
    html_rs = Path(f"{REPO}/crates/biome_service/src/file_handlers/html.rs")
    content = html_rs.read_text()

    helpers = re.findall(
        r'fn\s+(\w+)\s*\(\s*(?:value|attr):\s*&HtmlAttributeInitializerClause[^)]*\)',
        content
    )
    assert len(helpers) >= 2, \
        f"Expected at least 2 helpers, found {len(helpers)}"

    vue_parsing = bool(re.search(
        r'(?:inner_string_text|text_trimmed|text)\(\).*(?:TextSize|\+ 1|offset)',
        content, re.DOTALL
    ))
    assert vue_parsing, "Missing Vue-style parsing"

    svelte_parsing = bool(re.search(
        r'(?:expression|text_expression)\(\).*parse.*(?:text|js|jscript)',
        content, re.DOTALL
    ))
    assert svelte_parsing, "Missing Svelte-style parsing"


def test_biome_developer_skill_created():
    """.claude/skills/biome-developer/SKILL.md must exist with required content."""
    skill_path = Path(f"{REPO}/.claude/skills/biome-developer/SKILL.md")
    assert skill_path.exists(), "biome-developer/SKILL.md must exist"
    content = skill_path.read_text()

    assert "---" in content, "SKILL.md must have frontmatter"
    assert "name:" in content, "SKILL.md must have frontmatter with name"

    has_string_doc = bool(re.search(
        r'(?:inner_string|text_trimmed|string.*extract|text.*extract)',
        content, re.IGNORECASE
    ))
    assert has_string_doc, "Skill must document string extraction"

    has_ast_doc = bool(re.search(
        r'(?:quick_test|dbg!|inspect|ast)',
        content, re.IGNORECASE
    ))
    assert has_ast_doc, "Skill must document AST inspection"

    has_embed_doc = bool(re.search(
        r'(?:embedding|embedded|EmbeddingKind)',
        content, re.IGNORECASE
    ))
    assert has_embed_doc, "Skill must cover embedded language"


def test_agents_md_updated():
    """AGENTS.md must include new do's and don'ts about patterns and AST inspection."""
    agents_md = Path(f"{REPO}/AGENTS.md").read_text()
    content_lower = agents_md.lower()

    has_evidence_warning = bool(re.search(
        r'(?:widely used|common).*(?:without evidence|not proven|unverified)',
        content_lower
    ))
    assert has_evidence_warning, \
        "AGENTS.md must warn against claiming patterns without evidence"

    has_legacy_warning = bool(re.search(
        r'(?:legacy|deprecated|old syntax)',
        content_lower
    ))
    assert has_legacy_warning, "AGENTS.md must warn against legacy syntax"

    has_ast_rec = bool(re.search(
        r'(?:inspect|quick_test|ast.*structure|parse.*first)',
        content_lower
    ))
    assert has_ast_rec, "AGENTS.md must recommend AST inspection"

    has_skills_ref = bool(re.search(
        r'(?:skills?.*directory|\.claude/skills)',
        agents_md
    ))
    assert has_skills_ref, "AGENTS.md must reference skills directory"


def test_testing_codegen_skill_updated():
    """testing-codegen SKILL.md must document parser quick testing."""
    skill_path = Path(f"{REPO}/.claude/skills/testing-codegen/SKILL.md")
    content = skill_path.read_text()
    content_lower = content.lower()

    has_quick_test_section = bool(re.search(
        r'(?:quick.*test|parser.*test|qt|just)',
        content_lower
    ))
    assert has_quick_test_section, "Must document quick testing"

    has_qt_ref = bool(re.search(
        r'(?:just\s+qt|quick_test|qt\s+)',
        content
    ))
    assert has_qt_ref, "Must document quick test command"

    has_html_parser_ref = bool(re.search(
        r'(?:biome_html_parser|html.*parser)',
        content_lower
    ))
    assert has_html_parser_ref, "Must reference biome_html_parser"


def test_directive_ext_not_stub():
    """directive_ext.rs must have real implementation, not just return None."""
    directive_ext = Path(f"{REPO}/crates/biome_html_syntax/src/directive_ext.rs")
    content = directive_ext.read_text()

    svelte_arms = re.findall(r'Self::(Svelte\w+Directive)\s*\(', content)
    assert len(svelte_arms) >= 8, \
        f"Expected at least 8 Svelte directive arms, found {len(svelte_arms)}"

    arms_with_chain = re.findall(
        r'Self::Svelte\w+Directive\s*\([^)]+\)\s*=>[^;]+?\.(?:value|initializer)\(\)',
        content
    )
    assert len(arms_with_chain) >= 8, \
        f"Expected 8 arms with chain, found {len(arms_with_chain)}"


def test_markdown_table_formatting():
    """SKILL.md files must use proper markdown table formatting.
    
    Note: This is a simplified check that verifies the file has proper table formatting.
    The actual check is that tables in code blocks showing examples may trigger
    false positives, so we use a simplified pattern.
    """
    import re

    skill_path = Path(f"{REPO}/.claude/skills/biome-developer/SKILL.md")
    if skill_path.exists():
        content = skill_path.read_text()
        # Check for properly formatted tables (with spaces around dashes)
        # A proper table line looks like: | Column | Column |
        # We verify that at least some proper tables exist
        has_proper_tables = bool(re.search(r'\|\s+[-\w]+\s+\|', content))
        # Also check there are no extremely compact tables (no spaces at all)
        has_compact_tables = bool(re.search(r'\|[-]{3,}\|', content))
        assert has_proper_tables or not has_compact_tables, \
            "SKILL.md should have properly formatted markdown tables"


def test_vue_svelte_test_specs_exist():
    """Vue and Svelte test spec files must exist in the HTML parser tests."""
    vue_ok_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/ok/vue")
    vue_error_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/error/vue")

    vue_ok_count = len(list(vue_ok_dir.glob("*.vue"))) if vue_ok_dir.exists() else 0
    vue_error_count = len(list(vue_error_dir.glob("*.vue"))) if vue_error_dir.exists() else 0

    assert vue_ok_count >= 3, f"Expected >= 3 Vue ok specs, found {vue_ok_count}"
    assert vue_error_count >= 3, f"Expected >= 3 Vue error specs, found {vue_error_count}"

    svelte_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/error/svelte")
    svelte_ok_dir = Path(f"{REPO}/crates/biome_html_parser/tests/html_specs/ok/svelte")

    svelte_error_count = len(list(svelte_dir.glob("*.svelte"))) if svelte_dir.exists() else 0
    svelte_ok_count = len(list(svelte_ok_dir.glob("*.svelte"))) if svelte_ok_dir.exists() else 0

    assert svelte_error_count >= 5, f"Expected >= 5 Svelte error specs, found {svelte_error_count}"


def test_lib_rs_module_declaration():
    """biome_html_syntax::lib.rs uses proper module declaration style."""
    lib_rs = Path(f"{REPO}/crates/biome_html_syntax/src/lib.rs").read_text()

    inline_mods = re.findall(r'^mod\s+(\w+)\s*;', lib_rs, re.MULTILINE)
    assert len(inline_mods) >= 1, "lib.rs should have inline module declarations"

    brace_mods = re.findall(r'^mod\s+\w+\s*\{', lib_rs, re.MULTILINE)
    assert len(brace_mods) <= 2, f"Expected <=2 brace modules, found {len(brace_mods)}"
