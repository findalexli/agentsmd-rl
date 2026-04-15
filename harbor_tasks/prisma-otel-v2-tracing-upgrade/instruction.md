# Upgrade OpenTelemetry SDK v1 → v2 in Tracing Tests and Documentation

## Problem

The `@opentelemetry/resources`, `@opentelemetry/sdk-trace-base`, and `@opentelemetry/semantic-conventions` packages have been upgraded to their v2 major versions. Several APIs used throughout the tracing test files and the `@prisma/instrumentation` README are now deprecated and need to be migrated to their v2 replacements.

The deprecated v1 APIs and their v2 equivalents are documented below. Each migration point must be updated in all affected files.

### 1. Resource creation (`@opentelemetry/resources`)

The v1 constructor `new Resource({...})` is removed. The v2 SDK exports a factory function `resourceFromAttributes({...})` that serves the same purpose.

### 2. Semantic convention constants (`@opentelemetry/semantic-conventions`)

The v1 constants `SEMRESATTRS_SERVICE_NAME` and `SEMRESATTRS_SERVICE_VERSION` are removed. The v2 SDK exports `ATTR_SERVICE_NAME` and `ATTR_SERVICE_VERSION` as their replacements.

### 3. Provider initialization (`@opentelemetry/sdk-trace-base` + `@opentelemetry/api`)

The v1 pattern of calling `provider.addSpanProcessor(processor)` followed by `provider.register()` is deprecated. In v2:
- Span processors are passed as a `spanProcessors` array in the `BasicTracerProvider` constructor options.
- Global provider registration uses `trace.setGlobalTracerProvider(provider)`, where `trace` is imported from `@opentelemetry/api`.

### 4. Parent span access

The `span.parentSpanId` property is removed in the v2 SDK. Parent span IDs are now accessed via `span.parentSpanContext?.spanId` through the `parentSpanContext` property on `ReadableSpan`.

## Scope

All four tracing functional test files and the instrumentation README must be updated:
- `packages/client/tests/functional/tracing-disabled/tests.ts`
- `packages/client/tests/functional/tracing-filtered-spans/tests.ts`
- `packages/client/tests/functional/tracing-no-sampling/tests.ts`
- `packages/client/tests/functional/tracing/tests.ts`
- `packages/instrumentation/README.md` — the Jaeger tracing example code must reflect the v2 API patterns
