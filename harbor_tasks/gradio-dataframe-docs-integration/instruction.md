# Integrate Dataframe Standalone Documentation

## Problem

The `@gradio/dataframe` package has comprehensive documentation in `js/dataframe/standalone/README.md`, but this documentation is not being surfaced in the main package README or the website documentation system.

Currently:
1. `js/dataframe/README.md` only contains minimal API documentation with `BaseDataFrame` and `BaseExample` exports
2. `js/dataframe/standalone/README.md` contains the full user-facing documentation (install instructions, usage examples, props, events, styling)
3. The website documentation system at `js/_website/` is not configured to display dataframe documentation

## Expected Changes

### Documentation Consolidation
Move the comprehensive documentation from `js/dataframe/standalone/README.md` to `js/dataframe/README.md`. The main README should become the single source of truth for dataframe documentation, including:
- Install instructions (npm/pnpm)
- Usage examples with Svelte code
- Props documentation with TypeScript interfaces
- Events documentation
- Custom styling guide with CSS variables

After moving, delete `js/dataframe/standalone/README.md` as it's no longer needed.

### Website Routing Updates
The website documentation system needs updates to support displaying the dataframe documentation:

1. **Layout Server** (`js/_website/src/routes/[[version]]/docs/+layout.server.ts`):
   - Add a `components_to_document` array that includes `["dataframe", "js-client"]`
   - Filter `js_pages` to only include these documented components

2. **JS Index Page** (`js/_website/src/routes/[[version]]/docs/js/+page.server.ts`):
   - Replace the hardcoded redirect to `atoms` with dynamic URL checking
   - Implement a `urlExists()` helper that checks if `/docs/js/dataframe` exists
   - Redirect to dataframe if available, fallback to js-client

3. **Syntax Highlighting** (`js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts` and others):
   - Add `import "prism-svelte"` for Svelte syntax highlighting
   - Extend the `langs` map to include: `svelte`, `sv`, `md`, `css`

4. **Navigation Cleanup** (`js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.svelte` and storybook page):
   - Remove the prev/next navigation links (they reference non-existent pages)

### Package.json Exports
The `@gradio/code` package needs export updates (`js/code/package.json`):
- Reorder exports to put `types` first
- Add `"default"` export pointing to the `.svelte` files
- Ensure both `.` and `./example` exports have consistent structure

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
