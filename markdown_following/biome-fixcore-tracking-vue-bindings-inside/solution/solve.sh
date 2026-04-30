#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'fn initializer.*HtmlAttributeInitializerClause' crates/biome_html_syntax/src/directive_ext.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 <<'PYEOF'
import os
import re

os.chdir("/workspace/biome")

# ===== Create new files =====

# Create biome-developer/SKILL.md
os.makedirs(".claude/skills/biome-developer", exist_ok=True)
with open(".claude/skills/biome-developer/SKILL.md", "w") as f:
    f.write("""---
name: biome-developer
description: General development best practices and common gotchas when working on Biome. Use for avoiding common mistakes, understanding Biome-specific patterns, and learning technical tips. Examples:<example>Working with Biome's AST and syntax nodes</example><example>Understanding string extraction methods</example><example>Handling embedded languages and directives</example>
---

## Purpose

This skill provides general development best practices, common gotchas, and Biome-specific patterns that apply across different areas of the codebase. Use this as a reference when you encounter unfamiliar APIs or need to avoid common mistakes.

## Prerequisites

- Basic familiarity with Rust
- Understanding of Biome's architecture (parser, analyzer, formatter)
- Development environment set up (see CONTRIBUTING.md)

## Common Gotchas and Best Practices

### Working with AST and Syntax Nodes

**DO:**
- Use parser crate's `quick_test` to inspect AST structure before implementing
- Understand the node hierarchy and parent-child relationships
- Check both general cases AND specific types (e.g., Vue has both `VueDirective` and `VueV*ShorthandDirective`)
- Verify your solution works for all relevant variant types, not just the first one you find

**DON'T:**
- Build the full Biome binary just to inspect syntax (expensive) - use parser crate's `quick_test` instead
- Assume syntax patterns without inspecting the AST first

**Example - Inspecting AST:**
```rust
// In crates/biome_html_parser/tests/quick_test.rs
// Modify the quick_test function:
#[test]
pub fn quick_test() {
    let code = r#"<button on:click={handleClick}>Click</button>"#;
    let source_type = HtmlFileSource::svelte();
    let options = HtmlParseOptions::from(&source_type);
    let root = parse_html(code, options);
    dbg!(&root.syntax());  // Shows full AST structure
}
```

Run: `just qt biome_html_parser`

### String Extraction and Text Handling

**DO:**
- Use `inner_string_text()` when extracting content from quoted strings (removes quotes)
- Use `text_trimmed()` when you need the full token text without leading/trailing whitespace
- Use `token_text_trimmed()` on nodes like `HtmlAttributeName` to get the text content
- Verify whether values use `HtmlString` (quotes) or `HtmlTextExpression` (curly braces)

**DON'T:**
- Use `text_trimmed()` when you need `inner_string_text()` for extracting quoted string contents

**Example - String Extraction:**
```rust
// WRONG: text_trimmed() includes quotes
let html_string = value.as_html_string()?;
let content = html_string.value_token()?.text_trimmed(); // Returns: "\\"handler\\""

// CORRECT: inner_string_text() removes quotes
let html_string = value.as_html_string()?;
let inner_text = html_string.inner_string_text().ok()?;
let content = inner_text.text(); // Returns: "handler"
```

### Working with Embedded Languages

**DO:**
- Verify changes work for different value formats (quoted strings vs text expressions) when handling multiple frameworks
- Use appropriate `EmbeddingKind` for context (Vue, Svelte, Astro, etc.)
- Check if embedded content needs `is_source: true` (script tags) vs `is_source: false` (template expressions)
- Calculate offsets correctly: token start + 1 for opening quote, or use `text_range().start()` for text expressions

**DON'T:**
- Assume all frameworks use the same syntax (Vue uses quotes, Svelte uses curly braces)
- Implement features for "widely used" patterns without evidence - ask the user first

### Borrow Checker and Temporary Values

**DO:**
- Use intermediate `let` bindings to avoid temporary value borrows that get dropped
- Store method results that return owned values before calling methods on them

**DON'T:**
- Create temporary value borrows that get dropped before use

**Example - Avoiding Borrow Issues:**
```rust
// WRONG: Temporary borrow gets dropped
let html_string = value.value().ok()?.as_html_string()?;
let token = html_string.value_token().ok()?; // ERROR: html_string dropped

// CORRECT: Store intermediate result
let value_node = value.value().ok()?;
let html_string = value_node.as_html_string()?;
let token = html_string.value_token().ok()?; // OK
```

### Clippy and Code Style

**DO:**
- Use `let` chains to collapse nested `if let` statements (cleaner and follows Rust idioms)
- Run `just l` before committing to catch clippy warnings
- Fix clippy suggestions unless there's a good reason not to

**DON'T:**
- Ignore clippy warnings - they often catch real issues or suggest better patterns

### Legacy and Deprecated Syntax

**DO:**
- Ask users before implementing deprecated/legacy syntax support
- Wait for user demand before spending time on legacy features
- Document when features are intentionally not supported due to being legacy

**DON'T:**
- Implement legacy/deprecated syntax without checking with the user first
- Claim patterns are "widely used" or "common" without evidence

### Testing and Development

**DO:**
- Use `just qt <package>` to run quick tests (handles test execution automatically)
- Review snapshot changes carefully - don't blindly accept
- Test with multiple variants when working with enums (e.g., all `VueV*ShorthandDirective` types)
- Add tests for both valid and invalid cases
- Use CLI tests for testing embedded languages (Vue/Svelte directives, etc.)

**DON'T:**
- Blindly accept all snapshot changes
- Try to test embedded languages in analyzer packages (they don't have embedding capabilities)

## Pattern Matching Tips

### Working with Node Variants

When working with enum variants (like `AnySvelteDirective`), check if there are also non-enum types that need handling:

```rust
// Check AnySvelteDirective enum (bind:, class:, style:, etc.)
if let Some(directive) = AnySvelteDirective::cast_ref(&element) {
    // Handle special Svelte directives
}

// But also check regular HTML attributes with specific prefixes
if let Some(attribute) = HtmlAttribute::cast_ref(&element) {
    if let Ok(name) = attribute.name() {
        // Some directives might be parsed as regular attributes
    }
}
```

## Common API Confusion

### String/Text Methods

| Method | Use When | Returns |
| --- | --- | --- |
| `inner_string_text()` | Extracting content from quoted strings | Content without quotes |
| `text_trimmed()` | Getting token text without whitespace | Full token text |
| `token_text_trimmed()` | Getting text from nodes like `HtmlAttributeName` | Node text content |
| `text()` | Getting raw text | Exact text as written |

### Value Extraction Methods

| Type | Method | Framework |
| --- | --- | --- |
| `HtmlString` | `inner_string_text()` | Vue (quotes) |
| `HtmlAttributeSingleTextExpression` | `expression()` | Svelte (curly braces) |
| `HtmlTextExpression` | `html_literal_token()` | Template expressions |

## References

- Main contributing guide: `../../CONTRIBUTING.md`
- Testing workflows: `../testing-codegen/SKILL.md`
- Parser development: `../parser-development/SKILL.md`
- Biome internals docs: https://biomejs.dev/internals

## Documentation and Markdown Formatting

**DO:**
- Use spaces around table separators: `| --- | --- | --- |` (not `|---|---|---|`)
- Ensure all Markdown tables follow "compact" style with proper spacing

**DON'T:**
- Use compact table separators without spaces (causes CI linting failures)

## When to Use This Skill

Load this skill when:
- Working with unfamiliar Biome APIs
- Getting borrow checker errors with temporary values
- Extracting strings or text from syntax nodes
- Implementing support for embedded languages (Vue, Svelte, etc.)
- Wondering why your AST inspection doesn't match expectations
- Making decisions about legacy/deprecated syntax support
- Writing or updating markdown documentation
""")

# Create directive_ext.rs
with open("crates/biome_html_syntax/src/directive_ext.rs", "w") as f:
    f.write("""use crate::{AnySvelteDirective, HtmlAttributeInitializerClause};

impl AnySvelteDirective {
    /// Returns the initializer from a Svelte directive's value, if available.
    pub fn initializer(&self) -> Option<HtmlAttributeInitializerClause> {
        match self {
            Self::SvelteBindDirective(dir) => dir.value().ok()?.initializer(),
            Self::SvelteTransitionDirective(dir) => dir.value().ok()?.initializer(),
            Self::SvelteInDirective(dir) => dir.value().ok()?.initializer(),
            Self::SvelteOutDirective(dir) => dir.value().ok()?.initializer(),
            Self::SvelteUseDirective(dir) => dir.value().ok()?.initializer(),
            Self::SvelteAnimateDirective(dir) => dir.value().ok()?.initializer(),
            Self::SvelteStyleDirective(dir) => dir.value().ok()?.initializer(),
            Self::SvelteClassDirective(dir) => dir.value().ok()?.initializer(),
        }
    }
}
""")

# Add mod directive_ext to lib.rs
with open("crates/biome_html_syntax/src/lib.rs") as f:
    lib_content = f.read()

lib_content = lib_content.replace(
    "pub mod attribute_ext;",
    "pub mod attribute_ext;\nmod directive_ext;"
)

with open("crates/biome_html_syntax/src/lib.rs", "w") as f:
    f.write(lib_content)

# Update README.md skills
with open(".claude/skills/README.md") as f:
    readme = f.read()

readme = readme.replace(
    "| **[testing-codegen](./testing-codegen/SKILL.md)** | Run tests, manage snapshots, create changesets, generate code | Any agent | ~200 |",
    "| **[biome-developer](./biome-developer/SKILL.md)** | General development best practices, common gotchas, Biome-specific patterns | Any agent | ~320 |\n| **[testing-codegen](./testing-codegen/SKILL.md)** | Run tests, manage snapshots, create changesets, generate code | Any agent | ~200 |"
)

readme = readme.replace(
    " ├── lint-rule-development/",
    " ├── biome-developer/\n│   └── SKILL.md\n├── lint-rule-development/"
)

with open(".claude/skills/README.md", "w") as f:
    f.write(readme)

# Update AGENTS.md
with open("AGENTS.md") as f:
    agents = f.readlines()

new_lines = []
for line in agents:
    new_lines.append(line)
    if line.strip() == "- Blindly accept all snapshot changes":
        new_lines.append('- Claim patterns are "widely used" or "common" without evidence\n')
        new_lines.append("- Implement legacy/deprecated syntax without checking with the user first\n")
        new_lines.append("- Make assumptions about API design - inspect actual code structure first\n")
    elif line.strip() == "- Link to related issues":
        new_lines.append("- Inspect AST structure before implementing (use parser crate's quick_test)\n")
        new_lines.append("- Ask users about legacy/deprecated syntax support - wait for demand before implementing\n")
        new_lines.append("- Verify your solution works for all relevant cases, not just the first one you find\n")
        new_lines.append("- Reference the skills in .claude/skills/ for technical implementation details\n")

with open("AGENTS.md", "w") as f:
    f.writelines(new_lines)

# Update testing-codegen SKILL.md
with open(".claude/skills/testing-codegen/SKILL.md") as f:
    skill = f.read()

skill = skill.replace(
    "// Uncomment #[ignore] and modify:",
    "// Modify the quick_test function:"
)
skill = skill.replace(
    "cd crates/biome_js_analyze\ncargo test quick_test -- --show-output",
    "just qt biome_js_analyze"
)

parser_section = """### Quick Test for Parser Development

**IMPORTANT:** Use this instead of building full Biome binary for syntax inspection - it is much faster!

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

"""

skill = skill.replace(
    "### Snapshot Testing with Insta",
    parser_section + "### Snapshot Testing with Insta"
)

tips = "- **Parser inspection**: Use `just qt <package>` to run quick_test and inspect AST, NOT full Biome builds (much faster)\n- **String extraction**: Use `inner_string_text()` for quoted strings, not `text_trimmed()` (which includes quotes)\n- **Legacy syntax**: Ask users before implementing deprecated/legacy syntax - wait for user demand\n- **Borrow checker**: Avoid temporary borrows that get dropped - use `let binding = value; binding.method()` pattern"

skill = skill.replace(
    "- **Test performance**: Use `#[ignore]` for slow tests, run with `cargo test -- --ignored`",
    "- **Test performance**: Use `#[ignore]` for slow tests, run with `cargo test -- --ignored`\n" + tips
)

with open(".claude/skills/testing-codegen/SKILL.md", "w") as f:
    f.write(skill)

# Update html.rs
with open("crates/biome_service/src/file_handlers/html.rs") as f:
    html = f.read()

html = html.replace(
    """use biome_html_syntax::{
    AstroEmbeddedContent, HtmlDoubleTextExpression, HtmlElement, HtmlFileSource, HtmlLanguage,
    HtmlRoot, HtmlSingleTextExpression, HtmlSyntaxNode, HtmlTextExpression, HtmlTextExpressions,
    HtmlVariant,
};""",
    """use biome_html_syntax::{
    AnySvelteDirective, AstroEmbeddedContent, HtmlAttributeInitializerClause,
    HtmlDoubleTextExpression, HtmlElement, HtmlFileSource, HtmlLanguage, HtmlRoot,
    HtmlSingleTextExpression, HtmlSyntaxNode, HtmlTextExpression, HtmlTextExpressions, HtmlVariant,
    VueDirective, VueVBindShorthandDirective, VueVOnShorthandDirective, VueVSlotShorthandDirective,
};"""
)

html = html.replace(
    "use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode};",
    "use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode, TextSize};"
)

vue_marker = """                    nodes.push((content.into(), file_source));
                }
            }
        }
        HtmlVariant::Svelte => {"""

vue_code = """                    nodes.push((content.into(), file_source));
                }
            }

            // Parse Vue directive attributes (v-on, v-bind, v-if, etc.)
            for element in html_root.syntax().descendants() {
                if let Some(directive) = VueVOnShorthandDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer, cache, biome_path, settings, file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }
                if let Some(directive) = VueVBindShorthandDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer, cache, biome_path, settings, file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }
                if let Some(directive) = VueVSlotShorthandDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer, cache, biome_path, settings, file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }
                if let Some(directive) = VueDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source =
                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
                            setup: false,
                            is_source: false,
                        });
                    if let Some((content, doc_source)) = parse_directive_string_value(
                        &initializer, cache, biome_path, settings, file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }
            }
        }
        HtmlVariant::Svelte => {"""

html = html.replace(vue_marker, vue_code)

svelte_marker = """                    nodes.push((content.into(), file_source));
                }
            }
        }
    }"""

svelte_code = """                    nodes.push((content.into(), file_source));
                }
            }

            // Parse Svelte directive attributes (bind:, class:, use:, etc.)
            for element in html_root.syntax().descendants() {
                if let Some(directive) = AnySvelteDirective::cast_ref(&element)
                    && let Some(initializer) = directive.initializer()
                {
                    let file_source = embedded_file_source
                        .with_embedding_kind(EmbeddingKind::Svelte { is_source: false });
                    if let Some((content, doc_source)) = parse_directive_text_expression(
                        &initializer, cache, biome_path, settings, file_source,
                    ) {
                        nodes.push((content.into(), doc_source));
                    }
                }
            }
        }
    }"""

html = html.replace(svelte_marker, svelte_code)

helper_marker = """    parse_text_expression(expression, cache, biome_path, settings, file_source)
}

fn debug_syntax_tree"""

helper_code = """    parse_text_expression(expression, cache, biome_path, settings, file_source)
}

/// Parses a directive attribute's string value as JavaScript
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

fn debug_syntax_tree"""

html = html.replace(helper_marker, helper_code)

with open("crates/biome_service/src/file_handlers/html.rs", "w") as f:
    f.write(html)

print("All changes applied successfully!")
PYEOF

echo "Patch applied successfully."
