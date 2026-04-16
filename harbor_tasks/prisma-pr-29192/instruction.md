# Null Handling Bug in adapter-ppg Type Parsers

## Problem

The PPG (Prisma Postgres Serverless) driver adapter crashes with a `TypeError` when querying models with nullable columns of certain types. The error occurs because the PPG client passes `null` values through to type parsers for nullable columns, unlike the standard pg client.

When a nullable `DateTime`, `TimeTZ`, `Money`, or `Bytea` column contains a null value in the database, the type parser functions crash with errors like:

- `TypeError: Cannot read properties of null (reading 'replace')`
- `TypeError: Cannot read properties of null (reading 'slice')`

This affects the following parser functions in `packages/adapter-ppg/src/conversion.ts`:

- `normalize_timestamp`
- `normalize_timestamptz`
- `normalize_timez`
- `normalize_money`
- `convertBytes`

And their corresponding array parsers.

## Expected Behavior

When a null value is passed to any of these type parsers, they should gracefully return `null` instead of crashing. The parsers should also continue to work correctly with non-null values.

## File to Fix

`packages/adapter-ppg/src/conversion.ts`

## Hint

Look at how `normalize_bool` already handles null values and apply similar null guards to the other parser functions.
