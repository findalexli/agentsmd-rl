# Add JS Dataframe documentation to docs

## Problem

The JS Dataframe documentation was incomplete. The standalone README at `js/dataframe/standalone/README.md` existed separately, but the main `js/dataframe/README.md` lacked comprehensive documentation. Additionally, the website's JS docs page redirected to `/docs/js/atoms` which was outdated.

## Expected Behavior

1. The main `js/dataframe/README.md` should have comprehensive documentation including Install, Usage, Props, Events, and Custom Styling sections
2. The `js/dataframe/standalone/README.md` should be removed (content merged into main README)
3. The `/docs/js` page should redirect to `/docs/js/dataframe` instead of `/docs/js/atoms`
4. The docs layout should filter `js_pages` to only show "dataframe" and "js-client" components
5. Syntax highlighting should support Svelte via `prism-svelte`

## Files to Look At

- `js/dataframe/README.md` — main README that needs comprehensive documentation
- `js/dataframe/standalone/README.md` — should be removed after merging content
- `js/_website/src/routes/[[version]]/docs/js/+page.server.ts` — redirect logic
- `js/_website/src/routes/[[version]]/docs/+layout.server.ts` — component filtering
- `js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts` — syntax highlighting
- `js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts` — syntax highlighting
- `js/code/package.json` — exports configuration
