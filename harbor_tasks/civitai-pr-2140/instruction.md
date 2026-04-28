# Fix Follower Notification Timeout Death Spiral

## Problem

Follower notification queries (`new-model-from-following` and `new-model-version`) in the send-notifications job have been timing out since April 3-4, blocking all follower notifications platform-wide. Over 140 timeout errors have been observed in production monitoring.

**Root cause**: The `new-model-from-following` query performs a full sequential scan of 620K+ rows on every notification run because there is no database index on the `Model` table covering the `status` and `publishedAt` columns.

**Death spiral**: When the query times out, the cursor (stored in the `KeyValue` table under `last-sent-notification-new-model-from-following` and `last-sent-notification-new-model-version`) never advances. On the next job execution (every minute), the window between the stuck cursor and the current time grows even larger, guaranteeing another timeout. This creates an unrecoverable feedback loop.

## Desired Behavior

1. **Database index**: There must be a database index `Model_status_publishedAt_idx` on `Model(status, publishedAt)` to eliminate the full table scan on the `new-model-from-following` query.

2. **Window capping**: The notification job must cap query windows to a maximum duration using a constant `MAX_NOTIFICATION_WINDOW_MS` set to `10 * 60 * 1000` (10 minutes in milliseconds). When the cursor has fallen behind by more than this amount, the query window should be limited to the most recent 10 minutes, allowing the system to catch up incrementally over subsequent runs. An `effectiveNow` field should be added to the `NotificationProcessorRunInput` type to support this window capping — it represents the upper bound for the query window and should be used in SQL queries instead of bare `now()` calls.

3. **SQL query updates**: All notification SQL queries in the model notifications processor (`new-model-version`, `new-model-from-following`, `early-access-complete`) must use the `effectiveNow` parameter for their upper time bound instead of Postgres `now()`. This allows the window capping mechanism to control the query range.

4. **Lookback buffer**: The `new-model-from-following` query must include a `59-second` lookback buffer (subtracting `interval '59 second'` from the cursor timestamp) to handle a race condition between the `send-notifications` and `process-scheduled-publishing` jobs, which both run on a `*/1 * * * *` cron schedule. Without this buffer, a model published just before the cursor advances can be permanently missed.

5. **Timeout safety valve**: When a notification query times out but the window was already capped, the cursor should still be advanced to the capped `effectiveNow` value rather than remaining stuck. This prevents a single persistent issue from permanently stalling notifications.

6. **Logging**: When the window is capped, a warning log event with the name `Notification window capped` should be emitted to Axiom (via `logToAxiom`). When a capped query times out, an error log with the name `Notification query timed out with capped window - advancing cursor` should be emitted.

## Verification

After implementing the fix, the following must pass:
- The modified notification source files must pass ESLint and Prettier formatting checks
- The migration file must be present in `prisma/migrations/`

The codebase uses TypeScript, Prisma ORM, and Express-style server jobs. The notification system uses `createNotificationProcessor` with `prepareQuery` functions that return SQL template strings. The notification processing types are defined in the `NotificationProcessorRunInput` type. The `send-notifications` job runs via `createJob` at 1-minute intervals.

## Code Style Requirements

- **ESLint**: All files must pass `npx eslint` (or `pnpm run lint` which uses Next.js lint)
- **Prettier**: All files must pass `pnpm prettier --check` formatting
