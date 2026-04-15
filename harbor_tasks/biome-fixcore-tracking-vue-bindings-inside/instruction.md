# Fix Vue/Svelte directive variable tracking in Biome linter

## Problem

Biome's `noUnusedVariables` lint rule incorrectly reports variables as unused when they are only referenced inside Vue or Svelte directive attributes. For example:

- In Vue: `@click="handler"`, `:disabled="!supported"`, `v-if="count > 0"` — the variables `handler`, `supported`, `count` are flagged as unused even though they are used in the template.
- In Svelte: `bind:value={inputValue}`, `class:active={isActive}` — the variables `inputValue`, `isActive` are flagged as unused.

The linter is not extracting and analyzing the JavaScript expressions inside these directive attributes, so variables referenced there are invisible to the usage tracker.

## Expected Behavior

Variables used inside Vue and Svelte directive attribute values should be recognized as "used" by the linter. Running `biome lint --only=noUnusedVariables` on a `.vue` or `.svelte` file with directive-bound variables should report zero warnings for those variables.

## Technical Details

### Vue directives

Vue directive attributes (`@click`, `:prop`, `#slot`, `v-if`, `v-on:`, `v-bind:`, etc.) store their JavaScript expression as a **quoted string** inside `HtmlAttributeInitializerClause`. The value is accessed via `.initializer()` on the directive node.

The parser must:
1. Cast each Vue directive type using `::cast_ref` and call `.initializer()` to extract the value clause
2. Use `inner_string_text()` to extract the string content without quotes
3. Offset the text range by `TextSize::from(1)` for the opening quote character
4. Tag embedded content with `EmbeddingKind::Vue`

Vue has 4 directive types that need separate handling:
- `VueVOnShorthandDirective` — `@click`, `@input`, etc.
- `VueVBindShorthandDirective` — `:disabled`, `:value`, etc.
- `VueVSlotShorthandDirective` — `#default`, `#header`, etc.
- `VueDirective` — `v-if`, `v-show`, `v-on:`, `v-bind:`, etc.

### Svelte directives

Svelte directive attributes (`bind:`, `class:`, `style:`, `use:`, `transition:`, `in:`, `out:`, `animate:`) store their JavaScript expression as a **text expression** (curly braces) inside `HtmlAttributeInitializerClause`. The value is accessed via `.initializer()` on the directive node.

The parser must:
1. Cast using `AnySvelteDirective::cast_ref` and call `.initializer()` to extract the value clause
2. Use `as_html_attribute_single_text_expression()` then `.expression()` to extract the expression
3. Tag embedded content with `EmbeddingKind::Svelte`

There are **8 Svelte directive variants** that must all be handled:
- `SvelteBindDirective`, `SvelteTransitionDirective`, `SvelteInDirective`, `SvelteOutDirective`
- `SvelteUseDirective`, `SvelteAnimateDirective`, `SvelteStyleDirective`, `SvelteClassDirective`

Each variant must chain `.value().ok()?.initializer()` in a match arm.

## Files to Modify

### New file: `crates/biome_html_syntax/src/directive_ext.rs`

Create a new module that implements `initializer()` on `AnySvelteDirective`. The method returns `Option<HtmlAttributeInitializerClause>` and must have a match with **all 8** Svelte directive variants, each calling `.value().ok()?.initializer()`.

### `crates/biome_html_syntax/src/lib.rs`

Register the new module by adding `mod directive_ext;`.

### `crates/biome_service/src/file_handlers/html.rs`

In the `parse_embedded_nodes` function (under the `HtmlVariant::Vue` and `HtmlVariant::Svelte` match arms), add parsing logic for directive attributes:

- For Vue: handle all 4 Vue directive types. Each case calls `directive.initializer()` to get the value clause, passes it to a helper function that uses `inner_string_text()` and `TextSize::from(1)` to extract the JS expression, and tags it with `EmbeddingKind::Vue`.
- For Svelte: call `AnySvelteDirective::cast_ref` on each descendant, then `.initializer()` on the result, and pass to a helper that uses `as_html_attribute_single_text_expression()`.

Both helper functions (`parse_directive_string_value` for Vue quoted strings, `parse_directive_text_expression` for Svelte curly braces) take `HtmlAttributeInitializerClause` as their first parameter.

## Documentation Updates

After fixing the code, update the relevant agent instruction and skill files to document the patterns and lessons from this fix:

### `AGENTS.md`

Add guidance that:
- Do NOT claim patterns are "widely used" or "common" without evidence — ask the user first
- Do NOT implement legacy/deprecated syntax without checking with the user first
- Do inspect the AST structure (using the parser crate's `quick_test`) before implementing
- Reference `.claude/skills/` for implementation details

### `.claude/skills/testing-codegen/SKILL.md`

Add a section on **Quick Test for Parser Development** that:
- Documents the `just qt` command for running quick tests
- References `biome_html_parser` for HTML/embedded language testing
- Shows how to use `dbg!` to inspect AST structure

### `.claude/skills/biome-developer/SKILL.md` (new file)

Create a new skill file covering:
- `inner_string_text()` usage for extracting quoted string content (not `text_trimmed()`)
- `quick_test` for AST inspection
- `EmbeddingKind` variants for embedded language tagging
- A section on "Common Gotchas" or "Common API Confusion"

**Markdown table formatting**: Use spaces around separators (`| --- | --- | --- |`), not compact style (`|---|---|---|`), or CI linting will fail.

## Test Files

The following test fixture files must exist after the fix:

- Vue ok specs: `crates/biome_html_parser/tests/html_specs/ok/vue/` — at least 3 `.vue` files
- Vue error specs: `crates/biome_html_parser/tests/html_specs/error/vue/` — at least 3 `.vue` files
- Svelte error specs: `crates/biome_html_parser/tests/html_specs/error/svelte/` — at least 5 `.svelte` files
- Svelte ok specs: `crates/biome_html_parser/tests/html_specs/ok/svelte/` — must exist
