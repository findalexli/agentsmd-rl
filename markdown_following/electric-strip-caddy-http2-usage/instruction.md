# Remove Caddy HTTP/2 proxy from examples and documentation

## Problem

The project currently uses Caddy as a reverse proxy to provide HTTP/2 support for local development. This was needed because browsers limit HTTP/1.1 to 6 concurrent connections per domain, and Electric shapes load over HTTP — so without HTTP/2, shapes appear slow in local dev.

However, the `@electric-sql/client` package now supports subdomain sharding (as of v1.0.13), which automatically bypasses the browser's HTTP/1.1 connection limits without needing an external proxy. The Caddy dependency is now unnecessary.

## Symptom

Several files throughout the repository still reference Caddy:
- The tanstack-db-web-starter example has a Vite plugin that auto-starts Caddy
- The burn example includes a Caddyfile
- Multiple READMEs document Caddy installation and setup, including `### Caddy` sections, `caddy trust` commands, and `caddy start` instructions
- The root AGENTS.md troubleshooting section uses the phrase `HTTP/2 proxy (Caddy/nginx)` to recommend a local proxy
- The troubleshooting docs suggest to `run Caddy` as a workaround

## Expected Behavior

All Caddy-related code, configuration, and documentation should be removed. The examples should be updated to use `@electric-sql/client` v1.0.13 or later, which handles connection multiplexing automatically via subdomain sharding.

After updating the code, documentation and agent instruction files should be updated to reflect the new approach. Specifically:

- **tanstack-db-web-starter vite.config.ts** should not import any Caddy plugin and should not set `server.host: true`
- **tanstack-db-web-starter README.md** should direct users to `localhost:5173` (not the old Caddy HTTPS domain at `tanstack-start-db-electric-starter.localhost`)
- **burn README.md** should reference `localhost:4000` directly (not port `4001` via a Caddy proxy, and should not instruct to start Caddy)
- **Both example package.json files** should depend on `@electric-sql/client` version `^1.0.13` or later
- **AGENTS.md** should mention `@electric-sql/client` v1.0.13 as the fix (not HTTP/2 proxy via Caddy/nginx)
- **website troubleshooting docs** should describe subdomain sharding as the solution and mention client v1.0.13 (not recommend running Caddy)