# Task: Fold unreleased RunState schema changes into 1.8

## Context

The OpenAI agents-js repository uses a schema versioning system for RunState serialization in `packages/agents-core/src/runState.ts`. Schema versions track changes to the serialized run state format.

## What needs to be done

The repository currently has two pending unreleased schema changes:
- Schema version **1.8**: Adds tool search item variants to serialized run state payloads
- Schema version **1.9**: Adds batched computer actions and GA computer tool aliasing

Both of these schema versions exist only on the current branch and have not been released to any external consumer yet. Since there is no released or otherwise supported durable-state consumer that depends on either version, these two schema changes should be **folded into a single schema version 1.8** rather than released as separate 1.8 and 1.9 steps.

## Specific changes required

The code changes center on `packages/agents-core/src/runState.ts`. Currently `CURRENT_SCHEMA_VERSION` is `'1.9'`, `SUPPORTED_SCHEMA_VERSIONS` includes `'1.8'` as a separate supported version, and `assertSchemaVersionSupportsToolSearch` treats both `'1.8'` and `'1.9'` as tool-search-capable schema versions.

After this change:
- `CURRENT_SCHEMA_VERSION` should be `'1.8'`
- `SUPPORTED_SCHEMA_VERSIONS` should not contain `'1.8'` as a separate entry (it is now the current version) and should not contain `'1.9'` at all
- `assertSchemaVersionSupportsToolSearch` should accept only `'1.8'` and should reject `'1.9'`
- The version history comment describing schema `1.8` should cover the full combined set of changes (tool search item variants, batched computer actions, and GA computer tool aliasing)

Additionally:
- Update the implementation strategy guidance to clarify that unreleased post-tag formats can be rewritten directly when no supported snapshot consumer exists yet
- Add a changeset file under `.changeset/`

## How to validate

Run `pnpm -F agents-core build` to verify the TypeScript compiles correctly. Run `pnpm -F agents-core build-check` to verify type validation passes.

The existing test suite (if any) should continue to pass.

## Notes

- This is an unreleased change on a branch - there is no released consumer depending on either 1.8 or 1.9 schema versions
- The implementation strategy for this repository advises: *interfaces introduced or changed after the latest release tag may be rewritten without compatibility shims unless they already have a released or otherwise supported durable-state consumer*
- Focus on the `runState.ts` file for the functional code changes
