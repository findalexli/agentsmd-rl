# Multi-level .localhost subdomains blocked by dev origin check

## Problem

The Next.js dev server blocks requests from multi-level `.localhost` subdomains like `sub.app.localhost` or `a.b.c.localhost`, returning a 403 Forbidden response. All `.localhost` domains resolve to loopback (127.0.0.1) per RFC 6761, so they should be considered safe in development.

Single-level subdomains like `app.localhost` work fine, but as soon as there is more than one subdomain level, the request is rejected by the cross-site origin protection.

## Expected Behavior

Any depth of `.localhost` subdomain should be automatically allowed during development, since they all resolve to loopback regardless of nesting depth.

## Files to Look At

- `packages/next/src/server/lib/router-utils/block-cross-site-dev.ts` — constructs the built-in dev origin allowlist and enforces cross-origin blocking
- `packages/next/src/server/app-render/csrf-protection.ts` — implements `matchWildcardDomain` which supports both single-level and multi-level wildcard patterns
