# Bug: OpenTelemetry span names missing route when handler is invoked directly

## Context

Next.js exports `handler` functions from build templates (`app-page.ts`, `app-route.ts`, `pages-api.ts`) and the pages handler (`pages-handler.ts`). These handlers can be invoked directly by custom entrypoint servers — without going through `base-server` — for use cases like adapter deployments on platforms like Vercel.

## Problem

When a `handler` export is called directly (not wrapped by `base-server`), the OpenTelemetry span names only contain the HTTP method (e.g., `"GET"`) instead of the full route path (e.g., `"GET /app/[param]/rsc-fetch"`). This makes the spans nearly useless for observability because you can't tell which route was hit.

The root cause is in the span-naming logic inside each handler template. Currently, the code only sets proper route attributes on the span when `rootSpanAttributes.get('next.route')` returns a value. When the handler is invoked outside of `base-server`, this attribute is never set, so the span falls through to a minimal name with just the method.

## Affected files

- `packages/next/src/build/templates/app-page.ts` — the app page handler template
- `packages/next/src/build/templates/app-route.ts` — the app route handler template
- `packages/next/src/build/templates/pages-api.ts` — the pages API handler template
- `packages/next/src/server/route-modules/pages/pages-handler.ts` — the pages SSR handler

Each of these files has a section that creates/updates OpenTelemetry spans. The span-naming logic needs to reliably include the route path regardless of whether `base-server` has set `next.route` in the root span attributes.

Additionally, in `pages-handler.ts`, there's a code path that decides whether to create a new trace span or reuse an existing active span. This branching logic also needs to correctly handle the direct-invocation case where `base-server` is not wrapping the call.

## Expected behavior

When handlers are invoked directly by a custom entrypoint server:
1. Span names should include both the method and the route (e.g., `"GET /app/[param]/rsc-fetch"`)
2. Span attributes `next.route`, `http.route`, and `next.span_name` should always be set
3. Parent span names should be propagated correctly
