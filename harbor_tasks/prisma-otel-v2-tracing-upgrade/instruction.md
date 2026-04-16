# Upgrade OpenTelemetry SDK v1 → v2 in Tracing Tests and Documentation

## Problem

The `@opentelemetry/resources`, `@opentelemetry/sdk-trace-base`, and `@opentelemetry/semantic-conventions` packages have been upgraded to their v2 major versions. Several APIs used throughout the tracing test files and the `@prisma/instrumentation` README now emit deprecation warnings or will be removed in future releases. The code must be updated to use the v2 SDK APIs.

## Migration Points

The following API patterns are deprecated or removed in the v2 OpenTelemetry SDK and must be migrated:

1. **`@opentelemetry/resources`**: The v1 pattern for creating a Resource object is no longer available in v2. The v2 SDK uses a factory function to produce Resource instances from attribute maps.

2. **`@opentelemetry/semantic-conventions`**: The v1 constant names for service name and version attributes have been replaced with different names in v2.

3. **`@opentelemetry/sdk-trace-base` + `@opentelemetry/api`**: The v1 pattern for initializing a tracer provider—adding span processors to a registered provider and calling a registration method—is deprecated in v2. The v2 SDK passes span processors as a constructor option and uses a different API for global provider registration.

4. **`@opentelemetry/sdk-trace-base`**: The v2 SDK's `ReadableSpan` interface exposes parent span information through a different property path than v1.

## Scope

Update the following files to use v2-compatible OpenTelemetry SDK APIs (no deprecated v1 patterns):
- `packages/client/tests/functional/tracing-disabled/tests.ts`
- `packages/client/tests/functional/tracing-filtered-spans/tests.ts`
- `packages/client/tests/functional/tracing-no-sampling/tests.ts`
- `packages/client/tests/functional/tracing/tests.ts`
- `packages/instrumentation/README.md`

The README's Jaeger tracing example code must be updated to use the current v2 SDK APIs.

## Verification

After migration:
- No `new Resource(` constructor calls should remain (v1 pattern)
- No `SEMRESATTRS_*` constant references should remain (v1 names)
- No `addSpanProcessor` method calls should remain (v1 pattern)
- No `.register()` calls on providers should remain (v1 pattern)
- No bare `parentSpanId` property accesses should remain (v1 API)
- All files should use the v2 SDK factory functions and constants
- All TypeScript test files must have valid syntax and compile successfully