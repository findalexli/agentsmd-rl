#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'fn initializer.*HtmlAttributeInitializerClause' crates/biome_html_syntax/src/directive_ext.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.claude/skills/README.md b/.claude/skills/README.md
index 7a46ec655b4b..d06f9eab90ef 100644
--- a/.claude/skills/README.md
+++ b/.claude/skills/README.md
@@ -27,6 +27,7 @@ Skills complement the specialized **agents** in `.claude/agents/` - agents are p

 | Skill | Purpose | Best Used With | Lines |
 | ------- | --------- | ---------------- | ------- |
+| **[biome-developer](./biome-developer/SKILL.md)** | General development best practices, common gotchas, Biome-specific patterns | Any agent | ~320 |
 | **[testing-codegen](./testing-codegen/SKILL.md)** | Run tests, manage snapshots, create changesets, generate code | Any agent | ~200 |
 | **[type-inference](./type-inference/SKILL.md)** | Work with module graph and type inference system | `biome-lint-engineer` | ~180 |
 | **[diagnostics-development](./diagnostics-development/SKILL.md)** | Create user-friendly error messages and diagnostics | Any agent | ~170 |
@@ -166,6 +167,8 @@ Skills are designed to be **quick reference cards** - scan in 30 seconds and kno
 ```
 .claude/skills/
 ├── README.md (this file)
+├── biome-developer/
+│   └── SKILL.md
 ├── lint-rule-development/
 │   └── SKILL.md
 ├── formatter-development/
diff --git a/.claude/skills/biome-developer/SKILL.md b/.claude/skills/biome-developer/SKILL.md
new file mode 100644
index 000000000000..9f8f3adabf2e
--- /dev/null
+++ b/.claude/skills/biome-developer/SKILL.md
@@ -0,0 +1,265 @@
+---
+name: biome-developer
+description: General development best practices and common gotchas when working on Biome. Use for avoiding common mistakes, understanding Biome-specific patterns, and learning technical tips. Examples:<example>Working with Biome's AST and syntax nodes</example><example>Understanding string extraction methods</example><example>Handling embedded languages and directives</example>
+---
+
+## Purpose
+
+This skill provides general development best practices, common gotchas, and Biome-specific patterns that apply across different areas of the codebase. Use this as a reference when you encounter unfamiliar APIs or need to avoid common mistakes.
+
+## Prerequisites
+
+- Basic familiarity with Rust
+- Understanding of Biome's architecture (parser, analyzer, formatter)
+- Development environment set up (see CONTRIBUTING.md)
+
+## Common Gotchas and Best Practices
+
+### Working with AST and Syntax Nodes
+
+**DO:**
+- ✅ Use parser crate's `quick_test` to inspect AST structure before implementing
+- ✅ Understand the node hierarchy and parent-child relationships
+- ✅ Check both general cases AND specific types (e.g., Vue has both `VueDirective` and `VueV*ShorthandDirective`)
+- ✅ Verify your solution works for all relevant variant types, not just the first one you find
+
+**DON'T:**
+- ❌ Build the full Biome binary just to inspect syntax (expensive) - use parser crate's `quick_test` instead
+- ❌ Assume syntax patterns without inspecting the AST first
+
+**Example - Inspecting AST:**
+```rust
+// In crates/biome_html_parser/tests/quick_test.rs
+// Modify the quick_test function:
+#[test]
+pub fn quick_test() {
+    let code = r#"<button on:click={handleClick}>Click</button>"#;
+    let source_type = HtmlFileSource::svelte();
+    let options = HtmlParseOptions::from(&source_type);
+    let root = parse_html(code, options);
+    dbg!(&root.syntax());  // Shows full AST structure
+}
+```
+
+Run: `just qt biome_html_parser`
+
+### String Extraction and Text Handling
+
+**DO:**
+- ✅ Use `inner_string_text()` when extracting content from quoted strings (removes quotes)
+- ✅ Use `text_trimmed()` when you need the full token text without leading/trailing whitespace
+- ✅ Use `token_text_trimmed()` on nodes like `HtmlAttributeName` to get the text content
+- ✅ Verify whether values use `HtmlString` (quotes) or `HtmlTextExpression` (curly braces)
+
+**DON'T:**
+- ❌ Use `text_trimmed()` when you need `inner_string_text()` for extracting quoted string contents
+
+**Example - String Extraction:**
+```rust
+// WRONG: text_trimmed() includes quotes
+let html_string = value.as_html_string()?;
+let content = html_string.value_token()?.text_trimmed(); // Returns: "\"handler\""
+
+// CORRECT: inner_string_text() removes quotes
+let html_string = value.as_html_string()?;
+let inner_text = html_string.inner_string_text().ok()?;
+let content = inner_text.text(); // Returns: "handler"
+```
+
+### Working with Embedded Languages
+
+**DO:**
+- ✅ Verify changes work for different value formats (quoted strings vs text expressions) when handling multiple frameworks
+- ✅ Use appropriate `EmbeddingKind` for context (Vue, Svelte, Astro, etc.)
+- ✅ Check if embedded content needs `is_source: true` (script tags) vs `is_source: false` (template expressions)
+- ✅ Calculate offsets correctly: token start + 1 for opening quote, or use `text_range().start()` for text expressions
+
+**DON'T:**
+- ❌ Assume all frameworks use the same syntax (Vue uses quotes, Svelte uses curly braces)
+- ❌ Implement features for "widely used" patterns without evidence - ask the user first
+
+**Example - Different Value Formats:**
+```rust
+// Vue directives use quoted strings: @click="handler"
+let html_string = value.as_html_string()?;
+let inner_text = html_string.inner_string_text().ok()?;
+
+// Svelte directives use text expressions: on:click={handler}
+let text_expression = value.as_html_attribute_single_text_expression()?;
+let expression = text_expression.expression().ok()?;
+```
+
+### Borrow Checker and Temporary Values
+
+**DO:**
+- ✅ Use intermediate `let` bindings to avoid temporary value borrows that get dropped
+- ✅ Store method results that return owned values before calling methods on them
+
+**DON'T:**
+- ❌ Create temporary value borrows that get dropped before use
+
+**Example - Avoiding Borrow Issues:**
+```rust
+// WRONG: Temporary borrow gets dropped
+let html_string = value.value().ok()?.as_html_string()?;
+let token = html_string.value_token().ok()?; // ERROR: html_string dropped
+
+// CORRECT: Store intermediate result
+let value_node = value.value().ok()?;
+let html_string = value_node.as_html_string()?;
+let token = html_string.value_token().ok()?; // OK
+```
+
+### Clippy and Code Style
+
+**DO:**
+- ✅ Use `let` chains to collapse nested `if let` statements (cleaner and follows Rust idioms)
+- ✅ Run `just l` before committing to catch clippy warnings
+- ✅ Fix clippy suggestions unless there's a good reason not to
+
+**DON'T:**
+- ❌ Ignore clippy warnings - they often catch real issues or suggest better patterns
+
+**Example - Collapsible If:**
+```rust
+// WRONG: Nested if let (clippy::collapsible_if warning)
+if let Some(directive) = VueDirective::cast_ref(&element) {
+    if let Some(initializer) = directive.initializer() {
+        // ... do something
+    }
+}
+
+// CORRECT: Use let chains
+if let Some(directive) = VueDirective::cast_ref(&element)
+    && let Some(initializer) = directive.initializer()
+{
+    // ... do something
+}
+```
+
+### Legacy and Deprecated Syntax
+
+**DO:**
+- ✅ Ask users before implementing deprecated/legacy syntax support
+- ✅ Wait for user demand before spending time on legacy features
+- ✅ Document when features are intentionally not supported due to being legacy
+
+**DON'T:**
+- ❌ Implement legacy/deprecated syntax without checking with the user first
+- ❌ Claim patterns are "widely used" or "common" without evidence
+
+**Example:**
+Svelte's `on:click` event handler syntax is legacy (Svelte 3/4). Modern Svelte 5 runes mode uses regular attributes. Unless users specifically request it, don't implement legacy syntax support.
+
+### Testing and Development
+
+**DO:**
+- ✅ Use `just qt <package>` to run quick tests (handles test execution automatically)
+- ✅ Review snapshot changes carefully - don't blindly accept
+- ✅ Test with multiple variants when working with enums (e.g., all `VueV*ShorthandDirective` types)
+- ✅ Add tests for both valid and invalid cases
+- ✅ Use CLI tests for testing embedded languages (Vue/Svelte directives, etc.)
+
+**DON'T:**
+- ❌ Blindly accept all snapshot changes
+- ❌ Try to test embedded languages in analyzer packages (they don't have embedding capabilities)
+
+## Pattern Matching Tips
+
+### Working with Node Variants
+
+When working with enum variants (like `AnySvelteDirective`), check if there are also non-enum types that need handling:
+
+```rust
+// Check AnySvelteDirective enum (bind:, class:, style:, etc.)
+if let Some(directive) = AnySvelteDirective::cast_ref(&element) {
+    // Handle special Svelte directives
+}
+
+// But also check regular HTML attributes with specific prefixes
+if let Some(attribute) = HtmlAttribute::cast_ref(&element) {
+    if let Ok(name) = attribute.name() {
+        // Some directives might be parsed as regular attributes
+    }
+}
+```
+
+### Checking Multiple Variant Types
+
+For frameworks with multiple directive syntaxes, handle each type:
+
+```rust
+// Vue has multiple shorthand types
+if let Some(directive) = VueVOnShorthandDirective::cast_ref(&element) {
+    // Handle @click
+}
+if let Some(directive) = VueVBindShorthandDirective::cast_ref(&element) {
+    // Handle :prop
+}
+if let Some(directive) = VueVSlotShorthandDirective::cast_ref(&element) {
+    // Handle #slot
+}
+if let Some(directive) = VueDirective::cast_ref(&element) {
+    // Handle v-if, v-show, etc.
+}
+```
+
+## Common API Confusion
+
+### String/Text Methods
+
+| Method | Use When | Returns |
+| --- | --- | --- |
+| `inner_string_text()` | Extracting content from quoted strings | Content without quotes |
+| `text_trimmed()` | Getting token text without whitespace | Full token text |
+| `token_text_trimmed()` | Getting text from nodes like `HtmlAttributeName` | Node text content |
+| `text()` | Getting raw text | Exact text as written |
+
+### Value Extraction Methods
+
+| Type | Method | Framework |
+| --- | --- | --- |
+| `HtmlString` | `inner_string_text()` | Vue (quotes) |
+| `HtmlAttributeSingleTextExpression` | `expression()` | Svelte (curly braces) |
+| `HtmlTextExpression` | `html_literal_token()` | Template expressions |
+
+## References
+
+- Main contributing guide: `../../CONTRIBUTING.md`
+- Testing workflows: `../testing-codegen/SKILL.md`
+- Parser development: `../parser-development/SKILL.md`
+- Biome internals docs: https://biomejs.dev/internals
+
+## Documentation and Markdown Formatting
+
+**DO:**
+- ✅ Use spaces around table separators: `| --- | --- | --- |` (not `|---|---|---|`)
+- ✅ Ensure all Markdown tables follow "compact" style with proper spacing
+- ✅ Test documentation changes with markdown linters before committing
+
+**DON'T:**
+- ❌ Use compact table separators without spaces (causes CI linting failures)
+
+**Example - Table Formatting:**
+```markdown
+<!-- WRONG: No spaces around separators -->
+| Method | Use When | Returns |
+|--------|----------|---------|
+
+<!-- CORRECT: Spaces around separators -->
+| Method | Use When | Returns |
+| --- | --- | --- |
+```
+
+The CI uses `markdownlint-cli2` which enforces the "compact" style requiring spaces.
+
+## When to Use This Skill
+
+Load this skill when:
+- Working with unfamiliar Biome APIs
+- Getting borrow checker errors with temporary values
+- Extracting strings or text from syntax nodes
+- Implementing support for embedded languages (Vue, Svelte, etc.)
+- Wondering why your AST inspection doesn't match expectations
+- Making decisions about legacy/deprecated syntax support
+- Writing or updating markdown documentation
diff --git a/.claude/skills/testing-codegen/SKILL.md b/.claude/skills/testing-codegen/SKILL.md
index a78ae7df6c8c..79f6d1411d92 100644
--- a/.claude/skills/testing-codegen/SKILL.md
+++ b/.claude/skills/testing-codegen/SKILL.md
@@ -44,7 +44,7 @@ Fast iteration during development:

 ```rust
 // In crates/biome_js_analyze/tests/quick_test.rs
-// Uncomment #[ignore] and modify:
+// Modify the quick_test function:

 const SOURCE: &str = r#"
 const x = 1;
@@ -56,10 +56,43 @@ let rule_filter = RuleFilter::Rule("nursery", "noVar");

 Run:
 ```shell
-cd crates/biome_js_analyze
-cargo test quick_test -- --show-output
+just qt biome_js_analyze
+```
+
+### Quick Test for Parser Development
+
+**IMPORTANT:** Use this instead of building full Biome binary for syntax inspection - it's much faster!
+
+For inspecting AST structure when implementing parsers or working with embedded languages:
+
+```rust
+// In crates/biome_html_parser/tests/quick_test.rs
+// Modify the quick_test function:
+
+#[test]
+pub fn quick_test() {
+    let code = r#"<button on:click={handleClick}>Click</button>"#;
+
+    let source_type = HtmlFileSource::svelte();
+    let options = HtmlParseOptions::from(&source_type);
+    let root = parse_html(code, options);
+    let syntax = root.syntax();
+
+    dbg!(&syntax, root.diagnostics(), root.has_errors());
+}
+```

 Run:
+```shell
+just qt biome_html_parser
+```
+
+The `dbg!` output shows the full AST tree structure, helping you understand:
+- How directives/attributes are parsed (e.g., `HtmlAttribute` vs `SvelteBindDirective`)
+- Whether values use `HtmlString` (quotes) or `HtmlTextExpression` (curly braces)
+- Token ranges and offsets needed for proper snippet creation
+- Node hierarchy and parent-child relationships
+
 ### Snapshot Testing with Insta

 Run tests and generate snapshots:
@@ -263,6 +296,10 @@ cargo test test_name -- --show-output
 - **Changeset timing**: Create before opening PR, can edit after
 - **Snapshot review**: Always review snapshots carefully - don't blindly accept
 - **Test performance**: Use `#[ignore]` for slow tests, run with `cargo test -- --ignored`
+- **Parser inspection**: Use `just qt <package>` to run quick_test and inspect AST, NOT full Biome builds (much faster)
+- **String extraction**: Use `inner_string_text()` for quoted strings, not `text_trimmed()` (which includes quotes)
+- **Legacy syntax**: Ask users before implementing deprecated/legacy syntax - wait for user demand
+- **Borrow checker**: Avoid temporary borrows that get dropped - use `let binding = value; binding.method()` pattern

 ## Common Test Patterns

diff --git a/AGENTS.md b/AGENTS.md
index c2fbdda45469..daa0309acbcc 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -361,6 +361,9 @@ Before opening a PR, verify:
 - Commit without formatting/linting
 - Open PRs without tests
 - Blindly accept all snapshot changes
+- Claim patterns are "widely used" or "common" without evidence
+- Implement legacy/deprecated syntax without checking with the user first
+- Make assumptions about API design - inspect actual code structure first

 ✅ **Do:**
 - Ask the user if unsure about changesets
@@ -371,6 +374,10 @@ Before opening a PR, verify:
 - Review snapshot changes carefully
 - Disclose AI assistance
 - Link to related issues
+- Inspect AST structure before implementing (use parser crate's `quick_test`)
+- Ask users about legacy/deprecated syntax support - wait for demand before implementing
+- Verify your solution works for all relevant cases, not just the first one you find
+- Reference the skills in `.claude/skills/` for technical implementation details

 ## Getting Help:

diff --git a/crates/biome_html_syntax/src/directive_ext.rs b/crates/biome_html_syntax/src/directive_ext.rs
new file mode 100644
index 000000000000..132ac2d19d96
--- /dev/null
+++ b/crates/biome_html_syntax/src/directive_ext.rs
@@ -0,0 +1,17 @@
+use crate::{AnySvelteDirective, HtmlAttributeInitializerClause};
+
+impl AnySvelteDirective {
+    /// Returns the initializer from a Svelte directive's value, if available.
+    pub fn initializer(&self) -> Option<HtmlAttributeInitializerClause> {
+        match self {
+            Self::SvelteBindDirective(dir) => dir.value().ok()?.initializer(),
+            Self::SvelteTransitionDirective(dir) => dir.value().ok()?.initializer(),
+            Self::SvelteInDirective(dir) => dir.value().ok()?.initializer(),
+            Self::SvelteOutDirective(dir) => dir.value().ok()?.initializer(),
+            Self::SvelteUseDirective(dir) => dir.value().ok()?.initializer(),
+            Self::SvelteAnimateDirective(dir) => dir.value().ok()?.initializer(),
+            Self::SvelteStyleDirective(dir) => dir.value().ok()?.initializer(),
+            Self::SvelteClassDirective(dir) => dir.value().ok()?.initializer(),
+        }
+    }
+}
diff --git a/crates/biome_html_syntax/src/lib.rs b/crates/biome_html_syntax/src/lib.rs
index 2ad781b975f0..ae58bc51de63 100644
--- a/crates/biome_html_syntax/src/lib.rs
+++ b/crates/biome_html_syntax/src/lib.rs
@@ -3,6 +3,7 @@
 #[macro_use]
 mod attr_ext;
 pub mod attribute_ext;
+mod directive_ext;
 pub mod element_ext;
 mod file_source;
 mod generated;
diff --git a/crates/biome_service/src/file_handlers/html.rs b/crates/biome_service/src/file_handlers/html.rs
index e93100ab0f5d..8dcf79865154 100644
--- a/crates/biome_service/src/file_handlers/html.rs
+++ b/crates/biome_service/src/file_handlers/html.rs
@@ -41,16 +41,17 @@ use biome_html_formatter::{
 use biome_html_parser::{HtmlParseOptions, parse_html_with_cache};
 use biome_html_syntax::element_ext::AnyEmbeddedContent;
 use biome_html_syntax::{
-    AstroEmbeddedContent, HtmlDoubleTextExpression, HtmlElement, HtmlFileSource, HtmlLanguage,
-    HtmlRoot, HtmlSingleTextExpression, HtmlSyntaxNode, HtmlTextExpression, HtmlTextExpressions,
-    HtmlVariant,
+    AnySvelteDirective, AstroEmbeddedContent, HtmlAttributeInitializerClause,
+    HtmlDoubleTextExpression, HtmlElement, HtmlFileSource, HtmlLanguage, HtmlRoot,
+    HtmlSingleTextExpression, HtmlSyntaxNode, HtmlTextExpression, HtmlTextExpressions, HtmlVariant,
+    VueDirective, VueVBindShorthandDirective, VueVOnShorthandDirective, VueVSlotShorthandDirective,
 };
 use biome_js_parser::parse_js_with_offset_and_cache;
 use biome_js_syntax::{EmbeddingKind, JsFileSource, JsLanguage};
 use biome_json_parser::parse_json_with_offset_and_cache;
 use biome_json_syntax::{JsonFileSource, JsonLanguage};
 use biome_parser::AnyParse;
-use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode};
+use biome_rowan::{AstNode, AstNodeList, BatchMutation, NodeCache, SendNode, TextSize};
 use camino::Utf8Path;
 use either::Either;
 use std::borrow::Cow;
@@ -614,6 +615,89 @@ fn parse_embedded_nodes(
                     nodes.push((content.into(), file_source));
                 }
             }
+
+            // Parse Vue directive attributes (v-on, v-bind, v-if, etc.)
+            for element in html_root.syntax().descendants() {
+                // Handle @click shorthand (VueVOnShorthandDirective)
+                if let Some(directive) = VueVOnShorthandDirective::cast_ref(&element)
+                    && let Some(initializer) = directive.initializer()
+                {
+                    let file_source =
+                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
+                            setup: false,
+                            is_source: false,
+                        });
+                    if let Some((content, doc_source)) = parse_directive_string_value(
+                        &initializer,
+                        cache,
+                        biome_path,
+                        settings,
+                        file_source,
+                    ) {
+                        nodes.push((content.into(), doc_source));
+                    }
+                }
+
+                // Handle :prop shorthand (VueVBindShorthandDirective)
+                if let Some(directive) = VueVBindShorthandDirective::cast_ref(&element)
+                    && let Some(initializer) = directive.initializer()
+                {
+                    let file_source =
+                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
+                            setup: false,
+                            is_source: false,
+                        });
+                    if let Some((content, doc_source)) = parse_directive_string_value(
+                        &initializer,
+                        cache,
+                        biome_path,
+                        settings,
+                        file_source,
+                    ) {
+                        nodes.push((content.into(), doc_source));
+                    }
+                }
+
+                // Handle #slot shorthand (VueVSlotShorthandDirective)
+                if let Some(directive) = VueVSlotShorthandDirective::cast_ref(&element)
+                    && let Some(initializer) = directive.initializer()
+                {
+                    let file_source =
+                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
+                            setup: false,
+                            is_source: false,
+                        });
+                    if let Some((content, doc_source)) = parse_directive_string_value(
+                        &initializer,
+                        cache,
+                        biome_path,
+                        settings,
+                        file_source,
+                    ) {
+                        nodes.push((content.into(), doc_source));
+                    }
+                }
+
+                // Handle full directives (v-on:, v-bind:, v-if, v-show, etc.)
+                if let Some(directive) = VueDirective::cast_ref(&element)
+                    && let Some(initializer) = directive.initializer()
+                {
+                    let file_source =
+                        embedded_file_source.with_embedding_kind(EmbeddingKind::Vue {
+                            setup: false,
+                            is_source: false,
+                        });
+                    if let Some((content, doc_source)) = parse_directive_string_value(
+                        &initializer,
+                        cache,
+                        biome_path,
+                        settings,
+                        file_source,
+                    ) {
+                        nodes.push((content.into(), doc_source));
+                    }
+                }
+            }
         }
         HtmlVariant::Svelte => {
             let mut elements = vec![];
@@ -678,6 +762,28 @@ fn parse_embedded_nodes(
                     nodes.push((content.into(), file_source));
                 }
             }
+
+            // Parse Svelte directive attributes (bind:, class:, use:, etc.)
+            // Note: on: event handlers are legacy Svelte 3/4 syntax and not supported.
+            // Svelte 5 runes mode uses regular attributes for event handlers.
+            for element in html_root.syntax().descendants() {
+                // Handle special Svelte directives (bind:, class:, etc.)
+                if let Some(directive) = AnySvelteDirective::cast_ref(&element)
+                    && let Some(initializer) = directive.initializer()
+                {
+                    let file_source = embedded_file_source
+                        .with_embedding_kind(EmbeddingKind::Svelte { is_source: false });
+                    if let Some((content, doc_source)) = parse_directive_text_expression(
+                        &initializer,
+                        cache,
+                        biome_path,
+                        settings,
+                        file_source,
+                    ) {
+                        nodes.push((content.into(), doc_source));
+                    }
+                }
+            }
         }
     }

@@ -1007,6 +1113,79 @@ pub(crate) fn parse_vue_text_expression(
     parse_text_expression(expression, cache, biome_path, settings, file_source)
 }

+/// Parses a directive attribute's string value as JavaScript
+///
+/// Extracts the JavaScript expression from a Vue/Svelte directive attribute value
+/// (e.g., `@click="handler()"` -> `handler()`) and parses it as an embedded JavaScript snippet.
+fn parse_directive_string_value(
+    value: &HtmlAttributeInitializerClause,
+    cache: &mut NodeCache,
+    biome_path: &BiomePath,
+    settings: &SettingsWithEditor,
+    file_source: JsFileSource,
+) -> Option<(EmbeddedSnippet<JsLanguage>, DocumentFileSource)> {
+    let value_node = value.value().ok()?;
+    let html_string = value_node.as_html_string()?;
+    let content_token = html_string.value_token().ok()?;
+    let inner_text = html_string.inner_string_text().ok()?;
+    let text = inner_text.text();
+    let token_range = content_token.text_trimmed_range();
+    let inner_offset = token_range.start() + TextSize::from(1);
+    let document_file_source = DocumentFileSource::Js(file_source);
+    let options = settings.parse_options::<JsLanguage>(biome_path, &document_file_source);
+    let parse = parse_js_with_offset_and_cache(text, inner_offset, file_source, options, cache);
+    let snippet = EmbeddedSnippet::new(
+        parse.into(),
+        value.range(),
+        token_range,
+        inner_offset,
+    );
+    Some((snippet, document_file_source))
+}
+
+/// Parses a Svelte directive attribute's text expression value as JavaScript
+///
+/// Unlike Vue which uses quoted strings, Svelte uses curly braces with text expressions.
+fn parse_directive_text_expression(
+    value: &HtmlAttributeInitializerClause,
+    cache: &mut NodeCache,
+    biome_path: &BiomePath,
+    settings: &SettingsWithEditor,
+    file_source: JsFileSource,
+) -> Option<(EmbeddedSnippet<JsLanguage>, DocumentFileSource)> {
+    let value_node = value.value().ok()?;
+    let text_expression = value_node.as_html_attribute_single_text_expression()?;
+    let expression = text_expression.expression().ok()?;
+    let document_file_source = DocumentFileSource::Js(file_source);
+    parse_text_expression(expression, cache, biome_path, settings, file_source)
+        .map(|(snippet, _)| (snippet, document_file_source))
+}

PATCH

echo "Patch applied successfully."
