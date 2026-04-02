# SQL injection in database queue message queries

## Problem

Several queue message operations in Supabase Studio construct SQL queries by directly interpolating user-controlled values into template strings without any sanitization. This means a payload containing a single quote (e.g. `{"key": "it's a value"}`) will break the query and could allow arbitrary SQL execution.

The affected operations are:
- **Sending a queue message** — the `payload` field is arbitrary user-provided JSON, directly interpolated into the SQL string
- **Querying queue messages with pagination** — the `afterTimestamp` value is interpolated into a WHERE clause without escaping
- **Archiving a queue message** — `queueName` and `messageId` are interpolated raw
- **Deleting a queue message** — same raw interpolation of `queueName` and `messageId`

## Expected Behavior

All user-controlled string values must be properly escaped before being interpolated into SQL. Numeric values should be safely handled to prevent edge cases. The queue operations should work correctly with payloads containing special characters like single quotes.

## Files to Look At

- `apps/studio/data/database-queues/database-queue-messages-send-mutation.ts` — sends a message to a queue via `pgmq.send()`
- `apps/studio/data/database-queues/database-queue-messages-infinite-query.ts` — paginated query with `afterTimestamp` filter
- `apps/studio/data/database-queues/database-queue-messages-archive-mutation.ts` — archives a message via `pgmq.archive()`
- `apps/studio/data/database-queues/database-queue-messages-delete-mutation.ts` — deletes a message via `pgmq.delete()`
