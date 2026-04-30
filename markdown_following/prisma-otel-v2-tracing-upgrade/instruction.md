# Upgrade OpenTelemetry SDK v1 → v2 in Tracing Tests and Documentation

## Problem

The `@opentelemetry/resources`, `@opentelemetry/sdk-trace-base`, and `@opentelemetry/semantic-conventions` packages have been upgraded to their v2 major versions. Several APIs used throughout the tracing test files and the `@prisma/instrumentation` README now emit deprecation warnings or will be removed in future releases. The code must be updated to use the v2 SDK APIs.

The v2 SDK API surface is documented in the published npm packages. See the OpenTelemetry JS SDK v2 migration guidance at: https://www.npmjs.com/package/@opentelemetry/sdk-trace-base

## Migration Points

The following API patterns are deprecated or removed in the v2 OpenTelemetry SDK and must be migrated:

1. **`@opentelemetry/resources`**: The v1 `new Resource({...})` constructor pattern is no longer available in v2. The v2 SDK exports a factory function `resourceFromAttributes` that produces Resource instances from plain attribute objects.

2. **`@opentelemetry/semantic-conventions`**: The v1 constant names `SEMRESATTRS_SERVICE_NAME` and `SEMRESATTRS_SERVICE_VERSION` have been replaced in v2 with `ATTR_SERVICE_NAME` and `ATTR_SERVICE_VERSION`.

3. **`@opentelemetry/sdk-trace-base` + `@opentelemetry/api`**: The v1 pattern of calling `addSpanProcessor()` on a provider and then calling `.register()` is deprecated in v2. The v2 SDK requires passing span processors via the `spanProcessors` constructor option and uses `trace.setGlobalTracerProvider()` for global provider registration.

4. **`@opentelemetry/sdk-trace-base`**: The v2 SDK's `ReadableSpan` interface exposes parent span information through the `parentSpanContext?.spanId` property path instead of the v1 bare `parentSpanId` property.

## Scope

Update the Prisma client's tracing functional test files and the instrumentation README to use v2-compatible OpenTelemetry SDK APIs (no deprecated v1 patterns):

- The tracing-disabled functional test
- The tracing-filtered-spans functional test
- The tracing-no-sampling functional test
- The tracing functional test
- The instrumentation package README (Jaeger tracing example code)

All files are within the `packages/` directory of the prisma/prisma monorepo. The TypeScript test files are under the client functional test tree; the README is in the instrumentation package.

## Verification

After migration:
- No `new Resource(` constructor calls should remain (v1 pattern)
- No `SEMRESATTRS_*` constant references should remain (v1 names)
- No `addSpanProcessor` method calls should remain (v1 pattern)
- No `.register()` calls on providers should remain (v1 pattern)
- No bare `parentSpanId` property accesses should remain (v1 API)
- All files should use `resourceFromAttributes` for Resource creation (v2)
- All files should use `ATTR_SERVICE_NAME` and `ATTR_SERVICE_VERSION` constants (v2)
- All files should pass `spanProcessors` as a constructor option (v2)
- All files should use `trace.setGlobalTracerProvider()` for provider registration (v2)
- All files should use `parentSpanContext?.spanId` for parent span access (v2)
- All TypeScript test files must have valid syntax and compile successfully

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
