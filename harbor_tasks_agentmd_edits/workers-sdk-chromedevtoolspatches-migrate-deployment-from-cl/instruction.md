# Migrate chrome-devtools-patches deployment from Cloudflare Pages to Workers + Assets

## Problem

The `packages/chrome-devtools-patches` package is currently deployed as a Cloudflare Pages project, but it needs to be migrated to a Cloudflare Workers + Assets deployment. This means:

1. The inspector proxy in both **miniflare** and **wrangler** only allows WebSocket connections from `pages.dev` origins. After migration, the DevTools frontend will be served from `workers.dev` domains instead, so WebSocket connections from the new domain will be rejected by the origin allowlist.

2. The deployment infrastructure (Makefile, CI workflow, package.json scripts) still uses `wrangler pages deploy` and the Pages-specific preview URL format.

3. There is no `wrangler.jsonc` configuration file for the Workers + Assets deployment.

## Expected Behavior

- The inspector proxy origin allowlists in both `packages/miniflare/src/plugins/core/inspector-proxy/inspector-proxy-controller.ts` and `packages/wrangler/templates/startDevWorker/InspectorProxyWorker.ts` should accept connections from the new `workers.dev` domain patterns (both the base domain and versioned preview subdomains), while keeping the legacy `pages.dev` patterns for backward compatibility.

- A `wrangler.jsonc` configuration should be created in `packages/chrome-devtools-patches/` to define the Workers + Assets project.

- The Makefile `publish` target should use `wrangler deploy` instead of `wrangler pages deploy`. A new `publish-preview` target should use `wrangler versions upload`.

- The CI workflow and package.json should be updated to use the new deploy commands and URL extraction patterns.

- After making the code changes, update the package's README.md to accurately reflect the new deployment architecture. The documentation should describe the current deployment method, not the legacy Pages setup.

## Files to Look At

- `packages/miniflare/src/plugins/core/inspector-proxy/inspector-proxy-controller.ts` — miniflare's inspector proxy origin allowlist
- `packages/wrangler/templates/startDevWorker/InspectorProxyWorker.ts` — wrangler's inspector proxy origin allowlist
- `packages/chrome-devtools-patches/Makefile` — build and deploy targets
- `packages/chrome-devtools-patches/package.json` — npm scripts for deployment
- `packages/chrome-devtools-patches/README.md` — deployment documentation
- `.github/workflows/deploy-previews.yml` — CI preview deployment workflow

## Notes

- Don't forget to create a changeset for the affected packages.
- The `workers.dev` preview URLs use a different subdomain pattern than `pages.dev` — check how other Workers + Assets projects handle versioned previews.
