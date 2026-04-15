# SQL injection in database queue message queries

## Problem

Several queue message operations in Supabase Studio construct SQL queries by directly interpolating user-controlled values into template strings without any sanitization. This means a payload containing a single quote (e.g. `{"key": "it's a value"}`) will break the query and could allow arbitrary SQL execution.

The affected operations are:
- **Sending a queue message** — the `payload` and `delay` fields are arbitrary user-provided values, directly interpolated into the SQL string
- **Querying queue messages with pagination** — the `afterTimestamp` value is interpolated into a WHERE clause without escaping
- **Archiving a queue message** — `queueName` and `messageId` are interpolated raw
- **Deleting a queue message** — same raw interpolation of `queueName` and `messageId`

## Expected Behavior

All user-controlled string values must be properly escaped before being interpolated into SQL. The Supabase codebase provides a `literal()` escaping function (from the `pg-format` module) that handles:
- Strings: doubles embedded single quotes (e.g., `"it's a value"` → `'it''s a value'`)
- Objects: serializes to JSON with a `::jsonb` cast suffix
- `null`: outputs the SQL keyword `NULL` (unquoted)
- Numbers: outputs the plain numeric string (unquoted)

Numeric values should be safely handled to prevent edge cases. The queue operations should work correctly with payloads containing special characters like single quotes.

## Files to Look At

- `apps/studio/data/database-queues/database-queue-messages-send-mutation.ts` — sends a message to a queue via `pgmq.send()`, needs to escape `queueName`, `payload`, and `delay`
- `apps/studio/data/database-queues/database-queue-messages-infinite-query.ts` — paginated query with `afterTimestamp` filter, needs to escape `afterTimestamp` in a WHERE clause
- `apps/studio/data/database-queues/database-queue-messages-archive-mutation.ts` — archives a message via `pgmq.archive()`, needs to escape `queueName` and `messageId`
- `apps/studio/data/database-queues/database-queue-messages-delete-mutation.ts` — deletes a message via `pgmq.delete()`, needs to escape `queueName` and `messageId`

## Escaping Mechanism

Use the `literal()` function from the `pg-format` module (`@supabase/pg-meta/src/pg-format` or `pg-format` depending on your import path) to safely escape user-controlled values before interpolating them into SQL template strings. Each user-controlled parameter in the SQL call should be wrapped in `literal()` — for example: `literal(queueName)`, `literal(payload)`, `literal(delay)`, `literal(messageId)`, `literal(afterTimestamp)`.