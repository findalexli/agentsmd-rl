# Integrate Dataframe Standalone Documentation

## Problem

The `@gradio/dataframe` package has comprehensive documentation in `js/dataframe/standalone/README.md`, but this documentation is not being surfaced in the main package README or the website documentation system.

Currently:
1. `js/dataframe/README.md` only contains minimal API documentation with `BaseDataFrame` and `BaseExample` exports
2. `js/dataframe/standalone/README.md` contains the full user-facing documentation (install instructions, usage examples, props, events, styling)
3. The website documentation system at `js/_website/` is not configured to display dataframe documentation
4. The JS index page redirects to `atoms` which is being deprecated
5. Svelte syntax highlighting is not available in the documentation pages

## Requirements

### Documentation Consolidation
Move the comprehensive documentation from `js/dataframe/standalone/README.md` to `js/dataframe/README.md`. After moving, delete `js/dataframe/standalone/README.md`.

The consolidated README must contain these specific sections:
- "Standalone Svelte component" (description of the component)
- "Install" (installation instructions with npm/pnpm commands)
- "Usage" (Svelte code examples)
- "Props" (props documentation including `show_search` or row numbers documentation)
- "Events" (events documentation)

### Website Routing Updates

The website documentation system needs updates to support displaying the dataframe documentation:

1. **Layout Server** (`js/_website/src/routes/[[version]]/docs/+layout.server.ts`):
   - Filter `js_pages` to only include documented components: `dataframe` and `js-client`
   - The filtering logic should check if each component is in the list `["dataframe", "js-client"]`

2. **JS Index Page** (`js/_website/src/routes/[[version]]/docs/js/+page.server.ts`):
   - Must implement dynamic URL checking to determine redirect destination
   - Use a HEAD request to check URL availability (more efficient than GET)
   - Must redirect to `/docs/js/dataframe` if available, fallback to `/docs/js/js-client`
   - Must not hardcode redirect to `atoms`

3. **Syntax Highlighting** - Add to these files:
   - `js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts`
   - `js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts`
   - `js/_website/src/routes/[[version]]/docs/js/storybook/+page.server.ts`
   - `js/_website/src/routes/changelog/+page.server.ts`

   Each must:
   - Import `prism-svelte` for Svelte syntax highlighting
   - Extend the `langs` map to include:
     - `svelte: "svelte"`
     - `sv: "svelte"`
     - `md: "markdown"`
     - `css: "css"`

4. **Navigation Cleanup** (`js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.svelte` and storybook page):
   - Remove the prev/next navigation links (they reference non-existent pages)

### Package.json Exports
The `@gradio/code` package needs export updates (`js/code/package.json`):
- Main export (`.`) must have `"default": "./dist/Index.svelte"`
- Example export (`./example`) must have `"default": "./dist/Example.svelte"`
- Types should be ordered first in each export

## Files to Modify

- `js/dataframe/README.md` — Replace minimal content with comprehensive docs
- `js/dataframe/standalone/README.md` — Delete after content move
- `js/_website/src/routes/[[version]]/docs/+layout.server.ts` — Add component filtering
- `js/_website/src/routes/[[version]]/docs/js/+page.server.ts` — Dynamic redirect logic
- `js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts` — Prism-svelte + langs
- `js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts` — Prism-svelte + langs
- `js/_website/src/routes/[[version]]/docs/js/storybook/+page.server.ts` — Prism-svelte + langs
- `js/_website/src/routes/changelog/+page.server.ts` — Extended langs map
- `js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.svelte` — Remove nav links
- `js/_website/src/routes/[[version]]/docs/js/storybook/+page.svelte` — Remove nav links
- `js/code/package.json` — Add default exports
