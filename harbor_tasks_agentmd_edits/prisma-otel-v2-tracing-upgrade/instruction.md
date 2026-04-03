# Upgrade OpenTelemetry SDK v1 → v2 in Tracing Tests and Documentation

## Problem

The `@opentelemetry/resources`, `@opentelemetry/sdk-trace-base`, and `@opentelemetry/semantic-conventions` packages have been upgraded to their v2 major versions. Several APIs used throughout the tracing test files and the `@prisma/instrumentation` README are now deprecated and need to be migrated to their v2 replacements.

The affected deprecated APIs include:
- `new Resource({...})` from `@opentelemetry/resources` — replaced by a new factory function
- `SEMRESATTRS_SERVICE_NAME` / `SEMRESATTRS_SERVICE_VERSION` from `@opentelemetry/semantic-conventions` — replaced by shorter constant names
- `basicTracerProvider.addSpanProcessor(...)` followed by `basicTracerProvider.register()` — the v2 SDK uses a different initialization pattern
- `span.parentSpanId` — the v2 SDK accesses parent span info through a different property

## Expected Behavior

All four tracing functional test files should be updated to use the OpenTelemetry SDK v2 APIs consistently. The `@prisma/instrumentation` package README should also be updated so that its Jaeger example code reflects the new API patterns.

## Files to Look At

- `packages/client/tests/functional/tracing-disabled/tests.ts` — tracing disabled scenario
- `packages/client/tests/functional/tracing-filtered-spans/tests.ts` — filtered spans scenario
- `packages/client/tests/functional/tracing-no-sampling/tests.ts` — zero-sampling scenario
- `packages/client/tests/functional/tracing/tests.ts` — main tracing test (also uses parent span filtering)
- `packages/instrumentation/README.md` — Jaeger tracing example code shown to users

After fixing the code, update the `packages/instrumentation/README.md` to reflect the new SDK patterns. The example code should match how the tracing setup is actually done in the test files.
