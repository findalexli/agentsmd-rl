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
1. Span names should include both the method and the route (e.g., `"GET /app/[param]/rsc-fetch"`). When `rootSpanAttributes.get('next.route')` returns nothing (as happens when `base-server` is not wrapping the call), the route must fall back to other available identifiers such as `normalizedSrcPage` or `srcPage`. The resulting route must be a non-empty string starting with `/`.
2. Span attributes `next.route`, `http.route`, and `next.span_name` should always be set unconditionally — do NOT guard the span attribute assignment inside `if (route)`. The `http.route` attribute must be set on the parent span via `parentSpan.setAttribute('http.route', route)` regardless of whether the route came from `rootSpanAttributes` or a fallback.
3. In `pages-handler.ts`, the branching logic that decides whether to reuse an existing active span must correctly detect whether the handler is wrapped by `base-server` (look for variables such as `isWrappedByNextServer` that reflect this wrapping state). A bare `if (activeSpan)` without wrapping detection is insufficient.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
