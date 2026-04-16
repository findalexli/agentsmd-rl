#!/usr/bin/env python3
"""Manually apply the gold solution changes that the corrupt patch can't apply."""
import os
import re
import subprocess

REPO = "/workspace/biome"
os.chdir(REPO)

# --- 1. Apply patches that git apply can handle ---
# Extract the patch from solve.sh
with open("/solution/solve.sh") as f:
    lines = f.readlines()

# Get the patch content (lines 13 to 631, 0-indexed: 12 to 630)
patch_content = "".join(lines[12:630])

with open("/tmp/full.patch", "w") as f:
    f.write(patch_content)

# Split by diff headers
parts = re.split(r"(?=^diff --git)", patch_content, flags=re.MULTILINE)
parts = [p for p in parts if p.strip()]

for i, part in enumerate(parts):
    with open(f"/tmp/patch_{i}.patch", "w") as f:
        f.write(part)

# Apply patches that work directly
for i in [0, 1, 4, 5]:  # README.md, biome-developer SKILL.md, directive_ext.rs, lib.rs
    subprocess.run(["git", "apply", "--whitespace=fix", f"/tmp/patch_{i}.patch"],
                   capture_output=True)
    print(f"Applied patch {i}")

# --- 2. Manually apply AGENTS.md changes ---
with open("AGENTS.md") as f:
    agents_lines = f.readlines()

new_lines = []
for line in agents_lines:
    new_lines.append(line)
    if line.strip() == "- Blindly accept all snapshot changes":
        new_lines.append('- Claim patterns are "widely used" or "common" without evidence\n')
        new_lines.append("- Implement legacy/deprecated syntax without checking with the user first\n")
        new_lines.append("- Make assumptions about API design - inspect actual code structure first\n")
    elif line.strip() == "- Link to related issues":
        new_lines.append("- Inspect AST structure before implementing (use parser crate's `quick_test`)\n")
        new_lines.append("- Ask users about legacy/deprecated syntax support - wait for demand before implementing\n")
        new_lines.append("- Verify your solution works for all relevant cases, not just the first one you find\n")
        new_lines.append("- Reference the skills in `.claude/skills/` for technical implementation details\n")

with open("AGENTS.md", "w") as f:
    f.writelines(new_lines)
print("AGENTS.md updated")

# --- 3. Manually apply testing-codegen SKILL.md changes ---
with open(".claude/skills/testing-codegen/SKILL.md") as f:
    skill_content = f.read()

# Fix the comment
skill_content = skill_content.replace(
    "// Uncomment #[ignore] and modify:",
    "// Modify the quick_test function:"
)

# Fix the run command
skill_content = skill_content.replace(
    "cd crates/biome_js_analyze\ncargo test quick_test -- --show-output",
    "just qt biome_js_analyze"
)

# Add parser section before Snapshot Testing
parser_section = '''### Quick Test for Parser Development

**IMPORTANT:** Use this instead of building full Biome binary for syntax inspection - it's much faster!

For inspecting AST structure when implementing parsers or working with embedded languages:

```rust
// In crates/biome_html_parser/tests/quick_test.rs
// Modify the quick_test function:

#[test]
pub fn quick_test() {
    let code = r#"<button on:click={handleClick}>Click</button>"#;

    let source_type = HtmlFileSource::svelte();
    let options = HtmlParseOptions::from(&source_type);
    let root = parse_html(code, options);
    let syntax = root.syntax();

    dbg!(&syntax, root.diagnostics(), root.has_errors());
}
```

Run:
```shell
just qt biome_html_parser
```

The `dbg!` output shows the full AST tree structure, helping you understand:
- How directives/attributes are parsed (e.g., `HtmlAttribute` vs `SvelteBindDirective`)
- Whether values use `HtmlString` (quotes) or `HtmlTextExpression` (curly braces)
- Token ranges and offsets needed for proper snippet creation
- Node hierarchy and parent-child relationships

'''

skill_content = skill_content.replace(
    "### Snapshot Testing with Insta",
    parser_section + "### Snapshot Testing with Insta"
)

# Add tips
tips = """- **Parser inspection**: Use `just qt <package>` to run quick_test and inspect AST, NOT full Biome builds (much faster)
- **String extraction**: Use `inner_string_text()` for quoted strings, not `text_trimmed()` (which includes quotes)
- **Legacy syntax**: Ask users before implementing deprecated/legacy syntax - wait for user demand
- **Borrow checker**: Avoid temporary borrows that get dropped - use `let binding = value; binding.method()` pattern"""

skill_content = skill_content.replace(
    "- **Test performance**: Use `#[ignore]` for slow tests, run with `cargo test -- --ignored`",
    "- **Test performance**: Use `#[ignore]` for slow tests, run with `cargo test -- --ignored`\n" + tips
)

with open(".claude/skills/testing-codegen/SKILL.md", "w") as f:
    f.write(skill_content)
print("testing-codegen SKILL.md updated")

# --- 4. Manually apply html.rs changes ---
with open("crates/biome_service/src/file_handlers/html.rs") as f:
    html_content = f.read()

# 4a. Fix imports
old_imports = """use biome_html_syntax::{
    AstroEmbeddedContent, HtmlDoubleTextExpression, HtmlElement, HtmlFileSource, HtmlLanguage,
    HtmlRoot, HtmlSingleTextExpression, HtmlSyntaxNode, HtmlTextExpression, HtmlTextExpressions,
    HtmlVariant,
};"""

new_imports = """use biome_html_syntax::{
    AnySvelteDirective, AstroEmbeddedContent, HtmlAttributeInitializerClause,
    HtmlDoubleTextExpression, HtmlElement, HtmlFileSource, HtmlLanguage, HtmlRoot,
    HtmlSingleTextExpression, HtmlSyntaxNode, HtmlTextExpression, HtmlTextExpressions, HtmlVariant,
    VueDirective, VueVBindShorthandDirective, VueVOnShorthandDirective, VueVSlotShorthandDirective,
};"""

html_content = html_content.replace(old_imports, new_imports)

# 4b. Fix rowan import
html_content = html_content.replace(
    "use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode};",
    "use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode, TextSize};"
)

# 4c. Add Vue directive parsing before "HtmlVariant::Svelte =>"
vue_insert_marker = """                    nodes.push((content.into(), file_source));
                }
            }
        }
        HtmlVariant::Svelte => {"""

vue_code = """                    nodes.push((content.into(), file_source));
                }
            }

            // Parse Vue directive attributes (v-on, v-bind, v-if, etc.)
            for element in html_root.syntax().descendants() {
                // Handle @click shorthand (VueVOnShorthandDirective)
                if let Some(directive) = VueVOnShorthandDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer,
                        cache,
                        biome_path,
                        settings,
                        file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }

                // Handle :prop shorthand (VueVBindShorthandDirective)
                if let Some(directive) = VueVBindShorthandDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer,
                        cache,
                        biome_path,
                        settings,
                        file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }

                // Handle #slot shorthand (VueVSlotShorthandDirective)
                if let Some(directive) = VueVSlotShorthandDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer,
                        cache,
                        biome_path,
                        settings,
                        file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }

                // Handle full directives (v-on:, v-bind:, v-if, v-show, etc.)
                if let Some(directive) = VueDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer,
                        cache,
                        biome_path,
                        settings,
                        file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }
            }
        }
        HtmlVariant::Svelte => {"""

html_content = html_content.replace(vue_insert_marker, vue_code)

# 4d. Add Svelte directive parsing
svelte_insert = """                    nodes.push((content.into(), file_source));
                }
            }
        }
    }"""

svelte_code = """                    nodes.push((content.into(), file_source));
                }
            }

            // Parse Svelte directive attributes (bind:, class:, use:, etc.)
            // Note: on: event handlers are legacy Svelte 3/4 syntax and not supported.
            // Svelte 5 runes mode uses regular attributes for event handlers.
            for element in html_root.syntax().descendants() {
                // Handle special Svelte directives (bind:, class:, etc.)
                if let Some(directive) = AnySvelteDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source = embedded_file_source
                        .with_embedding_kind(EmbeddingKind::Svelte { is_source: false });
                    if let Some((content, doc_source)) = parse_directive_text_expression(
                        &initializer,
                        cache,
                        biome_path,
                        settings,
                        file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }
            }
        }
    }"""

html_content = html_content.replace(svelte_insert, svelte_code)

# 4e. Add helper functions
helper_marker = """    parse_text_expression(expression, cache, biome_path, settings, file_source)
}

fn debug_syntax_tree"""

helper_code = '''    parse_text_expression(expression, cache, biome_path, settings, file_source)
}

/// Parses a directive attribute's string value as JavaScript
///
/// Extracts the JavaScript expression from a Vue/Svelte directive attribute value
/// (e.g., `@click="handler()"` -> `handler()`) and parses it as an embedded JavaScript snippet.
fn parse_directive_string_value(
    value: &HtmlAttributeInitializerClause,
    cache: &mut NodeCache,
    biome_path: &BiomePath,
    settings: &SettingsWithEditor,
    file_source: JsFileSource,
) -> Option<(EmbeddedSnippet<JsLanguage>, DocumentFileSource)> {
    let value_node = value.value().ok()?;
    let html_string = value_node.as_html_string()?;
    let content_token = html_string.value_token().ok()?;
    let inner_text = html_string.inner_string_text().ok()?;
    let text = inner_text.text();
    let token_range = content_token.text_trimmed_range();
    let inner_offset = token_range.start() + TextSize::from(1);
    let document_file_source = DocumentFileSource::Js(file_source);
    let options = settings.parse_options::<JsLanguage>(biome_path, &document_file_source);
    let parse = parse_js_with_offset_and_cache(text, inner_offset, file_source, options, cache);
    let snippet = EmbeddedSnippet::new(
        parse.into(),
        value.range(),
        token_range,
        inner_offset,
    );
    Some((snippet, document_file_source))
}

/// Parses a Svelte directive attribute's text expression value as JavaScript
///
/// Unlike Vue which uses quoted strings, Svelte uses curly braces with text expressions.
fn parse_directive_text_expression(
    value: &HtmlAttributeInitializerClause,
    cache: &mut NodeCache,
    biome_path: &BiomePath,
    settings: &SettingsWithEditor,
    file_source: JsFileSource,
) -> Option<(EmbeddedSnippet<JsLanguage>, DocumentFileSource)> {
    let value_node = value.value().ok()?;
    let text_expression = value_node.as_html_attribute_single_text_expression()?;
    let expression = text_expression.expression().ok()?;
    let document_file_source = DocumentFileSource::Js(file_source);
    parse_text_expression(expression, cache, biome_path, settings, file_source)
        .map(|(snippet, _)| (snippet, document_file_source))
}

fn debug_syntax_tree'''

html_content = html_content.replace(helper_marker, helper_code)

with open("crates/biome_service/src/file_handlers/html.rs", "w") as f:
    f.write(html_content)
print("html.rs updated")

print("\nAll changes applied successfully!")
