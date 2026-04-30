# Migrate google-pubsub events module to the alpha MetricsService

## Background

Backstage exposes a stable backend service `MetricsService` (currently in the
`alpha` entrypoint of `@backstage/backend-plugin-api`) for emitting application
metrics. New code is expected to depend on this service instead of reaching for
the global OpenTelemetry API directly. The
`@backstage/plugin-events-backend-module-google-pubsub` plugin still uses the
old pattern: it imports `Counter` and `metrics` from `@opentelemetry/api`,
calls `metrics.getMeter('default').createCounter(...)` inside its publishers,
and is therefore not pluggable, not testable with the standard Backstage test
mocks, and pulls in a dependency that should otherwise be unnecessary for the
plugin.

## What needs to change

Migrate the metrics integration in this plugin from the OpenTelemetry global
API to the Backstage `MetricsService`, in a way that satisfies the contract
below.

### Behavioral contract

After the change, the following must hold:

1. Both `GooglePubSubConsumingEventPublisher` and
   `EventConsumingGooglePubSubPublisher` must obtain their counters from a
   `MetricsService` instance that callers inject through the constructor /
   factory `options` object. The constructor must not look up a meter from a
   global registry.
2. The injected `MetricsService` must come from the `alpha` entrypoint of
   `@backstage/backend-plugin-api` (i.e. `MetricsService` /
   `MetricsServiceCounter`) and the corresponding service ref
   (`metricsServiceRef`, also from the `alpha` entrypoint) must be wired into
   the plugin's backend module dependency declaration so the framework
   provides it at runtime.
3. The counter created by `GooglePubSubConsumingEventPublisher` must be named
   `events.google.pubsub.consumer.messages.total`.
4. The counter created by `EventConsumingGooglePubSubPublisher` must be named
   `events.google.pubsub.publisher.messages.total`.
5. Both counters must be created with the unit string `{message}` (the
   UCUM-style annotation for "messages"). The previous unit value `short` is
   no longer correct.
6. The counter type must carry the attribute shape
   `{ subscription: string; status: string }`. Calls that record a sample
   (`counter.add(1, { subscription, status })`) must keep working.
7. `@opentelemetry/api` must be removed from the plugin's `package.json`
   `dependencies` (and `devDependencies`) since the plugin no longer needs it
   at runtime or in tests.
8. The plugin's existing unit tests under `src/**/*.test.ts` must continue to
   pass. Update any test setup that constructs a publisher so it provides the
   new injected metrics service — the mock `metricsServiceMock` exported from
   `@backstage/backend-test-utils/alpha` is the intended way to do this.

You do not need to add new behaviour beyond what the migration requires. The
counters' descriptions, attribute keys, and call sites should otherwise stay
the same.

## Where to make changes

This is a contained change inside one plugin:

- `plugins/events-backend-module-google-pubsub/`

There are two publisher classes (`GooglePubSubConsumingEventPublisher` and
`EventConsumingGooglePubSubPublisher`), each with its own backend-module
registration file, plus the plugin's `package.json`.

## Code Style Requirements

The plugin runs `backstage-cli package lint` (Backstage's eslint configuration
on top of `@backstage/eslint-config`, with notice/license-header checks
included) and `backstage-cli package test` (jest). Before submitting, your
changes must:

- Pass `yarn backstage-cli package lint` for this plugin (no eslint errors,
  including the notice/license header rule).
- Pass `yarn backstage-cli package test` for this plugin (all jest suites
  green).

Match the existing coding style of the surrounding files: license header at
the top of every new TypeScript file, `import type` for type-only imports
where appropriate, and 2-space indentation.

## Changeset

Backstage requires every change that affects a published package to ship with
a `.changeset/*.md` entry. Add one targeting
`@backstage/plugin-events-backend-module-google-pubsub` at `patch` level that
briefly describes the migration for adopters.
