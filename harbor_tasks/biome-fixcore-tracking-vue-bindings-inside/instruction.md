# Fix Vue/Svelte Directive Variable Tracking in Biome Linter

## Problem

Biome's `noUnusedVariables` lint rule incorrectly reports variables as unused when they are only referenced inside Vue or Svelte directive attributes. For example:

- In Vue: `@click="handler"`, `:disabled="!supported"`, `v-if="count > 0"` — the variables `handler`, `supported`, `count` are flagged as unused even though they are used in the template.
- In Svelte: `bind:value={inputValue}`, `class:active={isActive}` — the variables `inputValue`, `isActive` are flagged as unused.

The linter's embedded-language extraction does not currently process directive attributes, so JavaScript expressions inside them are invisible to the variable usage tracker.

### Implementation Notes

The biome_html_syntax crate requires a new module (named `directive_ext`) that provides an `initializer()` method on `AnySvelteDirective` to access the directive's value clause.

The HTML file handler (`crates/biome_service/src/file_handlers/html.rs`) must be updated to handle these Vue directive AST types: `VueDirective`, `VueVOnShorthandDirective`, `VueVBindShorthandDirective`, and `VueVSlotShorthandDirective`. Each must be tagged as `EmbeddingKind::Vue` embedded content.

For Svelte, `AnySvelteDirective` must be handled and tagged as `EmbeddingKind::Svelte` embedded content.

Two helper functions are required for directive value parsing:
- One that extracts values from quoted-string directives using `inner_string_text()` (Vue style)
- One that extracts values from text-expression directives using `as_html_attribute_single_text_expression()` (Svelte style)

Both helpers accept an `HtmlAttributeInitializerClause` parameter.

### Requirements

### Vue Directive Support

The embedded-node extraction logic must handle Vue directive AST types. Vue directives come in 4 forms:

- Shorthand `@` for events (e.g., `@click`)
- Shorthand `:` for bindings (e.g., `:disabled`)
- Shorthand `#` for slots (e.g., `#default`)
- Full form (e.g., `v-if`, `v-show`)

Vue directive values are quoted strings — the inner content (without quotes) must be extracted and parsed as embedded JavaScript tagged with the Vue embedding kind.

### Svelte Directive Support

The embedded-node extraction logic must handle Svelte directive AST types. Svelte directives have 8 variants:

- `SvelteBindDirective` — `bind:value={x}`
- `SvelteClassDirective` — `class:active={x}`
- `SvelteInDirective` — `in:animation={x}`
- `SvelteOutDirective` — `out:animation={x}`
- `SvelteStyleDirective` — `style:color={x}`
- `SvelteTransitionDirective` — `transition:name={x}`
- `SvelteUseDirective` — `use:action={x}`
- `SvelteAnimateDirective` — `animate:name={x}`

Unlike Vue quoted strings, Svelte directives use curly-brace text expressions — the expression content (without braces) must be extracted and parsed as embedded JavaScript tagged with the Svelte embedding kind.

### Helper Functions

Two helper functions are needed for directive value parsing:

- One for extracting values from quoted-string directives (Vue style)
- One for extracting values from text-expression directives (Svelte style)

Both helpers accept an attribute initializer clause parameter.

### Documentation Updates

#### `AGENTS.md`

Add new items to the project's do's and don'ts:

- Warn against claiming patterns are "widely used" or "common" without evidence
- Warn against implementing legacy/deprecated syntax without checking with the user first
- Recommend inspecting AST structure before implementing
- Reference the `.claude/skills/` directory for technical implementation details

#### `.claude/skills/testing-codegen/SKILL.md`

Add a section on quick testing for parser development covering:

- The `just qt` command for running quick tests
- Using `biome_html_parser` for HTML/embedded language parser testing

#### `.claude/skills/biome-developer/SKILL.md` (new file)

Create a developer skill file with YAML frontmatter (including a `name:` field) that documents:

- String extraction patterns for syntax nodes
- AST inspection techniques
- Embedded language handling

Markdown tables in skill files must use proper formatting with spaces around separators (e.g., `| --- | --- |` not `|---|---|`).

### Test Fixtures

The following test fixture directories must be populated:

- `crates/biome_html_parser/tests/html_specs/ok/vue/` — at least 3 `.vue` files
- `crates/biome_html_parser/tests/html_specs/error/vue/` — at least 3 `.vue` files
- `crates/biome_html_parser/tests/html_specs/error/svelte/` — at least 5 `.svelte` files
- `crates/biome_html_parser/tests/html_specs/ok/svelte/` — directory must exist
