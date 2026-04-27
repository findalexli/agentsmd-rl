# Enrich PostHog organization `groupIdentify` calls

The backend telemetry service emits PostHog `groupIdentify` calls so that
organizations show up as group profiles in PostHog. Today those calls only
carry the org `name` (and even that is conditionally omitted), which makes
PostHog dashboards unable to break down org behavior by plan, deployment
type, or org age.

Enrich the `groupIdentify` payload so every emission for `groupType:
"organization"` carries the following properties:

| key | type | source |
|---|---|---|
| `name` | `string` | `event.organizationName` if set, else `org.name` looked up from the database. Omit if neither is available. |
| `is_cloud` | `boolean` | `true` when the running instance type is `InstanceType.Cloud`, otherwise `false`. Always present. |
| `plan` | `string` | The plan `slug` from the license service. When the license server returns a `null` slug (e.g. self-hosted on the on-prem feature fallback), default to the literal string `"free"`. |
| `seat_count` | `number` | The `membersUsed` field from the org's current plan. |
| `created_at` | `string` | The org's creation timestamp in ISO 8601 format (i.e. the result of calling `.toISOString()` on the stored `createdAt`). |

The same enriched payload must be emitted from **both** call sites that
currently emit `groupIdentify` for `groupType: "organization"`:

1. The direct (non-aggregated) telemetry path used when an event arrives
   one at a time.
2. The aggregated path that flushes batched events from the keystore in
   buckets.

## Behavioral requirements

- **Always include `properties`** — the payload must always contain at
  least `is_cloud`, regardless of whether the org name is known. The
  prior behavior of conditionally omitting `properties` when the name was
  unknown is no longer acceptable.

- **Resilient enrichment** — the database lookup (org row) and the
  license-service call (plan) must each be guarded so that a failure in
  one does not prevent the other fields, or `is_cloud`, from being
  emitted. A failure should be logged and the call should continue to
  emit whatever properties were resolved (`is_cloud` is always
  resolvable).

- **Per-bucket caching in the aggregated path** — within a single
  invocation of the bucket-flush routine, looking up the same
  organization more than once is wasteful: every event in a bucket goes
  through the same flush and many users typically share the same org. In
  the aggregated path, look up each org's enrichment **at most once per
  bucket flush** even when multiple users in that bucket share the same
  organization. Different bucket flushes need not share state.

- **Non-blocking in the direct path** — `sendPostHogEvents` is awaited by
  ~50 HTTP route handlers. The new enrichment work (DB + license-server
  calls) must not block the HTTP response: in the direct path, fire the
  enrichment and the resulting `groupIdentify` asynchronously without
  awaiting them on the request path. Errors in the asynchronous chain
  must still be logged.

## Wiring

The telemetry service is constructed via a factory in
`backend/src/services/telemetry/telemetry-service.ts`. To do the
enrichment you will need access to the org's database row (via the
existing org DAL) and to the plan from the license service. Both are
already instantiated in the dependency-injection wiring at
`backend/src/server/routes/index.ts`. Add the necessary dependency to
the factory's typed `TTelemetryServiceFactoryDep` contract — the
license-service `Pick<...>` already narrows the surface area; widen it
to expose the additional method you need, and add a new dependency for
the org DAL with the minimal `Pick<...>` covering the lookup you use.

## Code Style Requirements

The backend uses ESLint with the `simple-import-sort/imports` rule. New
imports must be placed in the correct group (third-party packages →
`@app/*` imports → relative imports). After your edits, both
`npm run lint:fix` and `npm run type:check` from the `backend/`
directory must succeed (the repo's `make reviewable-api` runs both).

## Verification

Tests verify that:

1. Both telemetry paths (direct and aggregated) emit `groupIdentify` with
   the five enriched properties listed above.
2. `is_cloud` is `false` and `plan` is `"free"` on a self-hosted instance
   whose plan slug is `null`.
3. The aggregated path performs the org lookup at most once per
   organization within a single bucket flush, regardless of how many
   users in that bucket belong to the org.
4. A thrown error from the org-row lookup does not prevent
   `is_cloud`/`plan`/`seat_count`/`name` from being emitted.
5. The whole backend still type-checks (`npm run type:check`).
