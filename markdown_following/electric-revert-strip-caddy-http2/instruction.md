# Fix Slow Electric Shapes in Local Development

## Problem

Local development with Electric SQL suffers from slow shape loading. Browsers limit HTTP/1.1 to 6 concurrent connections per domain, which bottlenecks shape subscriptions. The current `AGENTS.md` at the repo root incorrectly states this is "Fixed by default in `@electric-sql/client` v1.0.13+ UPGRADE!" — this is wrong and misleading.

The `examples/tanstack-db-web-starter/` project needs HTTP/2 proxy support integrated into its Vite dev server workflow to work around this browser limitation.

## What to Do

1. **Create a Vite plugin** at `examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts`. The module must export a function named `caddyPlugin`. When called, `caddyPlugin()` must return a valid Vite `Plugin` object with:
   - `name`: `"vite-plugin-caddy"`
   - `configureServer`: a function
   - `buildEnd`: a function

2. **Wire the plugin into `examples/tanstack-db-web-starter/vite.config.ts`**: import `caddyPlugin` and add `caddyPlugin()` to the plugins array. The config must also set `server.host` to `true` (i.e., the literal config `host: true`) so Caddy can proxy correctly.

3. **Fix the inaccurate slow-shapes tip in `AGENTS.md`** at the repo root — the outdated text containing `UPGRADE!` must be removed entirely. Replace it with accurate information that mentions both **HTTP/2** and **proxy** as the fix for slow shapes.

4. **Update `examples/tanstack-db-web-starter/README.md`** to document Caddy. The README must:
   - Mention **Caddy** by name
   - Mention **HTTP/2**
   - Explain the HTTP/1.1 connection limit problem (e.g., multiplexing, connection limits, or 6 concurrent/simultaneous connections)
   - Include the **`caddy trust`** command as a setup step

Read the project's `AGENTS.md` and `examples/tanstack-db-web-starter/AGENTS.md` for coding conventions and architecture patterns before starting.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
