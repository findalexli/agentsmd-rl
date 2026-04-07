# Fix Vue/Svelte directive variable tracking in Biome linter

## Problem

Biome's `noUnusedVariables` lint rule incorrectly reports variables as unused when they are only referenced inside Vue or Svelte directive attributes. For example:

- In Vue: `@click="handler"`, `:disabled="!supported"`, `v-if="count > 0"` — the variables `handler`, `supported`, `count` are flagged as unused even though they are used in the template.
- In Svelte: `bind:value={inputValue}`, `class:active={isActive}` — the variables `inputValue`, `isActive` are flagged as unused.

The linter is not extracting and analyzing the JavaScript expressions inside these directive attributes, so variables referenced there are invisible to the usage tracker.

## Expected Behavior

Variables used inside Vue and Svelte directive attribute values should be recognized as "used" by the linter. Running `biome lint --only=noUnusedVariables` on a `.vue` or `.svelte` file with directive-bound variables should report zero warnings for those variables.

## Files to Look At

- `crates/biome_service/src/file_handlers/html.rs` — handles parsing of embedded JavaScript inside HTML-like files (Vue, Svelte, Astro). The `parse_embedded_nodes` function is where directive attribute values need to be extracted and parsed as JS snippets.
- `crates/biome_html_syntax/src/` — syntax types for HTML/Svelte/Vue AST nodes. A new module may be needed to provide convenience methods on directive types.
- `crates/biome_html_syntax/src/lib.rs` — module registration for new files.

## Additional Requirements

After fixing the code, update the relevant agent instruction and skill files to document the patterns and lessons from this fix:

- The project's `AGENTS.md` should be updated with new guidance relevant to working with directives, embedded languages, and AST inspection.
- The `.claude/skills/testing-codegen/SKILL.md` should be updated to cover parser-level quick test workflows.
- A new skill file should be created under `.claude/skills/` for general Biome development best practices.
