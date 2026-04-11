# Remove Caddy HTTP/2 proxy from examples and documentation

## Problem

The project currently uses Caddy as a reverse proxy to provide HTTP/2 support for local development. This was needed because browsers limit HTTP/1.1 to 6 concurrent connections per domain, and Electric shapes load over HTTP — so without HTTP/2, shapes appear slow in local dev.

However, the `@electric-sql/client` package now supports subdomain sharding (as of v1.0.13), which automatically bypasses the browser's HTTP/1.1 connection limits without needing an external proxy. The Caddy dependency is now unnecessary.

Several examples still reference Caddy:
- The tanstack-db-web-starter example includes a Vite plugin (`src/vite-plugin-caddy.ts`) that auto-starts Caddy
- The burn example includes a `Caddyfile`
- Multiple READMEs document Caddy installation and setup
- The root `AGENTS.md` troubleshooting section recommends using Caddy/nginx as an HTTP/2 proxy

## Expected Behavior

All Caddy-related code, configuration, and documentation should be removed. The examples should be updated to use `@electric-sql/client` v1.0.13 or later, which handles connection multiplexing automatically. Documentation should reflect that subdomain sharding is now the recommended solution.

## Files to Look At

- `examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts` — Caddy Vite plugin to remove
- `examples/tanstack-db-web-starter/vite.config.ts` — imports the Caddy plugin
- `examples/tanstack-db-web-starter/package.json` — client version to bump
- `examples/tanstack-db-web-starter/README.md` — extensive Caddy documentation to remove
- `examples/burn/Caddyfile` — Caddy configuration to remove
- `examples/burn/assets/package.json` — client version to bump
- `examples/burn/README.md` — Caddy setup instructions to remove
- `AGENTS.md` — troubleshooting tip recommending Caddy/nginx proxy
- `website/docs/guides/troubleshooting.md` — Caddy setup instructions in official docs

After updating the code, make sure to update the relevant documentation and agent instruction files to reflect the new approach. The project's AGENTS.md, example READMEs, and troubleshooting guide should all be updated to remove Caddy references and document the subdomain sharding solution instead.
