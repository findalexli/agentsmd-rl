# Fix Vue/Svelte directive variable tracking in Biome linter

## Problem

Biome's `noUnusedVariables` lint rule incorrectly reports variables as unused when they are only referenced inside Vue or Svelte directive attributes. For example:

- In Vue: `@click="handler"`, `:disabled="!supported"`, `v-if="count > 0"` — the variables `handler`, `supported`, `count` are flagged as unused even though they are used in the template.
- In Svelte: `bind:value={inputValue}`, `class:active={isActive}` — the variables `inputValue`, `isActive` are flagged as unused.

The linter's embedded-language extraction does not currently process directive attributes, so JavaScript expressions inside them are invisible to the variable usage tracker.

## Requirements

### Vue Directive Tracking

The embedded-node extraction logic must recognize and parse all 4 Vue directive AST types:

- `VueDirective` (handles `v-if`, `v-show`, `v-on:click`, etc.)
- `VueVOnShorthandDirective` (handles `@click`, `@input`, etc.)
- `VueVBindShorthandDirective` (handles `:prop`, `:disabled`, etc.)
- `VueVSlotShorthandDirective` (handles `#slot`, `#default`, etc.)

Each must be detected via `cast_ref`, have its `.initializer()` extracted, and be parsed as embedded JavaScript tagged with `EmbeddingKind::Vue`. Vue directive values are quoted strings (e.g., `@click="handler"`), so the inner string content must be extracted (not the raw token with quotes). Proper offset calculation using `TextSize` is required so that error positions map correctly back to the source.

### Svelte Directive Tracking

All 8 variants of the `AnySvelteDirective` enum must be handled:

- `SvelteBindDirective`
- `SvelteClassDirective`
- `SvelteInDirective`
- `SvelteOutDirective`
- `SvelteStyleDirective`
- `SvelteTransitionDirective`
- `SvelteUseDirective`
- `SvelteAnimateDirective`

A `directive_ext` module must be added to the `biome_html_syntax` crate (declared in its `lib.rs`) that provides a way to obtain the `HtmlAttributeInitializerClause` from any `AnySvelteDirective` variant. This module must match on all 8 variants and chain through `.value()` and `.initializer()` for each. The extracted content should be parsed as embedded JavaScript tagged with `EmbeddingKind::Svelte`.

Unlike Vue, Svelte directives use curly-brace text expressions (e.g., `bind:value={x}`), so the implementation must extract text expressions rather than quoted strings.

### Helper Functions

At least 2 helper functions must exist that accept an `HtmlAttributeInitializerClause` parameter — one for parsing Vue-style quoted string values (using `inner_string_text()` and `TextSize` offset calculation) and one for parsing Svelte-style text expression values (using `expression()` and the existing text expression parsing infrastructure).

### Documentation Updates

#### `AGENTS.md`

Add new items to the project's do's and don'ts:

- Warn against claiming patterns are "widely used" or "common" without evidence
- Warn against implementing legacy/deprecated syntax without checking with the user first
- Recommend inspecting AST structure (e.g., using the parser crate's `quick_test`) before implementing
- Reference the `.claude/skills/` directory for technical implementation details

#### `.claude/skills/testing-codegen/SKILL.md`

Add a section on quick testing for parser development covering:

- The `just qt` command for running quick tests
- Using `biome_html_parser` for HTML/embedded language parser testing

#### `.claude/skills/biome-developer/SKILL.md` (new file)

Create a developer skill file with YAML frontmatter (including a `name:` field) that documents:

- String extraction patterns (mention `inner_string_text` or similar text extraction methods)
- AST inspection techniques (mention `quick_test`, `dbg!`, or similar AST inspection tools)
- Embedded language handling (mention `EmbeddingKind` or embedded language concepts)

Markdown tables in skill files must use proper formatting with spaces around separators (e.g., `| --- | --- |` not `|---|---|`).

### Test Fixtures

The following test fixture directories must be populated:

- `crates/biome_html_parser/tests/html_specs/ok/vue/` — at least 3 `.vue` files
- `crates/biome_html_parser/tests/html_specs/error/vue/` — at least 3 `.vue` files
- `crates/biome_html_parser/tests/html_specs/error/svelte/` — at least 5 `.svelte` files
- `crates/biome_html_parser/tests/html_specs/ok/svelte/` — directory must exist
