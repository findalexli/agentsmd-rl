# Upgrade OpenTelemetry dependencies and refresh tracing setup

## Problem

The project's OpenTelemetry dependencies (`@opentelemetry/resources`, `@opentelemetry/sdk-trace-base`, `@opentelemetry/semantic-conventions`, etc.) are on older v1.x versions. The `@opentelemetry/sdk-trace-base` v2 introduced breaking API changes:

- `Resource` constructor replaced by `resourceFromAttributes()` function
- `SEMRESATTRS_SERVICE_NAME` / `SEMRESATTRS_SERVICE_VERSION` renamed to `ATTR_SERVICE_NAME` / `ATTR_SERVICE_VERSION`
- `BasicTracerProvider.addSpanProcessor()` replaced by `spanProcessors` constructor option
- `provider.register()` replaced by `trace.setGlobalTracerProvider(provider)`
- `span.parentSpanId` replaced by `span.parentSpanContext?.spanId`

The client tracing functional tests and the `@prisma/instrumentation` package README both use the old APIs.

## Expected Behavior

- All `@opentelemetry/*` dependencies in `packages/client/package.json` and `packages/query-plan-executor/package.json` should be upgraded to their latest compatible versions
- The four tracing functional test files under `packages/client/tests/functional/tracing*/` must be updated to use the new v2 SDK APIs
- The `packages/instrumentation/README.md` Jaeger tracing example must be updated to reflect the new configuration patterns so developers following the documentation get working code

## Files to Look At

- `packages/client/package.json` — OpenTelemetry dependency versions
- `packages/query-plan-executor/package.json` — OpenTelemetry dependency versions
- `packages/client/tests/functional/tracing-disabled/tests.ts` — tracing disabled test setup
- `packages/client/tests/functional/tracing-filtered-spans/tests.ts` — filtered spans test setup
- `packages/client/tests/functional/tracing-no-sampling/tests.ts` — no-sampling test setup
- `packages/client/tests/functional/tracing/tests.ts` — main tracing test (also uses `parentSpanId`)
- `packages/instrumentation/README.md` — Jaeger setup example code that users follow
