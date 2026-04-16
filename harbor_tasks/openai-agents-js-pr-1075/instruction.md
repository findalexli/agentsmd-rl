# Task: Fold unreleased RunState schema changes into 1.8

## Context

The OpenAI agents-js repository uses a schema versioning system for RunState serialization in `packages/agents-core/src/runState.ts`. Schema versions track changes to the serialized run state format.

## What needs to be done

The repository currently has two pending unreleased schema changes:
- Schema version **1.8**: Adds tool search item variants to serialized run state payloads
- Schema version **1.9**: Adds batched computer actions and GA computer tool aliasing

Both of these schema versions exist only on the current branch and have not been released to any external consumer yet. Since there is no released or otherwise supported durable-state consumer that depends on either version, these two schema changes should be **folded into a single schema version 1.8** rather than released as separate 1.8 and 1.9 steps.

## Specific changes required

1. **Schema version constant** (`packages/agents-core/src/runState.ts`):
   - `CURRENT_SCHEMA_VERSION` should be changed to `'1.8'` (currently `'1.9'`)
   - The version 1.8 comment should be updated to include all pending changes

2. **Supported versions list** (`packages/agents-core/src/runState.ts`):
   - Remove `'1.8'` from `SUPPORTED_SCHEMA_VERSIONS` (since it's now the CURRENT_SCHEMA_VERSION)
   - Remove `'1.9'` entirely since it's being folded into 1.8

3. **Assertion function** (`packages/agents-core/src/runState.ts`):
   - The `assertSchemaVersionSupportsToolSearch` function should only accept `'1.8'`, not `'1.8'` or `'1.9'`

4. **Documentation**:
   - Update the implementation strategy guidance to clarify that unreleased post-tag formats can be rewritten directly when no supported snapshot consumer exists yet
   - Add a changeset file under `.changeset/`

## How to validate

Run `pnpm -F agents-core build` to verify the TypeScript compiles correctly.

The existing test suite (if any) should continue to pass.

## Notes

- This is an unreleased change on a branch - there is no released consumer depending on either 1.8 or 1.9 schema versions
- The implementation strategy for this repository advises: *interfaces introduced or changed after the latest release tag may be rewritten without compatibility shims unless they already have a released or otherwise supported durable-state consumer*
- Focus on the `runState.ts` file for the functional code changes
