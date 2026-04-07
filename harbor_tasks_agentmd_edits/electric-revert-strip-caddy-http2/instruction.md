# Fix Slow Electric Shapes in Local Development

## Problem

Local development with Electric SQL suffers from slow shape loading. Browsers limit HTTP/1.1 to 6 concurrent connections per domain, which bottlenecks shape subscriptions. The current `AGENTS.md` at the repo root incorrectly states this is "Fixed by default in `@electric-sql/client` v1.0.13+ UPGRADE!" — this is wrong and misleading.

The `examples/tanstack-db-web-starter/` project needs HTTP/2 proxy support integrated into its Vite dev server workflow to work around this browser limitation.

## What to Do

1. **Create a Vite plugin** at `examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts` that integrates Caddy as an HTTP/2 reverse proxy. The plugin should auto-start Caddy when the Vite dev server starts, generate an appropriate Caddyfile based on the project name and port, override Vite's URL display, and handle process cleanup on exit.

2. **Wire the plugin into `examples/tanstack-db-web-starter/vite.config.ts`**, importing and activating it in the plugins array. Also enable `server.host: true` so Caddy can proxy correctly.

3. **Fix the inaccurate slow-shapes tip in `AGENTS.md`** at the repo root — replace the "v1.0.13+ UPGRADE!" text with accurate information about the HTTP/1.1 connection limit and the HTTP/2 proxy fix.

4. **Update `examples/tanstack-db-web-starter/README.md`** to document Caddy as a prerequisite. Explain why HTTP/2 is needed (multiplexing bypasses the 6-connection limit), include setup instructions (`caddy trust`), and add troubleshooting guidance for common Caddy issues.

5. **Update `website/docs/guides/troubleshooting.md`** to recommend Caddy as the solution for slow shapes in local dev.

Read the project's `AGENTS.md` and `examples/tanstack-db-web-starter/AGENTS.md` for coding conventions and architecture patterns before starting.
