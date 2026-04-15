# Fix Vue/Svelte directive variable tracking in Biome linter

## Problem

Biome's `noUnusedVariables` lint rule incorrectly reports variables as unused when they are only referenced inside Vue or Svelte directive attributes. For example:

- In Vue: `@click="handler"`, `:disabled="!supported"`, `v-if="count > 0"` — the variables `handler`, `supported`, `count` are flagged as unused even though they are used in the template.
- In Svelte: `bind:value={inputValue}`, `class:active={isActive}` — the variables `inputValue`, `isActive` are flagged as unused.

The linter is not extracting and analyzing the JavaScript expressions inside these directive attributes, so variables referenced there are invisible to the usage tracker.

## Requirements

### Code Changes

#### 1. `crates/biome_html_syntax/src/directive_ext.rs` (new file)

Create a new module that implements an `initializer()` method on `AnySvelteDirective`. The method must:
- Return `Option<HtmlAttributeInitializerClause>`
- Match on all 8 Svelte directive variants: `SvelteBindDirective`, `SvelteClassDirective`, `SvelteInDirective`, `SvelteOutDirective`, `SvelteStyleDirective`, `SvelteTransitionDirective`, `SvelteUseDirective`, `SvelteAnimateDirective`

#### 2. `crates/biome_html_syntax/src/lib.rs`

Register the new module by adding `mod directive_ext;`.

#### 3. `crates/biome_service/src/file_handlers/html.rs`

Add directive attribute parsing logic in the `parse_embedded_nodes` function:

For Vue directives, handle these 4 directive types:
- `VueDirective`
- `VueVOnShorthandDirective`
- `VueVBindShorthandDirective`
- `VueVSlotShorthandDirective`

Vue directive values are quoted strings stored in `HtmlAttributeInitializerClause`. They must be:
- Extracted and parsed as JavaScript
- Tagged with `EmbeddingKind::Vue`

For Svelte directives:
- Match with `AnySvelteDirective::cast_ref`
- Call the `initializer()` method to get `HtmlAttributeInitializerClause`
- Tag with `EmbeddingKind::Svelte`

Svelte directive expressions are curly-braced text expressions in `HtmlAttributeInitializerClause`.

Both Vue and Svelte directive handlers require helper functions that:
- Accept `HtmlAttributeInitializerClause` as parameter
- For Vue (quoted strings): Use `inner_string_text()` for extraction and offset by `TextSize::from(1)` for the opening quote
- For Svelte (curly braces): Use `as_html_attribute_single_text_expression()` for extraction

### Documentation Updates

#### `AGENTS.md`

Add guidance on:
- Not claiming patterns are "widely used" or "common" without evidence — ask the user first
- Not implementing legacy/deprecated syntax without checking with the user first
- Inspecting AST structure (using the parser crate's `quick_test`) before implementing
- Referencing `.claude/skills/` for implementation details

#### `.claude/skills/testing-codegen/SKILL.md`

Add a "Quick Test for Parser Development" section covering:
- The `just qt` command for running quick tests
- `biome_html_parser` for HTML/embedded language testing
- Using `dbg!` to inspect AST structure

#### `.claude/skills/biome-developer/SKILL.md` (new file)

Create a skill file with:
- `inner_string_text()` usage for extracting quoted string content (not `text_trimmed()`)
- `quick_test` for AST inspection
- `EmbeddingKind` variants for embedded language tagging
- A "Common Gotchas" or "Common API Confusion" section

Markdown table formatting must use spaces around separators: `| --- | --- | --- |` (not `|---|---|---|`).

### Test Fixtures

The following test fixture directories must exist:
- `crates/biome_html_parser/tests/html_specs/ok/vue/` — at least 3 `.vue` files
- `crates/biome_html_parser/tests/html_specs/error/vue/` — at least 3 `.vue` files
- `crates/biome_html_parser/tests/html_specs/error/svelte/` — at least 5 `.svelte` files
- `crates/biome_html_parser/tests/html_specs/ok/svelte/` — must exist
